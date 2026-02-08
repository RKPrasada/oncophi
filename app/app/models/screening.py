"""
CervixAI Screening Model - Episodes linking patients, images, and diagnoses
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class ScreeningStatus(str, enum.Enum):
    """Status of a screening episode."""
    PENDING = "pending"           # Images uploaded, awaiting AI analysis
    AI_ANALYZED = "ai_analyzed"   # AI has provided initial triage
    UNDER_REVIEW = "under_review" # Clinician is reviewing
    COMPLETED = "completed"       # Final diagnosis made
    CANCELLED = "cancelled"       # Screening cancelled


class Screening(Base):
    """Screening episode - a single screening session for a patient."""
    __tablename__ = "screenings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    
    # Status tracking
    status = Column(String(50), default=ScreeningStatus.PENDING.value)
    
    # Clinical context
    clinical_notes = Column(Text, nullable=True)
    reason_for_screening = Column(String(255), nullable=True)
    
    # Timestamps
    screening_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="screenings")
    images = relationship("ScreeningImage", back_populates="screening")
    diagnosis = relationship("Diagnosis", back_populates="screening", uselist=False)
    
    def __repr__(self):
        return f"<Screening {self.id} for Patient {self.patient_id}>"
