from abc import ABC, abstractmethod


class MetricsProvider(ABC):

    @abstractmethod
    def get_metrics(
        self,
        service: str,
    ) -> dict:
        pass