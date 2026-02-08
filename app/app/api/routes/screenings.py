"""
CervixAI Screening Routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user, require_clinician
from app.models import User, Patient, Screening, ScreeningStatus, AuditLog
from app.schemas import (
    ScreeningCreate, ScreeningUpdate, ScreeningResponse, ScreeningListResponse
)

router = APIRouter(prefix="/screenings", tags=["Screenings"])


@router.get("", response_model=ScreeningListResponse)
def list_screenings(
    patient_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """List screening episodes with optional filters."""
    query = db.query(Screening)
    
    if patient_id:
        query = query.filter(Screening.patient_id == patient_id)
    
    if status:
        query = query.filter(Screening.status == status)
    
    query = query.order_by(Screening.created_at.desc())
    
    total = query.count()
    screenings = query.offset(offset).limit(limit).all()
    
    return ScreeningListResponse(total=total, items=screenings)


@router.post("", response_model=ScreeningResponse, status_code=status.HTTP_201_CREATED)
def create_screening(
    screening_data: ScreeningCreate,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Create a new screening episode for a patient."""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == screening_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check consent
    if not patient.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient consent is required before screening"
        )
    
    screening = Screening(
        patient_id=screening_data.patient_id,
        reason_for_screening=screening_data.reason_for_screening,
        clinical_notes=screening_data.clinical_notes,
        status=ScreeningStatus.PENDING.value
    )
    
    db.add(screening)
    db.commit()
    db.refresh(screening)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="screening.create",
        entity_type="screening",
        entity_id=screening.id
    )
    db.add(audit)
    db.commit()
    
    return screening


@router.get("/{screening_id}", response_model=ScreeningResponse)
def get_screening(
    screening_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Get screening episode by ID."""
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening not found"
        )
    
    return screening


@router.patch("/{screening_id}", response_model=ScreeningResponse)
def update_screening(
    screening_id: str,
    screening_update: ScreeningUpdate,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Update screening episode."""
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening not found"
        )
    
    update_data = screening_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(screening, field, value)
    
    db.commit()
    db.refresh(screening)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="screening.update",
        entity_type="screening",
        entity_id=screening.id
    )
    db.add(audit)
    db.commit()
    
    return screening
