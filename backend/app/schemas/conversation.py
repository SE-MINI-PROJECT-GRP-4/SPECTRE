"""Conversation and Messaging Pydantic Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.query import CitationSchema, LegalDomainEnum


class MessageResponse(BaseModel):
    """Message item representation in conversation history (REQ-HIST-01, REQ-HIST-03)."""

    id: int
    conversation_id: int
    role: str
    content: str
    legal_domain: Optional[str] = None
    citations: List[CitationSchema] = []
    procedural_steps: List[str] = []
    confidence: Optional[float] = None
    disclaimer: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Request payload to initiate a new legal query conversation thread."""

    title: Optional[str] = Field(None, max_length=255, description="Conversation title or subject")
    legal_domain: Optional[LegalDomainEnum] = None


class ConversationResponse(BaseModel):
    """Conversation summary metadata response."""

    id: int
    user_id: int
    title: str
    legal_domain: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Detailed conversation representation including chronological message history."""

    messages: List[MessageResponse] = []


class QuerySubmitRequest(BaseModel):
    """Payload to submit a legal query in a conversation (REQ-QUERY-01, REQ-QUERY-11)."""

    question: str = Field(..., min_length=2, max_length=2000, description="Legal question or follow-up query")
    top_k: Optional[int] = Field(5, ge=1, le=20)
