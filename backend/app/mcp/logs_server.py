from mcp.server import MCPServer

from app.providers.simulator_logs import SimulatorLogProvider
from app.tools.logs import search_logs as search_logs_tool


mcp = MCPServer(
    "traceforge-logs"
)

provider = SimulatorLogProvider()


@mcp.tool()
def search_logs(
    service: str,
    query: str | None = None,
) -> dict:
    """
    Search application logs for a service.

    Use this tool to investigate runtime errors,
    failures, database problems, timeouts, and
    other application issues.
    """

    result = search_logs_tool(
        provider=provider,
        service=service,
        query=query,
    )

    return result.model_dump()


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8100,
    )

# python -m app.mcp.logs_server

# $env:PYTHONPATH = (Get-Location).Path
# mcp dev app\mcp\logs_server.py