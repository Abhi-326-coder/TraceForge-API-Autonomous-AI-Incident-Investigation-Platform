from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import AgentMemory
from app.schemas.memory import MemoryCreate


def store_memory(
    db: Session,
    memory_data: MemoryCreate,
) -> AgentMemory:
    memory = AgentMemory(
        project_id=memory_data.project_id,
        investigation_id=memory_data.investigation_id,
        memory_type=memory_data.memory_type,
        title=memory_data.title,
        summary=memory_data.summary,
        details=memory_data.details,
        outcome_status=memory_data.outcome_status,
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


def retrieve_memories(
    db: Session,
    project_id: int,
    query: str,
    limit: int = 5,
) -> list[AgentMemory]:
    if not query.strip():
        return []

    # Keep retrieval within the requested project.
    terms = list(dict.fromkeys(
        term.strip(".,:;!?()[]{}").lower()
        for term in query.split()
        if len(term.strip(".,:;!?()[]{}")) >= 3
    ))[:8]

    if not terms:
        return []

    conditions = []

    for term in terms:
        pattern = f"%{term}%"
        conditions.append(
            or_(
                AgentMemory.title.ilike(pattern),
                AgentMemory.summary.ilike(pattern),
            )
        )

    return (
        db.query(AgentMemory)
        .filter(AgentMemory.project_id == project_id)
        .filter(or_(*conditions))
        .order_by(AgentMemory.created_at.desc())
        .limit(max(1, min(limit, 20)))
        .all()
    )