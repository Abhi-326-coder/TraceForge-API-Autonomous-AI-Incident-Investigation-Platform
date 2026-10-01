from fastapi import FastAPI

app = FastAPI(
    title="TraceForge API: Autonomous AI Incident Investigation Platform",
    description="Autonomous AI Incident Investigation Platform",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {
        "status":"healthy",
        "service":"traceforge-api is working fine"
    }
