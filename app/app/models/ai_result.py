"""
CervixAI AI Result Model - AI inference outcomes with explainability
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Float, Index
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class AIResult(Base):
    """AI Result model storing inference outcomes, confidence, and explainability data."""
    __tablename__ = "ai_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Sample reference
    sample_id = Column(String(36), ForeignKey("samples.id"), nullable=False, index=True)
    
    # Diagnosis results as JSON
    # Structure: {"primary": "lsil", "secondary": null, "raw_predictions": {...}}
    diagnosis = Column(JSON, nullable=False)
    
    # Confidence scores as JSON
    # Structure: {"nilm": 0.05, "asc_us": 0.1, "lsil": 0.75, "hsil": 0.1, ...}
    confidence_scores = Column(JSON, nullable=False)
    
    # Primary prediction for quick access
    primary_prediction = Column(String(50), nullable=True)
    primary_confidence = Column(Float, nullable=True)
    
    # Explainability - heatmap image path
    heatmap_path = Column(String(500), nullable=True)
    
    # AI model information for audit trail
    model_version = Column(String(100), nullable=True)
    model_name = Column(String(100), nullable=True)
    
    # Processing notes from AI
    ai_notes = Column(Text, nullable=True)
    
    # Timestamps
    processed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sample = relationship("Sample", back_populates="ai_results")
    annotations = relationship("Annotation", back_populates="ai_result", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_ai_results_processed_at", "processed_at"),
        Index("idx_ai_results_primary_prediction", "primary_prediction"),
    )
    
    def __repr__(self):
        return f"<AIResult {self.id[:8]} - {self.primary_prediction} ({self.primary_confidence:.1%})>"
    
    def get_top_predictions(self, n: int = 3) -> list:
        """Get top N predictions by confidence."""
        if not self.confidence_scores:
            return []
        sorted_scores = sorted(
            self.confidence_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_scores[:n]
