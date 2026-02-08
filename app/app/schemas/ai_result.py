"""
CervixAI AI Result Schemas
Pydantic models for AIResult API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from uuid import UUID


class AIResultBase(BaseModel):
    """Base AI result schema."""
    sample_id: UUID
    diagnosis: Dict[str, float] = Field(
        ..., 
        example={"primary": "lsil", "raw_predictions": {"nilm": 0.1, "lsil": 0.8}}
    )
    confidence_scores: Dict[str, float] = Field(
        ...,
        example={"nilm": 0.05, "asc_us": 0.1, "lsil": 0.75, "hsil": 0.1}
    )
    heatmap_path: Optional[str] = None


class AIResultCreate(AIResultBase):
    """Schema for creating an AI result."""
    primary_prediction: Optional[str] = None
    primary_confidence: Optional[float] = None
    model_version: Optional[str] = None
    model_name: Optional[str] = None
    ai_notes: Optional[str] = None


class AIResultRead(AIResultBase):
    """Schema for reading an AI result."""
    id: UUID
    primary_prediction: Optional[str] = None
    primary_confidence: Optional[float] = None
    model_version: Optional[str] = None
    model_name: Optional[str] = None
    ai_notes: Optional[str] = None
    processed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AIResultWithAnnotations(AIResultRead):
    """AI result with clinician annotations."""
    annotations: list = Field(default_factory=list)


class AIAnalysisRequest(BaseModel):
    """Request to run AI analysis on a sample/screening."""
    screening_id: Optional[UUID] = None
    sample_id: Optional[UUID] = None


class AIAnalysisResponse(BaseModel):
    """Response from AI analysis."""
    result_id: UUID
    sample_id: UUID
    ai_prediction: str
    ai_confidence: float
    top_predictions: List[Tuple[str, float]] = Field(default_factory=list)
    heatmap_url: Optional[str] = None
    ai_notes: Optional[str] = None
