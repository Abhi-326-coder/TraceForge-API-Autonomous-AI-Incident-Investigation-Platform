from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Incident, Project
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    LogResponse,
    MetricsResponse,
)
from simulator.main import get_logs, get_metrics


router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
)


@router.post(
    "",
    response_model=IncidentResponse,
)
def create_incident(
    incident: IncidentCreate,
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    incident_count = (
        db.query(Incident)
        .count()
    )

    external_id = f"INC-{incident_count + 1:03d}"

    new_incident = Incident(
        external_id=external_id,
        title=incident.title,
        description=incident.description,
        service=incident.service,
        severity=incident.severity,
        status="OPEN",
        project_id=project_id,
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    db: Session = Depends(get_db),
):
    return db.query(Incident).all()


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.get(
    "/{incident_id}/logs",
    response_model=list[LogResponse],
)
def get_incident_logs(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return get_logs(incident.service)


@router.get(
    "/{incident_id}/metrics",
    response_model=MetricsResponse,
)
def get_incident_metrics(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    metrics = get_metrics(incident.service)

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="Metrics not found",
        )

    return metrics