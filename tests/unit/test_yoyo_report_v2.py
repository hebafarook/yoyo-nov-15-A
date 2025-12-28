"""
Tests for YoYo Report v2 Presentation Layer
============================================

Tests that verify:
1. Exactly 11 sections are generated
2. Correct order of sections
3. JSON keys exist even with missing optional fields
4. Report structure is valid
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from reporting.yoyo_report_v2 import (
    YoYoReportV2Formatter,
    format_yoyo_report_v2,
    validate_report_structure,
    SECTION_TITLES
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def minimal_assessment():
    """Minimal assessment data (some fields missing)."""
    return {
        "id": "test-assessment-001",
        "player_name": "Test Player",
        "age": 17,
        "position": "Midfielder"
    }


@pytest.fixture
def complete_assessment():
    """Complete assessment data with all fields."""
    return {
        "id": "test-assessment-002",
        "user_id": "user-001",
        "player_name": "Complete Test Player",
        "age": 18,
        "position": "Forward",
        "gender": "male",
        "height_cm": 180,
        "weight_kg": 75,
        "dominant_foot": "right",
        "assessment_date": "2024-01-15",
        "sprint_30m": 4.1,
        "yo_yo_test": 2000,
        "vo2_max": 58,
        "vertical_jump": 55,
        "body_fat": 10,
        "ball_control": 4,
        "passing_accuracy": 82,
        "dribbling_success": 78,
        "shooting_accuracy": 80,
        "defensive_duels": 75,
        "game_intelligence": 4,
        "positioning": 4,
        "decision_making": 4,
        "coachability": 5,
        "mental_toughness": 4,
        "overall_score": 78,
        "current_injuries": None
    }


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "id": "user-001",
        "username": "testplayer",
        "full_name": "Test Full Name",
        "age": 18,
        "position": "Forward",
        "gender": "male"
    }


@pytest.fixture
def sample_benchmark():
    """Sample benchmark data."""
    return {
        "user_id": "user-001",
        "overall_score": 78,
        "performance_level": "Advanced",
        "target_score": 85,
        "elite_score": 95
    }


@pytest.fixture
def sample_generated_report():
    """Sample generated comprehensive report."""
    return {
        "user_id": "user-001",
        "ai_analysis": "Player shows strong technical skills with good tactical awareness.",
        "strengths": [
            "Strong ball control",
            "Excellent passing accuracy",
            "Good game intelligence"
        ],
        "weaknesses": [
            "Needs improvement in speed",
            "Work on defensive positioning"
        ],
        "coach_recommendations": [
            "Focus on speed training",
            "Continue technical skill development",
            "Improve tactical positioning",
            "Work on endurance and cardio",
            "Add strength gym sessions"
        ],
        "development_roadmap": {
            "phase_1": "Foundation building",
            "phase_2": "Skill enhancement",
            "phase_3": "Performance optimization"
        },
        "scores": {
            "performance_level": "Advanced"
        }
    }


@pytest.fixture
def sample_training_program():
    """Sample training program data."""
    return {
        "player_id": "user-001",
        "program_content": "8-week training program",
        "weekly_schedule": {
            "Monday": "Speed training",
            "Wednesday": "Technical skills",
            "Friday": "Match simulation"
        },
        "weekly_sessions": 5,
        "total_weeks": 8
    }


@pytest.fixture
def goalkeeper_assessment():
    """Assessment for a goalkeeper."""
    return {
        "id": "test-gk-001",
        "player_name": "Test Goalkeeper",
        "age": 19,
        "position": "Goalkeeper"
    }


# ============================================================================
# TEST: SECTION COUNT
# ============================================================================

class TestSectionCount:
    """Test that exactly 11 sections are generated."""
    
    def test_exactly_11_sections_with_minimal_data(self, minimal_assessment):
        """Report should have exactly 11 sections even with minimal data."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        
        assert 'report_sections' in report
        assert len(report['report_sections']) == 11
    
    def test_exactly_11_sections_with_complete_data(
        self, complete_assessment, sample_user, sample_benchmark, 
        sample_generated_report, sample_training_program
    ):
        """Report should have exactly 11 sections with complete data."""
        report = format_yoyo_report_v2(
            user=sample_user,
            assessment=complete_assessment,
            benchmark=sample_benchmark,
            training_program=sample_training_program,
            generated_report=sample_generated_report
        )
        
        assert len(report['report_sections']) == 11
    
    def test_exactly_11_sections_with_no_data(self):
        """Report should have exactly 11 sections even with no data."""
        report = format_yoyo_report_v2()
        
        assert len(report['report_sections']) == 11
    
    def test_meta_section_count_matches(self, minimal_assessment):
        """Meta section_count should match actual count."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        
        assert report['meta']['section_count'] == 11
        assert report['meta']['section_count'] == len(report['report_sections'])


# ============================================================================
# TEST: SECTION ORDER
# ============================================================================

class TestSectionOrder:
    """Test that sections are in correct order."""
    
    def test_section_numbers_are_sequential(self, complete_assessment):
        """Section numbers should be 1 through 11."""
        report = format_yoyo_report_v2(assessment=complete_assessment)
        
        for i, section in enumerate(report['report_sections']):
            assert section['section_number'] == i + 1
    
    def test_section_titles_match_expected_order(self, complete_assessment):
        """Section titles should match expected order exactly."""
        report = format_yoyo_report_v2(assessment=complete_assessment)
        
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
        
        for i, section in enumerate(report['report_sections']):
            assert section['section_title'] == expected_titles[i], \
                f"Section {i+1} title mismatch: expected '{expected_titles[i]}', got '{section['section_title']}'"
    
    def test_section_titles_match_constant(self, minimal_assessment):
        """Section titles should match SECTION_TITLES constant."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        
        for i, section in enumerate(report['report_sections']):
            assert section['section_title'] == SECTION_TITLES[i]


