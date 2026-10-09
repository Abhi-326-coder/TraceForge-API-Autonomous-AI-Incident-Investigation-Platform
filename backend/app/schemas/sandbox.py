from datetime import datetime

from pydantic import BaseModel


class SandboxResult(BaseModel):
    status: str
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool
    started_at: datetime
    completed_at: datetime