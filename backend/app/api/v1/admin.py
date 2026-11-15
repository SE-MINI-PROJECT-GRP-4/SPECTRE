"""Administrator API v1 Endpoints (REQ-ADMIN-01 through REQ-ADMIN-07)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.audit_log import AuditLog
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.reference import LegalReference
from app.models.template import DocumentTemplate
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.admin import (
    AdminMetricsResponse,
    AuditLogResponse,
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

    # Record audit event
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
