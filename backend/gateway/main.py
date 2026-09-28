"""
FastAPI Application Entrypoint for Prompt Shield Gateway.
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from gateway.config import settings
from gateway.routes import router as api_router

app = FastAPI(
    title="Prompt Shield Gateway",
    description="Ultra-low latency inline security proxy gateway against LLM prompt injection and jailbreaks.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Injects mandatory security headers into every HTTP response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Include Gateway & Telemetry API Router
app.include_router(api_router)

# Resolve frontend dist assets directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_dist = os.path.join(root_dir, "frontend", "dist")

if os.path.exists(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="react_assets")


@app.get("/")
@app.get("/dashboard")
async def serve_dashboard():
    """Serves the Prompt Shield React Dashboard UI."""
    index_file = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    return {"message": "Prompt Shield API Gateway Running. React Frontend available after npm run build inside frontend/"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
