
import re
from pathlib import PurePosixPath

from app.guardrails.policies import (
    ALLOWED_AGENTS,
    ALLOWED_INVESTIGATION_TOOLS,
    POLICY,
)


def validate_investigation_plan(plan: list[str]) -> list[str]:
    if not isinstance(plan, list):
        raise ValueError("Investigation plan must be a list.")

    if len(plan) > POLICY.max_plan_steps:
        raise ValueError("Investigation plan exceeds step limit.")

    invalid = set(plan) - ALLOWED_AGENTS
    if invalid:
        raise ValueError(
            f"Unsupported agents in plan: {sorted(invalid)}"
        )

    if len(plan) != len(set(plan)):
        raise ValueError("Investigation plan contains duplicates.")

    return plan


def validate_tool_name(tool_name: str) -> str:
    if tool_name not in ALLOWED_INVESTIGATION_TOOLS:
        raise ValueError(f"Tool is not permitted: {tool_name}")

    return tool_name


def validate_tool_call_count(call_count: int) -> None:
    if call_count >= POLICY.max_tool_calls:
        raise ValueError("Investigation tool-call limit reached.")


def validate_evidence_ids(
    requested_ids: list[int],
    available_ids: set[int],
) -> list[int]:
    if len(requested_ids) > POLICY.max_evidence_items:
        raise ValueError("Too many evidence references.")

    if any(
        not isinstance(item, int) or isinstance(item, bool)
        or item <= 0
        for item in requested_ids
    ):
        raise ValueError("Evidence IDs must be positive integers.")

    if len(requested_ids) != len(set(requested_ids)):
        raise ValueError("Duplicate evidence IDs are not allowed.")

    missing = set(requested_ids) - available_ids
    if missing:
        raise ValueError(
            f"Unknown evidence IDs: {sorted(missing)}"
        )

    return requested_ids


def validate_repository_path(file_path: str) -> str:
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("File path must be a non-empty string.")

    # Reject absolute paths, Windows paths, traversal and control chars.
    if (
        "\\" in file_path
        or file_path.startswith("/")
        or re.match(r"^[A-Za-z]:", file_path)
        or any(ord(char) < 32 for char in file_path)
    ):
        raise ValueError("Unsafe repository file path.")

    path = PurePosixPath(file_path)

    if any(part in {".", ".."} for part in file_path.split("/")):
        raise ValueError("Path traversal is not allowed.")

    if path.suffix.lower() in {
        ".pem", ".key", ".p12", ".pfx",
    }:
        raise ValueError("Sensitive key files cannot be patched.")

    if path.name.lower() in {
        ".env", ".env.local", ".env.production",
    }:
        raise ValueError("Environment secret files cannot be patched.")

    return path.as_posix()


def require_human_approval(
    action: str,
    approval_status: str | None,
) -> None:
    from app.guardrails.policies import APPROVAL_REQUIRED_ACTIONS

    if action in APPROVAL_REQUIRED_ACTIONS:
        if approval_status != "APPROVED":
            raise PermissionError(
                f"Action '{action}' requires an approved patch."
            )
