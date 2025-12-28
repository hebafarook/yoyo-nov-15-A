"""Unit tests for auth service business logic."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from services.auth_service import AuthService
from domain.models import UserCreate, UserLogin, User


@pytest.fixture
def mock_user_repo():
    """Mock user repository."""
    repo = Mock()
    repo.is_email_taken = AsyncMock(return_value=False)
    repo.is_username_taken = AsyncMock(return_value=False)
    repo.create = AsyncMock(return_value={
        'id': 'user123',
        'username': 'testuser',
        'email': 'test@example.com',
        'full_name': 'Test User',
        'role': 'player',
        'hashed_password': 'hashed',
        'is_active': True,
        'is_coach': False
    })
    repo.find_by_email = AsyncMock(return_value=None)
    repo.find_by_id = AsyncMock(return_value={
        'id': 'user123',
        'username': 'testuser',
        'email': 'test@example.com',
        'full_name': 'Test User',
        'role': 'player',
        'hashed_password': 'hashed',
        'is_active': True
    })
    repo.update_last_login = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def mock_profile_repo():
    """Mock profile repository."""
    repo = Mock()
    repo.create_default_profile = AsyncMock(return_value={
        'user_id': 'user123',
        'players_managed': [],
        'saved_reports': [],
        'benchmarks': []
    })
    repo.find_by_user_id = AsyncMock(return_value={
        'user_id': 'user123',
        'players_managed': [],
        'saved_reports': []
    })
    return repo


@pytest.fixture
def auth_service(mock_user_repo, mock_profile_repo):
    """Auth service with mocked repositories."""
    service = AuthService()
    service.user_repo = mock_user_repo
    service.profile_repo = mock_profile_repo
    service.parent_relationship_repo = Mock()
    service.parent_relationship_repo.create = AsyncMock()
    service.coach_relationship_repo = Mock()
    service.coach_relationship_repo.create = AsyncMock()
    service.invitation_repo = Mock()
    service.invitation_repo.create = AsyncMock()
    service.invitation_repo.find_pending_by_email = AsyncMock(return_value=[])
    return service


@pytest.mark.unit
class TestAuthService:
    """Test auth service business logic."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_user_repo, mock_profile_repo):
        """Test successful user registration."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="password123",
            role="player"
        )
        
        user, token = await auth_service.register_user(user_data)
        
        # Verify user was created
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert token is not None
        assert len(token) > 0
        
        # Verify repositories were called
        mock_user_repo.is_email_taken.assert_called_once_with("test@example.com")
        mock_user_repo.is_username_taken.assert_called_once_with("testuser")
        mock_user_repo.create.assert_called_once()
        mock_profile_repo.create_default_profile.assert_called_once_with('user123')
    
    @pytest.mark.asyncio
    async def test_register_user_email_taken(self, auth_service, mock_user_repo):
        """Test registration fails when email is taken."""
        mock_user_repo.is_email_taken.return_value = True
        
        user_data = UserCreate(
            username="testuser",
            email="existing@example.com",
            full_name="Test User",
            password="password123",
            role="player"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "email already registered" in exc_info.value.detail.lower()
        mock_user_repo.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_register_user_username_taken(self, auth_service, mock_user_repo):
        """Test registration fails when username is taken."""
        mock_user_repo.is_username_taken.return_value = True
        
        user_data = UserCreate(
            username="existinguser",
            email="test@example.com",
            full_name="Test User",
            password="password123",
            role="player"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "username already taken" in exc_info.value.detail.lower()
        mock_user_repo.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, auth_service, mock_user_repo):
        """Test successful user login."""
        # Setup mock to return user with hashed password
        hashed_password = auth_service.hash_password("password123")
        mock_user_repo.find_by_email.return_value = {
            'id': 'user123',
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'role': 'player',
            'hashed_password': hashed_password,
            'is_active': True
        }
        
        credentials = UserLogin(
            email="test@example.com",
            password="password123"
        )
        
        user, token = await auth_service.login_user(credentials)
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert token is not None
        mock_user_repo.update_last_login.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service, mock_user_repo):
        """Test login fails when user not found."""
        mock_user_repo.find_by_email.return_value = None
        
        credentials = UserLogin(
            email="notfound@example.com",
            password="password123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "invalid email or password" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_login_user_wrong_password(self, auth_service, mock_user_repo):
        """Test login fails with wrong password."""
        mock_user_repo.find_by_email.return_value = {
            'id': 'user123',
            'username': 'testuser',
            'email': 'test@example.com',
            'hashed_password': auth_service.hash_password("correctpassword"),
            'role': 'player'
        }
        
        credentials = UserLogin(
            email="test@example.com",
            password="wrongpassword"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "invalid email or password" in exc_info.value.detail.lower()
    
    def test_hash_password(self, auth_service):
        """Test password hashing is consistent."""
        password = "testpassword123"
        hash1 = auth_service.hash_password(password)
        hash2 = auth_service.hash_password(password)
        
        # Same password should produce same hash
        assert hash1 == hash2
        # Hash should be hex string
        assert len(hash1) == 64  # SHA256 produces 64 char hex
    
    def test_verify_password(self, auth_service):
        """Test password verification."""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        # Correct password should verify
        assert auth_service.verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert auth_service.verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self, auth_service):
        """Test JWT token creation."""
        token = auth_service.create_access_token(
            user_id="user123",
            username="testuser",
            role="player"
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self, auth_service):
        """Test verifying a valid token."""
        token = auth_service.create_access_token(
            user_id="user123",
            username="testuser",
            role="player"
        )
        
        payload = auth_service.verify_token(token)
        
        assert payload['user_id'] == "user123"
        assert payload['username'] == "testuser"
        assert payload['role'] == "player"
    
    def test_verify_token_invalid(self, auth_service):
        """Test verifying an invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
        assert "invalid token" in exc_info.value.detail.lower()
