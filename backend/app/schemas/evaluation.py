from pydantic import BaseModel, Field
from typing import Literal

from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    case_id: str
    description: str
    expected_root_cause: str
    required_evidence_terms: list[str] = Field(
        default_factory=list
    )
    forbidden_claims: list[str] = Field(
        default_factory=list
    )


class EvaluationInput(BaseModel):
    case: EvaluationCase
    predicted_root_cause: str
    explanation: str = ""
    evidence_ids: list[int] = Field(default_factory=list)
    available_evidence: list[dict] = Field(
        default_factory=list
    )
    tool_calls: int = Field(default=0, ge=0)
    duration_ms: float = Field(default=0, ge=0)
    remediation_approved: bool = False


class EvaluationResult(BaseModel):
    case_id: str
    root_cause_match: bool
    evidence_grounded: bool
    required_evidence_covered: bool
    forbidden_claim_detected: bool
    remediation_policy_passed: bool
    tool_calls: int
    duration_ms: float
    passed: bool
    failures: list[str] = Field(default_factory=list)
