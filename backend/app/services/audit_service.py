
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditEvent


ALLOWED_ACTIONS = {
    "AUTH_LOGIN_SUCCESS",
    "AUTH_LOGIN_FAILURE",
    "INVESTIGATION_STARTED",
    "INVESTIGATION_COMPLETED",
    "INVESTIGATION_FAILED",
    "PATCH_CREATED",
    "PATCH_APPROVED",
    "PATCH_REJECTED",
    "GITHUB_BRANCH_CREATED",
    "GITHUB_PR_CREATED",
    "ACCESS_DENIED",
}

ALLOWED_OUTCOMES = {
    "SUCCESS",
    "FAILURE",
    "DENIED",
}

SAFE_METADATA_KEYS = {
    "reason_code",
    "severity",
    "provider",
    "investigation_id",
    "patch_id",
    "pr_number",
    "http_status",
}


def record_audit_event(
    db: Session,
    *,
    action: str,
    outcome: str,
    actor_user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    correlation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = False,
) -> AuditEvent:
    """
    Add a validated audit event to the current transaction.

    commit=False lets callers commit the audit event together
    with the business operation it records.
    """

    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unsupported audit action: {action}")

    if outcome not in ALLOWED_OUTCOMES:
        raise ValueError(f"Unsupported audit outcome: {outcome}")

    if metadata is None:
        metadata = {}

    if not isinstance(metadata, dict):
        raise ValueError("Audit metadata must be a dictionary.")

    unknown_keys = set(metadata) - SAFE_METADATA_KEYS

    if unknown_keys:
        raise ValueError(
            "Unsupported audit metadata keys: "
            f"{sorted(unknown_keys)}"
        )

    event = AuditEvent(
        actor_user_id=actor_user_id,
        action=action,
        outcome=outcome,
        resource_type=resource_type,
        resource_id=(
            str(resource_id)
            if resource_id is not None
            else None
        ),
        correlation_id=correlation_id,
        event_metadata=metadata,
    )

    db.add(event)

    if commit:
        try:
            db.commit()
            db.refresh(event)
        except Exception:
            db.rollback()
            raise

    return event
