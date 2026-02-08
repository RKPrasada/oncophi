"""
CervixAI Patient Model
Enhanced with JSONB contact_info and longitudinal tracking support.
"""
from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Boolean, Text, JSON, Index
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Patient(Base):
    """Patient model for tracking individuals undergoing screening."""
    __tablename__ = "patients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=True)
    
    # Contact as JSONB for flexibility
    # Structure: {"email": "...", "phone": "...", "address": {...}}
    contact_info = Column(JSON, nullable=True, default=dict)
    
    # Legacy contact fields for compatibility
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Medical identifiers
    medical_record_number = Column(String(50), unique=True, index=True)
    
    # Consent tracking
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime, nullable=True)
    consent_document_path = Column(String(500), nullable=True)
    
    # Clinical notes
    notes = Column(Text, nullable=True)
    
    # Risk factors and history as JSON
    # Structure: {"hpv_positive": true, "previous_abnormal": false, "smoking": false, ...}
    risk_factors = Column(JSON, nullable=True, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    screenings = relationship("Screening", back_populates="patient", cascade="all, delete-orphan")
    samples = relationship("Sample", back_populates="patient", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_patients_name", "last_name", "first_name"),
        Index("idx_patients_dob", "date_of_birth"),
    )
    
    @property
    def full_name(self) -> str:
        """Get patient's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self) -> int:
        """Calculate patient's current age."""
        today = date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    def get_contact_email(self) -> str:
        """Get email from contact_info or legacy field."""
        if self.contact_info and self.contact_info.get("email"):
            return self.contact_info["email"]
        return self.email or ""
    
    def __repr__(self):
        return f"<Patient {self.full_name}>"
