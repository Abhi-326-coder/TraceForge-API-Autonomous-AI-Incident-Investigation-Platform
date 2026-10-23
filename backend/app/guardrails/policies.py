
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailPolicy:
    max_tool_calls: int = 20
    max_plan_steps: int = 8
    max_evidence_items: int = 100
    max_file_size_bytes: int = 500_000


POLICY = GuardrailPolicy()

ALLOWED_AGENTS = frozenset({
    "logs",
    "metrics",
    "code",
})

ALLOWED_INVESTIGATION_TOOLS = frozenset({
    "search_logs",
    "get_service_metrics",
    "get_file_contents",
    "search_code",
    "list_commits",
    "search_knowledge",
})

# Read-only investigation is separated from write operations.
APPROVAL_REQUIRED_ACTIONS = frozenset({
    "create_branch",
    "create_commit",
    "create_pull_request",
    "apply_patch",
    "deploy",
})
