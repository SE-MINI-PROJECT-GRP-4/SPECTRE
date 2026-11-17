"""Legal Reference Pydantic Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field


class ReferenceBase(BaseModel):
    """Base legal reference attributes (REQ-REF-01, REQ-REF-03, REQ-REF-04)."""

    title: str = Field(..., min_length=2, max_length=255)
    citation: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=255)
    legal_domain: str = Field(..., max_length=100)
    year: Optional[int] = None
    court: Optional[str] = Field(None, max_length=150)
    url: Optional[str] = Field(None, max_length=500)
    status: str = Field("active", description="active, outdated, or repealed (REQ-REF-06)")
    summary: Optional[str] = None
    content: Optional[str] = None


class ReferenceCreate(ReferenceBase):
    """Admin payload to create new legal reference (REQ-REF-07)."""
    pass


class ReferenceUpdate(BaseModel):
    """Admin payload to update reference metadata."""

    title: Optional[str] = None
    citation: Optional[str] = None
    source: Optional[str] = None
    legal_domain: Optional[str] = None
    year: Optional[int] = None
    court: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None


class ReferenceResponse(ReferenceBase):
    """Detailed response for legal reference with timestamps."""

    id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def domain(self) -> str:
        return self.legal_domain

    @computed_field
    @property
    def link(self) -> str:
        return self.url or ""

    @computed_field
    @property
    def date(self) -> str:
        if self.year:
            return f"{self.year}-01-01"
        return self.created_at.strftime("%Y-%m-%d") if self.created_at else ""

    model_config = ConfigDict(from_attributes=True)


class ReferenceListResponse(BaseModel):
    """Paginated list of legal references."""

    total: int
    page: int
    limit: int
    items: List[ReferenceResponse]
