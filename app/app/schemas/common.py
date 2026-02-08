"""
CervixAI Common/Shared Schemas
"""
from typing import Optional, List, Any
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Individual error detail."""
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: dict  # Contains code, message, details


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


class PaginationParams(BaseModel):
    """Pagination parameters."""
    limit: int = 20
    offset: int = 0
