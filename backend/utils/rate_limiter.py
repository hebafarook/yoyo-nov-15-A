"""
Rate Limiting Configuration
===========================

Rate limiter for auth endpoints with optional Redis backend.
Works standalone (in-memory) or distributed (Redis).

Environment Variables:
- RATE_LIMIT_ENABLED: "true" | "false" (default: "false" in dev, "true" in prod)
- RATE_LIMIT_REDIS_URL: Redis connection URL (optional, e.g., redis://localhost:6379/0)
- RATE_LIMIT_LOGIN_PER_MINUTE: Max login attempts per IP per minute (default: 10)
- RATE_LIMIT_REGISTER_PER_HOUR: Max registrations per IP per hour (default: 5)
- RATE_LIMIT_RESET_PER_HOUR: Max password reset requests per IP per hour (default: 5)

Storage Selection:
- If RATE_LIMIT_REDIS_URL is set and valid: Use Redis (distributed)
- Otherwise: Use in-memory (per-worker)

Usage:
    from utils.rate_limiter import RateLimitDependency, login_limiter
    
    @router.post("/login")
    async def login(request: Request, _: None = Depends(login_limiter)):
        ...
"""

import os
import time
import logging
from abc import ABC, abstractmethod
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


def _get_redis_url() -> Optional[str]:
    """Get Redis URL from environment."""
    return os.environ.get("RATE_LIMIT_REDIS_URL", "").strip() or None


# Default limits (conservative for production)
DEFAULT_LOGIN_PER_MINUTE = 10      # 10 login attempts per minute per IP
DEFAULT_REGISTER_PER_HOUR = 5     # 5 registrations per hour per IP
DEFAULT_RESET_PER_HOUR = 5        # 5 password resets per hour per IP


def get_rate_limit_config() -> dict:
    """Get current rate limit configuration."""
    redis_url = _get_redis_url()
    return {
        "enabled": _is_rate_limit_enabled(),
        "environment": "production" if _is_production() else "development",
        "backend": "redis" if redis_url else "memory",
        "redis_configured": bool(redis_url),
        "login_per_minute": int(os.environ.get("RATE_LIMIT_LOGIN_PER_MINUTE", DEFAULT_LOGIN_PER_MINUTE)),
        "register_per_hour": int(os.environ.get("RATE_LIMIT_REGISTER_PER_HOUR", DEFAULT_REGISTER_PER_HOUR)),
        "reset_per_hour": int(os.environ.get("RATE_LIMIT_RESET_PER_HOUR", DEFAULT_RESET_PER_HOUR)),
    }


# ============================================================================
# STORAGE INTERFACE
# ============================================================================

class RateLimitStore(ABC):
    """Abstract base class for rate limit storage backends."""
    
    @abstractmethod
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """
        Check if request is allowed and record it if so.
        
        Args:
            key: Unique identifier (e.g., "login:192.168.1.1")
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (allowed, remaining, reset_after_seconds)
        """
        pass
    
    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        pass
    
    @abstractmethod
    def reset_all(self) -> None:
        """Reset all rate limits."""
        pass


# ============================================================================
# IN-MEMORY STORE (Default, No Redis Required)
# ============================================================================

class InMemoryStore(RateLimitStore):
    """
    In-memory rate limit storage using sliding window.
    Thread-safe for use within a single process.
    
    Note: Each worker process has its own counter.
    For distributed rate limiting across workers, use RedisStore.
    """
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
    
    def _clean_old_requests(self, key: str, now: float, window_seconds: int) -> None:
        """Remove requests outside the current window."""
        cutoff = now - window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """Check if request is allowed using sliding window."""
        now = time.time()
        
        with self._lock:
            self._clean_old_requests(key, now, window_seconds)
            current_count = len(self._requests[key])
            
            if current_count >= max_requests:
                oldest = min(self._requests[key]) if self._requests[key] else now
                reset_after = int(window_seconds - (now - oldest)) + 1
                return False, 0, max(1, reset_after)
            
            self._requests[key].append(now)
            remaining = max_requests - current_count - 1
            return True, remaining, window_seconds
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        with self._lock:
            self._requests.pop(key, None)
    
    def reset_all(self) -> None:
        """Reset all rate limits."""
        with self._lock:
            self._requests.clear()


# ============================================================================
# REDIS STORE (Optional, Distributed)
# ============================================================================

