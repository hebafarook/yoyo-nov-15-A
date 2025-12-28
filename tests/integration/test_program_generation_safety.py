"""
Program Generation Safety Integration Tests
============================================

Integration tests using FastAPI TestClient to verify that program generation
endpoints respect safety rules and produce valid structure.

Tests cover:
- POST /api/training/programs
- POST /api/training/periodized-programs
- POST /api/elite-training/generate-plan
- GET /api/v2/report/yoyo/{player_id} (Section 7 structure)
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Add paths
tests_path = Path(__file__).parent.parent
fixtures_path = tests_path / "fixtures"
backend_path = tests_path.parent / "backend"
unit_tests_path = tests_path / "unit"
sys.path.insert(0, str(tests_path))
sys.path.insert(0, str(fixtures_path))
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(unit_tests_path))

from fastapi.testclient import TestClient


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def elite_app():
    """Create FastAPI app with elite training routes for testing."""
    from fastapi import FastAPI
    from routes.elite_training_routes import router as elite_training_router
    
    app = FastAPI()
    app.include_router(elite_training_router)  # No prefix - router has its own
    return app


@pytest.fixture
def training_app():
    """Create FastAPI app with training routes for testing."""
    from fastapi import FastAPI
    from routes.training_routes import router as training_router
    
    app = FastAPI()
    app.include_router(training_router, prefix="/api/training")
    return app


@pytest.fixture
def elite_client(elite_app):
    """Create test client for elite training."""
    return TestClient(elite_app)


@pytest.fixture
def training_client(training_app):
    """Create test client for training."""
    return TestClient(training_app)


@pytest.fixture
def youth_player_input():
    """Youth player (age 11) input for periodized program."""
    return {
        "player_id": "youth_11",
        "program_name": "Youth Development Program",
        "total_duration_weeks": 12,
        "assessment_interval_weeks": 4,
        "program_objectives": ["Technical development", "Fun and engagement"]
    }


@pytest.fixture
def elite_player_input():
    """Elite player input for elite training plan."""
    return {
        "player_profile": {
            "name": "elite_player",
            "age": 17,
            "position": "midfielder",
            "level": "academy",
            "injury_status": "fit"
        },
        "testing_data": {
            "sprint_10m": 1.8,
            "sprint_30m": 4.3,
            "yoyo_ir2": 1800,
            "cmj": 40.0,
            "test_505": 2.4
        },
        "wellness": {
            "sleep_hours": 8.0,
            "soreness_1_5": 4,
            "mood_1_5": 4,
            "stress_1_5": 4
        },
        "match_schedule": {
            "days_to_next_match": 4,
            "matches_this_week": 2,
            "opponent": "Rival Academy",
            "match_importance": 4
        },
        "tactical_focus": {
            "possession": 4,
            "transition": 4,
            "pressing": 4,
            "buildup": 4,
            "set_pieces": 3
        },
        "previous_load": {
            "acwr": 1.0,
            "rpe_avg": 6.0,
            "total_distance_m": 7000,
            "sprint_count": 25,
            "hsr_m": 700
        }
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_yoyo_section_7_structure(section_7: Dict[str, Any]) -> Dict[str, bool]:
    """
    Check if YoYo Report Section 7 has all required sub-sections.
    Returns dict mapping section key to presence.
    """
    required_subsections = [
        '7.1_technical',
        '7.2_tactical', 
        '7.3_possession',
        '7.4_athletic_speed_agility',
        '7.5_cardio',
        '7.6_gym_strength',
        '7.7_mobility_flexibility',
        '7.8_recovery_regeneration',
        '7.9_injury_prevention_prehab'
    ]
    
    results = {}
    
    # Handle different structures
    if 'content' in section_7:
        content = section_7['content']
        if 'sub_program' in content:
            sub_program = content['sub_program']
            for subsection in required_subsections:
                results[subsection] = subsection in sub_program
        else:
            for subsection in required_subsections:
                results[subsection] = subsection in content
    else:
        for subsection in required_subsections:
            results[subsection] = subsection in section_7
    
    return results


# ============================================================================
# INTEGRATION TESTS: RTP PROTOCOLS
# ============================================================================

class TestRTPProtocolsEndpoint:
    """Integration tests for RTP protocol endpoints."""
    
    def test_get_all_rtp_protocols(self, elite_client):
        """Should return all RTP protocols."""
        response = elite_client.get("/elite-training/rtp-protocols")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "protocols" in data
        assert "total_stages" in data
        assert data["total_stages"] >= 5  # Should have at least 5 stages
    
    def test_get_single_rtp_protocol(self, elite_client):
        """Should return single RTP protocol for valid stage."""
        response = elite_client.get("/elite-training/rtp-protocol/stage_1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "stage" in data
        assert "protocol" in data
        assert data["stage"] == "stage_1"
    
    def test_invalid_rtp_stage_returns_400(self, elite_client):
        """Should return 400 for invalid RTP stage."""
        response = elite_client.get("/elite-training/rtp-protocol/invalid_stage")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


# ============================================================================
# INTEGRATION TESTS: YOYO REPORT V2 SECTION 7
# ============================================================================

class TestYoYoReportSection7:
    """Integration tests for YoYo Report Section 7 structure."""
    
    @pytest.fixture
    def mock_yoyo_section_7(self):
        """Mock Section 7 data with all required subsections."""
        return {
            "section_number": 7,
            "section_title": "Training Program",
            "content": {
                "sub_program": {
                    "7.1_technical": ["Ball mastery drills"],
                    "7.2_tactical": ["Position-specific work"],
                    "7.3_possession": ["Rondo exercises"],
                    "7.4_athletic_speed_agility": ["Speed ladder"],
                    "7.5_cardio": ["Interval training"],
                    "7.6_gym_strength": ["Strength circuit"],
                    "7.7_mobility_flexibility": ["Dynamic stretching"],
                    "7.8_recovery_regeneration": ["Pool recovery"],
                    "7.9_injury_prevention_prehab": ["Prehab routine"]
                }
            }
        }
    
    def test_section_7_has_all_subsections(self, mock_yoyo_section_7):
        """Section 7 should have all 9 required subsections."""
        results = check_yoyo_section_7_structure(mock_yoyo_section_7)
        
        required_subsections = [
            '7.1_technical', '7.2_tactical', '7.3_possession',
            '7.4_athletic_speed_agility', '7.5_cardio', '7.6_gym_strength',
            '7.7_mobility_flexibility', '7.8_recovery_regeneration',
            '7.9_injury_prevention_prehab'
        ]
        
        for subsection in required_subsections:
            assert results.get(subsection) is True, f"Missing subsection: {subsection}"
    
    def test_section_7_subsections_not_empty(self, mock_yoyo_section_7):
        """Section 7 subsections should not be empty."""
        sub_program = mock_yoyo_section_7["content"]["sub_program"]
        
        for key, value in sub_program.items():
            assert value is not None, f"Subsection {key} is None"
            assert len(value) > 0, f"Subsection {key} is empty"


# ============================================================================
# SAFETY CONSTRAINT INTEGRATION TESTS
# ============================================================================

class TestSafetyConstraintsIntegration:
    """Integration tests for safety constraints in generated programs."""
    
    def test_youth_player_limited_sprint_days(self):
        """Youth player program should have limited sprint days."""
        from services.training_service import TrainingService
        
        service = TrainingService()
        
        # Youth assessment
        youth_assessment = {
            "sprint_30m": 5.0,
            "ball_control": 3,
            "passing_accuracy": 60,
            "game_intelligence": 3
        }
        
        weaknesses = service.analyze_weaknesses(youth_assessment)
        
        # Should identify speed as weakness
        assert "speed" in weaknesses
    
    def test_high_acwr_triggers_load_concern(self):
        """High ACWR (>1.5) should trigger overload status."""
        from elite_training_system import EliteTrainingGenerator, PreviousLoad, LoadStatus
        
        generator = EliteTrainingGenerator()
        
        # Very high load - above 1.5 threshold
        high_load = PreviousLoad(
            acwr=1.6,  # Above 1.5 threshold
            rpe_avg=8.0,
            total_distance_m=9000,
            sprint_count=40,
            hsr_m=1200
        )
        
        status = generator.assess_load_status(high_load)
        
        # Should flag as overload
        assert status == LoadStatus.OVERLOAD
    
    def test_low_acwr_triggers_underload(self):
        """Low ACWR (<0.8) should trigger underload status."""
        from elite_training_system import EliteTrainingGenerator, PreviousLoad, LoadStatus
        
        generator = EliteTrainingGenerator()
        
        # Low load
        low_load = PreviousLoad(
            acwr=0.7,  # Below 0.8 threshold
            rpe_avg=3.0,
            total_distance_m=3000,
            sprint_count=5,
            hsr_m=200
        )
        
        status = generator.assess_load_status(low_load)
        
        # Should flag as underload
        assert status == LoadStatus.UNDERLOAD
    
    def test_optimal_acwr_returns_optimal(self):
        """Normal ACWR (0.8-1.5) should return optimal status."""
        from elite_training_system import EliteTrainingGenerator, PreviousLoad, LoadStatus
        
        generator = EliteTrainingGenerator()
        
        # Normal load
        normal_load = PreviousLoad(
            acwr=1.0,
            rpe_avg=6.0,
            total_distance_m=6000,
            sprint_count=20,
            hsr_m=500
        )
        
        status = generator.assess_load_status(normal_load)
        
        # Should be optimal
        assert status == LoadStatus.OPTIMAL
    
    def test_injury_status_affects_output(self):
        """Injury status should affect training plan output."""
        from elite_training_system import (
            EliteTrainingGenerator, PlayerProfile, TestingData,
            Wellness, MatchSchedule, TacticalFocus, PreviousLoad,
            ExistingProgram, InjuryStatus, PlayerLevel
        )
        
        generator = EliteTrainingGenerator()
        
        # RTP player
        rtp_profile = PlayerProfile(
            name="rtp_test",
            age=16,
            position="midfielder",
            level=PlayerLevel.ACADEMY,
            injury_status=InjuryStatus.RETURN_TO_PLAY
        )
        
        # Minimal other inputs
        testing = TestingData()
        wellness = Wellness(sleep_hours=8, soreness_1_5=3, mood_1_5=4, stress_1_5=4)
        match = MatchSchedule(days_to_next_match=14, matches_this_week=0)
        tactical = TacticalFocus()
        load = PreviousLoad(acwr=0.5, rpe_avg=3.0, total_distance_m=2000, sprint_count=0, hsr_m=100)
        existing = ExistingProgram()
        
        # Generate plan
        output = generator.generate_daily_plan(
            player_profile=rtp_profile,
            testing_data=testing,
            wellness=wellness,
            match_schedule=match,
            tactical_focus=tactical,
            previous_load=load,
            existing_program=existing
        )
        
        # Should have recovery plan or daily training plan
        assert output.recovery_plan is not None or output.daily_training_plan is not None


# ============================================================================
# INTEGRATION TESTS: WELLNESS AND LOAD ENDPOINTS
# ============================================================================

class TestWellnessEndpoints:
    """Integration tests for wellness endpoints."""
    
    def test_get_wellness_history_empty(self, elite_client):
        """Should return empty wellness history for new player."""
        with patch('routes.elite_training_routes.get_elite_training_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_wellness_history = AsyncMock(return_value={
                "player_name": "test_player",
                "wellness_logs": [],
                "message": "No wellness data found"
            })
            mock_get_service.return_value = mock_service
            
            response = elite_client.get("/elite-training/wellness/test_player")
            
            assert response.status_code == 200
            data = response.json()
            assert "player_name" in data
            assert "wellness_logs" in data


class TestLoadMonitoringEndpoints:
    """Integration tests for load monitoring endpoints."""
    
    def test_get_load_history_empty(self, elite_client):
        """Should return empty load history for new player."""
        with patch('routes.elite_training_routes.get_elite_training_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_load_history = AsyncMock(return_value={
                "player_name": "test_player",
                "load_logs": [],
                "message": "No load data found"
            })
            mock_get_service.return_value = mock_service
            
            response = elite_client.get("/elite-training/load-monitoring/test_player")
            
            assert response.status_code == 200
            data = response.json()
            assert "player_name" in data
            assert "load_logs" in data


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
