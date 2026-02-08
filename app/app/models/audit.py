"""
CervixAI Audit Log Model - Immutable compliance logging
Enhanced with resource tracking and JSON details.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class AuditLog(Base):
    """Immutable audit log for HIPAA/GDPR compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Who performed the action
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)  # Denormalized for historical record
    
    # What action was performed
    action = Column(String(100), nullable=False, index=True)
    # Examples: "patient.create", "diagnosis.approve", "user.login", "annotation.sign_off"
    
    # Resource affected
    resource_type = Column(String(100), nullable=True)  # patient, sample, diagnosis, etc.
    resource_id = Column(String(36), nullable=True)
    
    # Additional details as JSON (tamper-evident via hash if needed)
    # Structure: {"before": {...}, "after": {...}, "changes": [...], "reason": "..."}
    details = Column(JSON, nullable=True, default=dict)
    
    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(36), nullable=True)  # For request tracing
    
    # Severity level
    severity = Column(String(20), default="info")  # info, warning, critical
    
    # Immutable timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_email} at {self.timestamp}>"
    
    @classmethod
    def log_action(cls, db_session, action: str, user=None, resource_type=None, 
                   resource_id=None, details=None, ip_address=None, severity="info"):
        """Helper to create audit log entry."""
        log = cls(
            action=action,
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            severity=severity
        )
        db_session.add(log)
        return log