# ============================================================================
# TEST: JSON KEYS EXIST
# ============================================================================

class TestJsonKeysExist:
    """Test that JSON keys exist even with missing optional fields."""
    
    def test_all_required_top_level_keys(self, minimal_assessment):
        """JSON should have all required top-level keys."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        json_obj = report['report_json']
        
        required_keys = [
            'player_id', 'name', 'age', 'gender', 'position', 'dominant_leg',
            'mode', 'profile_label', 'weekly_sessions', 'total_weeks',
            'benchmarks', 'safety_rules', 'sub_program', 'matches'
        ]
        
        for key in required_keys:
            assert key in json_obj, f"Missing required JSON key: {key}"
    
    def test_sub_program_has_required_keys(self, minimal_assessment):
        """sub_program should have required structure."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        sub_program = report['report_json']['sub_program']
        
        assert 'phases' in sub_program
        assert 'weekly_microcycle' in sub_program
        assert 'expanded_sections' in sub_program
    
    def test_expanded_sections_has_all_keys(self, minimal_assessment):
        """expanded_sections should have all 9 required keys."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        expanded = report['report_json']['sub_program']['expanded_sections']
        
        required_keys = [
            'technical', 'tactical', 'possession', 'cardio', 'gym',
            'speed_agility', 'mobility', 'recovery', 'prehab'
        ]
        
        for key in required_keys:
            assert key in expanded, f"Missing expanded_sections key: {key}"
    
    def test_json_keys_with_empty_data(self):
        """JSON keys should exist even with no input data."""
        report = format_yoyo_report_v2()
        json_obj = report['report_json']
        
        # All keys should exist
        assert 'player_id' in json_obj
        assert 'name' in json_obj
        assert 'benchmarks' in json_obj
        assert 'sub_program' in json_obj
        assert 'matches' in json_obj
        
        # Values should be empty strings/lists/dicts, not None
        assert json_obj['player_id'] == ""
        assert json_obj['matches'] == []
    
    def test_benchmarks_structure(self, sample_benchmark, minimal_assessment):
        """Benchmarks should have expected structure."""
        report = format_yoyo_report_v2(
            assessment=minimal_assessment,
            benchmark=sample_benchmark
        )
        benchmarks = report['report_json']['benchmarks']
        
        assert 'overall_score' in benchmarks
        overall = benchmarks['overall_score']
        assert 'now' in overall
        assert 'target' in overall
        assert 'elite' in overall


# ============================================================================
# TEST: VALIDATION FUNCTION
# ============================================================================

class TestValidateReportStructure:
    """Test the validate_report_structure function."""
    
    def test_valid_report_passes_validation(self, complete_assessment):
        """A properly generated report should pass validation."""
        report = format_yoyo_report_v2(assessment=complete_assessment)
        validation = validate_report_structure(report)
        
        assert validation['valid'] is True
        assert validation['errors'] == []
    
    def test_missing_sections_fails_validation(self):
        """Report with missing sections should fail validation."""
        invalid_report = {
            'report_sections': [],  # Empty sections
            'report_json': {},
            'meta': {}
        }
        validation = validate_report_structure(invalid_report)
        
        assert validation['valid'] is False
        assert any('11 sections' in err for err in validation['errors'])
    
    def test_missing_report_json_fails_validation(self):
        """Report without report_json should fail validation."""
        invalid_report = {
            'report_sections': [{} for _ in range(11)],
            'meta': {}
        }
        validation = validate_report_structure(invalid_report)
        
        assert validation['valid'] is False
        assert any('report_json' in err for err in validation['errors'])
    
    def test_wrong_section_order_fails_validation(self, minimal_assessment):
        """Report with wrong section order should fail validation."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        
        # Swap sections to break order
        report['report_sections'][0], report['report_sections'][1] = \
            report['report_sections'][1], report['report_sections'][0]
        
        validation = validate_report_structure(report)
        
        assert validation['valid'] is False


