"""
Tests for Rate Limiting
=======================

Verifies rate limiting behavior on auth endpoints.
Includes tests for both InMemory and Redis backends.
"""

import pytest
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from utils.rate_limiter import (
    InMemoryStore,
    RedisStore,
    RateLimiter,
    RateLimitDependency,
    _is_rate_limit_enabled,
    get_rate_limit_config,
    get_store,
    get_store_type,
    reset_store,
    set_store_for_testing,
    get_login_limiter,
    reinitialize_limiters,
)


# ============================================================================
# TEST: IN-MEMORY STORE
# ============================================================================

class TestInMemoryStore:
    """Test the in-memory storage backend."""
    
    def test_allows_requests_under_limit(self):
        """Requests under limit should be allowed."""
        store = InMemoryStore()
        
        for i in range(5):
            allowed, remaining, _ = store.is_allowed("test-key", max_requests=5, window_seconds=60)
            assert allowed is True
            assert remaining == 4 - i
    
    def test_blocks_requests_over_limit(self):
        """Requests over limit should be blocked."""
        store = InMemoryStore()
        
        # Use up the limit
        for _ in range(3):
            store.is_allowed("test-key", max_requests=3, window_seconds=60)
        
        # Next request should be blocked
        allowed, remaining, reset_after = store.is_allowed("test-key", max_requests=3, window_seconds=60)
        assert allowed is False
        assert remaining == 0
        assert reset_after > 0
    
    def test_different_keys_independent(self):
        """Different keys should have independent limits."""
        store = InMemoryStore()
        
        # Exhaust limit for key1
        store.is_allowed("key1", max_requests=2, window_seconds=60)
        store.is_allowed("key1", max_requests=2, window_seconds=60)
        allowed1, _, _ = store.is_allowed("key1", max_requests=2, window_seconds=60)
        
        # key2 should still be allowed
        allowed2, _, _ = store.is_allowed("key2", max_requests=2, window_seconds=60)
        
        assert allowed1 is False
        assert allowed2 is True
    
    def test_window_expiration(self):
        """Requests should be allowed after window expires."""
        store = InMemoryStore()
        
        # Use up the limit
        store.is_allowed("test-key", max_requests=1, window_seconds=1)
        allowed1, _, _ = store.is_allowed("test-key", max_requests=1, window_seconds=1)
        assert allowed1 is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        allowed2, _, _ = store.is_allowed("test-key", max_requests=1, window_seconds=1)
        assert allowed2 is True
    
    def test_reset_key(self):
        """Reset should clear limit for specific key."""
        store = InMemoryStore()
        
        store.is_allowed("test-key", max_requests=1, window_seconds=60)
        allowed1, _, _ = store.is_allowed("test-key", max_requests=1, window_seconds=60)
        assert allowed1 is False
        
        store.reset("test-key")
        
        allowed2, _, _ = store.is_allowed("test-key", max_requests=1, window_seconds=60)
        assert allowed2 is True
    
    def test_reset_all(self):
        """Reset all should clear all limits."""
        store = InMemoryStore()
        
        store.is_allowed("key1", max_requests=1, window_seconds=60)
        store.is_allowed("key2", max_requests=1, window_seconds=60)
        
        store.reset_all()
        
        allowed1, _, _ = store.is_allowed("key1", max_requests=1, window_seconds=60)
        allowed2, _, _ = store.is_allowed("key2", max_requests=1, window_seconds=60)
        assert allowed1 is True
        assert allowed2 is True


# ============================================================================
# TEST: REDIS STORE (Mocked)
# ============================================================================

