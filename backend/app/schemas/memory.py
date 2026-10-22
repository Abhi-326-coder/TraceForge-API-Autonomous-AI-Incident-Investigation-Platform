from typing import Literal

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    project_id: int
    investigation_id: int | None = None

    memory_type: Literal[
        "ROOT_CAUSE",
        "REMEDIATION",
        "LESSON",
        "OUTCOME",
    ]

    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1)
    details: dict = Field(default_factory=dict)

    outcome_status: Literal[
        "UNKNOWN",
        "SUCCESS",
        "FAILED",
        "PARTIAL",
    ] = "UNKNOWN"


class MemoryResponse(BaseModel):
    id: int
    project_id: int
    investigation_id: int | None
    memory_type: str
    title: str
    summary: str
    details: dict
    outcome_status: str

    model_config = {"from_attributes": True}