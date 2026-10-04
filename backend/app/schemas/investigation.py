from datetime import datetime

from pydantic import BaseModel


class InvestigationResponse(BaseModel):
    id: int
    incident_id: int
    status: str
    current_stage: str
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }