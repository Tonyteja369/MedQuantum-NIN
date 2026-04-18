import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware, logger
from app.routers import analysis, ecg, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings.create_directories()
    app.state.signals = {}
    logger.info(f"MedQuantum-NIN API v{settings.model_version} starting")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"CORS origins: {settings.allowed_origins_list}")
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_origin_regex=settings.allowed_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(ecg.router)
app.include_router(analysis.router)
app.include_router(report.router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "MedQuantum-NIN API",
        "version": "1.0.0",
        "description": "Clinical-grade ECG analysis with explainable AI",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
