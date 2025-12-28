"""
Player Scenario Fixtures for Program Generation Safety Tests
============================================================

6 golden test scenarios covering youth safety, female ACL prevention,
load management, injury RTP, goalkeeper specifics, and missing data handling.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional


# ============================================================================
# SCENARIO 1: Age 11, Male, Field Player, Healthy (Youth Safety Limits)
# ============================================================================

SCENARIO_1_YOUTH_MALE = {
    "name": "scenario_1_youth_male",
    "description": "Age 11, male field player, healthy - tests youth safety limits",
    "player_profile": {
        "name": "youth_player_11",
        "age": 11,
        "position": "midfielder",
        "level": "grassroots",
        "injury_status": "fit"
    },
    "testing_data": {
        "sprint_10m": 2.1,
        "sprint_30m": 5.0,
        "yoyo_ir2": 800,
        "cmj": 25.0,
        "test_505": 2.8
    },
    "wellness": {
        "sleep_hours": 9.0,
        "soreness_1_5": 5,
        "mood_1_5": 5,
        "stress_1_5": 5
    },
    "match_schedule": {
        "days_to_next_match": 5,
        "matches_this_week": 1,
        "opponent": "Youth Club B",
        "match_importance": 2
    },
    "tactical_focus": {
        "possession": 4,
        "transition": 2,
        "pressing": 2,
        "buildup": 4,
        "set_pieces": 2
    },
    "previous_load": {
        "acwr": 0.9,
        "rpe_avg": 5.0,
        "total_distance_m": 4000,
        "sprint_count": 10,
        "hsr_m": 200
    },
    "expected_constraints": {
        "max_sprint_days_per_week": 1,  # Youth under 14
        "min_rest_days": 2,  # Youth need more recovery
        "max_session_duration_min": 60,
        "no_heavy_lifting": True
    }
}


# ============================================================================
# SCENARIO 2: Age 13, Female, Winger, Healthy (ACL/Landing + Sprint Limits)
# ============================================================================

SCENARIO_2_FEMALE_ACL = {
    "name": "scenario_2_female_acl",
    "description": "Age 13, female winger, healthy - tests ACL prevention content",
    "player_profile": {
        "name": "female_winger_13",
        "age": 13,
        "position": "winger",
        "level": "academy",
        "injury_status": "fit",
        "gender": "female"  # Extended field for gender-specific programming
    },
    "testing_data": {
        "sprint_10m": 2.0,
        "sprint_30m": 4.8,
        "yoyo_ir2": 1000,
        "cmj": 28.0,
        "test_505": 2.6
    },
    "wellness": {
        "sleep_hours": 8.5,
        "soreness_1_5": 4,
        "mood_1_5": 4,
        "stress_1_5": 4
    },
    "match_schedule": {
        "days_to_next_match": 4,
        "matches_this_week": 2,
        "opponent": "Academy Team C",
        "match_importance": 3
    },
    "tactical_focus": {
        "possession": 3,
        "transition": 4,
        "pressing": 3,
        "buildup": 3,
        "set_pieces": 2
    },
    "previous_load": {
        "acwr": 1.0,
        "rpe_avg": 6.0,
        "total_distance_m": 5500,
        "sprint_count": 15,
        "hsr_m": 350
    },
    "expected_constraints": {
        "max_sprint_days_per_week": 1,  # Youth under 14
        "requires_acl_prehab": True,
        "requires_landing_control": True,
        "requires_hip_strengthening": True
    }
}


# ============================================================================
# SCENARIO 3: Age 16, Midfielder, High Availability (Load + Deload)
# ============================================================================

SCENARIO_3_LOAD_MANAGEMENT = {
    "name": "scenario_3_load_management",
    "description": "Age 16 midfielder, high availability - tests load/deload management",
    "player_profile": {
        "name": "midfielder_16",
        "age": 16,
        "position": "midfielder",
        "level": "academy",
        "injury_status": "fit"
    },
    "testing_data": {
        "sprint_10m": 1.85,
        "sprint_30m": 4.4,
        "yoyo_ir2": 1600,
        "cmj": 38.0,
        "test_505": 2.45,
        "squat_1rm": 80.0,
        "nordic_strength": 40.0
    },
    "wellness": {
        "sleep_hours": 7.5,
        "soreness_1_5": 3,
        "mood_1_5": 4,
        "stress_1_5": 3,
        "hrv_score": 55.0
    },
    "match_schedule": {
        "days_to_next_match": 3,
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
        "acwr": 1.25,  # Elevated - should trigger caution
        "rpe_avg": 7.5,
        "total_distance_m": 8500,
        "sprint_count": 35,
        "hsr_m": 900
    },
    "expected_constraints": {
        "max_sprint_days_per_week": 2,
        "load_progression_max_pct": 10,
        "requires_deload_consideration": True,  # ACWR > 1.2
        "min_rest_days": 1
    }
}


# ============================================================================
# SCENARIO 4: Age 15, Striker, Hamstring Injury (RTP - No Sprint/COD/Contact)
# ============================================================================

SCENARIO_4_HAMSTRING_RTP = {
    "name": "scenario_4_hamstring_rtp",
    "description": "Age 15 striker with hamstring injury - tests RTP protocol",
    "player_profile": {
        "name": "striker_15_rtp",
        "age": 15,
        "position": "striker",
        "level": "academy",
        "injury_status": "return_to_play"  # RTP status
    },
    "testing_data": {
        "sprint_10m": 1.9,
        "sprint_30m": 4.5,
        "yoyo_ir2": 1200,
        "cmj": 32.0,
        "test_505": 2.55
    },
    "wellness": {
        "sleep_hours": 8.0,
        "soreness_1_5": 3,  # Some residual soreness
        "mood_1_5": 4,
        "stress_1_5": 3
    },
    "match_schedule": {
        "days_to_next_match": 10,  # Further out during RTP
        "matches_this_week": 0,
        "opponent": None,
        "match_importance": 1
    },
    "tactical_focus": {
        "possession": 2,
        "transition": 1,
        "pressing": 1,
        "buildup": 2,
        "set_pieces": 1
    },
    "previous_load": {
        "acwr": 0.6,  # Lower during RTP
        "rpe_avg": 4.0,
        "total_distance_m": 3000,
        "sprint_count": 0,  # No sprinting during RTP
        "hsr_m": 100
    },
    "injury_details": {
        "type": "hamstring_strain",
        "location": "right_biceps_femoris",
        "grade": 2,
        "days_since_injury": 14,
        "current_rtp_stage": "stage_2"
    },
    "expected_constraints": {
        "no_sprints": True,
        "no_cod_drills": True,
        "no_contact": True,
        "requires_rtp_protocol": True,
        "max_intensity_pct": 70
    }
}


# ============================================================================
# SCENARIO 5: Age 14, Goalkeeper, Healthy (GK Mode + Shoulder/Wrist/Groin Prehab)
# ============================================================================

SCENARIO_5_GOALKEEPER = {
    "name": "scenario_5_goalkeeper",
    "description": "Age 14 goalkeeper, healthy - tests GK-specific programming",
    "player_profile": {
        "name": "goalkeeper_14",
        "age": 14,
        "position": "goalkeeper",
        "level": "academy",
        "injury_status": "fit"
    },
    "testing_data": {
        "sprint_10m": 1.95,
        "sprint_30m": 4.6,
        "yoyo_ir2": 1100,
        "cmj": 35.0,
        "test_505": 2.5
    },
    "wellness": {
        "sleep_hours": 8.0,
        "soreness_1_5": 4,
        "mood_1_5": 5,
        "stress_1_5": 4
    },
    "match_schedule": {
        "days_to_next_match": 4,
        "matches_this_week": 1,
        "opponent": "Academy D",
        "match_importance": 3
    },
    "tactical_focus": {
        "possession": 2,
        "transition": 3,
        "pressing": 1,
        "buildup": 3,
        "set_pieces": 4
    },
    "previous_load": {
        "acwr": 1.0,
        "rpe_avg": 5.5,
        "total_distance_m": 4500,
        "sprint_count": 12,
        "hsr_m": 250
    },
    "expected_constraints": {
        "requires_gk_specific_drills": True,
        "requires_dive_training": True,
        "requires_lateral_movement": True,
        "requires_shoulder_prehab": True,
        "requires_wrist_prehab": True,
        "requires_groin_prehab": True,
        "max_sprint_days_per_week": 2  # Age 14+
    }
}


# ============================================================================
# SCENARIO 6: Missing Optional Data (Safe Defaults + N/A Handling)
# ============================================================================

SCENARIO_6_MISSING_DATA = {
    "name": "scenario_6_missing_data",
    "description": "Missing optional data - tests safe defaults and N/A handling",
    "player_profile": {
        "name": "player_minimal_data",
        "age": 15,
        "position": "defender",
        "level": "grassroots",
        "injury_status": "fit"
    },
    "testing_data": {
        # Minimal testing data - only required fields
        "sprint_10m": None,
        "sprint_30m": None,
        "yoyo_ir2": None,
        "cmj": None,
        "test_505": None
    },
    "wellness": {
        "sleep_hours": 7.0,
        "soreness_1_5": 3,
        "mood_1_5": 3,
        "stress_1_5": 3
    },
    "match_schedule": {
        "days_to_next_match": 7,
        "matches_this_week": 1,
        "opponent": None,
        "match_importance": 2
    },
    "tactical_focus": {
        "possession": 3,
        "transition": 3,
        "pressing": 3,
        "buildup": 3,
        "set_pieces": 3
    },
    "previous_load": {
        "acwr": 1.0,
        "rpe_avg": 5.0,
        "total_distance_m": 5000,
        "sprint_count": 15,
        "hsr_m": 300
    },
    "expected_constraints": {
        "should_use_safe_defaults": True,
        "should_mark_missing_as_na": True,
        "should_still_generate_valid_plan": True
    }
}


# ============================================================================
# ALL SCENARIOS
# ============================================================================

ALL_SCENARIOS = [
    SCENARIO_1_YOUTH_MALE,
    SCENARIO_2_FEMALE_ACL,
    SCENARIO_3_LOAD_MANAGEMENT,
    SCENARIO_4_HAMSTRING_RTP,
    SCENARIO_5_GOALKEEPER,
    SCENARIO_6_MISSING_DATA
]


def get_scenario_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a scenario by its name."""
    for scenario in ALL_SCENARIOS:
        if scenario["name"] == name:
            return scenario
    return None


def get_elite_training_inputs(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Convert scenario to elite training input format."""
    return {
        "player_profile": scenario["player_profile"],
        "testing_data": scenario["testing_data"],
        "wellness": scenario["wellness"],
        "match_schedule": scenario["match_schedule"],
        "tactical_focus": scenario["tactical_focus"],
        "previous_load": scenario["previous_load"]
    }
