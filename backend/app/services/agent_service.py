from sqlalchemy.orm import Session

from app.agents.log_agent import LogAgent
from app.db.models import Incident, Investigation
from app.schemas.finding import Finding


def run_log_agent(
    db: Session,
    incident: Incident,
    investigation: Investigation,
) -> Finding:

    agent = LogAgent(db=db)

    return agent.investigate(
        incident=incident,
        investigation=investigation,
    )