from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.db.database import get_db
from app.schemas.github_branch import (
    CreateBranchRequest,
    CreatedBranchResponse,
)
from app.services.github_branch_service import (
    create_branch_for_approval,
)

router = APIRouter(
    prefix="/api/patches",
    tags=["GitHub Branches"],
)


@router.post(
    "/{patch_id}/branch",
    response_model=CreatedBranchResponse,
)
async def create_approved_patch_branch(
    patch_id: int,
    payload: CreateBranchRequest,
    db: Session = Depends(get_db),
):
    try:
        return await create_branch_for_approval(
            db=db,
            patch_id=patch_id,
            owner=payload.owner,
            repo=payload.repo,
            base_branch=payload.base_branch,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Patch approval not found":
            status_code = 404
        elif "must be approved" in message:
            status_code = 409
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "GitHub rejected the branch operation. "
                "Check repository access, token permissions, "
                "base branch, and whether the branch already exists."
            ),
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub.",
        ) from exc