# ============================================================================
# TEST: TRAINING MODE
# ============================================================================

class TestTrainingMode:
    """Test training mode detection."""
    
    def test_field_mode_for_outfield_player(self, complete_assessment):
        """Outfield player should get FIELD mode."""
        report = format_yoyo_report_v2(assessment=complete_assessment)
        
        mode_section = report['report_sections'][5]  # Section 6: Training Mode
        assert mode_section['content']['mode'] == "FIELD"
        
        assert report['report_json']['mode'] == "FIELD"
    
    def test_gk_mode_for_goalkeeper(self, goalkeeper_assessment):
        """Goalkeeper should get GK mode."""
        report = format_yoyo_report_v2(assessment=goalkeeper_assessment)
        
        mode_section = report['report_sections'][5]
        assert mode_section['content']['mode'] == "GK"
        
        assert report['report_json']['mode'] == "GK"
    
    def test_gk_mode_detection_variants(self):
        """Various goalkeeper position names should all get GK mode."""
        gk_positions = ["Goalkeeper", "GK", "goalkeeper", "Keeper"]
        
        for pos in gk_positions:
            assessment = {"player_name": "Test", "position": pos}
            report = format_yoyo_report_v2(assessment=assessment)
            assert report['report_json']['mode'] == "GK", f"Position '{pos}' should be GK mode"


# ============================================================================
# TEST: RETURN-TO-PLAY ENGINE
# ============================================================================

class TestReturnToPlayEngine:
    """Test Return-to-Play section."""
    
    def test_na_when_no_injury(self, complete_assessment):
        """Should return N/A when no injury."""
        report = format_yoyo_report_v2(assessment=complete_assessment)
        
        rtp_section = report['report_sections'][7]  # Section 8
        assert rtp_section['content'] == "N/A"
    
    def test_shows_injury_data_when_present(self):
        """Should show injury data when present."""
        assessment_with_injury = {
            "player_name": "Injured Player",
            "position": "Midfielder",
            "current_injuries": "Hamstring strain"
        }
        
        report = format_yoyo_report_v2(assessment=assessment_with_injury)
        
        rtp_section = report['report_sections'][7]
        assert rtp_section['content'] != "N/A"
        assert 'injury_status' in rtp_section['content']


# ============================================================================
# TEST: SAFETY GOVERNOR
# ============================================================================

class TestSafetyGovernor:
    """Test Safety Governor section."""
    
    def test_na_when_no_safety_rules(self, complete_assessment):
        """Should return N/A when no safety rules exist."""
        report = format_yoyo_report_v2(assessment=complete_assessment)
        
        safety_section = report['report_sections'][8]  # Section 9
        assert safety_section['content'] == "N/A"
    
    def test_shows_safety_rules_when_present(self):
        """Should show safety rules when present in training program."""
        training_program = {
            "safety_rules": [
                "No training with fever",
                "Mandatory warm-up before high intensity"
            ]
        }
        
        report = format_yoyo_report_v2(training_program=training_program)
        
        safety_section = report['report_sections'][8]
        assert safety_section['content'] != "N/A"
        assert 'safety_rules' in safety_section['content']


# ============================================================================
# TEST: DATA PASSTHROUGH (NO NEW CALCULATIONS)
# ============================================================================

class TestDataPassthrough:
    """Test that data is passed through without modification."""
    
    def test_assessment_values_unchanged(self, complete_assessment):
        """Assessment values should be passed through unchanged."""
        report = format_yoyo_report_v2(assessment=complete_assessment)
        
        snapshot = report['report_sections'][1]['content']
        
        assert snapshot['physical_metrics']['sprint_30m']['value'] == 4.1
        assert snapshot['physical_metrics']['yo_yo_test']['value'] == 2000
        assert snapshot['technical_metrics']['ball_control']['value'] == 4
    
    def test_user_values_used_as_fallback(self, sample_user):
        """User values should be used when assessment missing."""
        report = format_yoyo_report_v2(user=sample_user)
        
        identity = report['report_sections'][0]['content']
        
        assert identity['player_name'] == "Test Full Name"
        assert identity['age'] == 18
    
    def test_strengths_weaknesses_from_generated_report(
        self, minimal_assessment, sample_generated_report
    ):
        """Strengths/weaknesses should come from generated report."""
        report = format_yoyo_report_v2(
            assessment=minimal_assessment,
            generated_report=sample_generated_report
        )
        
        sw_section = report['report_sections'][2]['content']
        
        assert sw_section['strengths'] == sample_generated_report['strengths']
        assert sw_section['weaknesses'] == sample_generated_report['weaknesses']


# ============================================================================
# TEST: META DATA
# ============================================================================

class TestMetaData:
    """Test report metadata."""
    
    def test_meta_has_required_fields(self, minimal_assessment):
        """Meta should have all required fields."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        meta = report['meta']
        
        assert 'report_version' in meta
        assert 'generated_at' in meta
        assert 'section_count' in meta
    
    def test_report_version_is_2(self, minimal_assessment):
        """Report version should be 2.0."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        
        assert report['meta']['report_version'] == "2.0"
    
    def test_generated_at_is_iso_format(self, minimal_assessment):
        """generated_at should be ISO format timestamp."""
        report = format_yoyo_report_v2(assessment=minimal_assessment)
        
        # Should parse without error
        datetime.fromisoformat(report['meta']['generated_at'].replace('Z', '+00:00'))


# ============================================================================
# TEST: EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_input_produces_valid_report(self):
        """Empty input should still produce valid report structure."""
        report = format_yoyo_report_v2()
        validation = validate_report_structure(report)
        
        # Should have valid structure even if data is N/A
        assert len(report['report_sections']) == 11
        assert 'report_json' in report
    
    def test_none_values_handled_gracefully(self):
        """None values should be handled gracefully."""
        assessment = {
            "player_name": None,
            "age": None,
            "position": None
        }
        
        report = format_yoyo_report_v2(assessment=assessment)
        
        # Should not raise error
        assert len(report['report_sections']) == 11
    
    def test_match_history_formatting(self):
        """Match history should be formatted correctly."""
        matches = [
            {"date": "2024-01-15", "opponent": "Team A", "result": "Win"},
            {"date": "2024-01-08", "opponent": "Team B", "result": "Draw"}
        ]
        
        report = format_yoyo_report_v2(match_history=matches)
        
        assert len(report['report_json']['matches']) == 2
        assert report['report_json']['matches'][0]['opponent'] == "Team A"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
