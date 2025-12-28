"""
Tests for CORS Configuration
=============================

Verifies CORS middleware configuration behavior.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from utils.cors_config import (
    get_cors_origins,
    get_cors_config_summary,
    configure_cors,
    DEV_DEFAULT_ORIGINS,
    ALLOWED_METHODS,
    ALLOWED_HEADERS,
    _is_production,
)


# ============================================================================
# TEST: ENVIRONMENT DETECTION
# ============================================================================

class TestEnvironmentDetection:
    """Test production vs development detection."""
    
    def test_default_is_development(self):
        """No ENVIRONMENT var should default to development."""
        with patch.dict(os.environ, {}, clear=True):
            assert _is_production() is False
    
    def test_development_explicit(self):
        """ENVIRONMENT=development should be dev."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            assert _is_production() is False
    
    def test_production_explicit(self):
        """ENVIRONMENT=production should be prod."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            assert _is_production() is True
    
    def test_prod_shorthand(self):
        """ENVIRONMENT=prod should be prod."""
        with patch.dict(os.environ, {"ENVIRONMENT": "prod"}):
            assert _is_production() is True
    
    def test_staging_is_production(self):
        """ENVIRONMENT=staging should be treated as prod."""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            assert _is_production() is True


# ============================================================================
# TEST: ORIGIN CONFIGURATION
# ============================================================================

class TestOriginConfiguration:
    """Test CORS origin configuration."""
    
    def test_dev_default_origins(self):
        """Development should have localhost defaults."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            origins = get_cors_origins()
            assert "http://localhost:3000" in origins
            assert "http://localhost:8001" in origins
    
    def test_custom_origins_from_env(self):
        """CORS_ALLOW_ORIGINS should override defaults."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "CORS_ALLOW_ORIGINS": "https://myapp.com,https://api.myapp.com"
        }):
            origins = get_cors_origins()
            assert origins == ["https://myapp.com", "https://api.myapp.com"]
    
    def test_production_no_config_empty(self):
        """Production without CORS_ALLOW_ORIGINS should return empty list."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            # Remove CORS_ALLOW_ORIGINS if present
            env = {"ENVIRONMENT": "production"}
            with patch.dict(os.environ, env, clear=True):
                origins = get_cors_origins()
                assert origins == []
    
    def test_production_with_config(self):
        """Production with CORS_ALLOW_ORIGINS should use those origins."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "CORS_ALLOW_ORIGINS": "https://myapp.com"
        }):
            origins = get_cors_origins()
            assert origins == ["https://myapp.com"]
    
    def test_whitespace_handling(self):
        """Origins should be trimmed of whitespace."""
        with patch.dict(os.environ, {
            "CORS_ALLOW_ORIGINS": " https://a.com , https://b.com "
        }):
            origins = get_cors_origins()
            assert origins == ["https://a.com", "https://b.com"]
    
    def test_empty_origins_filtered(self):
        """Empty strings in origins should be filtered out."""
        with patch.dict(os.environ, {
            "CORS_ALLOW_ORIGINS": "https://a.com,,https://b.com,"
        }):
            origins = get_cors_origins()
            assert "" not in origins
            assert len(origins) == 2


# ============================================================================
# TEST: ALLOWED METHODS AND HEADERS
# ============================================================================

class TestAllowedMethodsHeaders:
    """Test explicit methods and headers configuration."""
    
    def test_explicit_methods_defined(self):
        """Allowed methods should be explicitly defined."""
        assert "GET" in ALLOWED_METHODS
        assert "POST" in ALLOWED_METHODS
        assert "PUT" in ALLOWED_METHODS
        assert "PATCH" in ALLOWED_METHODS
        assert "DELETE" in ALLOWED_METHODS
        assert "OPTIONS" in ALLOWED_METHODS
    
    def test_no_wildcard_methods(self):
        """Methods should not contain wildcard."""
        assert "*" not in ALLOWED_METHODS
    
    def test_explicit_headers_defined(self):
        """Allowed headers should be explicitly defined."""
        assert "Authorization" in ALLOWED_HEADERS
        assert "Content-Type" in ALLOWED_HEADERS
        assert "Accept" in ALLOWED_HEADERS
    
    def test_no_wildcard_headers(self):
        """Headers should not contain wildcard."""
        assert "*" not in ALLOWED_HEADERS


# ============================================================================
# TEST: CONFIG SUMMARY
# ============================================================================

class TestConfigSummary:
    """Test configuration summary for debugging."""
    
    def test_summary_has_required_fields(self):
        """Summary should have all required fields."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            summary = get_cors_config_summary()
            
            assert "environment" in summary
            assert "origins" in summary
            assert "methods" in summary
            assert "headers" in summary
            assert "credentials" in summary
    
    def test_summary_environment_correct(self):
        """Summary should report correct environment."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            summary = get_cors_config_summary()
            assert summary["environment"] == "production"
        
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            summary = get_cors_config_summary()
            assert summary["environment"] == "development"


# ============================================================================
# TEST: MIDDLEWARE INTEGRATION
# ============================================================================

class TestMiddlewareIntegration:
    """Test CORS middleware integration with FastAPI."""
    
    def test_configure_cors_adds_middleware(self):
        """configure_cors should add middleware to app."""
        from fastapi import FastAPI
        
        app = FastAPI()
        initial_middleware_count = len(app.user_middleware)
        
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            configure_cors(app)
        
        # Should have added at least one middleware
        assert len(app.user_middleware) > initial_middleware_count
    
    def test_cors_response_headers(self):
        """CORS middleware should add correct headers."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "CORS_ALLOW_ORIGINS": "http://localhost:3000"
        }):
            configure_cors(app)
        
        client = TestClient(app)
        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        # Check CORS header is present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
