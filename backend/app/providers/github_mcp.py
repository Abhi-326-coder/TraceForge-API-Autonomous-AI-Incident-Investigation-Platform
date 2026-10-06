from app.providers.github import GitHubProvider
from app.mcp.github_client import GitHubMCPClient

class GitHubMCPProvider(GitHubProvider):
    
    def __init__(self):
        self.client = GitHubMCPClient()
        
    async def get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str | None = None,
    ):

        arguments = {
            "owner": owner,
            "repo": repo,
            "path": path,
        }

        if ref:
            arguments["ref"] = ref

        return await self.client.call_tool(
            "get_file_contents",
            arguments,
        )
    async def search_code(
        self,
        query:str,
    ):
        return await self.client.call_tool(
            "search_code",
            {
                "query":query
            },
        )
    
    async def list_commits(
        self,
        owner:str,
        repo:str,
        per_page:int=10
    ):
        return await self.client.call_tool(
            "list_commits",
            {
                "owner": owner,
                "repo": repo,
                "perPage": per_page,
            },
        )