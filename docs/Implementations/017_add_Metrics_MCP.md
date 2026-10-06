## Add Metrics Server and Client

### Step 1 Creating a Simulator Metrics provider

```python
from simulator.main import get_metrics

from app.providers.metrics import MetricsProvider


class SimulatorMetricsProvider(MetricsProvider):

    def get_metrics(
        self,
        service: str,
    ) -> dict:

        metrics = get_metrics(service)

        if not metrics:
            raise ValueError(
                f"No metrics found for service: {service}"
            )

        return metrics
```

### Step 2 Creating the MCP server for Metrics which is going to use the above Metrics Simulator

```python
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

```

### Step 3 Creating the MCP client for Metrics which is going to call the metrics mcp server 

```python
from mcp import Client


class MetricsMCPClient:

    def __init__(
        self,
        server_url: str,
    ):
        self.server_url = server_url

    async def list_tools(self):

        async with Client(
            self.server_url
        ) as client:

            result = await client.list_tools()

            return result.tools

    async def get_metrics(
        self,
        service: str,
    ):

        async with Client(
            self.server_url
        ) as client:

            result = await client.call_tool(
                "get_metrics",
                {
                    "service": service,
                },
            )

            return result

```