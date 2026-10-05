from sqlalchemy.orm import Session

from app.agents.log_agent import LogAgent
from app.db.models import Incident, Investigation
from app.schemas.finding import Finding
from app.agents.gemini_log_agent import GeminiLogAgent

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
    
def run_gemini_log_agent(
    incident,
):
    agent = GeminiLogAgent()

    return agent.investigate(
        incident=incident,
    )