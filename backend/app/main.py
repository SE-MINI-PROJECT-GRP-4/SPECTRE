"""SPECTRE Legal Assistant — FastAPI Core Backend Orchestrator."""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.session import Base, engine, SessionLocal
from app.database.seed_data import seed_database

# Import API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.conversations import router as conversations_router, query_router
from app.api.v1.references import router as references_router
from app.api.v1.procedures import router as procedures_router
from app.api.v1.templates import router as templates_router
from app.api.v1.admin import router as admin_router
from app.api.v1.system import router as system_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spectre.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing SPECTRE backend database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Verifying and seeding initial legal references, templates, and admin user...")
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        logger.warning(f"Seed data execution note: {e}")
    finally:
        db.close()

    logger.info("SPECTRE backend orchestrator initialized successfully.")
    yield
    logger.info("Shutting down SPECTRE backend orchestrator.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "AI-Based Legal Assistant, e-Lawyer and Case Guidance System for Indian Legal Framework. "
        "Engineered by Member 1 (Backend & Integration / Technical Owner) according to SRS v1.0 specifications."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "detail": "An internal server error occurred. Please contact system support.",
        },
    )


# Root health redirect
@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
        "ui": "/ui" if os.path.isdir(frontend_dist) else "Run 'npm run dev' inside frontend/",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok", "app": settings.PROJECT_NAME}


# Mount API v1 Routers (SRS v1.0 specification)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(conversations_router, prefix=settings.API_V1_STR)
app.include_router(query_router, prefix=settings.API_V1_STR)
app.include_router(references_router, prefix=settings.API_V1_STR)
app.include_router(procedures_router, prefix=settings.API_V1_STR)
app.include_router(templates_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)

# Also mount under /api for frontend HTTP client compatibility
app.include_router(auth_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(references_router, prefix="/api")
app.include_router(procedures_router, prefix="/api")
app.include_router(templates_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(system_router, prefix="/api")

# Mount query_router at root /query for direct endpoint access
app.include_router(query_router)

# Mount frontend production build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.isdir(frontend_dist):
    app.mount("/ui", StaticFiles(directory=frontend_dist, html=True), name="frontend_ui")


