from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from app.db.database import SessionLocal
from app.db.models import OutboxEvent
from app.tasks.investigation_tasks import run_investigation_task


PROCESSING_TIMEOUT_SECONDS = 120


def utc_now():
    return datetime.now(timezone.utc)


def dispatch_pending_events(batch_size: int = 20) -> dict:
    db = SessionLocal()

    published = 0
    failed = 0

    try:
        now = utc_now()
        stale_before = now - timedelta(
            seconds=PROCESSING_TIMEOUT_SECONDS
        )

        # Recover events abandoned by a crashed dispatcher.
        db.execute(
            update(OutboxEvent)
            .where(
                OutboxEvent.status == "PROCESSING",
                OutboxEvent.locked_at < stale_before,
            )
            .values(
                status="PENDING",
                locked_at=None,
            )
        )
        db.commit()

        # Claim a batch without blocking other dispatchers.
        statement = (
            select(OutboxEvent)
            .where(OutboxEvent.status == "PENDING")
            .order_by(OutboxEvent.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        events = db.execute(statement).scalars().all()

        for event in events:
            event.status = "PROCESSING"
            event.locked_at = now

        db.commit()

        # Publish claimed events.
        for event in events:
            try:
                if event.event_type == "INVESTIGATION_REQUESTED":
                    investigation_id = event.payload[
                        "investigation_id"
                    ]

                    run_investigation_task.delay(
                        investigation_id
                    )

                else:
                    raise ValueError(
                        f"Unsupported event type: {event.event_type}"
                    )

                # Only mark published after Celery accepts the message.
                event.status = "PUBLISHED"
                event.published_at = utc_now()
                event.locked_at = None
                event.attempts += 1

                db.commit()
                published += 1

            except Exception:
                db.rollback()

                # Reload the event after rollback.
                current_event = db.get(
                    OutboxEvent,
                    event.id,
                )

                if current_event is not None:
                    current_event.status = "PENDING"
                    current_event.locked_at = None
                    current_event.attempts += 1

                    db.commit()

                failed += 1

        return {
            "published": published,
            "failed": failed,
            "status": "DISPATCH_COMPLETED",
        }

    finally:
        db.close()