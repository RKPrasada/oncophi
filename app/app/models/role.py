"""
CervixAI Role Model - RBAC permissions management
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Role(Base):
    """Role model for Role-Based Access Control."""
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Permissions stored as JSON for flexibility
    # Example: {"patients": ["read", "write"], "diagnoses": ["read", "write", "approve"]}
    permissions = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="role_ref")
    
    def __repr__(self):
        return f"<Role {self.role_name}>"
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if role has specific permission."""
        resource_perms = self.permissions.get(resource, [])
        return action in resource_perms or "*" in resource_perms


# Default roles to seed
DEFAULT_ROLES = [
    {
        "role_name": "admin",
        "description": "System administrator with full access",
        "permissions": {
            "users": ["*"],
            "patients": ["*"],
            "samples": ["*"],
            "diagnoses": ["*"],
            "annotations": ["*"],
            "audit": ["*"],
            "settings": ["*"]
        }
    },
    {
        "role_name": "pathologist",
        "description": "Pathologist - can review and approve diagnoses",
        "permissions": {
            "patients": ["read"],
            "samples": ["read", "write"],
            "diagnoses": ["read", "write", "approve"],
            "annotations": ["read", "write", "sign_off"],
            "audit": ["read"]
        }
    },
    {
        "role_name": "cytotechnologist",
        "description": "Cytotechnologist - screens samples, flags abnormalities",
        "permissions": {
            "patients": ["read"],
            "samples": ["read", "write"],
            "diagnoses": ["read", "write"],
            "annotations": ["read", "write"],
            "audit": ["read"]
        }
    },
    {
        "role_name": "physician",
        "description": "Physician - manages patients and orders screenings",
        "permissions": {
            "patients": ["read", "write"],
            "samples": ["read", "write"],
            "diagnoses": ["read"],
            "annotations": ["read"],
            "audit": ["read"]
        }
    },
    {
        "role_name": "it_admin",
        "description": "IT Administrator - manages integrations and system health",
        "permissions": {
            "users": ["read"],
            "settings": ["read", "write"],
            "integrations": ["*"],
            "audit": ["read"]
        }
    }
]
