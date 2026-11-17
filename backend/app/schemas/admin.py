"""Admin Management and Audit Pydantic Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, computed_field
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


class AdminStatsResponse(BaseModel):
    """Unified operational stats for admin dashboard (Frontend contract)."""

    users: int
    conversations: int
    knowledgeEntries: int
    references: int
    outdatedReferences: int
    templates: int


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

    @computed_field
    @property
    def at(self) -> str:
        return self.timestamp.isoformat() if self.timestamp else ""

    @computed_field
    @property
    def actor(self) -> str:
        return self.admin_email or (f"Admin #{self.admin_id}" if self.admin_id else "System")

    @computed_field
    @property
    def target(self) -> str:
        return f"{self.resource_type}:{self.resource_id}" if self.resource_id else self.resource_type

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdateRequest(BaseModel):
    """Admin request to change user access privileges."""

    role: UserRole


class UserStatusUpdateRequest(BaseModel):
    """Admin request to activate or deactivate a user account."""

    is_active: bool


class UserGenericUpdateRequest(BaseModel):
    """Unified user update request supporting role and active toggle."""

    role: Optional[str] = None
    active: Optional[bool] = None
    is_active: Optional[bool] = None