class TestRedisStore:
    """Test the Redis storage backend with mocked client."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        mock = MagicMock()
        mock.incr.return_value = 1
        mock.ttl.return_value = 60
        mock.expire.return_value = True
        mock.keys.return_value = []
        mock.delete.return_value = 0
        return mock
    
    def test_allows_first_request(self, mock_redis):
        """First request should be allowed and set expiry."""
        store = RedisStore(mock_redis)
        mock_redis.incr.return_value = 1
        
        allowed, remaining, _ = store.is_allowed("test", max_requests=10, window_seconds=60)
        
        assert allowed is True
        assert remaining == 9
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()
    
    def test_blocks_over_limit(self, mock_redis):
        """Requests over limit should be blocked."""
        store = RedisStore(mock_redis)
        mock_redis.incr.return_value = 11  # Over limit of 10
        mock_redis.ttl.return_value = 45
        
        allowed, remaining, reset_after = store.is_allowed("test", max_requests=10, window_seconds=60)
        
        assert allowed is False
        assert remaining == 0
        assert reset_after == 45
    
    def test_remaining_count_correct(self, mock_redis):
        """Remaining count should be calculated correctly."""
        store = RedisStore(mock_redis)
        mock_redis.incr.return_value = 3  # 3rd request of 10
        mock_redis.ttl.return_value = 50
        
        allowed, remaining, _ = store.is_allowed("test", max_requests=10, window_seconds=60)
        
        assert allowed is True
        assert remaining == 7  # 10 - 3 = 7
    
    def test_expire_only_on_first_request(self, mock_redis):
        """Expire should only be called when count is 1."""
        store = RedisStore(mock_redis)
        
        # First request
        mock_redis.incr.return_value = 1
        store.is_allowed("test", max_requests=10, window_seconds=60)
        assert mock_redis.expire.call_count == 1
        
        # Second request
        mock_redis.incr.return_value = 2
        store.is_allowed("test", max_requests=10, window_seconds=60)
        assert mock_redis.expire.call_count == 1  # Still 1, not called again
    
    def test_reset_deletes_keys(self, mock_redis):
        """Reset should delete matching keys."""
        store = RedisStore(mock_redis)
        mock_redis.keys.return_value = ["ratelimit:test:123", "ratelimit:test:124"]
        
        store.reset("test")
        
        mock_redis.keys.assert_called_once()
        mock_redis.delete.assert_called_once()
    
    def test_redis_error_raises(self, mock_redis):
        """Redis errors should be raised (to trigger fallback)."""
        store = RedisStore(mock_redis)
        mock_redis.incr.side_effect = Exception("Redis connection lost")
        
        with pytest.raises(Exception):
            store.is_allowed("test", max_requests=10, window_seconds=60)


# ============================================================================
# TEST: STORE SELECTION
# ============================================================================

class TestStoreSelection:
    """Test automatic store selection based on configuration."""
    
    def setup_method(self):
        """Reset store before each test."""
        reset_store()
        reinitialize_limiters()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_store()
        reinitialize_limiters()
    
    def test_memory_store_when_no_redis_url(self):
        """Should use in-memory store when RATE_LIMIT_REDIS_URL not set."""
        with patch.dict(os.environ, {}, clear=True):
            reset_store()
            store = get_store()
            assert isinstance(store, InMemoryStore)
            assert get_store_type() == "memory"
    
    def test_redis_store_when_url_set_and_valid(self):
        """Should use Redis store when URL is set and connection succeeds."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        
        with patch.dict(os.environ, {"RATE_LIMIT_REDIS_URL": "redis://localhost:6379/0"}):
            with patch("utils.rate_limiter._create_redis_client", return_value=mock_redis):
                reset_store()
                store = get_store()
                assert isinstance(store, RedisStore)
                assert get_store_type() == "redis"
    
    def test_fallback_to_memory_when_redis_fails(self):
        """Should fall back to in-memory when Redis connection fails."""
        with patch.dict(os.environ, {"RATE_LIMIT_REDIS_URL": "redis://invalid:6379/0"}):
            with patch("utils.rate_limiter._create_redis_client", return_value=None):
                reset_store()
                store = get_store()
                assert isinstance(store, InMemoryStore)
                assert get_store_type() == "memory"
    
    def test_config_shows_backend_type(self):
        """Config should show correct backend type."""
        with patch.dict(os.environ, {}, clear=True):
            reset_store()
            config = get_rate_limit_config()
            assert config["backend"] == "memory"
            assert config["redis_configured"] is False
        
        with patch.dict(os.environ, {"RATE_LIMIT_REDIS_URL": "redis://localhost:6379"}):
            config = get_rate_limit_config()
            assert config["redis_configured"] is True


