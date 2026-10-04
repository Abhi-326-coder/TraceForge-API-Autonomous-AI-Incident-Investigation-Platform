## Add the routes of Project Connections

```bash
POST /api/projects/{project_id}/connections
GET  /api/projects/{project_id}/connections
```

GitHub connection

Create:
```json
{
  "connection_type": "code",
  "provider": "github",
  "config": {
    "repository": "demo/traceforge-ecommerce",
    "branch": "main"
  }
}```
Logs connection

Create:

```json
{
  "connection_type": "logs",
  "provider": "simulator",
  "config": {
    "environment": "demo"
  }
}```

Metrics connection

Create:

```json
{
  "connection_type": "metrics",
  "provider": "simulator",
  "config": {
    "environment": "demo"
    }
}
```
Now:

```bash
Project #1
│
├── code
│    └── github
│
├── logs
│    └── simulator
│
└── metrics
     └── simulator
```