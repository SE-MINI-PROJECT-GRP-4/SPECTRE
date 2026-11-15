from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentTemplate


def get_template_by_id(
    db: Session,
    template_id: int,
) -> DocumentTemplate | None:
    """
    Retrieve a document template by ID.
    """

    return db.scalar(
        select(DocumentTemplate).where(
            DocumentTemplate.template_id == template_id
        )
    )


def get_templates_by_category(
    db: Session,
    category: str,
) -> list[DocumentTemplate]:
    """
    Retrieve active templates for a category.
    """

    return list(
        db.scalars(
            select(DocumentTemplate)
            .where(
                DocumentTemplate.category == category,
                DocumentTemplate.status == "active",
            )
        )
    )