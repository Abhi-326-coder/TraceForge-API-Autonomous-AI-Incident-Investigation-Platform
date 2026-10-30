from pydantic import BaseModel, Field


class EvaluationCaseSummary(BaseModel):
    case_id: str
    passed: bool
    root_cause_match: bool
    evidence_grounded: bool
    required_evidence_covered: bool
    forbidden_claim_detected: bool
    failures: list[str] = Field(default_factory=list)


class EvaluationDashboardResponse(BaseModel):
    mode: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    root_cause_accuracy: float
    evidence_grounding_rate: float
    average_duration_ms: float
    average_tool_calls: float
    cases: list[EvaluationCaseSummary]