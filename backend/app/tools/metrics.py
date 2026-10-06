from app.providers.metrics import MetricsProvider
from app.providers.simulator_metrics import SimulatorMetricsProvider


def get_service_metrics(
    provider: MetricsProvider,
    service: str,
) -> dict:

    return provider.get_metrics(
        service=service
    )