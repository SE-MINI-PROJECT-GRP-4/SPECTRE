"""Document Templates API v1 Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.template import (
    TemplateCreate,
    TemplateRenderRequest,
    TemplateRenderResponse,
    TemplateResponse,
    TemplateUpdate,
)
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["Legal Document Templates"])


@router.get(
    "",
    response_model=List[TemplateResponse],
    status_code=status.HTTP_200_OK,
    summary="List available legal document templates",
    description="Returns a list of standardized legal document templates categorized by legal domain (REQ-DOC-01, REQ-DOC-02, REQ-DOC-03).",
)
def list_templates(
    category: Optional[str] = Query(None, description="Category filter (consumer, criminal, constitutional, etc.)"),
    db: Session = Depends(get_db),
) -> List[TemplateResponse]:
    service = TemplateService(db)
    return service.list_templates(category=category)


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document template details",
    description="Retrieves a specific document template by ID along with its variable fields and raw template content (REQ-DOC-04, REQ-DOC-05).",
)
def get_template(template_id: int, db: Session = Depends(get_db)) -> TemplateResponse:
    service = TemplateService(db)
    return service.get_template(template_id)


@router.post(
    "/{template_id}/render",
    response_model=TemplateRenderResponse,
    status_code=status.HTTP_200_OK,
    summary="Render customized document",
    description="Substitutes variable parameters into the document template and generates a customized draft with professional disclaimers (REQ-DOC-04, REQ-DOC-08).",
)
def render_template(
    template_id: int,
    payload: TemplateRenderRequest,
    db: Session = Depends(get_db),
) -> TemplateRenderResponse:
    service = TemplateService(db)
    return service.render_template(template_id, payload)


@router.post(
    "",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create template (Admin only)",
    description="Allows administrators to add new legal document templates (REQ-DOC-06).",
)
def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TemplateResponse:
    service = TemplateService(db)
    return service.create_template(payload)


@router.put(
    "/{template_id}",
    response_model=TemplateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update template (Admin only)",
    description="Allows administrators to update or deactivate templates (REQ-DOC-07).",
)
def update_template(
    template_id: int,
    payload: TemplateUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TemplateResponse:
    service = TemplateService(db)
    return service.update_template(template_id, payload)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete template (Admin only)",
    description="Allows administrators to remove a document template.",
)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = TemplateService(db)
    service.delete_template(template_id)
    return {"status": "success", "message": "Document template successfully removed."}
