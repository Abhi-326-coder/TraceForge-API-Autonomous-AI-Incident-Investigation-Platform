from simulator.main import get_metrics

from app.providers.metrics import MetricsProvider


class SimulatorMetricsProvider(MetricsProvider):

    def get_metrics(
        self,
        service: str,
    ) -> dict:

        metrics = get_metrics(service)

        if not metrics:
            raise ValueError(
                f"No metrics found for service: {service}"
            )

        return metrics