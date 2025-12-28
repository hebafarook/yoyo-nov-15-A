"""
CORS Configuration
==================

Single source of truth for CORS settings.
Provides consistent behavior across server.py and main.py.

Environment Variables:
- ENVIRONMENT: "development" | "production" (default: "development")
- CORS_ALLOW_ORIGINS: Comma-separated list of allowed origins
  - Dev default: "http://localhost:3000,http://localhost:8001,http://127.0.0.1:3000"
  - Prod: MUST be set explicitly, otherwise denies all with warning

Usage:
    from utils.cors_config import configure_cors
    configure_cors(app)
"""

import os
import logging
from typing import List
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

# Environment detection
def _is_production() -> bool:
    env = os.environ.get("ENVIRONMENT", "development").lower()
    return env in ("production", "prod", "staging")

# Default origins for development
DEV_DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8001",
]

# Explicit allowed methods (no wildcards in production)
ALLOWED_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# Explicit allowed headers
ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
]


def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins based on environment.
    
    Development: Permissive defaults for localhost
    Production: Strict, must be explicitly configured
    
    Returns:
        List of allowed origin strings
    """
    # Check new var first, then fall back to old var for backward compatibility
    env_origins = os.environ.get("CORS_ALLOW_ORIGINS", "").strip()
    if not env_origins:
        env_origins = os.environ.get("CORS_ORIGINS", "").strip()
    
    is_prod = _is_production()
    
    if env_origins and env_origins != "*":
        # Parse comma-separated origins
        origins = [o.strip() for o in env_origins.split(",") if o.strip()]
        
        # Warn if wildcard in production
        if is_prod and "*" in origins:
            logger.warning(
                "⚠️  SECURITY WARNING: CORS origins contains '*' in production. "
                "This is insecure. Please specify explicit origins."
            )
        
        logger.info(f"CORS origins from env: {origins}")
        return origins
    
    # Wildcard or no env var set
    if env_origins == "*":
        if is_prod:
            logger.warning(
                "⚠️  SECURITY WARNING: CORS_ORIGINS='*' in production. "
                "This is insecure. Please specify explicit origins."
            )
        else:
            logger.info("CORS using wildcard '*' (development mode)")
        return ["*"]
    
    # No env var set
    if is_prod:
        # Production without explicit config = deny all (fail-safe)
        logger.warning(
            "⚠️  CORS_ALLOW_ORIGINS not set in production mode. "
            "Defaulting to empty list (denying all cross-origin requests). "
            "Set CORS_ALLOW_ORIGINS to your frontend domain(s)."
        )
        return []
    
    # Development defaults
    logger.info(f"CORS using development defaults: {DEV_DEFAULT_ORIGINS}")
    return DEV_DEFAULT_ORIGINS


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware on the FastAPI app.
    
    Call this once during app initialization.
    Single source of truth for CORS configuration.
    
    Args:
        app: FastAPI application instance
    """
    origins = get_cors_origins()
    is_prod = _is_production()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else [],
        allow_credentials=True,
        allow_methods=ALLOWED_METHODS,
        allow_headers=ALLOWED_HEADERS,
        expose_headers=["X-Request-ID"],
    )
    
    env_name = "production" if is_prod else "development"
    if origins and origins != ["*"]:
        logger.info(f"✅ CORS configured ({env_name}): {len(origins)} origin(s)")
    elif origins == ["*"]:
        logger.info(f"✅ CORS configured ({env_name}): allowing all origins (wildcard)")
    else:
        logger.warning(f"⚠️  CORS configured ({env_name}): NO origins allowed")


def get_cors_config_summary() -> dict:
    """
    Get current CORS configuration for debugging/health checks.
    
    Returns:
        Dict with current CORS settings
    """
    origins = get_cors_origins()
    return {
        "environment": "production" if _is_production() else "development",
        "origins": origins,
        "methods": ALLOWED_METHODS,
        "headers": ALLOWED_HEADERS,
        "credentials": True,
    }
