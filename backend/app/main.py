from fastapi import FastAPI

from app.routes.connections import router as connections_router
from app.routes.incidents import router as incidents_router
from app.routes.projects import router as projects_router
from app.routes.investigations import (
    router as investigations_router,
)
from app.routes.evidence import router as evidence_router
from app.routes.approvals import router as approvals_router

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

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "traceforge-api",
    }