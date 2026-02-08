"""
CervixAI Models Package
Exports all database models for the application.
"""
from app.models.user import User, UserRole
from app.models.role import Role, DEFAULT_ROLES
from app.models.patient import Patient
from app.models.screening import Screening, ScreeningStatus
from app.models.sample import Sample
from app.models.image import ScreeningImage, ImageType
from app.models.diagnosis import Diagnosis, DiagnosisCategory
from app.models.ai_result import AIResult
from app.models.annotation import Annotation
from app.models.audit import AuditLog
from app.models.integration_metadata import IntegrationMetadata

__all__ = [
    # User & Auth
    "User",
    "UserRole",
    "Role",
    "DEFAULT_ROLES",
    
    # Patient & Samples
    "Patient",
    "Screening",
    "ScreeningStatus",
    "Sample",
    "ScreeningImage",
    "ImageType",
    
    # AI & Diagnosis
    "Diagnosis",
    "DiagnosisCategory",
    "AIResult",
    "Annotation",
    
    # Compliance & Integration
    "AuditLog",
    "IntegrationMetadata",
]
