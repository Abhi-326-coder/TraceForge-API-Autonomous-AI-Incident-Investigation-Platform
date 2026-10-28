
from typing import Any


INCIDENT_FIXTURES: dict[str, dict[str, Any]] = {
    "checkout-db-pool-001": {
        "incident": {
            "id": "EVAL-001",
            "title": "Checkout API returns HTTP 500 errors",
            "description": (
                "Checkout requests fail while database "
                "connections approach the configured limit."
            ),
            "service": "checkout-api",
            "severity": "HIGH",
        },
        "logs": [
            {
                "id": 1,
                "level": "ERROR",
                "service": "checkout-api",
                "message": "Database connection pool exhausted",
            },
            {
                "id": 2,
                "level": "ERROR",
                "service": "checkout-api",
                "message": "Failed to execute checkout transaction",
            },
            {
                "id": 3,
                "level": "ERROR",
                "service": "checkout-api",
                "message": "HTTP 500 returned to client",
            },
        ],
        "metrics": {
            "error_rate": 0.42,
            "latency_ms": 1850,
            "database_connections": 98,
            "database_connection_limit": 100,
        },
        "expected_root_cause": (
            "database connection pool exhaustion"
        ),
        "required_evidence_terms": [
            "database connection pool exhausted",
            "98",
        ],
        "forbidden_claims": [
            "confirmed malicious attack",
            "database permanently destroyed",
        ],
    },
    "checkout-deployment-002": {
        "incident": {
            "id": "EVAL-002",
            "title": "Checkout errors increased after deployment",
            "description": (
                "Checkout error rate increased after version "
                "2.4.0 was deployed."
            ),
            "service": "checkout-api",
            "severity": "HIGH",
        },
        "logs": [
            {
                "id": 11,
                "level": "INFO",
                "service": "checkout-api",
                "message": "Deployment version 2.4.0 started",
            },
            {
                "id": 12,
                "level": "ERROR",
                "service": "checkout-api",
                "message": (
                    "Payment request validation failed: "
                    "missing currency field"
                ),
            },
            {
                "id": 13,
                "level": "ERROR",
                "service": "checkout-api",
                "message": "HTTP 500 returned to client",
            },
        ],
        "metrics": {
            "error_rate_before_deployment": 0.01,
            "error_rate_after_deployment": 0.31,
            "latency_ms": 1200,
        },
        "expected_root_cause": (
            "deployment regression involving missing currency field"
        ),
        "required_evidence_terms": [
            "version 2.4.0",
            "missing currency field",
        ],
        "forbidden_claims": [
            "confirmed malicious attack",
        ],
    },
    "checkout-insufficient-evidence-003": {
        "incident": {
            "id": "EVAL-003",
            "title": "Checkout requests are intermittently failing",
            "description": (
                "Some requests fail, but available telemetry "
                "does not identify the underlying cause."
            ),
            "service": "checkout-api",
            "severity": "MEDIUM",
        },
        "logs": [
            {
                "id": 21,
                "level": "ERROR",
                "service": "checkout-api",
                "message": "Request failed with HTTP 500",
            },
        ],
        "metrics": {
            "error_rate": 0.08,
        },
        "expected_root_cause": (
            "insufficient evidence to determine root cause"
        ),
        "required_evidence_terms": [],
        "forbidden_claims": [
            "definitely caused by a database outage",
            "confirmed malicious attack",
        ],
    },
}
