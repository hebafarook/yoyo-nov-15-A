"""
Tests for Rate Limiting
=======================

Verifies rate limiting behavior on auth endpoints.
"""

import pytest
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from utils.rate_limiter import (
    InMemoryRateLimiter,
    RateLimitDependency,
    _is_rate_limit_enabled,
    get_rate_limit_config,
    reset_all_limiters,
    reinitialize_limiters,
    get_login_limiter,
)


# ============================================================================
# TEST: IN-MEMORY RATE LIMITER
# ============================================================================

class TestInMemoryRateLimiter:
    """Test the core rate limiter logic."""
    
    def test_allows_requests_under_limit(self):
        """Requests under limit should be allowed."""
        limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)
        
        for i in range(5):
            allowed, remaining, _ = limiter.is_allowed("test-key")
            assert allowed is True
            assert remaining == 4 - i
    
    def test_blocks_requests_over_limit(self):
        """Requests over limit should be blocked."""
        limiter = InMemoryRateLimiter(max_requests=3, window_seconds=60)
        
        # Use up the limit
        for _ in range(3):
            limiter.is_allowed("test-key")
        
        # Next request should be blocked
        allowed, remaining, reset_after = limiter.is_allowed("test-key")
        assert allowed is False
        assert remaining == 0
        assert reset_after > 0
    
    def test_different_keys_independent(self):
        """Different keys should have independent limits."""
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
        
        # Exhaust limit for key1
        limiter.is_allowed("key1")
        limiter.is_allowed("key1")
        allowed1, _, _ = limiter.is_allowed("key1")
        
        # key2 should still be allowed
        allowed2, _, _ = limiter.is_allowed("key2")
        
        assert allowed1 is False
        assert allowed2 is True
    
    def test_window_expiration(self):
        """Requests should be allowed after window expires."""
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=1)
        
        # Use up the limit
        limiter.is_allowed("test-key")
        allowed1, _, _ = limiter.is_allowed("test-key")
        assert allowed1 is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        allowed2, _, _ = limiter.is_allowed("test-key")
        assert allowed2 is True
    
    def test_reset_key(self):
        """Reset should clear limit for specific key."""
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
        
        limiter.is_allowed("test-key")
        allowed1, _, _ = limiter.is_allowed("test-key")
        assert allowed1 is False
        
        limiter.reset("test-key")
        
        allowed2, _, _ = limiter.is_allowed("test-key")
        assert allowed2 is True
    
    def test_reset_all(self):
        """Reset all should clear all limits."""
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
        
        limiter.is_allowed("key1")
        limiter.is_allowed("key2")
        
        limiter.reset_all()
        
        allowed1, _, _ = limiter.is_allowed("key1")
        allowed2, _, _ = limiter.is_allowed("key2")
        assert allowed1 is True
        assert allowed2 is True


# ============================================================================
# TEST: ENVIRONMENT CONFIGURATION
# ============================================================================

class TestRateLimitConfig:
    """Test environment-based configuration."""
    
    def test_disabled_in_development_by_default(self):
        """Rate limiting should be disabled in dev by default."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            # Clear RATE_LIMIT_ENABLED
            env = {"ENVIRONMENT": "development"}
            with patch.dict(os.environ, env, clear=True):
                assert _is_rate_limit_enabled() is False
    
    def test_enabled_in_production_by_default(self):
        """Rate limiting should be enabled in prod by default."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            assert _is_rate_limit_enabled() is True
    
    def test_explicit_enable_overrides_default(self):
        """RATE_LIMIT_ENABLED=true should enable even in dev."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "RATE_LIMIT_ENABLED": "true"
        }):
            assert _is_rate_limit_enabled() is True
    
    def test_explicit_disable_overrides_default(self):
        """RATE_LIMIT_ENABLED=false should disable even in prod."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "RATE_LIMIT_ENABLED": "false"
        }):
            assert _is_rate_limit_enabled() is False
    
    def test_config_has_all_fields(self):
        """Config should have all required fields."""
        config = get_rate_limit_config()
        
        assert "enabled" in config
        assert "environment" in config
        assert "login_per_minute" in config
        assert "register_per_hour" in config
        assert "reset_per_hour" in config
    
    def test_custom_limits_from_env(self):
        """Custom limits should be read from env."""
        with patch.dict(os.environ, {
            "RATE_LIMIT_LOGIN_PER_MINUTE": "20",
            "RATE_LIMIT_REGISTER_PER_HOUR": "10",
            "RATE_LIMIT_RESET_PER_HOUR": "3"
        }):
            config = get_rate_limit_config()
            
            assert config["login_per_minute"] == 20
            assert config["register_per_hour"] == 10
            assert config["reset_per_hour"] == 3


