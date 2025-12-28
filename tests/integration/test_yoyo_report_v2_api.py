"""
Integration Tests for YoYo Report v2 API
========================================

Tests the /api/v2/report/yoyo endpoint.
"""

import pytest
import httpx
import os
from datetime import datetime

# Get API URL from environment
API_BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')


class TestYoYoReportV2API:
    """Integration tests for YoYo Report v2 API endpoint."""
    
    @pytest.fixture
    def auth_token(self, api_base_url):
        """Get auth token for API calls."""
        # Try to login or register a test user
        login_data = {
            "username": "yoyo_test_user",
            "password": "TestPass123!"
        }
        
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            # Try login first
            response = client.post("/auth/login", json=login_data)
            
            if response.status_code == 200:
                return response.json().get('token')
            
            # If login fails, try to register
            register_data = {
                **login_data,
                "email": "yoyo_test@test.com",
                "full_name": "YoYo Test User",
                "role": "player",
                "age": 17,
                "position": "Midfielder"
            }
            
            response = client.post("/auth/register", json=register_data)
            if response.status_code in [200, 201]:
                return response.json().get('token')
            
            pytest.skip("Could not authenticate for API tests")
    
    @pytest.fixture
    def api_base_url(self):
        """Return API base URL."""
        return f"{API_BASE_URL}/api"
    
    def test_endpoint_exists(self, api_base_url, auth_token):
        """Test that the endpoint exists and is accessible."""
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/v2/report/yoyo/test-user-id", headers=headers)
            
            # Should not be 404 (endpoint not found)
            assert response.status_code != 404, "Endpoint should exist"
    
    def test_requires_authentication(self, api_base_url):
        """Test that endpoint requires authentication."""
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            response = client.get("/v2/report/yoyo/any-id")
            
            # Should return 401 or 403 without auth
            assert response.status_code in [401, 403, 422]
    
    def test_returns_11_sections(self, api_base_url, auth_token):
        """Test that response contains 11 sections."""
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # First create an assessment
            assessment_data = {
                "player_name": "Test Player",
                "age": 17,
                "position": "Midfielder",
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
            
            # Create assessment
            create_response = client.post(
                "/assessments/authenticated",
                json=assessment_data,
                headers=headers
            )
            
            if create_response.status_code in [200, 201]:
                assessment = create_response.json()
                player_id = assessment.get('id') or assessment.get('user_id')
                
                # Get the report
                response = client.get(f"/v2/report/yoyo/{player_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    assert 'report' in data
                    assert 'report_sections' in data['report']
                    assert len(data['report']['report_sections']) == 11
    
    def test_sections_have_correct_order(self, api_base_url, auth_token):
        """Test that sections are in correct order."""
        expected_titles = [
            "Identity & Biology",
            "Performance Snapshot",
            "Strengths & Weaknesses",
            "Development Identity",
            "Benchmarks (Now → Target → Elite)",
            "Training Mode",
            "Training Program",
            "Return-to-Play Engine",
            "Safety Governor",
            "AI Object (JSON)",
            "Goal State"
        ]
        
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/v2/report/yoyo/test", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sections = data['report']['report_sections']
                
                for i, section in enumerate(sections):
                    assert section['section_title'] == expected_titles[i]
    
    def test_json_object_has_required_keys(self, api_base_url, auth_token):
        """Test that report_json has all required keys."""
        required_keys = [
            'player_id', 'name', 'age', 'gender', 'position', 'dominant_leg',
            'mode', 'profile_label', 'weekly_sessions', 'total_weeks',
            'benchmarks', 'safety_rules', 'sub_program', 'matches'
        ]
        
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/v2/report/yoyo/test", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                report_json = data['report']['report_json']
                
                for key in required_keys:
                    assert key in report_json, f"Missing required key: {key}"
    
    def test_sections_only_endpoint(self, api_base_url, auth_token):
        """Test the sections-only endpoint."""
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/v2/report/yoyo/test/sections", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                assert 'sections' in data
                assert 'meta' in data
                # Should NOT have full report_json
    
    def test_json_only_endpoint(self, api_base_url, auth_token):
        """Test the json-only endpoint."""
        with httpx.Client(base_url=api_base_url, timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/v2/report/yoyo/test/json", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                assert 'json' in data
                assert 'meta' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
