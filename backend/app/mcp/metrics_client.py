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