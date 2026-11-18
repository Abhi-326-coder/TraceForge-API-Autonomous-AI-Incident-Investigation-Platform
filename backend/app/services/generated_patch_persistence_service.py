from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas.approval import PatchApprovalCreate
from app.services.approval_service import create_patch_approval
from app.services.authorization_service import get_owned_investigation


def persist_generated_patch(
    db: Session,
    investigation_id: int,
    generated_patch,
    *,
    current_user: User,
):
    """Persist an AI proposal through the existing pending-approval workflow."""
    investigation = get_owned_investigation(db, investigation_id, current_user)
    proposed_files = getattr(generated_patch, "proposed_files", None)
    if not isinstance(proposed_files, dict) or not proposed_files:
        raise HTTPException(422, "Generated patch is missing proposed file contents.")
    if set(proposed_files) != set(generated_patch.changed_files):
        raise HTTPException(422, "Proposed file paths do not match changed files.")
    payload = PatchApprovalCreate(
        investigation_id=investigation.id,
        patch_summary=generated_patch.summary,
        diff=generated_patch.diff,
        changed_files=generated_patch.changed_files,
        tests_to_run=generated_patch.tests_to_run,
        risks=generated_patch.risks,
        assumptions=getattr(generated_patch, "assumptions", []),
        proposed_files=proposed_files,
    )
    try:
        return create_patch_approval(db, payload, current_user=current_user)
    except Exception:
        # create_patch_approval owns rollback for persistence/audit failures;
        # ensure validation or unexpected failures also leave no open transaction.
        db.rollback()
        raise


class GeneratedPatchPersistenceService:
    def persist(self, db: Session, investigation_id: int, generated_patch, user: User):
        return persist_generated_patch(
            db, investigation_id, generated_patch, current_user=user
        )
