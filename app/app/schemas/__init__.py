"""
CervixAI Schemas Package
Exports all API schemas.
"""
from app.schemas.user import (
    UserBase, UserCreate, UserLogin, UserUpdate, UserResponse, Token, TokenRefresh
)
from app.schemas.patient import (
    PatientBase, PatientCreate, PatientUpdate, PatientResponse, PatientListResponse
)
from app.schemas.screening import (
    ScreeningCreate, ScreeningUpdate, ScreeningResponse, ScreeningListResponse
)
from app.schemas.image import ImageResponse, ImageListResponse
from app.schemas.diagnosis import (
    AIAnalysisRequest, AIAnalysisResponse, ClinicianReviewRequest, DiagnosisResponse
)
from app.schemas.common import ErrorResponse, MessageResponse, PaginationParams
from app.schemas.sample import SampleBase, SampleCreate, SampleUpdate, SampleRead
from app.schemas.ai_result import AIResultBase, AIResultCreate, AIResultRead
from app.schemas.annotation import AnnotationBase, AnnotationCreate, AnnotationRead, AnnotationSignOff
from app.schemas.role import RoleBase, RoleCreate, RoleRead

__all__ = [
    # User
    "UserBase", "UserCreate", "UserLogin", "UserUpdate", "UserResponse",
    "Token", "TokenRefresh",
    # Patient
    "PatientBase", "PatientCreate", "PatientUpdate", "PatientResponse", "PatientListResponse",
    # Screening
    "ScreeningCreate", "ScreeningUpdate", "ScreeningResponse", "ScreeningListResponse",
    # Image
    "ImageResponse", "ImageListResponse",
    # Diagnosis
    "AIAnalysisRequest", "AIAnalysisResponse", "ClinicianReviewRequest", "DiagnosisResponse",
    # Common
    "ErrorResponse", "MessageResponse", "PaginationParams",
    # Sample
    "SampleBase", "SampleCreate", "SampleUpdate", "SampleRead",
    # AI Result
    "AIResultBase", "AIResultCreate", "AIResultRead",
    # Annotation
    "AnnotationBase", "AnnotationCreate", "AnnotationRead", "AnnotationSignOff",
    # Role
    "RoleBase", "RoleCreate", "RoleRead",
]
