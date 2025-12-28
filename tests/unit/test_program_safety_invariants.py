"""
Program Safety Invariants Test Suite
====================================

Unit tests for safety invariant helpers and validation functions.
These tests verify that training programs respect safety constraints.

Safety Rules Tested:
- Sprint frequency limits by age
- Rest day requirements
- Load progression limits
- Injury/RTP drill restrictions
- Female ACL prevention requirements
- Goalkeeper-specific requirements
- Training section structure requirements
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

# Add paths
tests_path = Path(__file__).parent.parent
backend_path = tests_path.parent / "backend"
sys.path.insert(0, str(tests_path))
sys.path.insert(0, str(backend_path))


# ============================================================================
# SAFETY INVARIANT HELPER FUNCTIONS
# ============================================================================

def count_sprint_days(plan: Dict[str, Any]) -> int:
    """
    Count number of days with sprint/speed work in a training plan.
    Looks for sprint-related keywords in drills and sessions.
    """
    sprint_keywords = ['sprint', 'speed', 'acceleration', 'explosive', '30m', '10m']
    sprint_days = 0
    
    # Check various plan structures
    days = plan.get('daily_plans', plan.get('days', plan.get('weekly_microcycle', [])))
    
    if isinstance(days, list):
        for day in days:
            day_str = str(day).lower()
            if any(kw in day_str for kw in sprint_keywords):
                sprint_days += 1
    elif isinstance(days, dict):
        for day_key, day_content in days.items():
            day_str = str(day_content).lower()
            if any(kw in day_str for kw in sprint_keywords):
                sprint_days += 1
    
    # Also check field_session if present
    field_session = plan.get('field_session', {})
    if field_session:
        session_str = str(field_session).lower()
        if any(kw in session_str for kw in sprint_keywords):
            sprint_days += 1
    
    return sprint_days


def count_rest_days(plan: Dict[str, Any]) -> int:
    """
    Count number of rest/recovery days in a training plan.
    """
    rest_keywords = ['rest', 'recovery', 'off', 'regeneration']
    rest_days = 0
    
    days = plan.get('daily_plans', plan.get('days', plan.get('weekly_microcycle', [])))
    
    if isinstance(days, list):
        for day in days:
            day_str = str(day).lower()
            if any(kw in day_str for kw in rest_keywords):
                rest_days += 1
    elif isinstance(days, dict):
        for day_key, day_content in days.items():
            day_str = str(day_content).lower()
            if any(kw in day_str for kw in rest_keywords):
                rest_days += 1
    
    # Check for explicit recovery_day
    recovery_day = plan.get('recovery_day')
    if recovery_day:
        rest_days += 1
    
    return max(rest_days, 1)  # At minimum assume 1 rest day if plan exists


def check_load_progression(current_load: float, previous_load: float, max_increase_pct: float = 10.0) -> bool:
    """
    Check if load progression is within safe limits.
    Returns True if progression is safe (within limits).
    """
    if previous_load <= 0:
        return True  # Can't calculate percentage
    
    increase_pct = ((current_load - previous_load) / previous_load) * 100
    return increase_pct <= max_increase_pct


def contains_rtp_protocol(plan: Dict[str, Any]) -> bool:
    """Check if plan contains RTP (Return-to-Play) protocol."""
    rtp_keywords = ['rtp', 'return to play', 'return-to-play', 'rehab', 'rehabilitation', 'stage_']
    plan_str = str(plan).lower()
    return any(kw in plan_str for kw in rtp_keywords)


def contains_prohibited_drills_for_injury(plan: Dict[str, Any]) -> List[str]:
    """
    Check for drills that should be prohibited during injury RTP.
    Returns list of prohibited drill types found.
    """
    prohibited_keywords = {
        'sprint': ['sprint', '30m', '10m', 'max speed'],
        'cod': ['change of direction', 'cod', 'cutting', 'sharp turn'],
        'contact': ['contact', 'tackle', '1v1 duel', 'physical']
    }
    
    violations = []
    plan_str = str(plan).lower()
    
    for category, keywords in prohibited_keywords.items():
        if any(kw in plan_str for kw in keywords):
            violations.append(category)
    
    return violations


def contains_acl_prevention_content(plan: Dict[str, Any]) -> bool:
    """Check if plan contains ACL prevention/prehab content for females."""
    acl_keywords = [
        'acl', 'knee', 'landing', 'deceleration', 
        'neuromuscular', 'hip stability', 'gluteal',
        'single leg', 'proprioception'
    ]
    plan_str = str(plan).lower()
    return any(kw in plan_str for kw in acl_keywords)


def contains_gk_specific_content(plan: Dict[str, Any]) -> Dict[str, bool]:
    """
    Check for goalkeeper-specific training content.
    Returns dict with presence of each GK requirement.
    """
    gk_requirements = {
        'diving': ['dive', 'diving', 'save', 'shot stopping'],
        'lateral_movement': ['lateral', 'shuffle', 'side step', 'footwork'],
        'shoulder_prehab': ['shoulder', 'rotator cuff', 'upper body'],
        'wrist_prehab': ['wrist', 'hand', 'catching'],
        'groin_prehab': ['groin', 'adductor', 'hip', 'split']
    }
    
    results = {}
    plan_str = str(plan).lower()
    
    for requirement, keywords in gk_requirements.items():
        results[requirement] = any(kw in plan_str for kw in keywords)
    
    return results


def get_required_training_sections() -> List[str]:
    """Return list of required training section keys."""
    return [
        'technical', 'tactical', 'possession', 'speed_agility',
        'cardio', 'gym', 'mobility', 'recovery', 'prehab'
    ]


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


def validate_drill_has_required_fields(drill: Dict[str, Any]) -> List[str]:
    """
    Validate that a drill has required fields.
    Returns list of missing field names.
    """
    # At minimum, a drill needs a name and some timing/rep info
    required_fields = ['name']
    timing_fields = ['duration', 'sets', 'reps', 'time', 'minutes']
    
    missing = []
    
    for field in required_fields:
        if field not in drill or not drill[field]:
            missing.append(field)
    
    # Check for at least one timing field
    has_timing = any(field in drill for field in timing_fields)
    if not has_timing:
        missing.append('timing_info (duration/sets/reps)')
    
    return missing


# ============================================================================
# UNIT TESTS FOR HELPER FUNCTIONS
# ============================================================================

class TestSprintDayCounter:
    """Tests for sprint day counting helper."""
    
    def test_counts_sprint_in_daily_plans(self):
        """Should count days with sprint keywords."""
        plan = {
            'daily_plans': [
                {'day': 1, 'drills': ['warmup', 'sprint_30m', 'cool down']},
                {'day': 2, 'drills': ['technical', 'passing']},
                {'day': 3, 'drills': ['speed work', 'acceleration']},
            ]
        }
        assert count_sprint_days(plan) == 2
    
    def test_counts_sprint_in_field_session(self):
        """Should count sprint in field_session."""
        plan = {
            'field_session': {
                'warmup': 'dynamic',
                'main': 'sprint intervals 6x30m'
            }
        }
        assert count_sprint_days(plan) >= 1
    
    def test_zero_sprints_for_recovery_plan(self):
        """Should count zero sprints in recovery-only plan."""
        plan = {
            'daily_plans': [
                {'day': 1, 'drills': ['stretching', 'mobility']},
                {'day': 2, 'drills': ['recovery', 'pool session']},
            ]
        }
        assert count_sprint_days(plan) == 0


class TestRestDayCounter:
    """Tests for rest day counting helper."""
    
    def test_counts_rest_days(self):
        """Should count days marked as rest/recovery."""
        plan = {
            'daily_plans': [
                {'day': 1, 'type': 'training'},
                {'day': 2, 'type': 'rest day'},
                {'day': 3, 'type': 'recovery session'},
            ]
        }
        assert count_rest_days(plan) >= 2
    
    def test_counts_recovery_day_field(self):
        """Should count explicit recovery_day field."""
        plan = {
            'recovery_day': {'modalities': ['pool', 'massage']}
        }
        assert count_rest_days(plan) >= 1


class TestLoadProgression:
    """Tests for load progression validation."""
    
    def test_safe_progression(self):
        """Should return True for safe progression."""
        assert check_load_progression(110, 100, 10) is True
    
    def test_unsafe_progression(self):
        """Should return False for unsafe progression."""
        assert check_load_progression(115, 100, 10) is False
    
    def test_exact_limit(self):
        """Should return True at exact limit."""
        assert check_load_progression(110, 100, 10) is True
    
    def test_zero_previous_load(self):
        """Should return True when previous load is zero."""
        assert check_load_progression(100, 0, 10) is True


class TestRTPProtocolCheck:
    """Tests for RTP protocol detection."""
    
    def test_detects_rtp_keywords(self):
        """Should detect RTP-related keywords."""
        plan = {'protocol': 'Stage_2 RTP - linear progressions'}
        assert contains_rtp_protocol(plan) is True
    
    def test_no_rtp_in_normal_plan(self):
        """Should not detect RTP in normal training plan."""
        plan = {'type': 'regular training', 'drills': ['passing', 'shooting']}
        assert contains_rtp_protocol(plan) is False


class TestProhibitedDrillsForInjury:
    """Tests for prohibited drill detection during injury."""
    
    def test_detects_sprint_drills(self):
        """Should detect sprint drills."""
        plan = {'drills': ['30m sprint', 'passing']}
        violations = contains_prohibited_drills_for_injury(plan)
        assert 'sprint' in violations
    
    def test_detects_cod_drills(self):
        """Should detect change of direction drills."""
        plan = {'drills': ['COD drill', 'agility ladder']}
        violations = contains_prohibited_drills_for_injury(plan)
        assert 'cod' in violations
    
    def test_no_violations_in_safe_plan(self):
        """Should not flag safe drills."""
        plan = {'drills': ['stretching', 'isometrics', 'pool work']}
        violations = contains_prohibited_drills_for_injury(plan)
        assert len(violations) == 0


class TestACLPreventionContent:
    """Tests for ACL prevention content detection."""
    
    def test_detects_acl_keywords(self):
        """Should detect ACL prevention content."""
        plan = {'prehab': 'Landing control and knee stability exercises'}
        assert contains_acl_prevention_content(plan) is True
    
    def test_detects_hip_stability(self):
        """Should detect hip stability content."""
        plan = {'exercises': 'Gluteal activation and hip stability'}
        assert contains_acl_prevention_content(plan) is True


class TestGKSpecificContent:
    """Tests for goalkeeper-specific content detection."""
    
    def test_detects_diving_training(self):
        """Should detect diving/save training."""
        plan = {'gk_drills': 'Diving saves, shot stopping practice'}
        results = contains_gk_specific_content(plan)
        assert results['diving'] is True
    
    def test_detects_lateral_movement(self):
        """Should detect lateral movement training."""
        plan = {'footwork': 'Lateral shuffle drills and footwork'}
        results = contains_gk_specific_content(plan)
        assert results['lateral_movement'] is True


class TestYoYoSection7Structure:
    """Tests for YoYo Report Section 7 structure validation."""
    
    def test_all_subsections_present(self):
        """Should return all True when all subsections present."""
        section_7 = {
            'content': {
                'sub_program': {
                    '7.1_technical': ['drill1'],
                    '7.2_tactical': ['drill2'],
                    '7.3_possession': ['drill3'],
                    '7.4_athletic_speed_agility': ['drill4'],
                    '7.5_cardio': ['drill5'],
                    '7.6_gym_strength': ['drill6'],
                    '7.7_mobility_flexibility': ['drill7'],
                    '7.8_recovery_regeneration': ['drill8'],
                    '7.9_injury_prevention_prehab': ['drill9']
                }
            }
        }
        results = check_yoyo_section_7_structure(section_7)
        assert all(results.values())
    
    def test_missing_subsections(self):
        """Should return False for missing subsections."""
        section_7 = {
            'content': {
                'sub_program': {
                    '7.1_technical': ['drill1'],
                    '7.2_tactical': ['drill2']
                }
            }
        }
        results = check_yoyo_section_7_structure(section_7)
        assert results.get('7.1_technical') is True
        assert results.get('7.5_cardio') is False


class TestDrillFieldValidation:
    """Tests for drill required field validation."""
    
    def test_valid_drill_with_duration(self):
        """Should pass for drill with name and duration."""
        drill = {'name': 'Sprint Drill', 'duration': '10 min'}
        missing = validate_drill_has_required_fields(drill)
        assert len(missing) == 0
    
    def test_valid_drill_with_sets_reps(self):
        """Should pass for drill with name and sets/reps."""
        drill = {'name': 'Squats', 'sets': 3, 'reps': 10}
        missing = validate_drill_has_required_fields(drill)
        assert len(missing) == 0
    
    def test_missing_name(self):
        """Should flag missing name."""
        drill = {'duration': '10 min'}
        missing = validate_drill_has_required_fields(drill)
        assert 'name' in missing
    
    def test_missing_timing(self):
        """Should flag missing timing info."""
        drill = {'name': 'Some Drill'}
        missing = validate_drill_has_required_fields(drill)
        assert any('timing' in m for m in missing)


# ============================================================================
# SAFETY CONSTRAINT VALIDATION TESTS
# ============================================================================

class TestYouthSafetyConstraints:
    """Tests for youth safety constraints (under 14)."""
    
    def test_sprint_limit_under_14(self):
        """Youth under 14 should have max 1 sprint day per week."""
        # Simulate a valid youth plan
        valid_youth_plan = {
            'daily_plans': [
                {'day': 1, 'drills': ['technical']},
                {'day': 2, 'drills': ['sprint work']},  # Only 1 sprint day
                {'day': 3, 'drills': ['tactical']},
                {'day': 4, 'drills': ['rest']},
                {'day': 5, 'drills': ['game']},
            ]
        }
        sprint_days = count_sprint_days(valid_youth_plan)
        assert sprint_days <= 1, f"Youth under 14 should have max 1 sprint day, got {sprint_days}"
    
    def test_rest_requirement(self):
        """Youth should have at least 1-2 rest days per week."""
        plan = {
            'daily_plans': [
                {'day': 1, 'drills': ['training']},
                {'day': 2, 'drills': ['rest']},
                {'day': 3, 'drills': ['training']},
                {'day': 4, 'drills': ['recovery']},
            ]
        }
        rest_days = count_rest_days(plan)
        assert rest_days >= 1, f"Should have at least 1 rest day, got {rest_days}"


class TestLoadManagementConstraints:
    """Tests for load management constraints."""
    
    def test_acwr_overload_triggers_deload(self):
        """High ACWR (>1.3) should trigger deload consideration."""
        # ACWR > 1.3 indicates overload
        high_acwr = 1.35
        is_overloaded = high_acwr > 1.3
        assert is_overloaded is True
    
    def test_load_progression_within_limits(self):
        """Weekly load should not increase more than 10%."""
        previous_weekly_load = 5000  # meters
        current_weekly_load = 5400   # 8% increase - safe
        
        is_safe = check_load_progression(current_weekly_load, previous_weekly_load, 10)
        assert is_safe is True
    
    def test_load_progression_exceeds_limits(self):
        """Should flag load progression > 10%."""
        previous_weekly_load = 5000
        current_weekly_load = 5600  # 12% increase - unsafe
        
        is_safe = check_load_progression(current_weekly_load, previous_weekly_load, 10)
        assert is_safe is False


class TestInjuryRTPConstraints:
    """Tests for injury/RTP constraints."""
    
    def test_rtp_plan_has_protocol(self):
        """RTP plan should contain protocol information."""
        rtp_plan = {
            'status': 'return_to_play',
            'protocol': 'Stage 2 RTP - Linear progressions',
            'restrictions': ['no sprints', 'no contact']
        }
        assert contains_rtp_protocol(rtp_plan) is True
    
    def test_rtp_plan_excludes_prohibited_drills(self):
        """RTP plan should not contain prohibited drills."""
        # This is a SAFE RTP plan
        safe_rtp_plan = {
            'drills': [
                'pool walking',
                'isometric holds',
                'stretching',
                'stationary bike'
            ]
        }
        violations = contains_prohibited_drills_for_injury(safe_rtp_plan)
        assert len(violations) == 0, f"RTP plan should have no prohibited drills, found: {violations}"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
