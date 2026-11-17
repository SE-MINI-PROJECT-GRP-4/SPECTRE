"""Administrator API v1 Endpoints (REQ-ADMIN-01 through REQ-ADMIN-07)."""

import json
import re
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.audit_log import AuditLog
from app.models.conversation import Conversation
from app.models.knowledge import KnowledgeEntry
from app.models.message import Message
from app.models.reference import LegalReference
from app.models.template import DocumentTemplate
from app.models.user import User, UserRole
from app.repositories.users import UserRepository
from app.schemas.admin import (
    AdminMetricsResponse,
    AdminStatsResponse,
    AuditLogResponse,
    UserGenericUpdateRequest,
    UserRoleUpdateRequest,
    UserStatusUpdateRequest,
)
from app.schemas.auth import UserResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["Administrator Management"])


@router.get(
    "/overview",
    response_model=AdminMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get system overview metrics",
    description="Returns aggregate counts of users, conversations, queries, references, and domain distribution (REQ-ADMIN-07).",
)
def get_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AdminMetricsResponse:
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_convs = db.scalar(select(func.count(Conversation.id))) or 0
    total_msgs = db.scalar(select(func.count(Message.id))) or 0
    total_refs = db.scalar(select(func.count(LegalReference.id))) or 0
    total_tpls = db.scalar(select(func.count(DocumentTemplate.id))) or 0
    total_audits = db.scalar(select(func.count(AuditLog.id))) or 0

    # Domain distribution
    domain_counts_raw = db.execute(
        select(Conversation.legal_domain, func.count(Conversation.id))
        .where(Conversation.legal_domain.isnot(None))
        .group_by(Conversation.legal_domain)
    ).all()

    domain_dict = {domain: count for domain, count in domain_counts_raw if domain}

    return AdminMetricsResponse(
        total_users=total_users,
        total_conversations=total_convs,
        total_messages=total_msgs,
        total_references=total_refs,
        total_templates=total_tpls,
        total_audit_events=total_audits,
        domain_distribution=domain_dict,
    )


@router.get(
    "/stats",
    response_model=AdminStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated statistics for admin dashboard",
)
def get_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AdminStatsResponse:
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_convs = db.scalar(select(func.count(Conversation.id))) or 0
    total_refs = db.scalar(select(func.count(LegalReference.id))) or 0
    outdated_refs = db.scalar(
        select(func.count(LegalReference.id)).where(LegalReference.status.in_(["outdated", "repealed", "inactive"]))
    ) or 0
    total_tpls = db.scalar(select(func.count(DocumentTemplate.id))) or 0
    total_kb = db.scalar(select(func.count(KnowledgeEntry.id))) or 0

    return AdminStatsResponse(
        users=total_users,
        conversations=total_convs,
        knowledgeEntries=total_kb,
        references=total_refs,
        outdatedReferences=outdated_refs,
        templates=total_tpls,
    )


@router.get(
    "/audit",
    response_model=List[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Get audit logs for admin dashboard",
)
def get_audit(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> List[AuditLogResponse]:
    service = AuditService(db)
    return service.list_logs(skip=skip, limit=limit)


@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="View administrative audit logs",
    description="Returns auditable log of administrative actions (REQ-ADMIN-06, NFR-SEC-10).",
)
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> List[AuditLogResponse]:
    service = AuditService(db)
    return service.list_logs(skip=skip, limit=limit)


# ============================================================================
# User Administration
# ============================================================================

@router.get(
    "/users",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all registered users",
    description="Allows administrator to review user accounts (REQ-ADMIN-05).",
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> List[UserResponse]:
    repo = UserRepository(db)
    users = repo.list_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user role",
    description="Promotes or updates user permissions, logging the change for auditability (REQ-ADMIN-05, REQ-ADMIN-06).",
)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserResponse:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    old_role = user.role.value
    updated = repo.update_role(user, payload.role)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="UPDATE_USER_ROLE",
        resource_type="user",
        resource_id=str(user.id),
        details={"old_role": old_role, "new_role": payload.role.value, "target_email": user.email},
        ip_address=request.client.host if request.client else None,
    )

    return UserResponse.model_validate(updated)


