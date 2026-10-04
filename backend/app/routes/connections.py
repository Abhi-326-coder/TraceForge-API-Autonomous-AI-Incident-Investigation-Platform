from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Project, ProjectConnection
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
)


router = APIRouter(
    prefix="/api/projects",
    tags=["Connections"],
)


@router.post(
    "/{project_id}/connections",
    response_model=ConnectionResponse,
)
def create_connection(
    project_id: int,
    connection: ConnectionCreate,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    new_connection = ProjectConnection(
        project_id=project_id,
        connection_type=connection.connection_type,
        provider=connection.provider,
        config=connection.config,
    )

    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)

    return new_connection


@router.get(
    "/{project_id}/connections",
    response_model=list[ConnectionResponse],
)
def list_connections(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return (
        db.query(ProjectConnection)
        .filter(
            ProjectConnection.project_id == project_id
        )
        .all()
    )