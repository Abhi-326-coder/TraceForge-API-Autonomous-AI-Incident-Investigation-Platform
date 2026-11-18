from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, update, or_
from sqlalchemy.orm import Session

from app.db.models import Investigation, OutboxEvent
from app.services.outbox_service import create_outbox_event


LEASE_SECONDS = 120


def utc_now():
    return datetime.now(timezone.utc)


def require_active_investigation_lease(
    db: Session,
    investigation_id: int,
    worker_id: str,
    lease_token: UUID,
) -> Investigation:
    """Lock the investigation row and verify the current execution fence.

    Callers keep this transaction open through their database side effect and
    commit it together, preventing recovery or a replacement claim from
    crossing that side effect.
    """
    investigation = db.execute(
        select(Investigation)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
            Investigation.worker_id == worker_id,
            Investigation.lease_token == lease_token,
        )
        .with_for_update()
    ).scalar_one_or_none()

    expires_at = investigation.lease_expires_at if investigation else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if investigation is None or expires_at is None or expires_at <= utc_now():
        raise RuntimeError("Investigation lease is no longer owned by this worker.")

    return investigation


def claim_investigation(
    db: Session,
    investigation_id: int,
    worker_id: str,
) -> UUID | None:

    now = utc_now()
    lease_token = uuid4()

    statement = (
        update(Investigation)
        .execution_options(synchronize_session=False)
        .where(
            Investigation.id == investigation_id,
            or_(
                Investigation.status == "QUEUED",
                (
                    (Investigation.status == "RUNNING")
                    & (
                        Investigation.lease_expires_at < now
                    )
                ),
            ),
        )
        .values(
            status="RUNNING",
            worker_id=worker_id,
            lease_token=lease_token,
            heartbeat_at=now,
            lease_expires_at=(
                now + timedelta(seconds=LEASE_SECONDS)
            ),
            started_at=now,
            completed_at=None,
            failure_category=None,
            failure_message=None,
            failure_is_terminal=None,
        )
    )

    result = db.execute(statement)
    db.commit()

    return lease_token if result.rowcount == 1 else None


def heartbeat_investigation(
    db: Session,
    investigation_id: int,
    worker_id: str,
    lease_token: UUID,
) -> bool:

    now = utc_now()

    statement = (
        update(Investigation)
        .execution_options(synchronize_session=False)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
            Investigation.worker_id == worker_id,
            Investigation.lease_token == lease_token,
            Investigation.lease_expires_at > now,
        )
        .values(
            heartbeat_at=now,
            lease_expires_at=(
                now + timedelta(seconds=LEASE_SECONDS)
            ),
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def complete_investigation(
    db: Session,
    investigation_id: int,
    worker_id: str,
    lease_token: UUID,
) -> bool:

    now = utc_now()

    statement = (
        update(Investigation)
        .execution_options(synchronize_session=False)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
            Investigation.worker_id == worker_id,
            Investigation.lease_token == lease_token,
            Investigation.lease_expires_at > now,
        )
        .values(
            status="COMPLETED",
            completed_at=now,
            worker_id=None,
            lease_token=None,
            lease_expires_at=None,
            failure_category=None,
            failure_message=None,
            failure_is_terminal=None,
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def fail_investigation(
    db: Session,
    investigation_id: int,
    worker_id: str,
    lease_token: UUID,
    failure_category: str | None = None,
    failure_message: str | None = None,
    failure_is_terminal: bool = True,
) -> bool:

    now = utc_now()

    statement = (
        update(Investigation)
        .execution_options(synchronize_session=False)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
            Investigation.worker_id == worker_id,
            Investigation.lease_token == lease_token,
            Investigation.lease_expires_at > now,
        )
        .values(
            status="FAILED",
            completed_at=utc_now(),
            worker_id=None,
            lease_token=None,
            lease_expires_at=None,
            failure_category=failure_category,
            failure_message=failure_message,
            failure_is_terminal=failure_is_terminal,
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def requeue_failed_investigation_for_retry(
    db: Session,
    investigation_id: int,
) -> None:
    statement = (
        update(Investigation)
        .execution_options(synchronize_session=False)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "FAILED",
            Investigation.failure_is_terminal.is_(False),
        )
        .values(
            status="QUEUED",
            completed_at=None,
            worker_id=None,
            lease_token=None,
            lease_expires_at=None,
            failure_category=None,
            failure_message=None,
            failure_is_terminal=None,
        )
    )

    result = db.execute(statement)
    if result.rowcount != 1:
        db.rollback()
        raise RuntimeError(
            f"Unable to requeue failed investigation {investigation_id}."
        )

    db.commit()


def recover_stale_investigations(
    db: Session,
) -> int:

    now = utc_now()
    lease_metadata_present = or_(
        Investigation.worker_id.is_not(None),
        Investigation.lease_token.is_not(None),
        Investigation.heartbeat_at.is_not(None),
        Investigation.lease_expires_at.is_not(None),
    )
    invalid_running_lease = or_(
        Investigation.lease_expires_at.is_(None),
        Investigation.lease_expires_at <= now,
        Investigation.lease_token.is_(None),
        Investigation.worker_id.is_(None),
        Investigation.heartbeat_at.is_(None),
    )
    stale = db.execute(
        select(Investigation)
        .where(
            or_(
                (Investigation.status == "RUNNING") & invalid_running_lease,
                (Investigation.status == "QUEUED") & lease_metadata_present,
                (Investigation.status == "COMPLETED") & lease_metadata_present,
            ),
        )
        .order_by(Investigation.id.asc())
        .with_for_update(skip_locked=True)
    ).scalars().all()

    try:
        recovered = 0
        for investigation in stale:
            # Recheck the locked row's state before mutating it.
            lease_expiry = investigation.lease_expires_at
            if lease_expiry is not None and lease_expiry.tzinfo is None:
                lease_expiry = lease_expiry.replace(tzinfo=timezone.utc)
            status = investigation.status
            lease_invalid = (
                lease_expiry is None
                or lease_expiry <= now
                or investigation.lease_token is None
                or investigation.worker_id is None
                or investigation.heartbeat_at is None
            )
            has_stale_metadata = any((
                investigation.worker_id is not None,
                investigation.lease_token is not None,
                investigation.heartbeat_at is not None,
                investigation.lease_expires_at is not None,
            ))

            if status == "RUNNING" and not lease_invalid:
                continue
            if status == "QUEUED" and not has_stale_metadata:
                continue
            if status == "COMPLETED" and not has_stale_metadata:
                continue
            if status not in {"RUNNING", "QUEUED", "COMPLETED"}:
                continue

            # Preserve terminal status; only scrub obsolete ownership metadata.
            if status == "RUNNING":
                investigation.status = "QUEUED"
            investigation.worker_id = None
            investigation.lease_token = None
            investigation.heartbeat_at = None
            investigation.lease_expires_at = None

            if status != "COMPLETED":
                _ensure_investigation_dispatch(db, investigation)

            recovered += 1

        db.commit()
        return recovered
    except Exception:
        db.rollback()
        raise


def _ensure_investigation_dispatch(db: Session, investigation: Investigation) -> None:
    key = f"investigation-created-{investigation.id}"
    event = db.execute(
        select(OutboxEvent)
        .where(OutboxEvent.idempotency_key == key)
        .with_for_update()
    ).scalar_one_or_none()
    if event is None:
        create_outbox_event(
            db,
            event_type="INVESTIGATION_REQUESTED",
            aggregate_type="Investigation",
            aggregate_id=str(investigation.id),
            idempotency_key=key,
            payload={"investigation_id": investigation.id},
        )
    elif event.status == "PUBLISHED" or event.status not in {"PENDING", "PROCESSING"}:
        # Reuse the unique durable intent instead of adding a duplicate.
        event.status = "PENDING"
        event.locked_at = None
        event.published_at = None
