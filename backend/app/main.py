from fastapi import FastAPI

from app.routes.incidents import router as incidents_router
from app.routes.projects import router as projects_router


app = FastAPI(
    title="TraceForge API",
    description="Autonomous AI Incident Investigation Platform",
    version="0.1.0",
)


app.include_router(projects_router)
app.include_router(incidents_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "traceforge-api",
    }