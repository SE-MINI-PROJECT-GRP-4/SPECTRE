"""System Health, Readiness, and Observability Endpoints."""

import sys
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.session import get_db

router = APIRouter(prefix="/system", tags=["System Health & Diagnostics"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Application liveness probe",
    description="Basic ping to check if application process is live and responsive.",
)
def liveness():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@router.get(
    "/readiness",
    status_code=status.HTTP_200_OK,
    summary="Application readiness probe",
    description="Validates that database connectivity and downstream dependencies are ready to serve requests.",
)
def readiness(db: Session = Depends(get_db)):
    db_ok = True
    db_error = None
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = False
        db_error = str(e)

    return {
        "status": "ready" if db_ok else "degraded",
        "database": {
            "connected": db_ok,
            "error": db_error,
        },
        "environment": settings.ENVIRONMENT,
    }


@router.get(
    "/info",
    status_code=status.HTTP_200_OK,
    summary="System and runtime metadata",
    description="Returns platform version and environment runtime details.",
)
def system_info():
    return {
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "python_version": sys.version.split()[0],
        "debug_mode": settings.DEBUG,
        "api_v1_prefix": settings.API_V1_STR,
    }
