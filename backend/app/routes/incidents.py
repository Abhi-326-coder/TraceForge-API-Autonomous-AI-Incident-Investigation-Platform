from fastapi import APIRouter, HTTPException

from simulator.main import (
    get_incident,
    get_logs,
    get_metrics,
)

from app.schemas.incident import (
    IncidentResponse,
    LogResponse,
    MetricsResponse,
)


router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_by_id(incident_id: str):

    incident = get_incident()

    if incident.id != incident_id:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.get(
    "/{incident_id}/logs",
    response_model=list[LogResponse],
)
def get_incident_logs(incident_id: str):

    incident = get_incident()

    if incident.id != incident_id:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return get_logs(incident.service)


@router.get(
    "/{incident_id}/metrics",
    response_model=MetricsResponse,
)
def get_incident_metrics(incident_id: str):

    incident = get_incident()

    if incident.id != incident_id:
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