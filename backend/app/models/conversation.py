"""Conversation database model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import TimestampMixin


class Conversation(Base, TimestampMixin):
    """Conversation session model for legal queries."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Legal Query")
    legal_domain = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="active")

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
