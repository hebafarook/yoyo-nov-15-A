"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os
from pathlib import Path
from typing import Generator
import asyncio

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


# Event loop configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def backend_url():
    """Backend URL for API tests."""
    return os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')


@pytest.fixture(scope="session")
def api_base_url(backend_url):
    """API base URL."""
    return f"{backend_url}/api"


@pytest.fixture
def test_user_data():
    """Test user data for authentication tests."""
    return {
        "username": "pytest_user",
        "email": "pytest@test.com",
        "password": "PytestPass123!",
        "full_name": "Pytest Test User",
        "role": "player",
        "age": 17,
        "position": "Forward"
    }


@pytest.fixture
def sample_assessment_data():
    """Sample assessment data for testing."""
    return {
        "player_name": "Test Player",
        "age": 17,
        "position": "Midfielder",
        "gender": "male",
        "height_cm": 175,
        "weight_kg": 68,
        "sprint_30m": 4.2,
        "yo_yo_test": 1800,
        "vo2_max": 58.0,
        "vertical_jump": 55,
        "body_fat": 10.5,
        "ball_control": 4,
        "passing_accuracy": 82,
        "dribbling_success": 78,
        "shooting_accuracy": 75,
        "defensive_duels": 80,
        "game_intelligence": 4,
        "positioning": 4,
        "decision_making": 4,
        "coachability": 5,
        "mental_toughness": 4
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing AI features."""
    return {
        "insights": [
            "Player shows strong technical skills",
            "Physical conditioning needs improvement",
            "Excellent tactical awareness"
        ],
        "recommendations": [
            "Focus on speed training",
            "Continue technical skill development",
            "Maintain tactical training"
        ],
        "motivation": "Keep pushing forward! Your progress is impressive."
    }


# Utility functions for tests
def assert_valid_token(token: str):
    """Assert that a token is valid format."""
    assert isinstance(token, str)
    assert len(token) > 0
    # JWT tokens have 3 parts separated by dots
    parts = token.split('.')
    assert len(parts) == 3


def assert_valid_user_response(user_data: dict):
    """Assert that user response has expected structure."""
    assert "id" in user_data or "user_id" in user_data
    assert "username" in user_data
    assert "email" in user_data
    assert "role" in user_data
    # Should not expose sensitive data
    assert "password" not in user_data
    assert "hashed_password" not in user_data


def assert_valid_assessment(assessment: dict):
    """Assert that assessment has expected structure."""
    required_fields = [
        "player_name", "age", "position",
        "sprint_30m", "ball_control", "game_intelligence"
    ]
    for field in required_fields:
        assert field in assessment, f"Missing required field: {field}"
