"""Database models package."""

from app.models.base import TimestampMixin
from app.models.user import User, UserRole
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.reference import LegalReference
from app.models.template import DocumentTemplate
from app.models.audit_log import AuditLog
from app.models.knowledge import KnowledgeEntry

__all__ = [
    "TimestampMixin",
    "User",
    "UserRole",
    "Conversation",
    "Message",
    "LegalReference",
    "DocumentTemplate",
    "AuditLog",
    "KnowledgeEntry",
]
