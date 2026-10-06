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