"""
CervixAI AI Results API Routes
Endpoints for AI analysis and results.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, AIResult, Sample
from app.schemas.ai_result import AIResultCreate, AIResultRead, AIAnalysisRequest, AIAnalysisResponse
from app.services.ai_result_service import AIResultService

router = APIRouter(prefix="/ai-results", tags=["ai-results"])


@router.post("/analyze", response_model=AIAnalysisResponse)
async def run_ai_analysis(
    request: AIAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run AI analysis on a screening or sample."""
    service = AIResultService(db, current_user)
    
    result = service.run_analysis(
        screening_id=str(request.screening_id) if request.screening_id else None,
        sample_id=str(request.sample_id) if request.sample_id else None
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Screening or sample not found")
    
    # Handle both Diagnosis (legacy) and AIResult models
    if hasattr(result, 'ai_prediction'):
        # Legacy Diagnosis model
        return AIAnalysisResponse(
            result_id=result.id,
            sample_id=result.screening_id,
            ai_prediction=result.ai_prediction,
            ai_confidence=result.ai_confidence,
            ai_notes=result.ai_notes
        )
    else:
        # New AIResult model
        return AIAnalysisResponse(
            result_id=result.id,
            sample_id=result.sample_id,
            ai_prediction=result.primary_prediction,
            ai_confidence=result.primary_confidence,
            top_predictions=result.get_top_predictions(3),
            heatmap_url=result.heatmap_path,
            ai_notes=result.ai_notes
        )


@router.get("/", response_model=list[AIResultRead])
async def list_ai_results(
    sample_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List AI results with optional filters."""
    query = db.query(AIResult)
    
    if sample_id:
        query = query.filter(AIResult.sample_id == sample_id)
    
    results = query.order_by(AIResult.processed_at.desc()).offset(skip).limit(limit).all()
    return results


@router.get("/{result_id}", response_model=AIResultRead)
async def get_ai_result(
    result_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific AI result by ID."""
    result = db.query(AIResult).filter(AIResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="AI result not found")
    return result


@router.get("/{result_id}/heatmap")
async def get_result_heatmap(
    result_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get heatmap for an AI result."""
    result = db.query(AIResult).filter(AIResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="AI result not found")
    
    if not result.heatmap_path:
        raise HTTPException(status_code=404, detail="Heatmap not available")
    
    from fastapi.responses import FileResponse
    return FileResponse(result.heatmap_path)