@router.put(
    "/users/{user_id}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate or deactivate user account",
    description="Enables or disables user access, maintaining audit log trail.",
)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserResponse:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    updated = repo.update_status(user, payload.is_active)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="UPDATE_USER_STATUS",
        resource_type="user",
        resource_id=str(user.id),
        details={"is_active": payload.is_active, "target_email": user.email},
        ip_address=request.client.host if request.client else None,
    )

    return UserResponse.model_validate(updated)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user role and/or active status",
)
def update_user_unified(
    user_id: int,
    payload: UserGenericUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserResponse:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    audit = AuditService(db)
    details = {}
    if payload.role:
        old_role = user.role.value
        try:
            target_role = UserRole(payload.role)
        except ValueError:
            target_role = UserRole.USER if str(payload.role).lower() == "user" else UserRole.ADMIN
        user = repo.update_role(user, target_role)
        details["role"] = {"old": old_role, "new": user.role.value}

    new_active = payload.active if payload.active is not None else payload.is_active
    if new_active is not None:
        old_active = user.is_active
        user = repo.update_status(user, new_active)
        details["active"] = {"old": old_active, "new": user.is_active}

    audit.record_action(
        admin_id=admin.id,
        action="UPDATE_USER",
        resource_type="user",
        resource_id=str(user.id),
        details=details,
        ip_address=request.client.host if request.client else None,
    )
    return UserResponse.model_validate(user)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user account",
)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    email = user.email
    db.delete(user)
    db.commit()

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="DELETE_USER",
        resource_type="user",
        resource_id=str(user_id),
        details={"email": email},
        ip_address=request.client.host if request.client else None,
    )
    return {"status": "success", "message": f"User {email} successfully deleted."}


# ============================================================================
# Knowledge Entries Administration
# ============================================================================

