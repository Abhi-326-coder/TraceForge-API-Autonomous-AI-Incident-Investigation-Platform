from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

class PatchApprovalCreate(BaseModel):
    investigation_id: int
    patch_summary: str
    diff: str
    changed_files: list[str]
    tests_to_run: list[str]
    risks: list[str]
    proposed_files: dict[str, str]


class ApprovalDecision(BaseModel):
    decision: Literal["APPROVED", "REJECTED"]
    note: str = Field(default="", max_length=2000)


class PatchApprovalResponse(BaseModel):
    id: int
    investigation_id: int
    patch_summary: str
    diff: str
    changed_files: list[str]
    tests_to_run: list[str]
    risks: list[str]
    status: str
    decision_note: str | None
    decided_by: str | None
    created_at: datetime
    decided_at: datetime | None

    model_config = {"from_attributes": True}