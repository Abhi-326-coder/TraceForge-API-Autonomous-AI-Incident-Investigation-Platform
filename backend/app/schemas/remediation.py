from typing import Literal

from pydantic import BaseModel, Field

class ProposedChange(BaseModel):
    file_path: str | None = None
    description: str
    rationale: str


class RemediationProposal(BaseModel):
    title: str
    summary: str

    change_type: Literal[
        "code_change",
        "configuration_change",
        "infrastructure_change",
        "investigation_required",
    ]

    risk: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    affected_files: list[str]
    proposed_changes: list[ProposedChange]

    test_plan: list[str]
    evidence_ids: list[int]

    rollback_plan: str
    assumptions: list[str] = Field(default_factory=list)
    uncertainty: str