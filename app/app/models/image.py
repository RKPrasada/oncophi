"""
CervixAI Image Model - Screening images (Pap smears, colposcopy)
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class ImageType(str, enum.Enum):
    """Type of cervical screening image."""
    PAP_SMEAR = "pap_smear"
    COLPOSCOPY = "colposcopy"
    OTHER = "other"


class ScreeningImage(Base):
    """Uploaded screening image."""
    __tablename__ = "screening_images"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screening_id = Column(String(36), ForeignKey("screenings.id"), nullable=False)
    
    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    mime_type = Column(String(50), nullable=True)
    
    # Image metadata
    image_type = Column(String(50), default=ImageType.PAP_SMEAR.value)
    
    # AI Analysis results (stored path to heatmap overlay)
    heatmap_path = Column(String(500), nullable=True)
    
    # Timestamps  
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    screening = relationship("Screening", back_populates="images")
    
    def __repr__(self):
        return f"<ScreeningImage {self.filename}>"
