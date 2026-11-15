"""Legal Document Templates Pydantic Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TemplateVariableSchema(BaseModel):
    """Schema for individual placeholder variable in template."""

    key: str
    label: str
    type: str = "string"  # 'string', 'integer', 'date', 'text'
    required: bool = True
    default: Optional[Any] = None


class TemplateBase(BaseModel):
    """Base template attributes (REQ-DOC-01, REQ-DOC-02, REQ-DOC-03)."""

    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., max_length=100)
    description: str
    content: str
    version: str = "1.0"
    status: str = "active"


class TemplateCreate(TemplateBase):
    """Admin payload to create a new template (REQ-DOC-06)."""

    variables: Optional[List[TemplateVariableSchema]] = None


class TemplateUpdate(BaseModel):
    """Admin payload to modify template (REQ-DOC-07)."""

    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    variables: Optional[List[TemplateVariableSchema]] = None


class TemplateResponse(TemplateBase):
    """Template representation with parsed variables."""

    id: int
    variables: List[TemplateVariableSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateRenderRequest(BaseModel):
    """Payload to render a template with user-provided parameters."""

    variables: Dict[str, Any] = Field(..., description="Key-value mapping of variable replacements")


class TemplateRenderResponse(BaseModel):
    """Rendered document output with mandatory review disclaimer (REQ-DOC-08)."""

    template_id: int
    template_name: str
    version: str
    rendered_document: str
    disclaimer: str
