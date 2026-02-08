"""
CervixAI User Model
Enhanced with role relationship and additional security fields.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User roles in CervixAI system (legacy enum, use Role model for RBAC)."""
    ADMIN = "admin"
    PATHOLOGIST = "pathologist"
    CYTOTECHNOLOGIST = "cytotechnologist"
    PHYSICIAN = "physician"
    IT_ADMIN = "it_admin"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(150), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    name = Column(String(255), nullable=False)
    
    # Role - supports both legacy string role and new RBAC
    role = Column(String(50), nullable=False, default=UserRole.PHYSICIAN.value)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification
    
    # MFA support
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    
    # Session management
    last_login_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(String(10), default="0")
    locked_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role_ref = relationship("Role", back_populates="users")
    diagnoses = relationship("Diagnosis", back_populates="reviewer")
    annotations = relationship("Annotation", back_populates="clinician")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def is_locked(self) -> bool:
        """Check if account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has specific permission via role."""
        if self.role_ref:
            return self.role_ref.has_permission(resource, action)
        # Fallback for legacy role
        return self.role == UserRole.ADMIN.value
