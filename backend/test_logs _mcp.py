import asyncio

from app.mcp.logs_client import LogsMCPClient


async def main():

    client = LogsMCPClient(
        "http://127.0.0.1:8100/mcp"
    )

    tools = await client.list_tools()

    print("Available tools:")

    for tool in tools:
        print(
            tool.name,
            tool.description,
        )

    result = await client.search_logs(
        service="checkout-api",
        query="database",
    )

    print("\nTool result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

