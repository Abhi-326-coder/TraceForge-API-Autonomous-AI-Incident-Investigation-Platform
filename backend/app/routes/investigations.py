from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Incident, Investigation
from app.schemas.investigation import InvestigationResponse
from app.services.investigation_service import (
    create_investigation,
    start_investigation,
)


router = APIRouter(
    prefix="/api/incidents",
    tags=["Investigations"],
)


@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationResponse,
)
def create_incident_investigation(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    investigation = create_investigation(
        db=db,
        incident=incident,
    )

    investigation = start_investigation(
        db=db,
        investigation=investigation,
    )

    return investigation


@router.get(
    "/{incident_id}/investigations",
    response_model=list[InvestigationResponse],
)
def list_investigations(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return (
        db.query(Investigation)
        .filter(
            Investigation.incident_id == incident_id
        )
        .all()
    )