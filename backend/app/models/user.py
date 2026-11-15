"""User and Role database models."""

import enum
from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import TimestampMixin


class UserRole(str, enum.Enum):
    """User access control roles."""

    USER = "user"
    ADMIN = "admin"
    ADVOCATE = "advocate"


class User(Base, TimestampMixin):
    """Registered user account model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="admin", foreign_keys="AuditLog.admin_id")
