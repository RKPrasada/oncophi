"""
CervixAI Audit Service
Business logic for compliance and audit logging.
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import AuditLog


class AuditService:
    """Service for audit and compliance operations."""
    
    def __init__(self, db: Session, current_user=None):
        self.db = db
        self.user = current_user
    
    def log_action(
        self,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        details: dict = None,
        ip_address: str = None,
        severity: str = "info"
    ) -> AuditLog:
        """Create an audit log entry."""
        log = AuditLog(
            action=action,
            user_id=self.user.id if self.user else None,
            user_email=self.user.email if self.user else None,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            severity=severity
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_logs(
        self,
        action: str = None,
        resource_type: str = None,
        resource_id: str = None,
        user_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        severity: str = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[AuditLog], int]:
        """Query audit logs with filters."""
        query = self.db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if severity:
            query = query.filter(AuditLog.severity == severity)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        total = query.count()
        logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
        
        return logs, total
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[AuditLog]:
        """Get recent activity for a user."""
        start_date = datetime.utcnow() - timedelta(days=days)
        logs, _ = self.get_logs(user_id=user_id, start_date=start_date, limit=100)
        return logs
    
    def get_resource_history(self, resource_type: str, resource_id: str) -> List[AuditLog]:
        """Get full audit history for a resource."""
        logs, _ = self.get_logs(resource_type=resource_type, resource_id=resource_id, limit=100)
        return logs
    
    def get_critical_actions(self, days: int = 7) -> List[AuditLog]:
        """Get critical actions for compliance review."""
        start_date = datetime.utcnow() - timedelta(days=days)
        logs, _ = self.get_logs(severity="critical", start_date=start_date, limit=200)
        return logs