# ============================================================================
# TEST: FASTAPI DEPENDENCY
# ============================================================================

class TestRateLimitDependency:
    """Test the FastAPI dependency."""
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request."""
        request = MagicMock()
        request.client.host = "192.168.1.100"
        request.headers = {}
        return request
    
    @pytest.mark.asyncio
    async def test_allows_when_disabled(self, mock_request):
        """Should allow all requests when disabled."""
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "false"}):
            limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
            dependency = RateLimitDependency(lambda: limiter, "test")
            
            # Should not raise even after "exceeding" limit
            for _ in range(10):
                await dependency(mock_request)
    
    @pytest.mark.asyncio
    async def test_raises_429_when_exceeded(self, mock_request):
        """Should raise 429 when limit exceeded."""
        from fastapi import HTTPException
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
            limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
            dependency = RateLimitDependency(lambda: limiter, "test")
            
            # First two should pass
            await dependency(mock_request)
            await dependency(mock_request)
            
            # Third should raise
            with pytest.raises(HTTPException) as exc_info:
                await dependency(mock_request)
            
            assert exc_info.value.status_code == 429
    
    @pytest.mark.asyncio
    async def test_429_has_correct_format(self, mock_request):
        """429 response should have standard error format."""
        from fastapi import HTTPException
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
            limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
            dependency = RateLimitDependency(lambda: limiter, "login")
            
            await dependency(mock_request)
            
            with pytest.raises(HTTPException) as exc_info:
                await dependency(mock_request)
            
            detail = exc_info.value.detail
            assert "error" in detail
            assert detail["error"]["code"] == "RATE_LIMITED"
            assert "message" in detail["error"]
    
    @pytest.mark.asyncio
    async def test_uses_forwarded_ip(self, mock_request):
        """Should use X-Forwarded-For header for IP."""
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
            limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
            dependency = RateLimitDependency(lambda: limiter, "test")
            
            # Request with forwarded IP
            mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 10.0.0.2"}
            await dependency(mock_request)
            
            # Different forwarded IP should have separate limit
            mock_request.headers = {"X-Forwarded-For": "10.0.0.99"}
            await dependency(mock_request)  # Should not raise


# ============================================================================
# TEST: INTEGRATION WITH FASTAPI
# ============================================================================

class TestFastAPIIntegration:
    """Test rate limiting in actual FastAPI app."""
    
    def test_login_endpoint_returns_429(self):
        """Login endpoint should return 429 when rate limited."""
        from fastapi import FastAPI, Request, Depends
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
        rate_limit = RateLimitDependency(lambda: limiter, "login")
        
        @app.post("/login")
        async def login(request: Request, _: None = Depends(rate_limit)):
            return {"status": "ok"}
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
            client = TestClient(app)
            
            # First two should succeed
            assert client.post("/login").status_code == 200
            assert client.post("/login").status_code == 200
            
            # Third should be rate limited
            response = client.post("/login")
            assert response.status_code == 429
            
            data = response.json()
            assert data["detail"]["error"]["code"] == "RATE_LIMITED"
    
    def test_rate_limit_disabled_in_dev(self):
        """Rate limiting should be disabled in dev mode."""
        from fastapi import FastAPI, Request, Depends
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
        rate_limit = RateLimitDependency(lambda: limiter, "login")
        
        @app.post("/login")
        async def login(request: Request, _: None = Depends(rate_limit)):
            return {"status": "ok"}
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "false"}):
            client = TestClient(app)
            
            # All requests should succeed even though limit is 1
            for _ in range(10):
                assert client.post("/login").status_code == 200


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
