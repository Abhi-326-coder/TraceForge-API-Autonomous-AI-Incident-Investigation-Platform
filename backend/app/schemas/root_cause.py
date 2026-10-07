from pydantic import BaseModel, Field


class AlternativeCause(BaseModel):
    cause: str
    reason_not_primary: str


class RootCauseResult(BaseModel):
    root_cause: str

    explanation: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence_ids: list[int]

    alternative_causes: list[AlternativeCause]

    uncertainty: str