from datetime import datetime

from pydantic import BaseModel

class ConnectionCreate(BaseModel):
    connection_type: str
    provider: str
    config: dict = {}


class ConnectionResponse(BaseModel):
    id: int
    project_id: int
    connection_type: str
    provider: str
    config: dict
    created_at: datetime

    model_config = {
        "from_attributes": True
    }