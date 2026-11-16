from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class LegalReference(Base):
    """
    Database model representing a legal or case-law reference.
    """

    __tablename__ = "legal_references"

    reference_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    legal_domain: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    reference_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    link: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )