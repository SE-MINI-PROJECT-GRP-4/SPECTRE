"""Public data contracts for the SPECTRE AI engine (see docs/AI_CONTRACT.md)."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AnswerStatus(str, Enum):
    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    OUT_OF_SCOPE = "out_of_scope"
    REFUSED = "refused"
    INVALID_INPUT = "invalid_input"
    ERROR = "error"


class ConfidenceLabel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class QueryRequest(BaseModel):
    question: str = Field(..., description="The user's legal question in natural language.")
    top_k: Optional[int] = Field(
        None, ge=1, le=20, description="Override the number of chunks retrieved."
    )


class Citation(BaseModel):
    source_id: str = Field(..., description="Marker used in the answer text, e.g. 'S1'.")
    chunk_id: str
    document: str = Field(..., description="Human-readable title of the source document.")
    section: Optional[str] = Field(None, description="Section / Article number if known.")
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    quote: str = Field(..., description="Verbatim excerpt from the source supporting the answer.")
    verified: bool = Field(True, description="Always true for citations returned to clients.")


class QueryResponse(BaseModel):
    status: AnswerStatus
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    confidence_label: ConfidenceLabel = ConfidenceLabel.NONE
    disclaimer: str = ""
    warnings: list[str] = Field(default_factory=list)
    helplines: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _answered_requires_verified_citations(self) -> "QueryResponse":
        if self.status == AnswerStatus.ANSWERED:
            if not self.citations:
                raise ValueError("An ANSWERED response must include at least one citation.")
            if not all(c.verified for c in self.citations):
                raise ValueError("An ANSWERED response may only contain verified citations.")
        elif self.citations:
            raise ValueError("Only ANSWERED responses may carry citations.")
        return self


class RetrievedChunk(BaseModel):
    """Internal: a chunk returned from the vector store."""

    chunk_id: str
    text: str
    score: float
    doc_id: str = ""
    document: str = ""
    short_name: str = ""
    category: str = ""
    section: Optional[str] = None
    section_heading: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    exact_match: bool = False

    def label(self) -> str:
        name = self.short_name or self.document
        return f"{name}, Section {self.section}" if self.section else name