# ============================================================================
# TEST: ENVIRONMENT CONFIGURATION
# ============================================================================

class TestRateLimitConfig:
    """Test environment-based configuration."""
    
    def test_disabled_in_development_by_default(self):
        """Rate limiting should be disabled in dev by default."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
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
        assert "backend" in config
        assert "redis_configured" in config
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
# TEST: RATE LIMITER CLASS
# ============================================================================

class TestRateLimiter:
    """Test the RateLimiter class."""
    
    def setup_method(self):
        """Reset store before each test."""
        reset_store()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_store()
    
    def test_uses_configured_store(self):
        """RateLimiter should use the configured store."""
        mock_store = MagicMock()
        mock_store.is_allowed.return_value = (True, 9, 60)
        set_store_for_testing(mock_store)
        
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        allowed, remaining, reset = limiter.is_allowed("test")
        
        assert allowed is True
        assert remaining == 9
        mock_store.is_allowed.assert_called_once_with("test", 10, 60)
    
    def test_fail_open_on_store_error(self):
        """Should allow request if store raises error (fail-open)."""
        mock_store = MagicMock()
        mock_store.is_allowed.side_effect = Exception("Store error")
        set_store_for_testing(mock_store)
        
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        allowed, remaining, reset = limiter.is_allowed("test")
        
        # Should allow (fail-open)
        assert allowed is True


# ============================================================================
# TEST: FASTAPI DEPENDENCY
# ============================================================================

class TestRateLimitDependency:
    """Test the FastAPI dependency."""
    
    def setup_method(self):
        """Reset store before each test."""
        reset_store()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_store()
    
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
            limiter = RateLimiter(max_requests=1, window_seconds=60)
            dependency = RateLimitDependency(lambda: limiter, "test")
            
            # Should not raise even after "exceeding" limit
            for _ in range(10):
                await dependency(mock_request)
    
    @pytest.mark.asyncio
    async def test_raises_429_when_exceeded(self, mock_request):
        """Should raise 429 when limit exceeded."""
        from fastapi import HTTPException
        
        # Use in-memory store for this test
        set_store_for_testing(InMemoryStore())
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
            limiter = RateLimiter(max_requests=2, window_seconds=60)
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
        
        set_store_for_testing(InMemoryStore())
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
            limiter = RateLimiter(max_requests=1, window_seconds=60)
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
        set_store_for_testing(InMemoryStore())
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "true"}):
            limiter = RateLimiter(max_requests=1, window_seconds=60)
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
    
    def setup_method(self):
        """Reset store before each test."""
        reset_store()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_store()
    
    def test_login_endpoint_returns_429(self):
        """Login endpoint should return 429 when rate limited."""
        from fastapi import FastAPI, Request, Depends
        from fastapi.testclient import TestClient
        
        set_store_for_testing(InMemoryStore())
        
        app = FastAPI()
        limiter = RateLimiter(max_requests=2, window_seconds=60)
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
        
        set_store_for_testing(InMemoryStore())
        
        app = FastAPI()
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        rate_limit = RateLimitDependency(lambda: limiter, "login")
        
        @app.post("/login")
        async def login(request: Request, _: None = Depends(rate_limit)):
            return {"status": "ok"}
        
        with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "false"}):
            client = TestClient(app)
            
            # All requests should succeed even though limit is 1
            for _ in range(10):
                assert client.post("/login").status_code == 200
    
    def test_with_redis_store_mock(self):
        """Test integration with mocked Redis store."""
        from fastapi import FastAPI, Request, Depends
        from fastapi.testclient import TestClient
        
        # Create mock Redis that tracks calls
        mock_redis = MagicMock()
        call_count = [0]
        
        def incr_side_effect(key):
            call_count[0] += 1
            return call_count[0]
        
        mock_redis.incr.side_effect = incr_side_effect
        mock_redis.ttl.return_value = 60
        mock_redis.expire.return_value = True
        
        redis_store = RedisStore(mock_redis)
        set_store_for_testing(redis_store)
        
        app = FastAPI()
        limiter = RateLimiter(max_requests=2, window_seconds=60)
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


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
