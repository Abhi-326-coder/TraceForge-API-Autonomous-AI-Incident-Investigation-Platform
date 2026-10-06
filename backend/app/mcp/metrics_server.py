from mcp.server import MCPServer

from app.providers.simulator_metrics import (
    SimulatorMetricsProvider,
)
from app.tools.metrics import get_service_metrics


mcp = MCPServer(
    "traceforge-metrics"
)

provider = SimulatorMetricsProvider()


@mcp.tool()
def get_metrics(
    service: str,
) -> dict:
    """
    Retrieve runtime metrics for an application service.

    Use this to investigate request rate, error rate,
    latency, database connection utilization,
    resource saturation, and other service health signals.
    """

    return get_service_metrics(
        provider=provider,
        service=service,
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8101,
    )