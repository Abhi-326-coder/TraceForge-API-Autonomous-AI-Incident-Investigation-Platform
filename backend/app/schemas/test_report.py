from typing import Literal

from pydantic import BaseModel, Field


class TestFinding(BaseModel):
    category: Literal[
        "test_failure",
        "environment_failure",
        "timeout",
        "possible_regression",
        "other",
    ]
    title: str
    explanation: str
    relevant_output: str = ""


class TestReport(BaseModel):
    status: Literal["PASSED", "FAILED", "INCONCLUSIVE"]
    exit_code: int | None
    duration_seconds: float

    summary: str
    findings: list[TestFinding] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)

    tests_executed: bool
    limitations: list[str] = Field(default_factory=list)