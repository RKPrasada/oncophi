"""
CervixAI Annotation Schemas
Pydantic models for Annotation API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class AnnotationBase(BaseModel):
    """Base annotation schema."""
    result_id: UUID
    agrees_with_ai: Optional[bool] = None
    clinician_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    override_flags: Optional[Dict[str, Any]] = Field(default_factory=dict)
    follow_up_recommended: bool = False
    follow_up_notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class AnnotationCreate(AnnotationBase):
    """Schema for creating an annotation."""
    pass


class AnnotationUpdate(BaseModel):
    """Schema for updating an annotation."""
    agrees_with_ai: Optional[bool] = None
    clinician_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    override_flags: Optional[Dict[str, Any]] = None
    follow_up_recommended: Optional[bool] = None
    follow_up_notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class AnnotationRead(AnnotationBase):
    """Schema for reading an annotation."""
    id: UUID
    clinician_id: UUID
    signed_off: bool = False
    signed_off_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnotationSignOff(BaseModel):
    """Schema for signing off an annotation."""
    annotation_id: UUID
    confirm_sign_off: bool = True


class ClinicianReviewRequest(BaseModel):
    """Request from clinician to review and annotate a diagnosis."""
    diagnosis_id: UUID
    agrees_with_ai: bool
    clinician_diagnosis: str
    clinician_notes: Optional[str] = None
    follow_up_recommended: bool = False
    follow_up_notes: Optional[str] = None
