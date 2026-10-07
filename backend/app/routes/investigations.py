from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Incident, Investigation
from app.schemas.investigation import InvestigationResponse
from app.services.investigation_service import (
    create_investigation,
    start_investigation,
)
from app.services.agent_service import run_log_agent
from app.schemas.finding import Finding
from app.services.agent_service import (
    run_gemini_log_agent,
)
from app.services.root_cause_service import (
    run_root_cause_analysis
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
    
@router.post(
    "/{incident_id}/investigate/logs",
    response_model=Finding,
)
def investigate_logs(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.incident_id == incident_id
        )
        .order_by(Investigation.id.desc())
        .first()
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return run_log_agent(
        db=db,
        incident=incident,
        investigation=investigation,
    )
    
@router.post(
    "/{incident_id}/investigate/gemini"
)
def investigate_with_gemini(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return {
        "incident_id": incident.id,
        "result": run_gemini_log_agent(
            incident=incident,
        ),
    }
    
@router.post(
    "/{incident_id}/root-cause",
)
def analyze_root_cause(
    incident_id: int,
    db: Session = Depends(get_db),
):

    incident = db.get(
        Incident,
        incident_id,
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.incident_id
            == incident_id
        )
        .order_by(
            Investigation.id.desc()
        )
        .first()
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    result = run_root_cause_analysis(
        db=db,
        investigation_id=investigation.id,
    )

    return result