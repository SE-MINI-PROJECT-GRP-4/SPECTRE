"""Legal Document Template Engine with variable customization."""

import json
import re
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.template import DocumentTemplate
from app.repositories.templates import TemplateRepository
from app.schemas.template import (
    TemplateCreate,
    TemplateRenderRequest,
    TemplateRenderResponse,
    TemplateResponse,
    TemplateUpdate,
    TemplateVariableSchema,
)

TEMPLATE_DISCLAIMER = (
    "DISCLAIMER & NOTICE: This template is generated based on standard formats under Indian law. "
    "Legal documents may require case-specific modifications, precise factual recitals, state-specific stamp duty, "
    "and professional review by a licensed advocate before execution or submission to courts or authorities."
)


class TemplateService:
    """Service handling template queries, variable rendering, and administration."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = TemplateRepository(db)

    def _to_dto(self, tpl: DocumentTemplate) -> TemplateResponse:
        vars_list = []
        if tpl.variables_json:
            try:
                raw_list = json.loads(tpl.variables_json)
                vars_list = [TemplateVariableSchema(**v) for v in raw_list]
            except Exception:
                vars_list = []

        return TemplateResponse(
            id=tpl.id,
            name=tpl.name,
            slug=tpl.slug,
            category=tpl.category,
            description=tpl.description,
            content=tpl.content,
            version=tpl.version,
            status=tpl.status,
            variables=vars_list,
            created_at=tpl.created_at,
            updated_at=tpl.updated_at,
        )

    def list_templates(self, category: Optional[str] = None) -> List[TemplateResponse]:
        items = self.repo.list_templates(category=category, status_filter="active")
        return [self._to_dto(t) for t in items]

    def get_template(self, template_id: int) -> TemplateResponse:
        tpl = self.repo.get_by_id(template_id)
        if not tpl:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found.")
        return self._to_dto(tpl)

    def render_template(self, template_id: int, payload: TemplateRenderRequest) -> TemplateRenderResponse:
        """
        Renders the document by substituting variables {{key}} with user-supplied values (REQ-DOC-04, REQ-DOC-08).
        """
        tpl = self.repo.get_by_id(template_id)
        if not tpl:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found.")

        rendered_text = tpl.content
        user_vars = payload.variables or {}

        # Replace tags like {{key}}
        for key, val in user_vars.items():
            pattern = re.compile(rf"\{{\{{\s*{re.escape(key)}\s*\}}\}}")
            rendered_text = pattern.sub(str(val), rendered_text)

        # Append mandatory template customization disclaimer
        final_doc = f"{rendered_text}\n\n{'='*70}\n{TEMPLATE_DISCLAIMER}\n{'='*70}"

        return TemplateRenderResponse(
            template_id=tpl.id,
            template_name=tpl.name,
            version=tpl.version,
            rendered_document=final_doc,
            disclaimer=TEMPLATE_DISCLAIMER,
        )

    def create_template(self, data: TemplateCreate) -> TemplateResponse:
        existing = self.repo.get_by_slug(data.slug)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Template slug already exists.")
        tpl = self.repo.create(data)
        return self._to_dto(tpl)

    def update_template(self, template_id: int, data: TemplateUpdate) -> TemplateResponse:
        tpl = self.repo.get_by_id(template_id)
        if not tpl:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found.")
        updated = self.repo.update(tpl, data)
        return self._to_dto(updated)

    def delete_template(self, template_id: int) -> None:
        tpl = self.repo.get_by_id(template_id)
        if not tpl:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found.")
        self.repo.delete(tpl)
