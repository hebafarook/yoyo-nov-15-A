"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError
from domain.models import User, UserCreate, UserLogin, AssessmentBenchmark


@pytest.mark.unit
class TestUserModels:
    """Test user domain model validation."""
    
    def test_user_create_valid(self):
        """Test creating a valid user."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="password123",
            role="player"
        )
        assert user_data.username == "testuser"
        assert user_data.email == "test@example.com"
        assert user_data.role == "player"
    
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="invalid-email",
                full_name="Test User",
                password="password123",
                role="player"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_user_create_short_username(self):
        """Test user creation with username too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",  # Only 2 characters
                email="test@example.com",
                full_name="Test User",
                password="password123",
                role="player"
            )
        assert "username" in str(exc_info.value).lower()
    
    def test_user_create_invalid_username(self):
        """Test user creation with invalid characters in username."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="test-user!",  # Contains invalid characters
                email="test@example.com",
                full_name="Test User",
                password="password123",
                role="player"
            )
        assert "alphanumeric" in str(exc_info.value).lower()
    
    def test_user_create_short_password(self):
        """Test user creation with password too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                password="123",  # Only 3 characters
                role="player"
            )
        assert "password" in str(exc_info.value).lower()
    
    def test_user_create_invalid_role(self):
        """Test user creation with invalid role."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                password="password123",
                role="invalid_role"
            )
        assert "role" in str(exc_info.value).lower()
    
    def test_user_create_player_with_optional_fields(self):
        """Test creating player with optional fields."""
        user_data = UserCreate(
            username="playertest",
            email="player@example.com",
            full_name="Player Test",
            password="password123",
            role="player",
            age=17,
            position="Forward",
            gender="male",
            height="175cm",
            weight="68kg",
            dominant_foot="Right"
        )
        assert user_data.age == 17
        assert user_data.position == "Forward"
        assert user_data.dominant_foot == "Right"
    
    def test_user_create_player_invalid_age(self):
        """Test player creation with invalid age."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="playertest",
                email="player@example.com",
                full_name="Player Test",
                password="password123",
                role="player",
                age=5  # Too young
            )
        assert "age" in str(exc_info.value).lower()
    
    def test_user_login_valid(self):
        """Test valid login credentials."""
        login = UserLogin(
            email="test@example.com",
            password="password123"
        )
        assert login.email == "test@example.com"
        assert login.password == "password123"
    
    def test_user_login_invalid_email(self):
        """Test login with invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                email="not-an-email",
                password="password123"
            )
        assert "email" in str(exc_info.value).lower()


class TestAssessmentModels:
    """Test assessment domain model validation."""
    
    def test_assessment_create_valid(self):
        """Test creating a valid assessment."""
        assessment = AssessmentBenchmark(
            user_id="user123",
            player_name="Test Player",
            age=17,
            position="Midfielder",
            assessment_date="2024-01-01",
            sprint_30m=4.2,
            ball_control=4,
            game_intelligence=4
        )
        assert assessment.player_name == "Test Player"
        assert assessment.age == 17
        assert assessment.sprint_30m == 4.2
    
    def test_assessment_invalid_age(self):
        """Test assessment with invalid age."""
        with pytest.raises(ValidationError) as exc_info:
            AssessmentBenchmark(
                user_id="user123",
                player_name="Test Player",
                age=5,  # Too young
                position="Midfielder",
                assessment_date="2024-01-01"
            )
        assert "age" in str(exc_info.value).lower()
    
    def test_assessment_invalid_ball_control(self):
        """Test assessment with ball_control out of range."""
        with pytest.raises(ValidationError) as exc_info:
            AssessmentBenchmark(
                user_id="user123",
                player_name="Test Player",
                age=17,
                position="Midfielder",
                assessment_date="2024-01-01",
                ball_control=6  # Should be 1-5
            )
        assert "ball_control" in str(exc_info.value).lower()
    
    def test_assessment_invalid_body_fat(self):
        """Test assessment with body_fat out of range."""
        with pytest.raises(ValidationError) as exc_info:
            AssessmentBenchmark(
                user_id="user123",
                player_name="Test Player",
                age=17,
                position="Midfielder",
                assessment_date="2024-01-01",
                body_fat=150  # Should be 0-100
            )
        assert "body_fat" in str(exc_info.value).lower()
