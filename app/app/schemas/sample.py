"""
CervixAI Sample Schemas
Pydantic models for Sample API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class SampleBase(BaseModel):
    """Base sample schema with common fields."""
    patient_id: UUID
    collection_date: datetime
    sample_type: Optional[str] = Field(None, example="pap_smear")
    batch_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SampleCreate(SampleBase):
    """Schema for creating a new sample."""
    pass


class SampleUpdate(BaseModel):
    """Schema for updating a sample."""
    sample_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    image_path: Optional[str] = None


class SampleRead(SampleBase):
    """Schema for reading a sample."""
    id: UUID
    status: str = "pending"
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SampleWithResults(SampleRead):
    """Sample with AI results included."""
    ai_results: list = Field(default_factory=list)
