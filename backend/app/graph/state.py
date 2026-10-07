from typing import TypedDict


class IncidentData(TypedDict):
    id: int
    external_id: str
    title: str
    description: str
    service: str
    severity: str


class InvestigationState(TypedDict, total=False):

    investigation_id: int

    incident: IncidentData

    evidence: list[dict]

    findings: list[dict]

    tool_calls: list[dict]

    investigation_plan: list[str]

    next_agent: str

    investigation_complete: bool

    final_finding: dict