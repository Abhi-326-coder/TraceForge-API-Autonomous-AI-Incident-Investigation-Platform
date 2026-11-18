from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Incident, Project, User
from app.security import get_current_user

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


@router.post("/seed", status_code=201)
def seed_demo_incident(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not settings.demo_mode:
        raise HTTPException(404, "Demo mode is disabled")
    project = db.query(Project).filter(Project.owner_id == user.id, Project.name == "TraceForge Demo").first()
    if project is None:
        project = Project(name="TraceForge Demo", description="Seeded deterministic incident scenario", owner_id=user.id)
        db.add(project)
        db.flush()
    incident = db.query(Incident).filter(Incident.project_id == project.id, Incident.external_id == "DEMO-CHECKOUT-001").first()
    if incident is None:
        incident = Incident(external_id="DEMO-CHECKOUT-001", title="Checkout API returning HTTP 500 errors",
            description="Customers cannot complete checkout. Seeded logs show database connection pool exhaustion.",
            service="checkout-api", severity="HIGH", status="OPEN", project_id=project.id)
        db.add(incident)
        db.commit()
        db.refresh(incident)
    elif incident.project_id != project.id:
        incident.project_id = project.id
        db.commit()
        db.refresh(incident)
    return incident
