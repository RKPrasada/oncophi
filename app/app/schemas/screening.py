"""
CervixAI Screening Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ScreeningCreate(BaseModel):
    """Schema for creating a screening episode."""
    patient_id: str
    reason_for_screening: Optional[str] = None
    clinical_notes: Optional[str] = None


class ScreeningUpdate(BaseModel):
    """Schema for updating a screening."""
    status: Optional[str] = None
    clinical_notes: Optional[str] = None


class ScreeningResponse(BaseModel):
    """Schema for screening response."""
    id: str
    patient_id: str
    status: str
    reason_for_screening: Optional[str] = None
    clinical_notes: Optional[str] = None
    screening_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ScreeningListResponse(BaseModel):
    """Schema for paginated screening list."""
    total: int
    items: List[ScreeningResponse]
