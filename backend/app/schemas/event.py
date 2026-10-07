from datetime import datetime
from typing import Any

from pydantic import BaseModel

class InvestigationEvent(BaseModel):

    event_type: str

    investigation_id: int

    message: str

    agent: str | None = None

    data: dict[str, Any] = {}

    timestamp: datetime