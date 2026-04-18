"""
FastAPI entry point for Vercel serverless deployment.

This module serves as the primary handler for all API requests on Vercel.
Vercel automatically detects and serves this as the ASGI application.

DO NOT use uvicorn.run() or if __name__ == "__main__" in this file.
Vercel handles the application lifecycle automatically.
"""

import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure api/ is in the path so we can import app modules
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware, logger
from app.routers import analysis, ecg, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    settings.create_directories()
    app.state.signals = {}
    logger.info(f"MedQuantum-NIN API v{settings.model_version} starting")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"CORS origins: {settings.allowed_origins}")
    yield
    # Shutdown: cleanup temp files older than 1 hour
    temp_dir = Path(settings.temp_dir)
    if temp_dir.exists():
        cutoff = time.time() - 3600
        cleaned = 0
        for f in temp_dir.iterdir():
            if f.stat().st_mtime < cutoff:
                f.unlink(missing_ok=True)
                cleaned += 1
        if cleaned:
            logger.info(f"Cleaned up {cleaned} temp files on shutdown")


app = FastAPI(
    title="MedQuantum-NIN API",
    version="1.0.0",
    description=(
        "Clinical-grade ECG analysis API with explainable AI. "
        "Offline-capable, rule-based ECG interpretation with detailed reasoning traces."
    ),
    lifespan=lifespan,
    openapi_tags=[
        {"name": "ECG", "description": "ECG signal upload and management"},
        {"name": "Analysis", "description": "ECG feature extraction and clinical diagnosis"},
        {"name": "Report", "description": "SOAP note and PDF report generation"},
    ],
)

# DO NOT use allowed_origin_regex or dynamic origin parsing here.
# allowed_origins must remain a list[str] defined in config.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Include all routers with /api prefix for Vercel routing
app.include_router(ecg.router)
app.include_router(analysis.router)
app.include_router(report.router)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


@app.get("/api", tags=["Health"])
@app.get("", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MedQuantum-NIN API",
        "version": "1.0.0",
        "description": "Clinical-grade ECG analysis with explainable AI",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/api/health",
    }


# Vercel automatically exports this ASGI app for serverless execution
__all__ = ["app"]
