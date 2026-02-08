"""
CervixAI Patient Service
Business logic for patient management.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Patient, AuditLog
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:
    """Service for patient-related operations."""
    
    def __init__(self, db: Session, current_user=None):
        self.db = db
        self.user = current_user
    
    def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient."""
        patient = Patient(
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            date_of_birth=patient_data.date_of_birth,
            email=patient_data.email,
            phone=patient_data.phone,
            medical_record_number=patient_data.medical_record_number,
            consent_given=patient_data.consent_given,
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        
        # Audit log
        self._log_action("patient.create", patient.id)
        
        return patient
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get a patient by ID."""
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if patient:
            self._log_action("patient.view", patient.id)
        return patient
    
    def get_patients(
        self, 
        search: Optional[str] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> tuple[List[Patient], int]:
        """Get paginated list of patients."""
        query = self.db.query(Patient).filter(Patient.is_active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.medical_record_number.ilike(search_term)
                )
            )
        
        total = query.count()
        patients = query.offset(skip).limit(limit).all()
        
        return patients, total
    
    def update_patient(self, patient_id: str, patient_data: PatientUpdate) -> Optional[Patient]:
        """Update a patient."""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return None
        
        update_data = patient_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        self.db.commit()
        self.db.refresh(patient)
        
        self._log_action("patient.update", patient.id, {"updated_fields": list(update_data.keys())})
        
        return patient
    
    def delete_patient(self, patient_id: str) -> bool:
        """Soft delete a patient."""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return False
        
        patient.is_active = False
        self.db.commit()
        
        self._log_action("patient.delete", patient.id)
        
        return True
    
    def get_patient_history(self, patient_id: str) -> dict:
        """Get patient's longitudinal history."""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return {}
        
        return {
            "patient": patient,
            "screenings": patient.screenings,
            "samples": patient.samples if hasattr(patient, 'samples') else [],
            "age": patient.get_age(),
        }
    
    def _log_action(self, action: str, resource_id: str, details: dict = None):
        """Log action to audit trail."""
        if self.user:
            AuditLog.log_action(
                self.db,
                action=action,
                user=self.user,
                resource_type="patient",
                resource_id=resource_id,
                details=details
            )
            self.db.commit()
