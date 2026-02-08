"""
CervixAI Diagnosis Routes - AI Analysis and Clinician Review
"""
import os
import random
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from PIL import Image
import numpy as np

from app.db.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user, require_clinician, require_pathologist
from app.models import (
    User, Screening, ScreeningImage, Diagnosis, 
    DiagnosisCategory, ScreeningStatus, AuditLog
)
from app.schemas import (
    AIAnalysisRequest, AIAnalysisResponse, 
    ClinicianReviewRequest, DiagnosisResponse
)

router = APIRouter(prefix="/diagnoses", tags=["Diagnoses"])


def mock_ai_analysis(image_path: str) -> tuple[str, float, str]:
    """
    Mock AI analysis for demo purposes.
    In production, this would call a real ML model.
    Returns: (prediction, confidence, notes)
    """
    categories = list(DiagnosisCategory)
    weights = [0.4, 0.2, 0.1, 0.15, 0.08, 0.02, 0.03, 0.01, 0.01]  # Weighted towards benign
    prediction = random.choices(categories, weights=weights)[0]
    confidence = random.uniform(0.7, 0.98)
    
    notes = f"AI analysis completed. "
    if prediction == DiagnosisCategory.NILM:
        notes += "No significant abnormalities detected."
    elif prediction in [DiagnosisCategory.HSIL, DiagnosisCategory.SCC]:
        notes += "High-grade abnormality detected. Urgent review recommended."
    else:
        notes += "Abnormality detected. Clinical review required."
    
    return prediction.value, confidence, notes


def generate_mock_heatmap(image_path: str, output_path: str):
    """Generate a simple mock heatmap overlay for demo purposes."""
    try:
        # Open original image
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # Create a red overlay with random intensity
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Add some random "hot spots"
        from PIL import ImageDraw
        draw = ImageDraw.Draw(overlay)
        
        for _ in range(random.randint(2, 5)):
            x = random.randint(width // 4, 3 * width // 4)
            y = random.randint(height // 4, 3 * height // 4)
            r = random.randint(30, 80)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 0, 0, 100))
        
        # Composite
        result = Image.alpha_composite(img, overlay)
        result.save(output_path, "PNG")
        return True
    except Exception:
        return False


@router.post("/analyze", response_model=AIAnalysisResponse)
def run_ai_analysis(
    request: AIAnalysisRequest,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Run AI analysis on a screening's images."""
    screening = db.query(Screening).filter(Screening.id == request.screening_id).first()
    if not screening:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screening not found"
        )
    
    # Get images for this screening
    images = db.query(ScreeningImage).filter(
        ScreeningImage.screening_id == request.screening_id
    ).all()
    
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images uploaded for this screening"
        )
    
    # Check if diagnosis already exists
    existing = db.query(Diagnosis).filter(Diagnosis.screening_id == request.screening_id).first()
    if existing and existing.ai_prediction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI analysis already completed for this screening"
        )
    
    # Run mock AI analysis on first image
    primary_image = images[0]
    prediction, confidence, notes = mock_ai_analysis(primary_image.file_path)
    
    # Generate heatmap
    heatmap_filename = f"heatmap_{primary_image.filename}"
    heatmap_path = os.path.join(settings.upload_dir, heatmap_filename)
    if os.path.exists(primary_image.file_path):
        generate_mock_heatmap(primary_image.file_path, heatmap_path)
        primary_image.heatmap_path = heatmap_path
    
    # Create or update diagnosis record
    if existing:
        diagnosis = existing
    else:
        diagnosis = Diagnosis(screening_id=request.screening_id)
        db.add(diagnosis)
    
    diagnosis.ai_prediction = prediction
    diagnosis.ai_confidence = confidence
    diagnosis.ai_notes = notes
    diagnosis.ai_analysis_date = datetime.utcnow()
    
    # Update screening status
    screening.status = ScreeningStatus.AI_ANALYZED.value
    
    db.commit()
    db.refresh(diagnosis)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="diagnosis.ai_analysis",
        entity_type="diagnosis",
        entity_id=diagnosis.id
    )
    db.add(audit)
    db.commit()
    
    return AIAnalysisResponse(
        diagnosis_id=diagnosis.id,
        screening_id=diagnosis.screening_id,
        ai_prediction=diagnosis.ai_prediction,
        ai_confidence=diagnosis.ai_confidence,
        ai_notes=diagnosis.ai_notes,
        ai_analysis_date=diagnosis.ai_analysis_date
    )


@router.post("/review", response_model=DiagnosisResponse)
def submit_clinician_review(
    request: ClinicianReviewRequest,
    current_user: User = Depends(require_pathologist),
    db: Session = Depends(get_db)
):
    """Submit clinician review for a diagnosis (mandatory human oversight)."""
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == request.diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    if diagnosis.review_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already submitted for this diagnosis"
        )
    
    # Update with clinician review
    diagnosis.reviewer_id = current_user.id
    diagnosis.clinician_agrees_with_ai = request.agrees_with_ai
    diagnosis.clinician_diagnosis = request.clinician_diagnosis
    diagnosis.clinician_notes = request.clinician_notes
    diagnosis.review_date = datetime.utcnow()
    diagnosis.follow_up_recommended = request.follow_up_recommended
    diagnosis.follow_up_notes = request.follow_up_notes
    
    # Finalize diagnosis
    diagnosis.final_diagnosis = request.clinician_diagnosis
    diagnosis.finalized_at = datetime.utcnow()
    
    # Update screening status
    screening = db.query(Screening).filter(Screening.id == diagnosis.screening_id).first()
    if screening:
        screening.status = ScreeningStatus.COMPLETED.value
    
    db.commit()
    db.refresh(diagnosis)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="diagnosis.clinician_review",
        entity_type="diagnosis",
        entity_id=diagnosis.id
    )
    db.add(audit)
    db.commit()
    
    return diagnosis


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
def get_diagnosis(
    diagnosis_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Get diagnosis by ID."""
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    return diagnosis


@router.get("/screening/{screening_id}", response_model=DiagnosisResponse)
def get_diagnosis_by_screening(
    screening_id: str,
    current_user: User = Depends(require_clinician),
    db: Session = Depends(get_db)
):
    """Get diagnosis for a specific screening."""
    diagnosis = db.query(Diagnosis).filter(Diagnosis.screening_id == screening_id).first()
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No diagnosis found for this screening"
        )
    return diagnosis
