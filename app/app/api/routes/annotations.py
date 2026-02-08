"""
CervixAI Annotations API Routes
Endpoints for clinician annotations and sign-offs.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import User, Annotation, AIResult
from app.schemas.annotation import AnnotationCreate, AnnotationRead, AnnotationUpdate, AnnotationSignOff
from app.schemas.common import MessageResponse
from app.services.annotation_service import AnnotationService

router = APIRouter(prefix="/annotations", tags=["annotations"])


@router.post("/", response_model=AnnotationRead, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    annotation_in: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new annotation for an AI result."""
    service = AnnotationService(db, current_user)
    annotation = service.create_annotation(annotation_in)
    return annotation


@router.get("/", response_model=list[AnnotationRead])
async def list_annotations(
    result_id: Optional[str] = None,
    signed_off: Optional[bool] = None,
    clinician_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List annotations with optional filters."""
    query = db.query(Annotation)
    
    if result_id:
        query = query.filter(Annotation.result_id == result_id)
    if signed_off is not None:
        query = query.filter(Annotation.signed_off == signed_off)
    if clinician_id:
        query = query.filter(Annotation.clinician_id == clinician_id)
    
    annotations = query.order_by(Annotation.created_at.desc()).offset(skip).limit(limit).all()
    return annotations


@router.get("/pending", response_model=list[AnnotationRead])
async def get_pending_annotations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get annotations pending sign-off for current user."""
    service = AnnotationService(db, current_user)
    return service.get_pending_annotations(current_user.id)


@router.get("/{annotation_id}", response_model=AnnotationRead)
async def get_annotation(
    annotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific annotation by ID."""
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


@router.patch("/{annotation_id}", response_model=AnnotationRead)
async def update_annotation(
    annotation_id: str,
    annotation_update: AnnotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an annotation."""
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    if annotation.signed_off:
        raise HTTPException(status_code=400, detail="Cannot update signed-off annotation")
    
    update_data = annotation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(annotation, field, value)
    
    db.commit()
    db.refresh(annotation)
    return annotation


@router.post("/{annotation_id}/sign-off", response_model=AnnotationRead)
async def sign_off_annotation(
    annotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sign off an annotation (mandatory clinical oversight)."""
    service = AnnotationService(db, current_user)
    annotation = service.sign_off_annotation(annotation_id)
    
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    return annotation
