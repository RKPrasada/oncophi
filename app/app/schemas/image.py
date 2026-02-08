"""
CervixAI Image Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ImageResponse(BaseModel):
    """Schema for image response."""
    id: str
    screening_id: str
    filename: str
    original_filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    image_type: str
    heatmap_path: Optional[str] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    """Schema for image list."""
    total: int
    items: List[ImageResponse]
