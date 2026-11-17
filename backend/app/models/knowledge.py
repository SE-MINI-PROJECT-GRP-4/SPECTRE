"""Legal Knowledge Entry database model (SRS Appendix B / Admin knowledge base)."""

import json
from typing import List, Optional
from sqlalchemy import Column, String, Text
from app.database.session import Base
from app.models.base import TimestampMixin


class KnowledgeEntry(Base, TimestampMixin):
    """Statutory guidance and procedure knowledge base entries."""

    __tablename__ = "knowledge_entries"

    id = Column(String(50), primary_key=True)
    domain = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    keywords_json = Column(Text, nullable=True)  # JSON-encoded keywords
    prerequisites_json = Column(Text, nullable=True)  # JSON-encoded prerequisites list
    steps_json = Column(Text, nullable=True)  # JSON-encoded steps list
    ref_ids_json = Column(Text, nullable=True)  # JSON-encoded reference IDs
    template_hint = Column(String(255), nullable=True)

    @property
    def keywords(self) -> List[str]:
        if not self.keywords_json:
            return []
        try:
            return json.loads(self.keywords_json)
        except Exception:
            return []

    @property
    def prerequisites(self) -> List[str]:
        if not self.prerequisites_json:
            return []
        try:
            return json.loads(self.prerequisites_json)
        except Exception:
            return []

    @property
    def steps(self) -> List[str]:
        if not self.steps_json:
            return []
        try:
            return json.loads(self.steps_json)
        except Exception:
            return []

    @property
    def refIds(self) -> List[str]:
        if not self.ref_ids_json:
            return []
        try:
            return json.loads(self.ref_ids_json)
        except Exception:
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "explanation": self.explanation,
            "keywords": self.keywords,
            "prerequisites": self.prerequisites,
            "steps": self.steps,
            "refIds": self.refIds,
            "templateHint": self.template_hint,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
