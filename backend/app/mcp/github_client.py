from contextlib import asynccontextmanager

from httpx2 import AsyncClient
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from app.config import settings


@asynccontextmanager
async def _authenticated_transport(url: str):
    async with AsyncClient(
        headers={
            "Authorization": f"Bearer {settings.github_token}",
        },
    ) as http_client:
        async with streamable_http_client(
            url,
            http_client=http_client,
        ) as streams:
            yield streams


class GitHubMCPClient:

    def __init__(self):
        self.url = settings.github_mcp_url

    async def list_tools(self):
        async with Client(_authenticated_transport(self.url)) as client:
            result = await client.list_tools()
            return result.tools

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):
        async with Client(_authenticated_transport(self.url)) as client:
            return await client.call_tool(
                tool_name,
                arguments,
            )
