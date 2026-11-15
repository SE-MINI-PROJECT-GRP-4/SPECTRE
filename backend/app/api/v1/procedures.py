"""Legal Procedures API v1 Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Query, status
from app.schemas.procedure import ProcedureGuideResponse, ProcedureSummary
from app.services.procedure_service import ProcedureService

router = APIRouter(prefix="/procedures", tags=["Legal Procedure Guidance"])


@router.get(
    "",
    response_model=List[ProcedureSummary],
    status_code=status.HTTP_200_OK,
    summary="List supported procedural guides",
    description="Returns available step-by-step procedural guides for common Indian legal issues (REQ-PROC-01, REQ-PROC-02).",
)
def list_procedures(
    domain: Optional[str] = Query(None, description="Filter by legal domain: criminal, consumer, constitutional, cyber"),
) -> List[ProcedureSummary]:
    service = ProcedureService()
    return service.list_procedures(domain=domain)


@router.get(
    "/{slug_or_id}",
    response_model=ProcedureGuideResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed procedural walkthrough",
    description="Retrieves prerequisites, required documents, step-by-step action items, statutory references, and escalation advice (REQ-PROC-01 through REQ-PROC-07).",
)
def get_procedure_detail(slug_or_id: str) -> ProcedureGuideResponse:
    service = ProcedureService()
    return service.get_procedure_by_slug(slug_or_id)
