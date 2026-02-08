"""
CervixAI Annotation Service
Business logic for clinician annotations and sign-offs.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Annotation, AIResult, Diagnosis, Screening, AuditLog
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate


class AnnotationService:
    """Service for clinician annotation and review operations."""
    
    def __init__(self, db: Session, current_user=None):
        self.db = db
        self.user = current_user
    
    def create_annotation(self, annotation_data: AnnotationCreate) -> Annotation:
        """Create a new annotation."""
        annotation = Annotation(
            result_id=str(annotation_data.result_id),
            clinician_id=self.user.id if self.user else None,
            agrees_with_ai=annotation_data.agrees_with_ai,
            clinician_diagnosis=annotation_data.clinician_diagnosis,
            notes=annotation_data.notes,
            override_flags=annotation_data.override_flags or {},
            follow_up_recommended=annotation_data.follow_up_recommended,
            follow_up_notes=annotation_data.follow_up_notes,
            follow_up_date=annotation_data.follow_up_date,
        )
        self.db.add(annotation)
        self.db.commit()
        self.db.refresh(annotation)
        
        self._log_action("annotation.create", annotation.id, {
            "agrees_with_ai": annotation.agrees_with_ai,
            "clinician_diagnosis": annotation.clinician_diagnosis
        })
        
        return annotation
    
    def review_diagnosis(
        self,
        diagnosis_id: str,
        agrees_with_ai: bool,
        clinician_diagnosis: str,
        clinician_notes: Optional[str] = None,
        follow_up_recommended: bool = False,
        follow_up_notes: Optional[str] = None
    ) -> Optional[Diagnosis]:
        """Submit clinician review for a diagnosis (legacy flow)."""
        diagnosis = self.db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not diagnosis:
            return None
        
        # Update diagnosis with clinician review
        diagnosis.clinician_diagnosis = clinician_diagnosis
        diagnosis.clinician_notes = clinician_notes
        diagnosis.agrees_with_ai = agrees_with_ai
        diagnosis.reviewed_by_id = self.user.id if self.user else None
        diagnosis.reviewed_at = datetime.utcnow()
        diagnosis.follow_up_recommended = follow_up_recommended
        diagnosis.follow_up_notes = follow_up_notes
        diagnosis.status = "completed"
        
        # Update screening status
        if diagnosis.screening:
            diagnosis.screening.status = "completed"
        
        self.db.commit()
        self.db.refresh(diagnosis)
        
        self._log_action("diagnosis.review", diagnosis.id, {
            "agrees_with_ai": agrees_with_ai,
            "clinician_diagnosis": clinician_diagnosis,
            "follow_up": follow_up_recommended
        }, severity="critical")  # Sign-off is a critical action
        
        return diagnosis
    
    def sign_off_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """Sign off an annotation (mandatory clinical oversight)."""
        annotation = self.db.query(Annotation).filter(Annotation.id == annotation_id).first()
        if not annotation:
            return None
        
        if annotation.signed_off:
            return annotation  # Already signed off
        
        annotation.sign_off()
        self.db.commit()
        self.db.refresh(annotation)
        
        self._log_action("annotation.sign_off", annotation.id, severity="critical")
        
        return annotation
    
    def get_annotation_by_id(self, annotation_id: str) -> Optional[Annotation]:
        """Get annotation by ID."""
        return self.db.query(Annotation).filter(Annotation.id == annotation_id).first()
    
    def get_annotations_by_result(self, result_id: str) -> List[Annotation]:
        """Get all annotations for an AI result."""
        return self.db.query(Annotation).filter(Annotation.result_id == result_id).all()
    
    def get_pending_annotations(self, clinician_id: str = None) -> List[Annotation]:
        """Get annotations pending sign-off."""
        query = self.db.query(Annotation).filter(Annotation.signed_off == False)
        if clinician_id:
            query = query.filter(Annotation.clinician_id == clinician_id)
        return query.all()
    
    def _log_action(self, action: str, resource_id: str, details: dict = None, severity: str = "info"):
        """Log action to audit trail."""
        if self.user:
            AuditLog.log_action(
                self.db,
                action=action,
                user=self.user,
                resource_type="annotation",
                resource_id=resource_id,
                details=details,
                severity=severity
            )
            self.db.commit()