class RedisStore(RateLimitStore):
    """
    Redis-backed rate limit storage using fixed window with atomic operations.
    Provides distributed rate limiting across multiple workers/processes.
    
    Uses INCR + EXPIRE pattern for atomic counter management.
    """
    
    def __init__(self, redis_client):
        """
        Args:
            redis_client: A Redis client instance (redis.Redis or compatible)
        """
        self._redis = redis_client
        self._prefix = "ratelimit:"
    
    def _make_key(self, key: str, window_seconds: int) -> str:
        """Create Redis key with time bucket for fixed window."""
        # Use fixed time windows (e.g., current minute for per-minute limits)
        bucket = int(time.time() // window_seconds)
        return f"{self._prefix}{key}:{bucket}"
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """
        Check if request is allowed using Redis atomic operations.
        
        Uses INCR + EXPIRE pattern for atomic counter with TTL.
        """
        redis_key = self._make_key(key, window_seconds)
        
        try:
            # Atomic increment
            current = self._redis.incr(redis_key)
            
            # Set expiry on first request (when count is 1)
            if current == 1:
                self._redis.expire(redis_key, window_seconds)
            
            if current > max_requests:
                # Get TTL for reset time
                ttl = self._redis.ttl(redis_key)
                reset_after = max(1, ttl if ttl > 0 else window_seconds)
                return False, 0, reset_after
            
            remaining = max_requests - current
            ttl = self._redis.ttl(redis_key)
            return True, remaining, max(1, ttl if ttl > 0 else window_seconds)
            
        except Exception as e:
            # Log error but don't crash - this will trigger fallback
            logger.error(f"Redis rate limit error: {e}")
            raise
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key (deletes all time buckets)."""
        try:
            pattern = f"{self._prefix}{key}:*"
            keys = self._redis.keys(pattern)
            if keys:
                self._redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis reset error: {e}")
    
    def reset_all(self) -> None:
        """Reset all rate limits."""
        try:
            pattern = f"{self._prefix}*"
            keys = self._redis.keys(pattern)
            if keys:
                self._redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis reset_all error: {e}")


# ============================================================================
# STORE FACTORY
# ============================================================================

_store_instance: Optional[RateLimitStore] = None
_store_type: Optional[str] = None


def _create_redis_client(url: str):
    """Create Redis client from URL."""
    try:
        import redis
        client = redis.from_url(url, decode_responses=True)
        # Test connection
        client.ping()
        return client
    except ImportError:
        logger.warning("redis package not installed. Install with: pip install redis")
        return None
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        return None


def get_store() -> RateLimitStore:
    """
    Get or create the rate limit store.
    
    Selection logic:
    1. If RATE_LIMIT_REDIS_URL is set, try Redis
    2. If Redis fails or not configured, use in-memory
    
    Returns:
        RateLimitStore instance (Redis or InMemory)
    """
    global _store_instance, _store_type
    
    if _store_instance is not None:
        return _store_instance
    
    redis_url = _get_redis_url()
    
    if redis_url:
        redis_client = _create_redis_client(redis_url)
        if redis_client:
            _store_instance = RedisStore(redis_client)
            _store_type = "redis"
            logger.info("✅ Rate limiter using Redis backend (distributed)")
            return _store_instance
        else:
            logger.warning(
                "⚠️  RATE_LIMIT_REDIS_URL is set but Redis connection failed. "
                "Falling back to in-memory storage. Rate limits will be PER-WORKER."
            )
    
    # Fall back to in-memory
    _store_instance = InMemoryStore()
    _store_type = "memory"
    
    if _is_production() and _is_rate_limit_enabled():
        logger.warning(
            "⚠️  Rate limiter using in-memory backend in production. "
            "Rate limits are PER-WORKER (not shared across processes). "
            "Set RATE_LIMIT_REDIS_URL for distributed rate limiting."
        )
    else:
        logger.info("✅ Rate limiter using in-memory backend")
    
    return _store_instance


def get_store_type() -> str:
    """Get the current store type ('redis' or 'memory')."""
    global _store_type
    if _store_type is None:
        get_store()  # Initialize if needed
    return _store_type or "memory"


def reset_store() -> None:
    """Reset the store instance (for testing)."""
    global _store_instance, _store_type
    if _store_instance:
        _store_instance.reset_all()
    _store_instance = None
    _store_type = None


# ============================================================================
# RATE LIMITER CLASS (Uses Store)
# ============================================================================

class RateLimiter:
    """
    Rate limiter that uses the configured storage backend.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Args:
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, key: str) -> Tuple[bool, int, int]:
        """Check if request is allowed for the given key."""
        store = get_store()
        try:
            return store.is_allowed(key, self.max_requests, self.window_seconds)
        except Exception as e:
            # If Redis fails mid-operation, log and allow (fail-open)
            logger.error(f"Rate limit check failed: {e}. Allowing request (fail-open).")
            return True, self.max_requests, self.window_seconds
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        get_store().reset(key)
    
    def reset_all(self) -> None:
        """Reset all rate limits."""
        get_store().reset_all()


# ============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================================

# Alias for backward compatibility with existing code
InMemoryRateLimiter = RateLimiter


# ============================================================================
# RATE LIMITER INSTANCES
# ============================================================================

_login_limiter: Optional[RateLimiter] = None
_register_limiter: Optional[RateLimiter] = None
_reset_limiter: Optional[RateLimiter] = None


def get_login_limiter() -> RateLimiter:
    """Get or create login rate limiter."""
    global _login_limiter
    if _login_limiter is None:
        limit = int(os.environ.get("RATE_LIMIT_LOGIN_PER_MINUTE", DEFAULT_LOGIN_PER_MINUTE))
        _login_limiter = RateLimiter(max_requests=limit, window_seconds=60)
    return _login_limiter


def get_register_limiter() -> RateLimiter:
    """Get or create registration rate limiter."""
    global _register_limiter
    if _register_limiter is None:
        limit = int(os.environ.get("RATE_LIMIT_REGISTER_PER_HOUR", DEFAULT_REGISTER_PER_HOUR))
        _register_limiter = RateLimiter(max_requests=limit, window_seconds=3600)
    return _register_limiter


def get_reset_limiter() -> RateLimiter:
    """Get or create password reset rate limiter."""
    global _reset_limiter
    if _reset_limiter is None:
        limit = int(os.environ.get("RATE_LIMIT_RESET_PER_HOUR", DEFAULT_RESET_PER_HOUR))
        _reset_limiter = RateLimiter(max_requests=limit, window_seconds=3600)
    return _reset_limiter


# ============================================================================
# FASTAPI DEPENDENCIES
# ============================================================================

def _get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
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
    reset_store()


def set_store_for_testing(store: RateLimitStore) -> None:
    """Inject a store for testing purposes."""
    global _store_instance, _store_type
    _store_instance = store
    _store_type = "test"
