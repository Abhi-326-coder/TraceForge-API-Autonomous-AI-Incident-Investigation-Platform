from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Incident, Investigation

from app.services.outbox_service import (
    create_outbox_event
)


def create_investigation(db, incident):

    investigation = Investigation(
        incident_id=incident.id,
        status="QUEUED",
    )

    db.add(investigation)

    # Generate the investigation ID without committing.
    db.flush()

    create_outbox_event(
        db,
        event_type="INVESTIGATION_REQUESTED",
        aggregate_type="Investigation",
        aggregate_id=str(investigation.id),
        idempotency_key=(
            f"investigation-created-{investigation.id}"
        ),
        payload={
            "investigation_id": investigation.id,
        },
    )

    # Both database records are saved together.
    db.commit()

    db.refresh(investigation)

    return investigation


def start_investigation(
    db: Session,
    investigation: Investigation,
) -> Investigation:

    investigation.status = "INVESTIGATING"
    investigation.current_stage = "INVESTIGATING"
    investigation.started_at = datetime.utcnow()

    db.commit()
    db.refresh(investigation)

    return investigation


def complete_investigation(
    db: Session,
    investigation: Investigation,
) -> Investigation:

    investigation.status = "COMPLETED"
    investigation.current_stage = "COMPLETED"
    investigation.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(investigation)

    return investigation