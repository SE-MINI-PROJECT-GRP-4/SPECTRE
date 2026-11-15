"""Legal Procedure Guidance Pydantic Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProcedureStep(BaseModel):
    """Individual procedural step."""

    step_number: int
    title: str
    description: str
    relevant_statute: Optional[str] = None
    action_items: List[str] = []


class ProcedureGuideResponse(BaseModel):
    """Detailed procedure guide representation (REQ-PROC-01 to REQ-PROC-07)."""

    id: str
    title: str
    slug: str
    legal_domain: str
    overview: str
    prerequisites: List[str] = []
    required_documents: List[str] = []
    jurisdiction_notes: str
    estimated_timeline: str
    steps: List[ProcedureStep] = []
    statutory_references: List[str] = []
    escalation_advice: str
    disclaimer: str


class ProcedureSummary(BaseModel):
    """Summary representation for procedure listing."""

    id: str
    title: str
    slug: str
    legal_domain: str
    overview: str
    step_count: int
