"""
CervixAI Database Configuration
Supports both sync and async operations with PostgreSQL/SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator

from app.core.config import settings

# Handle SQLite vs PostgreSQL connection args
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Sync engine
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database session (for non-FastAPI use)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import all models to ensure they're registered with Base
    from app.models import (
        User, Patient, Screening, ScreeningImage, 
        Diagnosis, AuditLog
    )
    Base.metadata.create_all(bind=engine)


def reset_db():
    """Reset database - USE WITH CAUTION."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# Async support (optional, for future use)
async_engine = None
AsyncSessionLocal = None

if settings.async_database_url:
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker as async_sessionmaker
        
        async_engine = create_async_engine(
            settings.async_database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    except ImportError:
        pass


async def get_async_db():
    """Async dependency for database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
