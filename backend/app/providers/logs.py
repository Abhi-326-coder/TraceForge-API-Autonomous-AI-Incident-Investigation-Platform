from abc import ABC, abstractmethod

from app.schemas.tool import LogEntry

# abstract class 
class LogProvider(ABC):

    @abstractmethod
    def search_logs(
        self,
        service: str,
        query: str | None = None,
    ) -> list[LogEntry]:
        pass