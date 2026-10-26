from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Incident, Investigation, User
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
from app.security import get_current_user
from app.services.authorization_service import get_owned_incident, get_owned_investigation
import asyncio
import json

from fastapi.responses import StreamingResponse

from app.services.event_bus import event_service

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
    user:User = Depends()
):
    incident = get_owned_incident(db, incident_id, user)

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
    user:User = Depends()
):
    incident = get_owned_incident(db, incident_id, user)

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
    user:User = Depends()
):
    incident = get_owned_incident(db, incident_id, user)

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
    user:User = Depends()
):
    incident = get_owned_incident(db, incident_id, user)

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
    user:User = Depends()
):

    incident = get_owned_incident(db, incident_id, user)


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

@router.get(
    "/{investigation_id}/events"
)
async def investigation_events(
    investigation_id: int,
):

    async def event_stream():

        sent = 0

        while True:

            events = event_service.get_events(
                investigation_id
            )

            while sent < len(events):

                event = events[sent]

                payload = (
                    event.model_dump_json()
                )

                yield (
                    f"event: {event.event_type}\n"
                    f"data: {payload}\n\n"
                )

                sent += 1

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )