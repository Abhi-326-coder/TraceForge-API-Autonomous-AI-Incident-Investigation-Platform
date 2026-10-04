from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Evidence, Investigation
from app.schemas.evidence import EvidenceResponse


router = APIRouter(
    prefix="/api/investigations",
    tags=["Evidence"],
)


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
