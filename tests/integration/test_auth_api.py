"""Integration tests for authentication API endpoints."""

import pytest
import httpx
import os
from datetime import datetime


@pytest.fixture(scope="module")
def api_url():
    """Get API URL from environment or use default."""
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    return f"{backend_url}/api"


@pytest.fixture
def unique_user_data():
    """Generate unique user data for each test."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "full_name": "Test User",
        "password": "testpass123",
        "role": "player",
        "age": 17,
        "position": "Forward"
    }


@pytest.mark.integration
@pytest.mark.backend
class TestAuthAPIIntegration:
    """Integration tests for auth API."""
    
    @pytest.mark.asyncio
    async def test_register_endpoint(self, api_url, unique_user_data):
        """Test user registration endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_url}/auth-v2/register",
                json=unique_user_data,
                timeout=30.0
            )
            
            # Assert response
            assert response.status_code == 201
            data = response.json()
            
            # Verify response structure
            assert "user" in data
            assert "token" in data
            assert "message" in data
            
            # Verify user data
            user = data["user"]
            assert user["username"] == unique_user_data["username"]
            assert user["email"] == unique_user_data["email"]
            assert user["role"] == unique_user_data["role"]
            assert "hashed_password" not in user  # Should not expose password
            
            # Verify token exists
            assert len(data["token"]) > 0
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, api_url, unique_user_data):
        """Test registration fails with duplicate email."""
        async with httpx.AsyncClient() as client:
            # Register first user
            response1 = await client.post(
                f"{api_url}/auth-v2/register",
                json=unique_user_data,
                timeout=30.0
            )
            assert response1.status_code == 201
            
            # Try to register again with same email
            duplicate_user = unique_user_data.copy()
            duplicate_user["username"] = "different_username"
            
            response2 = await client.post(
                f"{api_url}/auth-v2/register",
                json=duplicate_user,
                timeout=30.0
            )
            
            # Should fail with 400
            assert response2.status_code == 400
            error = response2.json()
            assert "email" in error["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_endpoint(self, api_url, unique_user_data):
        """Test user login endpoint."""
        async with httpx.AsyncClient() as client:
            # First register a user
            register_response = await client.post(
                f"{api_url}/auth-v2/register",
                json=unique_user_data,
                timeout=30.0
            )
            assert register_response.status_code == 201
            
            # Now login
            login_data = {
                "email": unique_user_data["email"],
                "password": unique_user_data["password"]
            }
            
            login_response = await client.post(
                f"{api_url}/auth-v2/login",
                json=login_data,
                timeout=30.0
            )
            
            # Assert login successful
            assert login_response.status_code == 200
            data = login_response.json()
            
            # Verify response structure
            assert "user" in data
            assert "token" in data
            assert "message" in data
            
            # Verify user data
            user = data["user"]
            assert user["email"] == unique_user_data["email"]
            assert "hashed_password" not in user
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, api_url, unique_user_data):
        """Test login fails with wrong password."""
        async with httpx.AsyncClient() as client:
            # First register a user
            register_response = await client.post(
                f"{api_url}/auth-v2/register",
                json=unique_user_data,
                timeout=30.0
            )
            assert register_response.status_code == 201
            
            # Try to login with wrong password
            login_data = {
                "email": unique_user_data["email"],
                "password": "wrongpassword123"
            }
            
            login_response = await client.post(
                f"{api_url}/auth-v2/login",
                json=login_data,
                timeout=30.0
            )
            
            # Should fail with 401
            assert login_response.status_code == 401
            error = login_response.json()
            assert "invalid" in error["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, api_url):
        """Test login fails for non-existent user."""
        async with httpx.AsyncClient() as client:
            login_data = {
                "email": "nonexistent@example.com",
                "password": "password123"
            }
            
            login_response = await client.post(
                f"{api_url}/auth-v2/login",
                json=login_data,
                timeout=30.0
            )
            
            # Should fail with 401
            assert login_response.status_code == 401
            error = login_response.json()
            assert "invalid" in error["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_profile_endpoint_with_token(self, api_url, unique_user_data):
        """Test getting user profile with valid token."""
        async with httpx.AsyncClient() as client:
            # Register and get token
            register_response = await client.post(
                f"{api_url}/auth-v2/register",
                json=unique_user_data,
                timeout=30.0
            )
            assert register_response.status_code == 201
            token = register_response.json()["token"]
            
            # Get profile with token
            profile_response = await client.get(
                f"{api_url}/auth-v2/profile",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            
            # Assert success
            assert profile_response.status_code == 200
            data = profile_response.json()
            
            # Verify response structure
            assert "user" in data
            assert "profile" in data
            
            # Verify user data
            user = data["user"]
            assert user["email"] == unique_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_profile_endpoint_without_token(self, api_url):
        """Test profile endpoint fails without token."""
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(
                f"{api_url}/auth-v2/profile",
                timeout=30.0
            )
            
            # Should fail with 403 (no credentials) or 401 (invalid credentials)
            assert profile_response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_profile_endpoint_invalid_token(self, api_url):
        """Test profile endpoint fails with invalid token."""
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(
                f"{api_url}/auth-v2/profile",
                headers={"Authorization": "Bearer invalid.token.here"},
                timeout=30.0
            )
            
            # Should fail with 401
            assert profile_response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_benchmarks_endpoint(self, api_url, unique_user_data):
        """Test getting user benchmarks."""
        async with httpx.AsyncClient() as client:
            # Register and get token
            register_response = await client.post(
                f"{api_url}/auth-v2/register",
                json=unique_user_data,
                timeout=30.0
            )
            token = register_response.json()["token"]
            
            # Get benchmarks
            benchmarks_response = await client.get(
                f"{api_url}/auth-v2/benchmarks",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            
            # Should return empty list for new user
            assert benchmarks_response.status_code == 200
            benchmarks = benchmarks_response.json()
            assert isinstance(benchmarks, list)
            # New user should have no benchmarks
            assert len(benchmarks) == 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, api_url):
        """Test health check endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{api_url}/auth-v2/health",
                timeout=30.0
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "auth"
