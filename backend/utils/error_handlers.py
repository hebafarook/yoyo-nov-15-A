"""
Central Error Handling
======================

Global exception handlers for consistent error responses.
Does NOT change any business logic or successful responses.

Error Response Schema:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message"
    }
}
"""

import logging
import traceback
import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

# Check if we're in development mode
IS_DEV = os.environ.get("ENVIRONMENT", "development").lower() in ("development", "dev", "local")


def create_error_response(code: str, message: str, status_code: int) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    Returns 422 with standardized format.
    """
    # Extract first error message for simplicity
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        msg = first_error.get("msg", "Validation error")
        message = f"{field}: {msg}" if field else msg
    else:
        message = "Request validation failed"
    
    logger.warning(f"Validation error on {request.url.path}: {message}")
    
    return create_error_response(
        code="VALIDATION_ERROR",
        message=message,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTPException (404, 401, 403, etc.).
    Preserves original status code.
    """
    # Map common status codes to error codes
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "RATE_LIMITED",
    }
    
    error_code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    message = str(exc.detail) if exc.detail else "An error occurred"
    
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} on {request.url.path}: {message}")
    else:
        logger.info(f"HTTP {exc.status_code} on {request.url.path}: {message}")
    
    return create_error_response(
        code=error_code,
        message=message,
        status_code=exc.status_code
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unhandled exceptions.
    Returns 500 without leaking stack traces to client.
    """
    # Log full stack trace for debugging
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    if IS_DEV:
        logger.error(traceback.format_exc())
    
    # Never expose internal details to client
    return create_error_response(
        code="INTERNAL_ERROR",
        message="An internal server error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers on the FastAPI app.
    Call this once during app initialization.
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    
    logger.info("✅ Central error handlers registered")
