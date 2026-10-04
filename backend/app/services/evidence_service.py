from sqlalchemy.orm import Session

from app.db.models import Evidence


def create_evidence(
    db: Session,
    investigation_id: int,
    source_type: str,
    provider: str,
    title: str,
    content: str,
    source_reference: str | None = None,
) -> Evidence:

    evidence = Evidence(
        investigation_id=investigation_id,
        source_type=source_type,
        provider=provider,
        title=title,
        content=content,
        source_reference=source_reference,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence