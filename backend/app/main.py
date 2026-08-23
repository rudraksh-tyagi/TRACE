"""
TRACE FastAPI application entry point.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.error_handlers import register_error_handlers
from app.logging_config import configure_logging

from app.routers.mock_api import (
    router as mock_router,
)

from app.routers.ingestion_api import (
    router as ingestion_router,
)


# ============================================================
# LOGGING
# ============================================================

configure_logging()

logger = logging.getLogger(
    "trace.main"
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=settings.system_name,
    version=settings.system_version,
    description=(
        "Marine Oil Spill Intelligence System "
        "prototype backend."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ERROR HANDLERS
# ============================================================

register_error_handlers(
    app
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    mock_router
)

app.include_router(
    ingestion_router
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {
        "status": "success",
        "service": settings.system_name,
        "version": settings.system_version,
        "mock_mode": settings.use_mock_data,
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "trace-backend",
        "mock_mode": settings.use_mock_data,
    }


# ============================================================
# STARTUP LOG
# ============================================================

@app.on_event("startup")
async def startup_event():

    logger.info(
        "TRACE backend started | version=%s | "
        "USE_MOCK_DATA=%s",
        settings.system_version,
        settings.use_mock_data,
    )

    if settings.use_mock_data:

        logger.warning(
            "OFFLINE DEMO MODE ENABLED - "
            "mock fallback data is active."
        )

    else:

        logger.info(
            "LIVE PIPELINE MODE ENABLED."
        )