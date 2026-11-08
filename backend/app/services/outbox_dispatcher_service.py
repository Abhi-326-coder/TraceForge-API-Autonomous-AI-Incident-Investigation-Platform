
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import OutboxEvent
from app.tasks.investigation_tasks import run_investigation_task


PROCESSING_TIMEOUT_SECONDS = 120


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def recover_stale_events(db: Session) -> int:
    """
    Return events stuck in PROCESSING to PENDING.

    This handles dispatcher crashes after an event was claimed.
    """
    cutoff = utc_now() - timedelta(
        seconds=PROCESSING_TIMEOUT_SECONDS
    )

    statement = (
        update(OutboxEvent)
        .where(
            OutboxEvent.status == "PROCESSING",
            OutboxEvent.locked_at < cutoff,
        )
        .values(
            status="PENDING",
            locked_at=None,
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount or 0


def claim_pending_events(
    db: Session,
    batch_size: int,
) -> list[dict]:
    """
    Atomically claim a batch of pending events.

    SKIP LOCKED allows multiple dispatcher processes to work
    without claiming the same rows in the same transaction.
    """
    now = utc_now()

    statement = (
        select(OutboxEvent)
        .where(OutboxEvent.status == "PENDING")
        .order_by(OutboxEvent.created_at.asc())
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )

    events = db.execute(statement).scalars().all()

    # Copy the required values before committing.
    claimed_events = [
        {
            "id": event.id,
            "event_type": event.event_type,
            "payload": event.payload,
        }
        for event in events
    ]

    for event in events:
        event.status = "PROCESSING"
        event.locked_at = now
        event.attempts += 1

    db.commit()

    return claimed_events


def mark_event_published(
    db: Session,
    event_id: int,
) -> None:
    event = db.get(OutboxEvent, event_id)

    if event is None:
        return

    event.status = "PUBLISHED"
    event.published_at = utc_now()
    event.locked_at = None

    db.commit()


def mark_event_failed(
    db: Session,
    event_id: int,
) -> None:
    db.rollback()

    event = db.get(OutboxEvent, event_id)

    if event is None:
        return

    event.status = "PENDING"
    event.locked_at = None

    db.commit()


def publish_event(event: dict) -> None:
    """
    Route an outbox event to its corresponding Celery task.
    """
    event_type = event["event_type"]
    payload = event["payload"]

    if event_type == "INVESTIGATION_REQUESTED":
        investigation_id = payload.get("investigation_id")

        if investigation_id is None:
            raise ValueError(
                "INVESTIGATION_REQUESTED event has no investigation_id"
            )

        run_investigation_task.delay(investigation_id)
        return

    raise ValueError(f"Unsupported outbox event: {event_type}")


def dispatch_pending_events(batch_size: int = 20) -> dict:
    """
    Main dispatcher entry point.

    1. Recover stale PROCESSING events.
    2. Claim pending events.
    3. Publish each event to Celery.
    4. Mark successful events as PUBLISHED.
    5. Return failed events to PENDING.
    """
    db: Session = SessionLocal()

    published = 0
    failed = 0

    try:
        recovered = recover_stale_events(db)

        claimed_events = claim_pending_events(
            db=db,
            batch_size=batch_size,
        )

        for event in claimed_events:
            try:
                publish_event(event)

                mark_event_published(
                    db=db,
                    event_id=event["id"],
                )

                published += 1

            except Exception:
                mark_event_failed(
                    db=db,
                    event_id=event["id"],
                )

                failed += 1

        return {
            "recovered_stale_events": recovered,
            "claimed_events": len(claimed_events),
            "published_events": published,
            "failed_events": failed,
        }

    finally:
        db.close()
