from datetime import datetime, timedelta, timezone

from sqlalchemy import update, or_
from sqlalchemy.orm import Session

from app.db.models import Investigation


LEASE_SECONDS = 120


def utc_now():
    return datetime.now(timezone.utc)


def claim_investigation(
    db: Session,
    investigation_id: int,
    worker_id: str,
) -> bool:

    now = utc_now()

    statement = (
        update(Investigation)
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
            heartbeat_at=now,
            lease_expires_at=(
                now + timedelta(seconds=LEASE_SECONDS)
            ),
            started_at=now,
            completed_at=None,
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def heartbeat_investigation(
    db: Session,
    investigation_id: int,
    worker_id: str,
) -> bool:

    now = utc_now()

    statement = (
        update(Investigation)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
            Investigation.worker_id == worker_id,
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
) -> bool:

    now = utc_now()

    statement = (
        update(Investigation)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
            Investigation.worker_id == worker_id,
            Investigation.lease_expires_at > now,
        )
        .values(
            status="COMPLETED",
            completed_at=now,
            worker_id=None,
            lease_expires_at=None,
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def fail_investigation(
    db: Session,
    investigation_id: int,
    worker_id: str,
) -> bool:

    statement = (
        update(Investigation)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
            Investigation.worker_id == worker_id,
        )
        .values(
            status="FAILED",
            completed_at=utc_now(),
            worker_id=None,
            lease_expires_at=None,
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def recover_stale_investigations(
    db: Session,
) -> int:

    now = utc_now()

    statement = (
        update(Investigation)
        .where(
            Investigation.status == "RUNNING",
            Investigation.lease_expires_at < now,
        )
        .values(
            status="QUEUED",
            worker_id=None,
            lease_expires_at=None,
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount