# Implemented the routes using Fastapi

- Server : http://127.0.0.1:8000

- 1. Health route: used to check if the server is working and responding properly
```bash
http://127.0.0.1:8000/health
```
```json
{
  "status": "healthy",
  "service": "traceforge-api is working fine"
}
```

- 2. incident route: return the details of the incident of particular using its id
```bash
http://127.0.0.1:8000/api/incidents/{incident_id}
```

```json
{
  "id": "INC-001",
  "title": "Checkout API returning HTTP 500 errors",
  "description": "Customers are unable to complete checkout. The checkout API has started returning HTTP 500 errors.",
  "service": "checkout-api",
  "severity": "HIGH",
  "status": "OPEN"
}
```
- 3. logs route: used to check if the server is working and responding properly
```bash
http://127.0.0.1:8000/api/incidents/INC-001/logs
```

```json
[
  {
    "timestamp": "2026-10-02T14:20:01",
    "service": "checkout-api",
    "level": "INFO",
    "message": "Checkout request received"
  },
  {
    "timestamp": "2026-10-02T14:20:02",
    "service": "checkout-api",
    "level": "INFO",
    "message": "Creating checkout transaction"
  },
  {
    "timestamp": "2026-10-02T14:20:03",
    "service": "checkout-api",
    "level": "ERROR",
    "message": "Database connection pool exhausted"
  },
  {
    "timestamp": "2026-10-02T14:20:03",
    "service": "checkout-api",
    "level": "ERROR",
    "message": "Failed to execute checkout transaction"
  },
  {
    "timestamp": "2026-10-02T14:20:03",
    "service": "checkout-api",
    "level": "ERROR",
    "message": "HTTP 500 returned to client"
  }
]
```
- 4. metrics route: return the metrics of the selected incident_id
```bash
http://127.0.0.1:8000/api/incidents/INC-001/metrics
```

```json
{
  "request_rate": 1250,
  "error_rate": 0.42,
  "latency_ms": 1850,
  "database_connections": 98,
  "database_connection_limit": 100
}
```


