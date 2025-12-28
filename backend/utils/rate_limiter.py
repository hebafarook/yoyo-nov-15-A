"""
Rate Limiting Configuration
===========================

In-memory rate limiter for auth endpoints.
No Redis required - works standalone.

Environment Variables:
- RATE_LIMIT_ENABLED: "true" | "false" (default: "false" in dev, "true" in prod)
- RATE_LIMIT_LOGIN_PER_MINUTE: Max login attempts per IP per minute (default: 10)
- RATE_LIMIT_REGISTER_PER_HOUR: Max registrations per IP per hour (default: 5)
- RATE_LIMIT_RESET_PER_HOUR: Max password reset requests per IP per hour (default: 5)

Usage:
    from utils.rate_limiter import RateLimitDependency, login_limiter
    
    @router.post("/login")
    async def login(request: Request, _: None = Depends(login_limiter)):
        ...
"""

import os
import time
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException, status

logger = logging.getLogger(__name__)


# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

def _is_production() -> bool:
    env = os.environ.get("ENVIRONMENT", "development").lower()
    return env in ("production", "prod", "staging")


def _is_rate_limit_enabled() -> bool:
    """Check if rate limiting is enabled."""
    env_value = os.environ.get("RATE_LIMIT_ENABLED", "").lower()
    
    if env_value == "true":
        return True
    if env_value == "false":
        return False
    
    # Default: enabled in production, disabled in development
    return _is_production()


# Default limits (conservative for production)
DEFAULT_LOGIN_PER_MINUTE = 10      # 10 login attempts per minute per IP
DEFAULT_REGISTER_PER_HOUR = 5     # 5 registrations per hour per IP
DEFAULT_RESET_PER_HOUR = 5        # 5 password resets per hour per IP


def get_rate_limit_config() -> dict:
    """Get current rate limit configuration."""
    return {
        "enabled": _is_rate_limit_enabled(),
        "environment": "production" if _is_production() else "development",
        "login_per_minute": int(os.environ.get("RATE_LIMIT_LOGIN_PER_MINUTE", DEFAULT_LOGIN_PER_MINUTE)),
        "register_per_hour": int(os.environ.get("RATE_LIMIT_REGISTER_PER_HOUR", DEFAULT_REGISTER_PER_HOUR)),
        "reset_per_hour": int(os.environ.get("RATE_LIMIT_RESET_PER_HOUR", DEFAULT_RESET_PER_HOUR)),
    }


# ============================================================================
# IN-MEMORY RATE LIMITER (No Redis Required)
# ============================================================================

class InMemoryRateLimiter:
    """
    Simple sliding window rate limiter using in-memory storage.
    Thread-safe for use with multiple workers.
    
    Note: In a multi-process deployment, each process has its own counter.
    For distributed rate limiting, use Redis-backed solution.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Args:
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
    
    def _clean_old_requests(self, key: str, now: float) -> None:
        """Remove requests outside the current window."""
        cutoff = now - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
    
    def is_allowed(self, key: str) -> Tuple[bool, int, int]:
        """
        Check if request is allowed for the given key.
        
        Args:
            key: Identifier (e.g., IP address)
        
        Returns:
            Tuple of (allowed, remaining, reset_after_seconds)
        """
        now = time.time()
        
        with self._lock:
            self._clean_old_requests(key, now)
            current_count = len(self._requests[key])
            
            if current_count >= self.max_requests:
                # Calculate when the oldest request will expire
                oldest = min(self._requests[key]) if self._requests[key] else now
                reset_after = int(self.window_seconds - (now - oldest)) + 1
                return False, 0, reset_after
            
            # Allow request and record it
            self._requests[key].append(now)
            remaining = self.max_requests - current_count - 1
            return True, remaining, self.window_seconds
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key (for testing)."""
        with self._lock:
            self._requests.pop(key, None)
    
    def reset_all(self) -> None:
        """Reset all rate limits (for testing)."""
        with self._lock:
            self._requests.clear()


# ============================================================================
# RATE LIMITER INSTANCES
# ============================================================================

# Create limiter instances with configurable limits
_login_limiter: Optional[InMemoryRateLimiter] = None
_register_limiter: Optional[InMemoryRateLimiter] = None
_reset_limiter: Optional[InMemoryRateLimiter] = None


def get_login_limiter() -> InMemoryRateLimiter:
    """Get or create login rate limiter."""
    global _login_limiter
    if _login_limiter is None:
        limit = int(os.environ.get("RATE_LIMIT_LOGIN_PER_MINUTE", DEFAULT_LOGIN_PER_MINUTE))
        _login_limiter = InMemoryRateLimiter(max_requests=limit, window_seconds=60)
    return _login_limiter


def get_register_limiter() -> InMemoryRateLimiter:
    """Get or create registration rate limiter."""
    global _register_limiter
    if _register_limiter is None:
        limit = int(os.environ.get("RATE_LIMIT_REGISTER_PER_HOUR", DEFAULT_REGISTER_PER_HOUR))
        _register_limiter = InMemoryRateLimiter(max_requests=limit, window_seconds=3600)
    return _register_limiter


def get_reset_limiter() -> InMemoryRateLimiter:
    """Get or create password reset rate limiter."""
    global _reset_limiter
    if _reset_limiter is None:
        limit = int(os.environ.get("RATE_LIMIT_RESET_PER_HOUR", DEFAULT_RESET_PER_HOUR))
        _reset_limiter = InMemoryRateLimiter(max_requests=limit, window_seconds=3600)
    return _reset_limiter


# ============================================================================
# FASTAPI DEPENDENCIES
# ============================================================================

def _get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for proxy headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct client
    return request.client.host if request.client else "unknown"


class RateLimitDependency:
    """
    FastAPI dependency for rate limiting.
    
    Usage:
        login_limiter = RateLimitDependency(get_login_limiter, "login")
        
        @router.post("/login")
        async def login(request: Request, _: None = Depends(login_limiter)):
            ...
    """
    
    def __init__(self, limiter_getter, endpoint_name: str):
        self.limiter_getter = limiter_getter
        self.endpoint_name = endpoint_name
    
    async def __call__(self, request: Request) -> None:
        """Check rate limit for the request."""
        if not _is_rate_limit_enabled():
            return  # Rate limiting disabled
        
        limiter = self.limiter_getter()
        client_ip = _get_client_ip(request)
        key = f"{self.endpoint_name}:{client_ip}"
        
        allowed, remaining, reset_after = limiter.is_allowed(key)
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {self.endpoint_name} from IP {client_ip}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": f"Too many {self.endpoint_name} attempts. Please try again in {reset_after} seconds."
                    }
                }
            )


# Pre-configured dependencies for auth endpoints
login_limiter = RateLimitDependency(get_login_limiter, "login")
register_limiter = RateLimitDependency(get_register_limiter, "registration")
reset_password_limiter = RateLimitDependency(get_reset_limiter, "password reset")


# ============================================================================
# TESTING UTILITIES
# ============================================================================

def reset_all_limiters() -> None:
    """Reset all rate limiters (for testing only)."""
    global _login_limiter, _register_limiter, _reset_limiter
    if _login_limiter:
        _login_limiter.reset_all()
    if _register_limiter:
        _register_limiter.reset_all()
    if _reset_limiter:
        _reset_limiter.reset_all()


def reinitialize_limiters() -> None:
    """Reinitialize limiters with current env config (for testing)."""
    global _login_limiter, _register_limiter, _reset_limiter
    _login_limiter = None
    _register_limiter = None
    _reset_limiter = None
