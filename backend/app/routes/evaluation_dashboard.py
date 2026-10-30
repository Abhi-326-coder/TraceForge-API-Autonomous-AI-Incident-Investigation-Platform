from fastapi import APIRouter, Depends

from app.schemas.evaluation_dashboard import (
    EvaluationDashboardResponse,
)
from app.services.evaluation_dashboard_service import (
    get_evaluation_dashboard,
)
from app.security import get_current_user

router = APIRouter(
    prefix="/api/evaluations",
    tags=["Evaluation Dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/dashboard",
    response_model=EvaluationDashboardResponse,
)
def evaluation_dashboard():
    return get_evaluation_dashboard()