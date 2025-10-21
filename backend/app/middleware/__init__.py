"""Middleware package for FlashCase backend."""

from app.middleware.rate_limit import setup_rate_limiting

__all__ = ["setup_rate_limiting"]
