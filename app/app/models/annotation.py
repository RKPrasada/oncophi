"""
CervixAI Annotation Model - Clinician overrides and sign-offs
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Boolean, Index
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Annotation(Base):
    """Annotation model for clinician review, overrides, and mandatory sign-offs."""
    __tablename__ = "annotations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # AI Result reference
    result_id = Column(String(36), ForeignKey("ai_results.id"), nullable=False, index=True)
    
    # Clinician reference
    clinician_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Clinical assessment
    agrees_with_ai = Column(Boolean, nullable=True)
    clinician_diagnosis = Column(String(50), nullable=True)
    
    # Notes and observations
    notes = Column(Text, nullable=True)
    
    # Override flags as JSON for flexibility
    # Structure: {"diagnosis_override": true, "urgency_elevated": true, "reason": "..."}
    override_flags = Column(JSON, nullable=True, default=dict)
    
    # Follow-up recommendations
    follow_up_recommended = Column(Boolean, default=False)
    follow_up_notes = Column(Text, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    
    # Mandatory sign-off (for compliance)
    signed_off = Column(Boolean, default=False)
    signed_off_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ai_result = relationship("AIResult", back_populates="annotations")
    clinician = relationship("User", back_populates="annotations")
    
    # Indexes
    __table_args__ = (
        Index("idx_annotations_signed_off", "signed_off"),
        Index("idx_annotations_created_at", "created_at"),
    )
    
    def __repr__(self):
        status = "Signed" if self.signed_off else "Pending"
        return f"<Annotation {self.id[:8]} by {self.clinician_id[:8]} - {status}>"
    
    def sign_off(self):
        """Mark annotation as signed off."""
        self.signed_off = True
        self.signed_off_at = datetime.utcnow()
