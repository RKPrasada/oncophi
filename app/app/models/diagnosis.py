"""
CervixAI Diagnosis Model - AI predictions and clinician reviews
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class DiagnosisCategory(str, enum.Enum):
    """Bethesda System cervical cytology categories."""
    NILM = "nilm"                    # Negative for Intraepithelial Lesion or Malignancy
    ASC_US = "asc_us"                # Atypical Squamous Cells of Undetermined Significance
    ASC_H = "asc_h"                  # Atypical Squamous Cells, cannot exclude HSIL
    LSIL = "lsil"                    # Low-grade Squamous Intraepithelial Lesion
    HSIL = "hsil"                    # High-grade Squamous Intraepithelial Lesion
    SCC = "scc"                      # Squamous Cell Carcinoma
    AGC = "agc"                      # Atypical Glandular Cells
    ADENOCARCINOMA = "adenocarcinoma"
    UNSATISFACTORY = "unsatisfactory"


class Diagnosis(Base):
    """
    Diagnosis record containing:
    - AI prediction (initial triage)
    - Clinician review (human oversight)
    - Final diagnosis
    """
    __tablename__ = "diagnoses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screening_id = Column(String(36), ForeignKey("screenings.id"), unique=True, nullable=False)
    
    # AI Prediction
    ai_prediction = Column(String(50), nullable=True)
    ai_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    ai_analysis_date = Column(DateTime, nullable=True)
    ai_notes = Column(Text, nullable=True)  # AI explanation
    
    # Clinician Review
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    clinician_agrees_with_ai = Column(Boolean, nullable=True)
    clinician_diagnosis = Column(String(50), nullable=True)
    clinician_notes = Column(Text, nullable=True)
    review_date = Column(DateTime, nullable=True)
    
    # Final Diagnosis
    final_diagnosis = Column(String(50), nullable=True)
    final_notes = Column(Text, nullable=True)
    finalized_at = Column(DateTime, nullable=True)
    
    # Recommendations
    follow_up_recommended = Column(Boolean, default=False)
    follow_up_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    screening = relationship("Screening", back_populates="diagnosis")
    reviewer = relationship("User", back_populates="diagnoses")
    
    def __repr__(self):
        return f"<Diagnosis {self.id} - {self.final_diagnosis or 'Pending'}>"
