from pydantic import BaseModel


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    service: str
    severity: str
    status: str


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

