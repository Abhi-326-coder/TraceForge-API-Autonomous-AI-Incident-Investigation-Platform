from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Evidence, Investigation, User
from app.schemas.evidence import EvidenceResponse
from app.services.authorization_service import get_owned_investigation
from app.security import get_current_user

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
    user:User = Depends(get_current_user)
):
    investigation = get_owned_investigation(db, investigation_id, user)

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
