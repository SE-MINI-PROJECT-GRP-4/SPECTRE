"""Legal References API v1 Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.reference import (
    ReferenceCreate,
    ReferenceListResponse,
    ReferenceResponse,
    ReferenceUpdate,
)
from app.services.reference_service import ReferenceService

router = APIRouter(prefix="/references", tags=["Legal References & Case Law"])


@router.get(
    "",
    response_model=ReferenceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search legal references",
    description="Search and retrieve authoritative Indian statutory acts, sections, and case-law citations (REQ-REF-01 through REQ-REF-06).",
)
def list_references(
    domain: Optional[str] = Query(None, description="Legal domain filter (consumer, criminal, cyber, etc.)"),
    search: Optional[str] = Query(None, description="Keyword search query"),
    status: Optional[str] = Query(None, description="Status filter: active, outdated, repealed"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ReferenceListResponse:
    service = ReferenceService(db)
    return service.search_references(
        domain=domain,
        search=search,
        status_filter=status,
        page=page,
        limit=limit,
    )


@router.get(
    "/{reference_id}",
    response_model=ReferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get legal reference by ID",
    description="Retrieve detailed identifying information, statutory citation, and full summary for a reference (REQ-REF-03, REQ-REF-04, REQ-REF-05).",
)
def get_reference(reference_id: int, db: Session = Depends(get_db)) -> ReferenceResponse:
    service = ReferenceService(db)
    return service.get_reference(reference_id)


@router.post(
    "",
    response_model=ReferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create legal reference (Admin only)",
    description="Allows authorized administrators to add new authoritative references (REQ-REF-07, REQ-REF-08).",
)
def create_reference(
    payload: ReferenceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ReferenceResponse:
    service = ReferenceService(db)
    return service.create_reference(payload)


@router.put(
    "/{reference_id}",
    response_model=ReferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update legal reference (Admin only)",
    description="Allows authorized administrators to modify or update reference metadata (REQ-REF-07, REQ-REF-08).",
)
def update_reference(
    reference_id: int,
    payload: ReferenceUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ReferenceResponse:
    service = ReferenceService(db)
    return service.update_reference(reference_id, payload)


@router.delete(
    "/{reference_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete legal reference (Admin only)",
    description="Allows authorized administrators to remove a reference record (REQ-REF-08).",
)
def delete_reference(
    reference_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = ReferenceService(db)
    service.delete_reference(reference_id)
    return {"status": "success", "message": "Legal reference successfully removed."}
