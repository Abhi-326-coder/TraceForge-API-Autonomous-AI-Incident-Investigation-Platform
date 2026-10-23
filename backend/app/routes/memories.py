from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.memory import MemoryCreate, MemoryResponse
from app.services.memory_service import (
    retrieve_memories,
    store_memory,
)

router = APIRouter(
    prefix="/api/projects",
    tags=["Agent Memory"],
)


@router.post(
    "/{project_id}/memories",
    response_model=MemoryResponse,
    status_code=201,
)
def create_memory(
    project_id: int,
    payload: MemoryCreate,
    db: Session = Depends(get_db),
):
    if payload.project_id != project_id:
        raise HTTPException(
            status_code=400,
            detail="Project ID does not match request path.",
        )

    return store_memory(db, payload)


@router.get(
    "/{project_id}/memories",
    response_model=list[MemoryResponse],
)
def search_memories(
    project_id: int,
    query: str = Query(min_length=1, max_length=500),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    return retrieve_memories(
        db=db,
        project_id=project_id,
        query=query,
        limit=limit,
    )
