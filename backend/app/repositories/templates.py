"""Document Template repository for database operations."""

import json
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.template import DocumentTemplate
from app.schemas.template import TemplateCreate, TemplateUpdate


class TemplateRepository:
    """Repository handling CRUD operations for DocumentTemplate entities."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, template_id: int) -> Optional[DocumentTemplate]:
        return self.db.scalar(select(DocumentTemplate).where(DocumentTemplate.id == template_id))

    def get_by_slug(self, slug: str) -> Optional[DocumentTemplate]:
        return self.db.scalar(select(DocumentTemplate).where(DocumentTemplate.slug == slug.lower().strip()))

    def list_templates(self, category: Optional[str] = None, status_filter: Optional[str] = "active") -> List[DocumentTemplate]:
        stmt = select(DocumentTemplate)
        if category:
            stmt = stmt.where(DocumentTemplate.category == category.lower().strip())
        if status_filter:
            stmt = stmt.where(DocumentTemplate.status == status_filter.lower().strip())
        return list(self.db.scalars(stmt.order_by(DocumentTemplate.name.asc())).all())

    def create(self, data: TemplateCreate) -> DocumentTemplate:
        var_json = json.dumps([v.model_dump() for v in data.variables]) if data.variables else None
        tpl = DocumentTemplate(
            name=data.name,
            slug=data.slug.lower().strip(),
            category=data.category.lower().strip(),
            description=data.description,
            content=data.content,
            version=data.version,
            variables_json=var_json,
            status=data.status,
        )
        self.db.add(tpl)
        self.db.commit()
        self.db.refresh(tpl)
        return tpl

    def update(self, tpl: DocumentTemplate, data: TemplateUpdate) -> DocumentTemplate:
        update_dict = data.model_dump(exclude_unset=True)
        if "variables" in update_dict and update_dict["variables"] is not None:
            tpl.variables_json = json.dumps([v.model_dump() for v in data.variables])
            del update_dict["variables"]

        for key, value in update_dict.items():
            setattr(tpl, key, value)

        self.db.commit()
        self.db.refresh(tpl)
        return tpl

    def delete(self, tpl: DocumentTemplate) -> None:
        self.db.delete(tpl)
        self.db.commit()
