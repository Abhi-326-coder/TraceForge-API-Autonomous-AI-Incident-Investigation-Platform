## Adding the Evidence routes 

```python
@router.get(
    "/{investigation_id}/evidence",
    response_model=list[EvidenceResponse],
)
def list_evidence(
    investigation_id: int,
    db: Session = Depends(get_db),
):
    investigation = db.get(
        Investigation,
        investigation_id,
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return (
        db.query(Evidence)
        .filter(
            Evidence.investigation_id == investigation_id
        )
        .all()
    )
```

```bash
POST /api/investigations/{investigation_id}/evidence
```