from fastapi import FastAPI, HTTPException


from app.services.event_bus import event_service
from app.routes.investigation_jobs import (
    router as investigation_jobs_router
)
from app.routes.memories import router as memories_router

from app.routes.connections import router as connections_router
from app.routes.incidents import router as incidents_router
from app.routes.projects import router as projects_router
from app.routes.investigations import (
    router as investigations_router,
)
from app.routes.evidence import router as evidence_router
from app.routes.approvals import router as approvals_router
from app.routes.github_branches import router as github_branches_router
from app.routes.github_prs import router as github_prs_router

app = FastAPI(
    title="TraceForge API",
    description="Autonomous AI Incident Investigation Platform",
    version="0.1.0",
)


app.include_router(projects_router)
app.include_router(incidents_router)
app.include_router(connections_router)
app.include_router(investigations_router)
app.include_router(evidence_router)
app.include_router(approvals_router)
app.include_router(github_branches_router)
app.include_router(github_prs_router)
app.include_router(investigation_jobs_router)
app.include_router(memories_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "traceforge-api",
    }
    
@app.get("/health/redis")
def redis_health_check():
    try:
        event_service.health_check()
        return {
            "status":"healthy",
            "service":"traceforge-redis"
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Redis is unavailable",
        ) from exc