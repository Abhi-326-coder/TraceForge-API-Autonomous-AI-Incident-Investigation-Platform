from simulator.main import get_metrics


def get_service_metrics(
    service: str,
):
    metrics = get_metrics(service)

    if not metrics:
        raise ValueError(
            f"No metrics found for service: {service}"
        )

    return metrics