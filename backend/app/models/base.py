"""Base model definitions and mixins."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from app.database.session import Base


class TimestampMixin:
    """Provides created_at and updated_at datetime stamps."""

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
