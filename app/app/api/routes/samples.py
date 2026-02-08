"""
CervixAI Samples API Routes
Endpoints for sample management and batch upload.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, Sample, Patient, AuditLog
from app.schemas.sample import SampleCreate, SampleRead, SampleUpdate
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/samples", tags=["samples"])


@router.post("/", response_model=SampleRead, status_code=status.HTTP_201_CREATED)
async def create_sample(
    sample_in: SampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sample for a patient."""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == str(sample_in.patient_id)).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    sample = Sample(
        patient_id=str(sample_in.patient_id),
        collection_date=sample_in.collection_date,
        sample_type=sample_in.sample_type,
        batch_id=str(sample_in.batch_id) if sample_in.batch_id else None,
        metadata=sample_in.metadata or {}
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    
    # Audit log
    AuditLog.log_action(db, "sample.create", current_user, "sample", sample.id)
    db.commit()
    
    return sample


@router.get("/", response_model=list[SampleRead])
async def list_samples(
    patient_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List samples with optional filters."""
    query = db.query(Sample)
    
    if patient_id:
        query = query.filter(Sample.patient_id == patient_id)
    if batch_id:
        query = query.filter(Sample.batch_id == batch_id)
    if status:
        query = query.filter(Sample.status == status)
    
    samples = query.offset(skip).limit(limit).all()
    return samples


@router.get("/{sample_id}", response_model=SampleRead)
async def get_sample(
    sample_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific sample by ID."""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.patch("/{sample_id}", response_model=SampleRead)
async def update_sample(
    sample_id: str,
    sample_update: SampleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sample."""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    update_data = sample_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sample, field, value)
    
    db.commit()
    db.refresh(sample)
    
    AuditLog.log_action(db, "sample.update", current_user, "sample", sample.id)
    db.commit()
    
    return sample


@router.post("/{sample_id}/upload", response_model=SampleRead)
async def upload_sample_image(
    sample_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload an image for a sample."""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    # Save file
    import os
    from app.core.config import settings
    
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"{sample_id}_{file.filename}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    sample.image_path = file_path
    sample.status = "uploaded"
    db.commit()
    db.refresh(sample)
    
    AuditLog.log_action(db, "sample.upload_image", current_user, "sample", sample.id)
    db.commit()
    
    return sample


@router.delete("/{sample_id}", response_model=MessageResponse)
async def delete_sample(
    sample_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a sample."""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    db.delete(sample)
    db.commit()
    
    AuditLog.log_action(db, "sample.delete", current_user, "sample", sample_id)
    db.commit()
    
    return {"message": "Sample deleted successfully"}
