"""
CervixAI Patient Schemas
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class PatientBase(BaseModel):
    """Base patient schema."""
    first_name: str
    last_name: str
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    medical_record_number: Optional[str] = None
    notes: Optional[str] = None


class PatientCreate(PatientBase):
    """Schema for creating a patient."""
    consent_given: bool = False


class PatientUpdate(BaseModel):
    """Schema for updating a patient."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    consent_given: Optional[bool] = None


class PatientResponse(PatientBase):
    """Schema for patient response."""
    id: str
    consent_given: bool
    consent_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schema for paginated patient list."""
    total: int
    items: List[PatientResponse]
