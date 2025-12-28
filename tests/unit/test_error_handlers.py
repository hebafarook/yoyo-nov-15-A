"""
Tests for Central Error Handling
================================

Verifies standardized error response format.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel

from utils.error_handlers import register_exception_handlers


# ============================================================================
# TEST APP SETUP
# ============================================================================

def create_test_app() -> FastAPI:
    """Create a minimal test app with error handlers."""
    app = FastAPI()
    register_exception_handlers(app)
    
    class TestInput(BaseModel):
        name: str
        age: int
    
    @app.get("/test/ok")
    def test_ok():
        return {"status": "ok"}
    
    @app.post("/test/validate")
    def test_validate(data: TestInput):
        return {"received": data.dict()}
    
    @app.get("/test/not-found")
    def test_not_found():
        raise HTTPException(status_code=404, detail="Resource not found")
    
    @app.get("/test/unauthorized")
    def test_unauthorized():
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    @app.get("/test/forbidden")
    def test_forbidden():
        raise HTTPException(status_code=403, detail="Access denied")
    
    @app.get("/test/internal-error")
    def test_internal_error():
        raise RuntimeError("Simulated internal error")
    
    return app


@pytest.fixture
def client():
    """Test client fixture."""
    app = create_test_app()
    return TestClient(app, raise_server_exceptions=False)


# ============================================================================
# TEST: ERROR RESPONSE SCHEMA
# ============================================================================

class TestErrorResponseSchema:
    """Test that all errors follow the standard schema."""
    
    def test_error_has_correct_structure(self, client):
        """Error response should have { error: { code, message } }."""
        response = client.get("/test/not-found")
        data = response.json()
        
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
    
    def test_successful_response_unchanged(self, client):
        """Successful responses should NOT be modified."""
        response = client.get("/test/ok")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


# ============================================================================
# TEST: VALIDATION ERRORS (422)
# ============================================================================

class TestValidationErrors:
    """Test RequestValidationError handling."""
    
    def test_validation_error_returns_422(self, client):
        """Validation errors should return 422."""
        response = client.post("/test/validate", json={"name": "test"})
        # Missing required field 'age'
        
        assert response.status_code == 422
    
    def test_validation_error_has_standard_format(self, client):
        """Validation error should have standard error format."""
        response = client.post("/test/validate", json={"name": "test"})
        data = response.json()
        
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "message" in data["error"]
        assert len(data["error"]["message"]) > 0
    
    def test_validation_error_wrong_type(self, client):
        """Wrong type should return validation error."""
        response = client.post("/test/validate", json={"name": "test", "age": "not-a-number"})
        
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ============================================================================
# TEST: HTTP EXCEPTIONS (404, 401, 403, etc.)
# ============================================================================

class TestHTTPExceptions:
    """Test HTTPException handling."""
    
    def test_404_returns_correct_status(self, client):
        """404 should preserve status code."""
        response = client.get("/test/not-found")
        
        assert response.status_code == 404
    
    def test_404_has_standard_format(self, client):
        """404 should have standard error format."""
        response = client.get("/test/not-found")
        data = response.json()
        
        assert data["error"]["code"] == "NOT_FOUND"
        assert "not found" in data["error"]["message"].lower()
    
    def test_401_returns_correct_status(self, client):
        """401 should preserve status code."""
        response = client.get("/test/unauthorized")
        
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"
    
    def test_403_returns_correct_status(self, client):
        """403 should preserve status code."""
        response = client.get("/test/forbidden")
        
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"


# ============================================================================
# TEST: UNHANDLED EXCEPTIONS (500)
# ============================================================================

class TestUnhandledExceptions:
    """Test unhandled exception handling."""
    
    def test_internal_error_returns_500(self, client):
        """Unhandled exceptions should return 500."""
        response = client.get("/test/internal-error")
        
        assert response.status_code == 500
    
    def test_internal_error_has_standard_format(self, client):
        """500 should have standard error format."""
        response = client.get("/test/internal-error")
        data = response.json()
        
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert "internal" in data["error"]["message"].lower()
    
    def test_internal_error_does_not_leak_details(self, client):
        """500 should NOT expose internal error details."""
        response = client.get("/test/internal-error")
        data = response.json()
        
        # Should NOT contain the actual error message
        assert "Simulated" not in data["error"]["message"]
        assert "RuntimeError" not in data["error"]["message"]
        assert "traceback" not in str(data).lower()


# ============================================================================
# TEST: NON-EXISTENT ROUTES
# ============================================================================

class TestNonExistentRoutes:
    """Test handling of non-existent routes."""
    
    def test_unknown_route_returns_404(self, client):
        """Non-existent routes should return 404."""
        response = client.get("/this/route/does/not/exist")
        
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
