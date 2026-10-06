import asyncio

from app.providers.github_mcp import GitHubMCPProvider


async def main():

    provider = GitHubMCPProvider()

    tools = await provider.client.list_tools()

    print("GitHub MCP tools:")

    for tool in tools:
        print(
            "-",
            tool.name,
        )


if __name__ == "__main__":
    asyncio.run(main())