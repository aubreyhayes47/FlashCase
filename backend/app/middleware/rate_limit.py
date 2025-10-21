"""
Rate limiting middleware for AI endpoints.

Implements per-user rate limiting to control Grok API usage and costs.
Uses slowapi for rate limiting with in-memory storage.
"""

from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings


def get_user_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    
    Uses IP address as the identifier. In production with authentication,
    this should use the authenticated user ID.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Unique identifier for the user/client
    """
    # For now, use IP address
    # TODO: After authentication is implemented, use user ID
    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=[
        f"{settings.rate_limit_per_minute}/minute",
        f"{settings.rate_limit_per_hour}/hour"
    ],
    enabled=settings.rate_limit_enabled
)


def setup_rate_limiting(app):
    """
    Configure rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return limiter
