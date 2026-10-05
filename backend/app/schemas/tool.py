from pydantic import BaseModel


class LogEntry(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str


class SearchLogsResult(BaseModel):
    logs: list[LogEntry]
    total: int
    
