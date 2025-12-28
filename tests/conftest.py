"""Pytest configuration and fixtures for Yo-Yo Elite Soccer AI Coach tests."""

import pytest
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def backend_url():
    """Backend URL for API tests."""
    return "http://localhost:8001"


@pytest.fixture(scope="session")
def test_user_credentials():
    """Test user credentials for authentication tests."""
    return {
        "username": "pytest_user",
        "email": "pytest@test.com",
        "password": "PytestPass123!",
        "full_name": "Pytest Test User",
        "role": "player"
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
        "vo2_max": 58,
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
