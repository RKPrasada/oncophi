"""
CervixAI Sample Model - Cervical sample metadata and batch info
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Sample(Base):
    """Sample model for cervical samples collected for analysis."""
    __tablename__ = "samples"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Patient reference
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    
    # Sample details
    collection_date = Column(DateTime, nullable=False)
    batch_id = Column(String(36), nullable=True, index=True)  # For batch processing
    sample_type = Column(String(50), nullable=True)  # e.g., "pap_smear", "colposcopy"
    
    # Flexible metadata as JSON
    # Can store: collection_site, preparation_method, quality_indicators, etc.
    metadata = Column(JSON, nullable=True, default=dict)
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, analyzed, reviewed
    
    # File reference
    image_path = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="samples")
    ai_results = relationship("AIResult", back_populates="sample", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_samples_collection_date", "collection_date"),
        Index("idx_samples_status", "status"),
    )
    
    def __repr__(self):
        return f"<Sample {self.id[:8]} for Patient {self.patient_id[:8]}>"
