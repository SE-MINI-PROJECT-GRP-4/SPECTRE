"""Legal Reference repository for database operations."""

from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.models.reference import LegalReference
from app.schemas.reference import ReferenceCreate, ReferenceUpdate


class ReferenceRepository:
    """Repository handling CRUD and searching for LegalReference entities."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reference_id: int) -> Optional[LegalReference]:
        return self.db.scalar(select(LegalReference).where(LegalReference.id == reference_id))

    def search(
        self,
        domain: Optional[str] = None,
        search_query: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[LegalReference], int]:
        """Search and filter legal references by domain, keywords, and status (REQ-REF-02, REQ-REF-06)."""
        stmt = select(LegalReference)

        if domain:
            stmt = stmt.where(LegalReference.legal_domain == domain.lower().strip())
        if status:
            stmt = stmt.where(LegalReference.status == status.lower().strip())
        if search_query:
            term = f"%{search_query.strip()}%"
            stmt = stmt.where(
                or_(
                    LegalReference.title.ilike(term),
                    LegalReference.citation.ilike(term),
                    LegalReference.summary.ilike(term),
                )
            )

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.order_by(LegalReference.year.desc().nullslast()).offset(skip).limit(limit)).all())
        return items, total

    def create(self, data: ReferenceCreate) -> LegalReference:
        ref = LegalReference(
            title=data.title,
            citation=data.citation,
            source=data.source,
            legal_domain=data.legal_domain.lower(),
            year=data.year,
            court=data.court,
            url=data.url,
            status=data.status,
            summary=data.summary,
            content=data.content,
        )
        self.db.add(ref)
        self.db.commit()
        self.db.refresh(ref)
        return ref

    def update(self, ref: LegalReference, data: ReferenceUpdate) -> LegalReference:
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(ref, key, value)
        self.db.commit()
        self.db.refresh(ref)
        return ref

    def delete(self, ref: LegalReference) -> None:
        self.db.delete(ref)
        self.db.commit()
