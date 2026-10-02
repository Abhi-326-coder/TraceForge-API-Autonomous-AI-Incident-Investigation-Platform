from fastapi import FastAPI
from app.routes.incidents import router as incidents_router


app = FastAPI(
    title="TraceForge API: Autonomous AI Incident Investigation Platform",
    description="Autonomous AI Incident Investigation Platform",
    version="0.1.0",
)

app.include_router(incidents_router)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service":"traceforge-api is working fine"
    }
