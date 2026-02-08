"""
CervixAI Core Configuration
Enhanced configuration with PostgreSQL, OAuth2, caching, and logging settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "CervixAI"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    
    # Database - PostgreSQL (fallback to SQLite for dev)
    database_url: str = Field(
        default="sqlite:///./cervixai.db",
        validation_alias="DATABASE_URL"
    )
    
    # Async database URL for async operations
    async_database_url: Optional[str] = Field(
        default=None,
        validation_alias="ASYNC_DATABASE_URL"
    )
    
    # JWT Settings
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        validation_alias="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # OAuth2 Settings (for external IdP integration)
    oauth_client_id: Optional[str] = Field(default=None, validation_alias="OAUTH_CLIENT_ID")
    oauth_client_secret: Optional[str] = Field(default=None, validation_alias="OAUTH_CLIENT_SECRET")
    
    # Redis Cache (optional)
    redis_url: Optional[str] = Field(default=None, validation_alias="REDIS_URL")
    cache_ttl_seconds: int = 300  # 5 minutes default
    
    # RabbitMQ (optional for async processing)
    rabbitmq_url: Optional[str] = Field(default=None, validation_alias="RABBITMQ_URL")
    
    # File Upload
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    allowed_file_types: list = ["jpg", "jpeg", "png", "tiff", "dicom"]
    
    # AI Processing
    ai_model_path: str = Field(default="./models", validation_alias="AI_MODEL_PATH")
    ai_confidence_threshold: float = 0.85
    
    # Security
    bcrypt_rounds: int = 12
    cors_origins: list = ["*"]  # Configure appropriately in production
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    # Compliance
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 2555  # ~7 years for HIPAA compliance
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
