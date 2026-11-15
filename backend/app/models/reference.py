"""Legal Reference database model."""

from sqlalchemy import Column, Integer, String, Text
from app.database.session import Base
from app.models.base import TimestampMixin


class LegalReference(Base, TimestampMixin):
    """Authoritative legal acts, statutory sections, and case-law references."""

    __tablename__ = "legal_references"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    citation = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    legal_domain = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=True)
    court = Column(String(150), nullable=True)
    url = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="active")  # 'active', 'outdated', 'repealed'
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
