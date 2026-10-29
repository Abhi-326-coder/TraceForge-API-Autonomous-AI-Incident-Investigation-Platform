from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.services.demo_service import get_demo_scenario

router = APIRouter(prefix="/api/demo", tags=["Demo"])


@router.get("/scenario")
def read_demo_scenario():
    if not settings.demo_mode:
        raise HTTPException(
            status_code=404,
            detail="Demo mode is disabled",
        )

    return get_demo_scenario()