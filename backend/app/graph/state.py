from typing import TypedDict


class IncidentData(TypedDict):
    id: int
    external_id: str
    title: str
    description: str
    service: str
    severity: str


class InvestigationState(TypedDict, total=False):

    incident: IncidentData

    logs: list[dict]

    findings: list[dict]

    tool_calls: list[dict]

    next_action: str

    final_finding: dict