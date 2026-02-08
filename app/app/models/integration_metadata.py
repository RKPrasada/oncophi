"""
CervixAI Integration Metadata Model - External system connector configurations
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Text
import uuid

from app.db.database import Base


class IntegrationMetadata(Base):
    """Integration metadata for managing external system connectors."""
    __tablename__ = "integration_metadata"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # System identification
    system_name = Column(String(255), unique=True, nullable=False, index=True)
    system_type = Column(String(100), nullable=False)  # hl7, fhir, dicom, lis, ehr
    
    # Description
    description = Column(Text, nullable=True)
    
    # Connection configuration as JSON (encrypted at rest)
    # Structure depends on type: endpoints, auth tokens, mappings, etc.
    connector_config = Column(JSON, nullable=False, default=dict)
    
    # Data mapping configuration
    # Maps CervixAI fields to external system fields
    field_mappings = Column(JSON, nullable=True, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(50), nullable=True)  # success, failed, pending
    
    # Rate limiting
    rate_limit_requests = Column(String(50), default="100/minute")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"<Integration {self.system_name} ({self.system_type}) - {status}>"
