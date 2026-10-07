from sqlalchemy.orm import Session

from app.db.models import Evidence
from app.agents.root_cause_agent import RootCauseAgent


def run_root_cause_analysis(
    db: Session,
    investigation_id: int,
):

    evidence_rows = (
        db.query(Evidence)
        .filter(
            Evidence.investigation_id
            == investigation_id
        )
        .order_by(Evidence.id)
        .all()
    )

    evidence = [
        {
            "id": item.id,
            "source_type": item.source_type,
            "provider": item.provider,
            "title": item.title,
            "content": item.content,
            "source_reference": item.source_reference,
        }
        for item in evidence_rows
    ]

    if not evidence:
        raise ValueError(
            "No evidence available for investigation."
        )

    agent = RootCauseAgent()

    return agent.analyze(
        evidence=evidence
    )