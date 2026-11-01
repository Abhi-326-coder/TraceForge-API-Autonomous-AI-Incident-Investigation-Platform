from datetime import datetime, timezone

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.models import Investigation


def utc_now():
    return datetime.now(timezone.utc)


def claim_investigation(
    db: Session,
    investigation_id: int,
) -> bool:
    """
    Atomically claim a queued investigation.

    Only one worker can successfully change QUEUED to RUNNING.
    """

    statement = (
        update(Investigation)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "QUEUED",
        )
        .values(
            status="RUNNING",
            started_at=utc_now(),
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def complete_investigation(
    db: Session,
    investigation_id: int,
) -> bool:

    statement = (
        update(Investigation)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
        )
        .values(
            status="COMPLETED",
            completed_at=utc_now(),
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1


def fail_investigation(
    db: Session,
    investigation_id: int,
) -> bool:

    statement = (
        update(Investigation)
        .where(
            Investigation.id == investigation_id,
            Investigation.status == "RUNNING",
        )
        .values(
            status="FAILED",
            completed_at=utc_now(),
        )
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount == 1