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

    result = agent.analyze(
        evidence=evidence
    )

    valid_ids = {
        item["id"]
        for item in evidence
    }

    invalid_ids = [
        evidence_id
        for evidence_id in result.evidence_ids
        if evidence_id not in valid_ids
    ]

    if invalid_ids:
        raise ValueError(
            "Root Cause Agent referenced invalid "
            f"evidence IDs: {invalid_ids}"
        )

    return result
