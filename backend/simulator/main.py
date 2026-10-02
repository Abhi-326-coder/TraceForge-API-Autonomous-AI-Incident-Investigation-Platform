from .incidents import CHECKOUT_DATABASE_INCIDENT
from .logs import LOGS
from .metrics import METRICS


def get_incident():
    return CHECKOUT_DATABASE_INCIDENT


def get_logs(service: str):
    return [
        log
        for log in LOGS
        if log["service"] == service
    ]


def get_metrics(service: str):
    return METRICS.get(service, {})

