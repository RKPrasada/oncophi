"""
CervixAI API Routes Package
Registers all API routers.
"""
from fastapi import APIRouter
from app.api.routes import auth, users, patients, screenings, images, diagnoses, audit
from app.api.routes import samples, ai_results, annotations

api_router = APIRouter()

# Legacy routes
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(patients.router)
api_router.include_router(screenings.router)
api_router.include_router(images.router)
api_router.include_router(diagnoses.router)
api_router.include_router(audit.router)

# New enhanced routes
api_router.include_router(samples.router)
api_router.include_router(ai_results.router)
api_router.include_router(annotations.router)
