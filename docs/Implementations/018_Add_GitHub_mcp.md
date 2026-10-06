# Implementing the Github MCP

## making changes in the config Adding PAT token and github mcp remote url and also in .env

```bash
github_token: str // add in .env
github_mcp_url: str = (
    "https://api.githubcopilot.com/mcp/readonly"
)
```

## First Creating the Github Provider which is a class of abstract methods

GithubProvider

```python
@abstractmethod
    async def get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str | None = None,
    ):
        pass

    @abstractmethod
    async def search_code(
        self,
        query: str,
    ):
        pass

    @abstractmethod
    async def list_commits(
        self,
        owner: str,
        repo: str,
        per_page: int = 10,
    ):
        pass

```

## Second Creating GitHubMCPProvider which inherits the above abstract class with working methods

```bash
backend\app\providers\github_mcp.py
```

## before Second Step need to create a Github MCP client 
- Mainly it has two functions one is calling a list_tools and call_tool

```python
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
```