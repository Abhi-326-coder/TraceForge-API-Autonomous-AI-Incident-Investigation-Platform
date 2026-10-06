## Add MCP log server and log client :

```bash
pip install mcp[cli]
```


```python
from mcp.server import MCPServer

from app.providers.simulator_logs import SimulatorLogProvider
from app.tools.logs import search_logs


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

    result = search_logs(
        provider=provider,
        service=service,
        query=query,
    )

    return result.model_dump()


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )
```

- add logs_client.py

```python
from mcp import Client


class LogsMCPClient:

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

    async def search_logs(
        self,
        service: str,
        query: str | None = None,
    ):

        async with Client(
            self.server_url
        ) as client:

            result = await client.call_tool(
                "search_logs",
                {
                    "service": service,
                    "query": query,
                },
            )

            return result
```
To run the logs_server
- python -m app.mcp.logs_server


To see the developement workflow of logs_mcp
- $env:PYTHONPATH = (Get-Location).Path
- mcp dev app\mcp\logs_server.py

17.13 Convert Logs MCP to HTTP

At the bottom of:

app/mcp/logs_server.py

change:

if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )

to:

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8100,
    )

Now:

Logs MCP Server
       │
       │ HTTP
       ▼
http://127.0.0.1:8100/mcp

The SDK's MCPServer.run("streamable-http") starts the Streamable HTTP server, while streamable_http_app() can also be mounted into an existing ASGI application.

17.14 Run it

Terminal 1:

cd backend

python -m app.mcp.logs_server

You now have:

MCP Server
localhost:8100

with:

/mcp

as the MCP endpoint.