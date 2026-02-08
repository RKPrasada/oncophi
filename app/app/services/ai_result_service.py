"""
CervixAI AI Result Service
Business logic for AI inference and results.
"""
import random
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import AIResult, Sample, Screening, AuditLog
from app.schemas.ai_result import AIResultCreate


# Diagnosis categories for cervical screening
DIAGNOSIS_CATEGORIES = [
    "nilm",        # Negative for intraepithelial lesion or malignancy
    "asc_us",      # Atypical squamous cells of undetermined significance
    "asc_h",       # Atypical squamous cells, cannot exclude HSIL
    "lsil",        # Low-grade squamous intraepithelial lesion
    "hsil",        # High-grade squamous intraepithelial lesion
    "scc",         # Squamous cell carcinoma
    "agc",         # Atypical glandular cells
    "adenocarcinoma",
    "unsatisfactory"
]


class AIResultService:
    """Service for AI inference and result management."""
    
    def __init__(self, db: Session, current_user=None):
        self.db = db
        self.user = current_user
    
    def run_analysis(self, screening_id: str = None, sample_id: str = None) -> Optional[AIResult]:
        """Run AI analysis on a screening or sample."""
        # Get the sample/screening
        if screening_id:
            screening = self.db.query(Screening).filter(Screening.id == screening_id).first()
            if not screening:
                return None
            
            # Simulate AI inference
            result = self._simulate_ai_inference()
            
            # Create result (store in existing Diagnosis model or new AIResult)
            from app.models import Diagnosis, DiagnosisCategory
            
            diagnosis = Diagnosis(
                screening_id=screening_id,
                ai_prediction=result["primary_prediction"],
                ai_confidence=result["primary_confidence"],
                ai_notes=result["ai_notes"],
                status="pending_review"
            )
            self.db.add(diagnosis)
            
            # Update screening status
            screening.status = "ai_analyzed"
            
            self.db.commit()
            self.db.refresh(diagnosis)
            
            self._log_action("diagnosis.ai_analyze", diagnosis.id, {
                "prediction": result["primary_prediction"],
                "confidence": result["primary_confidence"]
            })
            
            return diagnosis
            
        elif sample_id:
            sample = self.db.query(Sample).filter(Sample.id == sample_id).first()
            if not sample:
                return None
            
            # Simulate AI inference
            result = self._simulate_ai_inference()
            
            # Create AIResult
            ai_result = AIResult(
                sample_id=sample_id,
                diagnosis=result["diagnosis"],
                confidence_scores=result["confidence_scores"],
                primary_prediction=result["primary_prediction"],
                primary_confidence=result["primary_confidence"],
                model_version="1.0.0",
                model_name="CervixAI-ResNet50",
                ai_notes=result["ai_notes"]
            )
            self.db.add(ai_result)
            
            # Update sample status
            sample.status = "analyzed"
            
            self.db.commit()
            self.db.refresh(ai_result)
            
            self._log_action("ai_result.create", ai_result.id, {
                "prediction": result["primary_prediction"],
                "confidence": result["primary_confidence"]
            })
            
            return ai_result
        
        return None
    
    def get_result_by_id(self, result_id: str) -> Optional[AIResult]:
        """Get AI result by ID."""
        return self.db.query(AIResult).filter(AIResult.id == result_id).first()
    
    def get_results_by_sample(self, sample_id: str) -> List[AIResult]:
        """Get all AI results for a sample."""
        return self.db.query(AIResult).filter(AIResult.sample_id == sample_id).all()
    
    def _simulate_ai_inference(self) -> dict:
        """Simulate AI inference for demo purposes."""
        # Generate random confidence scores
        scores = {}
        remaining = 1.0
        
        for i, category in enumerate(DIAGNOSIS_CATEGORIES[:-1]):
            if i == len(DIAGNOSIS_CATEGORIES) - 2:
                scores[category] = remaining
            else:
                score = random.uniform(0, remaining * 0.8)
                scores[category] = round(score, 4)
                remaining -= score
        
        scores[DIAGNOSIS_CATEGORIES[-1]] = 0.0  # Unsatisfactory usually 0
        
        # Find primary prediction
        primary = max(scores, key=scores.get)
        primary_confidence = scores[primary]
        
        # Generate notes
        notes = f"AI analysis complete. Primary finding: {primary.upper()} with {primary_confidence:.1%} confidence."
        if primary_confidence < 0.7:
            notes += " Low confidence - recommend manual review."
        
        return {
            "diagnosis": {"primary": primary, "raw_predictions": scores},
            "confidence_scores": scores,
            "primary_prediction": primary,
            "primary_confidence": primary_confidence,
            "ai_notes": notes
        }
    
    def _log_action(self, action: str, resource_id: str, details: dict = None):
        """Log action to audit trail."""
        if self.user:
            AuditLog.log_action(
                self.db,
                action=action,
                user=self.user,
                resource_type="ai_result",
                resource_id=resource_id,
                details=details
            )
            self.db.commit()
