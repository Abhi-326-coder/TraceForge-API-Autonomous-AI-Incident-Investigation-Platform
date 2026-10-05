# Add the log provider and log agent 

```bash
class Finding(BaseModel):
    title: str
    summary: str
    severity: str
    evidence_ids: list[int]
```

```bash

                    LogAgent
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   Search "error"            Search "database"
          │                         │
          └────────────┬────────────┘
                       ▼
                    Logs
                       │
                       ▼
                    Evidence
                       │
                       ▼
                    Finding
```

backend/app/services/agent_service.py
```python
def run_log_agent(
    db: Session,
    incident: Incident,
    investigation: Investigation,
) -> Finding:

    agent = LogAgent(db=db)

    return agent.investigate(
        incident=incident,
        investigation=investigation,
    )
```

### add routes POST /{incident_id}/investigate/logs

```python
@router.post(
    "/{incident_id}/investigate/logs",
    response_model=Finding,
)
def investigate_logs(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.incident_id == incident_id
        )
        .order_by(Investigation.id.desc())
        .first()
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return run_log_agent(
        db=db,
        incident=incident,
        investigation=investigation,
    )
```