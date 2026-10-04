from datetime import datetime

from pydantic import BaseModel


class EvidenceCreate(BaseModel):
    source_type: str
    provider: str
    title: str
    content: str
    source_reference: str | None = None


class EvidenceResponse(BaseModel):
    id: int
    investigation_id: int
    source_type: str
    provider: str
    title: str
    content: str
    source_reference: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }