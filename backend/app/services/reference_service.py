"""Service managing legal references, case-law retrieval, and administrative edits."""

from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.reference import LegalReference
from app.repositories.references import ReferenceRepository
from app.schemas.reference import ReferenceCreate, ReferenceListResponse, ReferenceResponse, ReferenceUpdate


class ReferenceService:
    """Service handling legal reference queries and admin operations (REQ-REF-01 to 08)."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ReferenceRepository(db)

    def search_references(
        self,
        domain: Optional[str] = None,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> ReferenceListResponse:
        skip = (page - 1) * limit
        items, total = self.repo.search(
            domain=domain,
            search_query=search,
            status=status_filter,
            skip=skip,
            limit=limit,
        )
        return ReferenceListResponse(
            total=total,
            page=page,
            limit=limit,
            items=[ReferenceResponse.model_validate(item) for item in items],
        )

    def get_reference(self, reference_id: int) -> ReferenceResponse:
        ref = self.repo.get_by_id(reference_id)
        if not ref:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal reference not found.",
            )
        return ReferenceResponse.model_validate(ref)

    def create_reference(self, data: ReferenceCreate) -> ReferenceResponse:
        ref = self.repo.create(data)
        return ReferenceResponse.model_validate(ref)

    def update_reference(self, reference_id: int, data: ReferenceUpdate) -> ReferenceResponse:
        ref = self.repo.get_by_id(reference_id)
        if not ref:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal reference not found.")
        updated = self.repo.update(ref, data)
        return ReferenceResponse.model_validate(updated)

    def delete_reference(self, reference_id: int) -> None:
        ref = self.repo.get_by_id(reference_id)
        if not ref:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal reference not found.")
        self.repo.delete(ref)
