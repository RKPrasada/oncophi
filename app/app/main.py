"""
CervixAI - FastAPI Application Entry Point
AI-Powered Cervical Cancer Screening Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db
from app.api import api_router

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
    CervixAI is an AI-powered clinical diagnostic platform for cervical cancer screening.
    
    ## Features
    - **AI-Driven Triage**: Automated analysis of Pap smear and colposcopy images
    - **Explainable AI**: Heatmap overlays showing areas of concern
    - **Human Oversight**: Mandatory clinician review before final diagnosis
    - **Episode-Based Monitoring**: Longitudinal patient tracking
    - **Compliance**: HIPAA/GDPR audit logging
    
    ## Workflow
    1. Register patient and obtain consent
    2. Create screening episode
    3. Upload cervical images
    4. Run AI analysis
    5. Clinician reviews and finalizes diagnosis
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to CervixAI",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
