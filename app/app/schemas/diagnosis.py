"""
CervixAI Diagnosis Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AIAnalysisRequest(BaseModel):
    """Schema for requesting AI analysis."""
    screening_id: str


class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis result."""
    diagnosis_id: str
    screening_id: str
    ai_prediction: str
    ai_confidence: float
    ai_notes: Optional[str] = None
    ai_analysis_date: datetime


class ClinicianReviewRequest(BaseModel):
    """Schema for clinician review submission."""
    diagnosis_id: str
    agrees_with_ai: bool
    clinician_diagnosis: str
    clinician_notes: Optional[str] = None
    follow_up_recommended: bool = False
    follow_up_notes: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """Full diagnosis response."""
    id: str
    screening_id: str
    
    # AI Results
    ai_prediction: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_analysis_date: Optional[datetime] = None
    ai_notes: Optional[str] = None
    
    # Clinician Review
    reviewer_id: Optional[str] = None
    clinician_agrees_with_ai: Optional[bool] = None
    clinician_diagnosis: Optional[str] = None
    clinician_notes: Optional[str] = None
    review_date: Optional[datetime] = None
    
    # Final
    final_diagnosis: Optional[str] = None
    final_notes: Optional[str] = None
    finalized_at: Optional[datetime] = None
    
    # Follow-up
    follow_up_recommended: bool = False
    follow_up_notes: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
