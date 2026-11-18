from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Evidence, User, PatchApproval
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


@router.get("/{investigation_id}/root-cause")
def read_root_cause(
    investigation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_owned_investigation(db, investigation_id, user)
    row = db.query(Evidence).filter(
        Evidence.investigation_id == investigation_id,
        Evidence.source_type == "ROOT_CAUSE",
    ).order_by(Evidence.id.desc()).first()
    if row is None:
        raise HTTPException(404, "Root-cause analysis is not available yet.")
    import json
    try:
        return json.loads(row.content)
    except (TypeError, ValueError) as exc:
        raise HTTPException(500, "Stored root-cause analysis is invalid.") from exc


@router.get("/{investigation_id}/patches")
def list_investigation_patches(
    investigation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_owned_investigation(db, investigation_id, user)
    return db.query(PatchApproval).filter(
        PatchApproval.investigation_id == investigation_id
    ).order_by(PatchApproval.id.desc()).all()
