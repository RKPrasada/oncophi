"""
CervixAI Role Schemas
Pydantic models for Role API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from uuid import UUID


class RoleBase(BaseModel):
    """Base role schema."""
    role_name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    permissions: Dict[str, List[str]] = Field(
        default_factory=dict,
        example={"patients": ["read", "write"], "diagnoses": ["read"]}
    )


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    description: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None


class RoleRead(RoleBase):
    """Schema for reading a role."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
