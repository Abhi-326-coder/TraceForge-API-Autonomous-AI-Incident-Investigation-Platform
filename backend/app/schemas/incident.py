from datetime import datetime

from pydantic import BaseModel


class IncidentCreate(BaseModel):
    title: str
    description: str
    service: str
    severity: str


class IncidentResponse(BaseModel):
    id: int
    external_id: str
    title: str
    description: str
    service: str
    severity: str
    status: str
    project_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class LogResponse(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str


class MetricsResponse(BaseModel):
    request_rate: int
    error_rate: float
    latency_ms: int
    database_connections: int
    database_connection_limit: int
