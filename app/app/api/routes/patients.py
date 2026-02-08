"""
CervixAI Patient Routes
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user, require_clinician
from app.models import User, Patient, AuditLog
from app.schemas import (
    PatientCreate, PatientUpdate, PatientResponse, PatientListResponse
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=PatientListResponse)
def list_patients(
    search: Optional[str] = Query(None, description="Search by name or MRN"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """List patients with optional search."""
    query = db.query(Patient)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(search_term)) |
            (Patient.last_name.ilike(search_term)) |
            (Patient.medical_record_number.ilike(search_term))
        )
    
    total = query.count()
    patients = query.offset(offset).limit(limit).all()
    
    return PatientListResponse(total=total, items=patients)


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Create a new patient record."""
    # Check for duplicate MRN
    if patient_data.medical_record_number:
        existing = db.query(Patient).filter(
            Patient.medical_record_number == patient_data.medical_record_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medical record number already exists"
            )
    
    patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        date_of_birth=patient_data.date_of_birth,
        email=patient_data.email,
        phone=patient_data.phone,
        medical_record_number=patient_data.medical_record_number,
        notes=patient_data.notes,
        consent_given=patient_data.consent_given,
        consent_date=datetime.utcnow() if patient_data.consent_given else None
    )
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="patient.create",
        entity_type="patient",
        entity_id=patient.id
    )
    db.add(audit)
    db.commit()
    
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Get patient by ID."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="patient.view",
        entity_type="patient",
        entity_id=patient.id
    )
    db.add(audit)
    db.commit()
    
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Update patient record."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "consent_given" and value and not patient.consent_given:
            patient.consent_date = datetime.utcnow()
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="patient.update",
        entity_type="patient",
        entity_id=patient.id
    )
    db.add(audit)
    db.commit()
    
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Delete patient record (soft delete in production)."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Audit log before deletion
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="patient.delete",
        entity_type="patient",
        entity_id=patient.id
    )
    db.add(audit)
    
    db.delete(patient)
    db.commit()
    
    return None
