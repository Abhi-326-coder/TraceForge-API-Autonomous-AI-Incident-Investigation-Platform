import asyncio

from app.mcp.metrics_client import MetricsMCPClient


async def main():
    
    client = MetricsMCPClient(
        "http://127.0.0.1:8101/mcp"
    )
    
    tools =await client.list_tools()
    
    for tool in tools:
        print(
            tool.name,
            tool.description,
        )
    
    result = await client.get_metrics(
        service="checkout-api"
    )
    print("\n Metrics: ")
    print(result.content)
    
if __name__=="__main__":
    asyncio.run(main())
    
