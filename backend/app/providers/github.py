from abc import ABC, abstractmethod

class GitHubProvider(ABC):

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

