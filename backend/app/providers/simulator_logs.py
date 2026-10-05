from simulator.main import get_logs

from app.providers.logs import LogProvider
from app.schemas.tool import LogEntry


class SimulatorLogProvider(LogProvider):

    def search_logs(
        self,
        service: str,
        query: str | None = None,
    ) -> list[LogEntry]:

        logs = get_logs(service)

        if query:
            query = query.lower()

            logs = [
                log
                for log in logs
                if query in log["message"].lower()
            ]

        return [
            LogEntry(**log)
            for log in logs
        ]