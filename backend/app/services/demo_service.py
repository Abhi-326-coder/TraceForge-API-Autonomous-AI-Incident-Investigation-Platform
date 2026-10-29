from simulator.main import get_incident, get_logs, get_metrics


def get_demo_scenario() -> dict:
    incident = get_incident()

    return {
        "mode": "DEMO",
        "incident": incident,
        "logs": get_logs(incident.service),
        "metrics": get_metrics(incident.service),
    }