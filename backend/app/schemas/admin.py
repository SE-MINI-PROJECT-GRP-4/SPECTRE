"""Admin Management and Audit Pydantic Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.models.user import UserRole
from app.schemas.auth import UserResponse


class AdminMetricsResponse(BaseModel):
    """System-wide operational metrics (REQ-ADMIN-07)."""

    total_users: int
    total_conversations: int
    total_messages: int
    total_references: int
    total_templates: int
    total_audit_events: int
    domain_distribution: Dict[str, int] = {}


class AuditLogResponse(BaseModel):
    """Audit log event representation (REQ-ADMIN-06)."""

    id: int
    admin_id: Optional[int] = None
    admin_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class UserRoleUpdateRequest(BaseModel):
    """Admin request to change user access privileges."""

    role: UserRole


class UserStatusUpdateRequest(BaseModel):
    """Admin request to activate or deactivate a user account."""

    is_active: bool
