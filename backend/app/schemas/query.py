"""AI Query and Citation Schemas matching SPECTRE AI Contract."""

import enum
from typing import List, Optional
from pydantic import BaseModel, Field


class LegalDomainEnum(str, enum.Enum):
    """Supported Indian legal domains."""

    CRIMINAL = "criminal"
    CIVIL = "civil"
    CONSUMER = "consumer"
    CYBER = "cyber"
    CONSTITUTIONAL = "constitutional"
    FAMILY = "family"
    LABOR = "labor"
    GENERAL = "general"


class CitationSchema(BaseModel):
    """Verified citation matching SPECTRE AI Contract."""

    source_id: str
    document: str
    section: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    quote: str
    verified: bool = True


class QueryRequest(BaseModel):
    """Input query request payload (REQ-QUERY-01, REQ-QUERY-02)."""

    question: str = Field(..., min_length=2, max_length=2000, description="Natural-language legal query")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Maximum retrieved source documents")


class QueryResultDTO(BaseModel):
    """Processed query result DTO."""

    status: str  # 'answered', 'insufficient_evidence', 'out_of_scope', 'refused', 'invalid_input', 'error'
    legal_domain: LegalDomainEnum
    answer: str
    procedural_steps: List[str] = []
    citations: List[CitationSchema] = []
    confidence: float = 0.0
    confidence_label: str = "none"  # 'high', 'medium', 'low', 'none'
    disclaimer: str
    warnings: List[str] = []
    helplines: List[str] = []