@router.get("/knowledge", status_code=status.HTTP_200_OK)
def list_knowledge(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> List[dict]:
    entries = db.query(KnowledgeEntry).all()
    return [e.to_dict() for e in entries]


@router.post("/knowledge", status_code=status.HTTP_201_CREATED)
def create_knowledge(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    entry_id = payload.get("id") or f"kb-{uuid.uuid4().hex[:8]}"
    entry = KnowledgeEntry(
        id=entry_id,
        domain=payload.get("domain", "General"),
        title=payload.get("title", ""),
        explanation=payload.get("explanation", ""),
        keywords_json=json.dumps(payload.get("keywords") or []),
        prerequisites_json=json.dumps(payload.get("prerequisites") or []),
        steps_json=json.dumps(payload.get("steps") or []),
        ref_ids_json=json.dumps(payload.get("refIds") or payload.get("ref_ids") or []),
        template_hint=payload.get("templateHint") or payload.get("template_hint"),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="CREATE_KNOWLEDGE",
        resource_type="knowledge",
        resource_id=str(entry.id),
        details={"title": entry.title, "domain": entry.domain},
        ip_address=request.client.host if request.client else None,
    )
    return entry.to_dict()


@router.put("/knowledge/{entry_id}", status_code=status.HTTP_200_OK)
def update_knowledge(
    entry_id: str,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge entry not found.")

    if "domain" in payload:
        entry.domain = payload["domain"]
    if "title" in payload:
        entry.title = payload["title"]
    if "explanation" in payload:
        entry.explanation = payload["explanation"]
    if "keywords" in payload:
        entry.keywords_json = json.dumps(payload["keywords"])
    if "prerequisites" in payload:
        entry.prerequisites_json = json.dumps(payload["prerequisites"])
    if "steps" in payload:
        entry.steps_json = json.dumps(payload["steps"])
    if "refIds" in payload or "ref_ids" in payload:
        entry.ref_ids_json = json.dumps(payload.get("refIds") or payload.get("ref_ids") or [])
    if "templateHint" in payload or "template_hint" in payload:
        entry.template_hint = payload.get("templateHint") or payload.get("template_hint")

    db.commit()
    db.refresh(entry)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="UPDATE_KNOWLEDGE",
        resource_type="knowledge",
        resource_id=str(entry.id),
        details={"title": entry.title},
        ip_address=request.client.host if request.client else None,
    )
    return entry.to_dict()


@router.delete("/knowledge/{entry_id}", status_code=status.HTTP_200_OK)
def delete_knowledge(
    entry_id: str,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge entry not found.")

    title = entry.title
    db.delete(entry)
    db.commit()

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="DELETE_KNOWLEDGE",
        resource_type="knowledge",
        resource_id=str(entry_id),
        details={"title": title},
        ip_address=request.client.host if request.client else None,
    )
    return {"status": "success", "message": "Knowledge entry successfully removed."}


# ============================================================================
# Legal References Administration
# ============================================================================

@router.get("/references", status_code=status.HTTP_200_OK)
def list_admin_references(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> List[dict]:
    refs = db.query(LegalReference).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "source": r.source or r.citation or "",
            "domain": r.legal_domain,
            "date": f"{r.year}-01-01" if r.year else (r.created_at.strftime("%Y-%m-%d") if r.created_at else ""),
            "link": r.url or "",
            "status": r.status,
        }
        for r in refs
    ]


@router.post("/references", status_code=status.HTTP_201_CREATED)
def create_admin_reference(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    year = None
    if payload.get("date"):
        try:
            year = int(str(payload["date"])[:4])
        except (ValueError, TypeError):
            pass

    ref = LegalReference(
        title=payload.get("title", ""),
        source=payload.get("source", ""),
        legal_domain=payload.get("domain") or payload.get("legal_domain", "General"),
        year=year or payload.get("year"),
        url=payload.get("link") or payload.get("url", ""),
        status=payload.get("status", "active"),
        summary=payload.get("summary", ""),
        content=payload.get("content", ""),
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="CREATE_REFERENCE",
        resource_type="reference",
        resource_id=str(ref.id),
        details={"title": ref.title},
        ip_address=request.client.host if request.client else None,
    )
    return {
        "id": ref.id,
        "title": ref.title,
        "source": ref.source or "",
        "domain": ref.legal_domain,
        "date": f"{ref.year}-01-01" if ref.year else "",
        "link": ref.url or "",
        "status": ref.status,
    }


@router.put("/references/{ref_id}", status_code=status.HTTP_200_OK)
def update_admin_reference(
    ref_id: int,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    ref = db.query(LegalReference).filter(LegalReference.id == ref_id).first()
    if not ref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal reference not found.")

    if "title" in payload:
        ref.title = payload["title"]
    if "source" in payload:
        ref.source = payload["source"]
    if "domain" in payload:
        ref.legal_domain = payload["domain"]
    elif "legal_domain" in payload:
        ref.legal_domain = payload["legal_domain"]
    if "link" in payload:
        ref.url = payload["link"]
    elif "url" in payload:
        ref.url = payload["url"]
    if "status" in payload:
        ref.status = payload["status"]
    if "date" in payload and payload["date"]:
        try:
            ref.year = int(str(payload["date"])[:4])
        except (ValueError, TypeError):
            pass

    db.commit()
    db.refresh(ref)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="UPDATE_REFERENCE",
        resource_type="reference",
        resource_id=str(ref.id),
        details={"title": ref.title},
        ip_address=request.client.host if request.client else None,
    )
    return {
        "id": ref.id,
        "title": ref.title,
        "source": ref.source or "",
        "domain": ref.legal_domain,
        "date": f"{ref.year}-01-01" if ref.year else "",
        "link": ref.url or "",
        "status": ref.status,
    }


@router.delete("/references/{ref_id}", status_code=status.HTTP_200_OK)
def delete_admin_reference(
    ref_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    ref = db.query(LegalReference).filter(LegalReference.id == ref_id).first()
    if not ref:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal reference not found.")

    title = ref.title
    db.delete(ref)
    db.commit()

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="DELETE_REFERENCE",
        resource_type="reference",
        resource_id=str(ref_id),
        details={"title": title},
        ip_address=request.client.host if request.client else None,
    )
    return {"status": "success", "message": "Legal reference successfully removed."}


# ============================================================================
# Document Templates Administration
# ============================================================================

@router.get("/templates", status_code=status.HTTP_200_OK)
def list_admin_templates(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> List[dict]:
    tpls = db.query(DocumentTemplate).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "slug": t.slug,
            "category": t.category,
            "description": t.description,
            "version": t.version,
            "status": t.status,
            "content": t.content,
        }
        for t in tpls
    ]


@router.post("/templates", status_code=status.HTTP_201_CREATED)
def create_admin_template(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    name = payload.get("name", "")
    slug = payload.get("slug")
    if not slug:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
        if not slug:
            slug = f"tpl-{uuid.uuid4().hex[:6]}"
        if db.query(DocumentTemplate).filter(DocumentTemplate.slug == slug).first():
            slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    tpl = DocumentTemplate(
        name=name,
        slug=slug,
        category=payload.get("category", "General"),
        description=payload.get("description", ""),
        version=payload.get("version", "1.0"),
        status=payload.get("status", "active"),
        content=payload.get("content", ""),
        variables_json=json.dumps(payload.get("variables") or []),
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="CREATE_TEMPLATE",
        resource_type="template",
        resource_id=str(tpl.id),
        details={"name": tpl.name},
        ip_address=request.client.host if request.client else None,
    )
    return {
        "id": tpl.id,
        "name": tpl.name,
        "slug": tpl.slug,
        "category": tpl.category,
        "description": tpl.description,
        "version": tpl.version,
        "status": tpl.status,
        "content": tpl.content,
    }


@router.put("/templates/{tpl_id}", status_code=status.HTTP_200_OK)
def update_admin_template(
    tpl_id: int,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    tpl = db.query(DocumentTemplate).filter(DocumentTemplate.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found.")

    if "name" in payload:
        tpl.name = payload["name"]
    if "category" in payload:
        tpl.category = payload["category"]
    if "description" in payload:
        tpl.description = payload["description"]
    if "version" in payload:
        tpl.version = payload["version"]
    if "status" in payload:
        tpl.status = payload["status"]
    if "content" in payload:
        tpl.content = payload["content"]

    db.commit()
    db.refresh(tpl)

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="UPDATE_TEMPLATE",
        resource_type="template",
        resource_id=str(tpl.id),
        details={"name": tpl.name},
        ip_address=request.client.host if request.client else None,
    )
    return {
        "id": tpl.id,
        "name": tpl.name,
        "slug": tpl.slug,
        "category": tpl.category,
        "description": tpl.description,
        "version": tpl.version,
        "status": tpl.status,
        "content": tpl.content,
    }


@router.delete("/templates/{tpl_id}", status_code=status.HTTP_200_OK)
def delete_admin_template(
    tpl_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    tpl = db.query(DocumentTemplate).filter(DocumentTemplate.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found.")

    name = tpl.name
    db.delete(tpl)
    db.commit()

    audit = AuditService(db)
    audit.record_action(
        admin_id=admin.id,
        action="DELETE_TEMPLATE",
        resource_type="template",
        resource_id=str(tpl_id),
        details={"name": name},
        ip_address=request.client.host if request.client else None,
    )
    return {"status": "success", "message": "Document template successfully removed."}
