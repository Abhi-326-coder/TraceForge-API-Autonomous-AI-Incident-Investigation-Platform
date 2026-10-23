
import pytest

from app.guardrails.validators import (
    validate_investigation_plan,
    validate_tool_name,
    validate_tool_call_count,
    validate_evidence_ids,
    validate_repository_path,
    require_human_approval,
)


def test_valid_investigation_plan():
    assert validate_investigation_plan(
        ["logs", "metrics", "code"]
    ) == ["logs", "metrics", "code"]


def test_rejects_unknown_agent():
    with pytest.raises(ValueError):
        validate_investigation_plan(["logs", "shell"])


def test_rejects_excessive_plan():
    with pytest.raises(ValueError):
        validate_investigation_plan(
            ["logs", "metrics", "code"] * 3
        )


def test_rejects_unknown_tool():
    with pytest.raises(ValueError):
        validate_tool_name("execute_arbitrary_shell")


def test_enforces_tool_call_limit():
    with pytest.raises(ValueError):
        validate_tool_call_count(20)


def test_rejects_unknown_evidence():
    with pytest.raises(ValueError):
        validate_evidence_ids([1, 999], {1, 2})


def test_accepts_safe_repository_path():
    assert validate_repository_path(
        "src/checkout.py"
    ) == "src/checkout.py"


@pytest.mark.parametrize("path", [
    "../secrets.txt",
    "/etc/passwd",
    r"..\secrets.txt",
    ".env",
    "config/.env.production",
    "private/server.pem",
])
def test_rejects_unsafe_repository_paths(path):
    with pytest.raises(ValueError):
        validate_repository_path(path)


def test_github_write_requires_approval():
    with pytest.raises(PermissionError):
        require_human_approval(
            "create_pull_request", "PENDING"
        )


def test_approved_write_passes_status_guard():
    require_human_approval(
        "create_pull_request", "APPROVED"
    )
