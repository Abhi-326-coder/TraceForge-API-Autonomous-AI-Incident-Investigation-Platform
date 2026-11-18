from simulator.main import get_incident, get_logs, get_metrics


def get_demo_scenario() -> dict:
    incident = get_incident()

    return {
        "mode": "DEMO",
        "incident": {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "service": incident.service,
            "severity": incident.severity,
            "status": incident.status,
        },
        "logs": get_logs(incident.service),
        "metrics": get_metrics(incident.service),
        "notice": "Deterministic simulated scenario; no external AI or GitHub operations are performed.",
    }
