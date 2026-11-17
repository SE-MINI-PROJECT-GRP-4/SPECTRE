"""Conversation and Messaging Pydantic Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.query import CitationSchema, LegalDomainEnum


"""Conversation and Messaging Pydantic Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, computed_field
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

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def text(self) -> str:
        return self.content

    @computed_field
    @property
    def domain(self) -> Optional[str]:
        return self.legal_domain

    @computed_field
    @property
    def createdAt(self) -> str:
        return self.created_at.isoformat()

    @computed_field
    @property
    def procedure(self) -> Optional[Dict[str, Any]]:
        if self.procedural_steps:
            return {
                "prerequisites": ["Relevant documentary records and proof of transaction/incident"],
                "steps": self.procedural_steps,
            }
        return None

    @computed_field
    @property
    def sources(self) -> List[Dict[str, Any]]:
        if not self.citations:
            return []
        res = []
        for i, c in enumerate(self.citations):
            title = c.document
            if c.section:
                title = f"{c.document} ({c.section})"
            res.append({
                "id": f"src-{i+1}",
                "title": title,
                "source": "India Code / Statutory Gazette",
                "status": "active",
                "link": "https://www.indiacode.nic.in",
            })
        return res

    @computed_field
    @property
    def notes(self) -> List[str]:
        return ["Procedures can vary by state, jurisdiction and facts (REQ-PROC-04)."]

    @computed_field
    @property
    def template(self) -> Optional[Dict[str, Any]]:
        domain_str = (self.legal_domain or "").lower()
        if "consumer" in domain_str:
            return {"id": 1, "name": "Legal notice for consumer complaint"}
        if "cyber" in domain_str:
            return {"id": 5, "name": "Cyber crime complaint"}
        if "rti" in domain_str or "constitutional" in domain_str:
            return {"id": 4, "name": "RTI application"}
        if "property" in domain_str or "tenancy" in domain_str or "civil" in domain_str:
            return {"id": 2, "name": "Rental agreement"}
        if "employment" in domain_str or "labor" in domain_str:
            return {"id": 3, "name": "Unpaid wages demand letter"}
        return None


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

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def domain(self) -> Optional[str]:
        return self.legal_domain

    @computed_field
    @property
    def messageCount(self) -> int:
        return self.message_count

    @computed_field
    @property
    def createdAt(self) -> str:
        return self.created_at.isoformat()

    @computed_field
    @property
    def updatedAt(self) -> str:
        return self.updated_at.isoformat()


class ConversationDetailResponse(ConversationResponse):
    """Detailed conversation representation including chronological message history."""

    messages: List[MessageResponse] = []


class QuerySubmitRequest(BaseModel):
    """Payload to submit a legal query in a conversation (REQ-QUERY-01, REQ-QUERY-11)."""

    question: str = Field(..., min_length=2, max_length=2000, description="Legal question or follow-up query")
    top_k: Optional[int] = Field(5, ge=1, le=20)


class FrontendQueryRequest(BaseModel):
    """Unified query payload submitted by frontend (REQ-QUERY-01 through REQ-QUERY-04)."""

    text: str = Field(..., min_length=2, max_length=2000, description="Legal question or problem description")
    conversationId: Optional[Union[int, str]] = None


class FrontendUserMessage(BaseModel):
    id: Union[int, str]
    role: str = "user"
    text: str
    createdAt: str


class FrontendAnswer(BaseModel):
    id: Union[int, str]
    role: str = "assistant"
    text: str
    domain: Optional[str] = None
    confidence: str = "medium"
    procedure: Optional[Dict[str, Any]] = None
    sources: List[Dict[str, Any]] = []
    notes: List[str] = []
    template: Optional[Dict[str, Any]] = None
    disclaimer: str
    createdAt: str


class FrontendQueryResponse(BaseModel):
    conversationId: Optional[int] = None
    userMessage: FrontendUserMessage
    answer: FrontendAnswer
