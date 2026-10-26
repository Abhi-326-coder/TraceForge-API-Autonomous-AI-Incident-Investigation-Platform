
import hashlib
import json
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import PatchApproval, User
from app.schemas.approval import (
    ApprovalDecision,
    PatchApprovalCreate,
)
from app.services.audit_service import record_audit_event
from app.services.authorization_service import (
    get_owned_investigation,
    get_owned_patch,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def calculate_patch_hash(
    diff: str,
    proposed_files: dict,
    changed_files: list,
) -> str:
    """Create a deterministic hash of the approved patch payload."""
    payload = {
        "diff": diff,
        "proposed_files": proposed_files,
        "changed_files": changed_files,
    }

    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        canonical_payload.encode("utf-8")
    ).hexdigest()


def create_patch_approval(
    db: Session,
    payload: PatchApprovalCreate,
    *,
    current_user: User,
) -> PatchApproval:
    """Create a pending patch approval for an owned investigation."""

    investigation = get_owned_investigation(
        db,
        payload.investigation_id,
        current_user,
    )

    proposed_files = payload.proposed_files or {}
    changed_files = payload.changed_files or []

    patch_hash = calculate_patch_hash(
        diff=payload.diff,
        proposed_files=proposed_files,
        changed_files=changed_files,
    )

    approval = PatchApproval(
        investigation_id=investigation.id,
        patch_summary=payload.patch_summary,
        diff=payload.diff,
        changed_files=changed_files,
        proposed_files=proposed_files,
        tests_to_run=payload.tests_to_run or [],
        risks=payload.risks or [],
        status="PENDING",
        patch_sha256=patch_hash,
    )

    try:
        db.add(approval)
        db.flush()

        record_audit_event(
            db,
            action="PATCH_CREATED",
            outcome="SUCCESS",
            actor_user_id=current_user.id,
            resource_type="PatchApproval",
            resource_id=approval.id,
            metadata={"patch_id": approval.id},
        )

        db.commit()
        db.refresh(approval)
        return approval

    except Exception:
        db.rollback()
        raise


def get_patch_approval(
    db: Session,
    patch_id: int,
    *,
    current_user: User,
) -> PatchApproval:
    """Return a patch approval if it belongs to the current user."""

    return get_owned_patch(db, patch_id, current_user)


def decide_patch_approval(
    db: Session,
    patch_id: int,
    decision: ApprovalDecision,
    *,
    current_user: User,
) -> PatchApproval:
    """Approve or reject a pending patch and record the decision."""

    approval = db.get(PatchApproval, patch_id)

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Patch approval not found.",
        )

    get_owned_investigation(
        db,
        approval.investigation_id,
        current_user,
    )

    if approval.status != "PENDING":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Patch is already {approval.status.lower()}; "
                "only pending patches can be decided."
            ),
        )

    requested_decision = decision.decision.upper()

    if requested_decision not in {"APPROVED", "REJECTED"}:
        raise HTTPException(
            status_code=422,
            detail="Decision must be APPROVED or REJECTED.",
        )

    approval.status = requested_decision
    approval.decision_note = decision.note
    approval.decided_by = str(current_user.id)
    approval.decided_at = utc_now()

    action = (
        "PATCH_APPROVED"
        if requested_decision == "APPROVED"
        else "PATCH_REJECTED"
    )

    try:
        record_audit_event(
            db,
            action=action,
            outcome="SUCCESS",
            actor_user_id=current_user.id,
            resource_type="PatchApproval",
            resource_id=approval.id,
            metadata={
                "patch_id": approval.id,
                "investigation_id": approval.investigation_id,
            },
        )

        # Approval status and audit record share one transaction.
        db.commit()
        db.refresh(approval)
        return approval

    except Exception:
        db.rollback()
        raise
