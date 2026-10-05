from sqlalchemy.orm import Session

from app.db.models import Evidence, Incident, Investigation
from app.providers.simulator_logs import SimulatorLogProvider
from app.schemas.finding import Finding
from app.tools.logs import search_logs


class LogAgent:
    # constructor
    def __init__(self, db: Session):
        self.db = db
        self.provider = SimulatorLogProvider()

    def investigate(
        self,
        incident: Incident,
        investigation: Investigation,
    ) -> Finding:

        # Search for error logs
        error_result = search_logs(
            provider=self.provider,
            service=incident.service,
            query="error",
        )

        # Search for database-related logs
        database_result = search_logs(
            provider=self.provider,
            service=incident.service,
            query="database",
        )

        evidence_ids = []

        for log in (
            error_result.logs
            + database_result.logs
        ):

            evidence = Evidence(
                investigation_id=investigation.id,
                source_type="logs",
                provider="simulator",
                title=log.message,
                content=log.message,
                source_reference=(
                    f"simulator://logs/"
                    f"{log.service}/"
                    f"{log.timestamp}"
                ),
            )

            self.db.add(evidence)
            self.db.commit()
            self.db.refresh(evidence)

            evidence_ids.append(evidence.id)

        return Finding(
            title="Log investigation completed",
            summary=(
                "Log investigation found database-related "
                "errors associated with the checkout failure."
            ),
            severity="HIGH",
            evidence_ids=evidence_ids,
        )