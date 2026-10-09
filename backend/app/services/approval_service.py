from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import Investigation, PatchApproval


def create_patch_approval(
    db: Session,
    investigation_id: int,
    patch_summary: str,
    diff: str,
    changed_files: list[str],
    tests_to_run: list[str],
    risks: list[str],
) -> PatchApproval:
    investigation = db.get(Investigation, investigation_id)

    if investigation is None:
        raise ValueError("Investigation not found")

    if not diff.strip():
        raise ValueError("Cannot submit an empty patch")

    if not changed_files:
        raise ValueError("Patch must identify changed files")

    approval = PatchApproval(
        investigation_id=investigation_id,
        patch_summary=patch_summary,
        diff=diff,
        changed_files=changed_files,
        tests_to_run=tests_to_run,
        risks=risks,
        status="PENDING",
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


def decide_patch(
    db: Session,
    patch_id: int,
    decision: str,
    note: str,
    decided_by: str,
) -> PatchApproval:
    approval = db.get(PatchApproval, patch_id)

    if approval is None:
        raise ValueError("Patch approval not found")

    if approval.status != "PENDING":
        raise ValueError(
            f"Cannot decide on a patch with status {approval.status}"
        )

    approval.status = decision
    approval.decision_note = note
    approval.decided_by = decided_by
    approval.decided_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(approval)

    return approval


def get_patch_approval(
    db: Session,
    patch_id: int,
) -> PatchApproval:
    approval = db.get(PatchApproval, patch_id)

    if approval is None:
        raise ValueError("Patch approval not found")

    return approval