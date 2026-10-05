from app.providers.simulator_logs import SimulatorLogProvider
from app.tools.logs import search_logs


provider = SimulatorLogProvider()


SEARCH_LOGS_TOOL = {
    "type": "function",
    "name": "search_logs",
    "description": (
        "Search application logs for a specific service. "
        "Use this when investigating errors, failures, "
        "timeouts, database problems, or other runtime issues."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "service": {
                "type": "string",
                "description": "The application service to search.",
            },
            "query": {
                "type": "string",
                "description": (
                    "Optional keyword or phrase to search "
                    "for in the log messages."
                ),
            },
        },
        "required": ["service"],
    },
}


def execute_search_logs(
    service: str,
    query: str | None = None,
):
    result = search_logs(
        provider=provider,
        service=service,
        query=query,
    )

    return result.model_dump()