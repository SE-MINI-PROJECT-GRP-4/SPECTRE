"""Message database model."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import TimestampMixin


class Message(Base, TimestampMixin):
    """Individual query or response message within a conversation."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    legal_domain = Column(String(100), nullable=True)
    citations_json = Column(Text, nullable=True)  # JSON-encoded verified citations
    procedural_steps_json = Column(Text, nullable=True)  # JSON-encoded procedural guidance
    confidence = Column(Float, nullable=True)
    disclaimer = Column(Text, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
