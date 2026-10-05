from app.providers.logs import LogProvider
from app.schemas.tool import SearchLogsResult


def search_logs(
    provider: LogProvider,
    service: str,
    query: str | None = None,
) -> SearchLogsResult:

    logs = provider.search_logs(
        service=service,
        query=query,
    )

    return SearchLogsResult(
        logs=logs,
        total=len(logs),
    )