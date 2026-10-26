
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import (
    User,
    Project,
    Incident,
    Investigation,
    Evidence,
    PatchApproval,
    AgentMemory,
)


def get_owned_project(
    db: Session,
    project_id: int,
    user: User,
) -> Project:
    project = db.get(Project, project_id)

    if project is None or project.owner_id != user.id:
        # Same response for missing and unauthorized resources.
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return project


def get_owned_incident(
    db: Session,
    incident_id: int,
    user: User,
) -> Incident:
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(404, "Incident not found.")

    get_owned_project(db, incident.project_id, user)
    return incident


def get_owned_investigation(
    db: Session,
    investigation_id: int,
    user: User,
) -> Investigation:
    investigation = db.get(Investigation, investigation_id)

    if investigation is None:
        raise HTTPException(404, "Investigation not found.")

    get_owned_incident(db, investigation.incident_id, user)
    return investigation


def get_owned_evidence(
    db: Session,
    evidence_id: int,
    user: User,
) -> Evidence:
    evidence = db.get(Evidence, evidence_id)

    if evidence is None:
        raise HTTPException(404, "Evidence not found.")

    get_owned_investigation(
        db, evidence.investigation_id, user
    )
    return evidence


def get_owned_patch(
    db: Session,
    patch_id: int,
    user: User,
) -> PatchApproval:
    patch = db.get(PatchApproval, patch_id)

    if patch is None:
        raise HTTPException(404, "Patch not found.")

    get_owned_investigation(
        db, patch.investigation_id, user
    )
    return patch


def get_owned_memory(
    db: Session,
    memory_id: int,
    user: User,
) -> AgentMemory:
    memory = db.get(AgentMemory, memory_id)

    if memory is None:
        raise HTTPException(404, "Memory not found.")

    get_owned_project(db, memory.project_id, user)
    return memory
