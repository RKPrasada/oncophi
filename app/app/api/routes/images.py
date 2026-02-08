"""
CervixAI Image Upload Routes
"""
import os
import shutil
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user, require_clinician
from app.models import User, Screening, ScreeningImage, ImageType, AuditLog
from app.schemas import ImageResponse, ImageListResponse

router = APIRouter(prefix="/images", tags=["Images"])

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif"}
MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes


@router.post("/upload/{screening_id}", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    screening_id: str,
    file: UploadFile = File(...),
    image_type: str = Query(ImageType.PAP_SMEAR.value),
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Upload a screening image (Pap smear, colposcopy, etc.)."""
    # Verify screening exists
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening not found"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file and check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create database record
    image = ScreeningImage(
        screening_id=screening_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(contents),
        mime_type=file.content_type,
        image_type=image_type
    )
    
    db.add(image)
    db.commit()
    db.refresh(image)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="image.upload",
        entity_type="image",
        entity_id=image.id
    )
    db.add(audit)
    db.commit()
    
    return image


@router.get("/{image_id}", response_model=ImageResponse)
def get_image_info(
    image_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Get image metadata."""
    image = db.query(ScreeningImage).filter(ScreeningImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    return image


@router.get("/{image_id}/file")
def download_image(
    image_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Download the actual image file."""
    image = db.query(ScreeningImage).filter(ScreeningImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    if not os.path.exists(image.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk"
        )
    
    return FileResponse(
        path=image.file_path,
        filename=image.original_filename,
        media_type=image.mime_type
    )


@router.get("/{image_id}/heatmap")
def get_heatmap(
    image_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Get AI-generated heatmap overlay for the image."""
    image = db.query(ScreeningImage).filter(ScreeningImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    if not image.heatmap_path or not os.path.exists(image.heatmap_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heatmap not yet generated. Run AI analysis first."
        )
    
    return FileResponse(
        path=image.heatmap_path,
        filename=f"heatmap_{image.original_filename}",
        media_type="image/png"
    )


@router.get("/screening/{screening_id}", response_model=ImageListResponse)
def list_screening_images(
    screening_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """List all images for a screening."""
    images = db.query(ScreeningImage).filter(
        ScreeningImage.screening_id == screening_id
    ).all()
    
    return ImageListResponse(total=len(images), items=images)
