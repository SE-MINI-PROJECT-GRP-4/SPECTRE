"""Audit Logging Service recording administrative actions (REQ-ADMIN-06)."""

import json
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.schemas.admin import AuditLogResponse


class AuditService:
    """Service handling audit recording and retrieval."""

    def __init__(self, db: Session):
        self.db = db

    def record_action(
        self,
        action: str,
        resource_type: str,
        admin_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Records an auditable administrative or security event."""
        log = AuditLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=json.dumps(details) if details else None,
            ip_address=ip_address,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_logs(self, skip: int = 0, limit: int = 50) -> List[AuditLogResponse]:
        logs = list(
            self.db.scalars(
                select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
            ).all()
        )

        results = []
        for l in logs:
            det = None
            if l.details_json:
                try:
                    det = json.loads(l.details_json)
                except Exception:
                    det = {}

            results.append(
                AuditLogResponse(
                    id=l.id,
                    admin_id=l.admin_id,
                    admin_email=l.admin.email if l.admin else None,
                    action=l.action,
                    resource_type=l.resource_type,
                    resource_id=l.resource_id,
                    details=det,
                    ip_address=l.ip_address,
                    timestamp=l.timestamp,
                )
            )
        return results
