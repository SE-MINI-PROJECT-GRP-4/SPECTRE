"""Document Template database model."""

from sqlalchemy import Column, Integer, String, Text
from app.database.session import Base
from app.models.base import TimestampMixin


class DocumentTemplate(Base, TimestampMixin):
    """Reusable legal document template model."""

    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False, index=True)  # 'consumer', 'criminal', 'civil', 'cyber'
    description = Column(Text, nullable=False)
    content = Column(Text, nullable=False)  # Raw template text with placeholder tags like {{name}}
    version = Column(String(50), nullable=False, default="1.0")
    variables_json = Column(Text, nullable=True)  # JSON array of variable schema objects
    status = Column(String(50), nullable=False, default="active")  # 'active', 'archived'
