from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Incident, Investigation


def create_investigation(
    db: Session,
    incident: Incident,
) -> Investigation:

    investigation = Investigation(
        incident_id=incident.id,
        status="CREATED",
        current_stage="CREATED",
    )

    db.add(investigation)
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