from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.approval import (
    ApprovalDecision,
    PatchApprovalCreate,
    PatchApprovalResponse,
)
from app.services.approval_service import (
    create_patch_approval,
    decide_patch_approval,
    get_patch_approval,
)
from app.security import get_current_user

router = APIRouter(
    prefix="/api/patches",
    tags=["Patch Approvals"],
)


@router.post(
    "",
    response_model=PatchApprovalResponse,
    status_code=201,
)
def submit_patch(
    payload: PatchApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_patch_approval(
            db=db,
            payload=payload,
            current_user=current_user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/{patch_id}",
    response_model=PatchApprovalResponse,
)
def read_patch(
    patch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_patch_approval(
            db,
            patch_id,
            current_user=current_user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/{patch_id}/decision",
    response_model=PatchApprovalResponse,
)
def submit_decision(
    patch_id: int,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return decide_patch_approval(
            db,
            patch_id=patch_id,
            decision=payload,
            current_user=current_user,
        )
    except ValueError as exc:
        status_code = 404 if str(exc) == "Patch approval not found" else 409
        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc