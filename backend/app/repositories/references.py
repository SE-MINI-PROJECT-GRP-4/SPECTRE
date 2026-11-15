from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LegalReference


def get_reference_by_id(
    db: Session,
    reference_id: int,
) -> LegalReference | None:
    """
    Retrieve a legal reference by ID.
    """

    return db.scalar(
        select(LegalReference).where(
            LegalReference.reference_id == reference_id
        )
    )


def get_references_by_domain(
    db: Session,
    legal_domain: str,
) -> list[LegalReference]:
    """
    Retrieve active legal references for a legal domain.
    """

    return list(
        db.scalars(
            select(LegalReference)
            .where(
                LegalReference.legal_domain == legal_domain,
                LegalReference.status == "active",
            )
        )
    )