import httpx

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.github_pr_service import commit_approved_patch

router = APIRouter(
    prefix="/api/patches",
    tags=["GitHub Pull Requests"],
)


class CreatePRRequest(BaseModel):
    owner: str = Field(min_length=1, max_length=100)
    repo: str = Field(min_length=1, max_length=100)
    base_branch: str = Field(min_length=1, max_length=255)


@router.post("/{patch_id}/pull-request")
async def create_pull_request(
    patch_id: int,
    payload: CreatePRRequest,
    db: Session = Depends(get_db),
):
    try:
        return await commit_approved_patch(
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
        elif (
            "approved" in message
            or "integrity" in message
            or "missing" in message
            or "match" in message
        ):
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
                "GitHub rejected a commit or pull-request operation. "
                "Check token permissions, branch state, and repository settings."
            ),
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub.",
        ) from exc