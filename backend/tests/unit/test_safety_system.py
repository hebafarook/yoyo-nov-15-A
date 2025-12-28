"""
Safety System Unit Tests
========================

Comprehensive tests proving unsafe plans CANNOT pass.

Tests:
1. Safety status computation
2. Allowed elements generation  
3. Coach override (can only make safer)
4. RED status enforcement
5. YELLOW status modifications
6. GREEN status age limits
7. Post-generation validation
8. Post-generation sanitization
9. Drill contraindication filtering
"""

import pytest
from datetime import datetime, timezone
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.safety_models import (
    SafetyStatus, InjuryStatus, AllowedElements, PlayerContext,
    LoadContext, AssessmentSummary, SafetyContext, PlanModification,
    DrillSelection, DayPlan, WeeklyPlan, TrainingProgramOutput
)
from services.safety_validator import SafetyValidator, get_safety_validator


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def validator():
    return SafetyValidator()


@pytest.fixture
def healthy_player() -> PlayerContext:
    return PlayerContext(
        player_id="player-healthy-1",
        player_name="Healthy Player",
        age=16,
        sex="male",
        position="midfielder",
        injury_status=InjuryStatus.HEALTHY,
        current_injuries=[]
    )


@pytest.fixture
def injured_player() -> PlayerContext:
    return PlayerContext(
        player_id="player-injured-1",
        player_name="Injured Player",
        age=17,
        sex="male",
        position="striker",
        injury_status=InjuryStatus.MODERATE,
        current_injuries=["hamstring"]
    )


@pytest.fixture
def severely_injured_player() -> PlayerContext:
    return PlayerContext(
        player_id="player-severe-1",
        player_name="Severe Injury Player",
        age=18,
        sex="male",
        position="defender",
        injury_status=InjuryStatus.SEVERE,
        current_injuries=["acl", "knee"]
    )


@pytest.fixture
def young_player() -> PlayerContext:
    return PlayerContext(
        player_id="player-young-1",
        player_name="Young Player",
        age=12,
        sex="male",
        position="any",
        injury_status=InjuryStatus.HEALTHY,
        current_injuries=[]
    )


@pytest.fixture
def high_load_context() -> LoadContext:
    return LoadContext(
        acwr=1.9,  # Critical level
        fatigue_level=5,
        soreness_level=4,
        consecutive_hard_days=4
    )


@pytest.fixture
def full_training_program() -> TrainingProgramOutput:
    """A full training program that needs validation."""
    days = []
    for i in range(1, 8):
        if i in [3, 7]:  # Rest days
            days.append(DayPlan(
                day_number=i,
                day_type='rest',
                intensity='rest',
                drills=[]
            ))
        else:
            days.append(DayPlan(
                day_number=i,
                day_type='training',
                intensity='high' if i in [1, 4] else 'moderate',
                drills=[
                    DrillSelection(
                        drill_id=f'drill_{i}',
                        name='Sprint Training' if i == 1 else 'Technical Drill',
                        section='speed_agility' if i == 1 else 'technical',
                        intensity='high' if i in [1, 4] else 'moderate'
                    )
                ],
                warmup_duration_min=10,
                cooldown_duration_min=6
            ))
    
    return TrainingProgramOutput(
        plan_type='full_training',
        safety_status=SafetyStatus.GREEN,
        weekly_plan=WeeklyPlan(
            week_number=1,
            days=days,
            sprint_days_count=1,
            hard_days_count=2,
            rest_days_count=2
        ),
        drills_by_section={
            'speed_agility': [DrillSelection(
                drill_id='sprint_1',
                name='Sprint Training',
                section='speed_agility',
                intensity='high'
            )],
            'technical': [DrillSelection(
                drill_id='tech_1',
                name='Technical Drill',
                section='technical',
                intensity='moderate'
            )]
        },
        safety_explanation='Standard training week',
        user_controls_offered=[]
    )


# =============================================================================
# SAFETY STATUS COMPUTATION TESTS
# =============================================================================

class TestSafetyStatusComputation:
    """Tests for safety status computation from player data."""
    
    def test_healthy_player_gets_green_status(self, validator, healthy_player):
        """Healthy player with no issues should get GREEN status."""
        status, flags = validator.compute_safety_status(healthy_player)
        
        assert status == SafetyStatus.GREEN
        assert len(flags) == 0
    
    def test_moderate_injury_gets_yellow_status(self, validator, injured_player):
        """Player with moderate injury should get YELLOW status."""
        status, flags = validator.compute_safety_status(injured_player)
        
        assert status == SafetyStatus.YELLOW
        assert any('INJURY' in f for f in flags)
    
    def test_severe_injury_gets_red_status(self, validator, severely_injured_player):
        """Player with severe injury should get RED status."""
        status, flags = validator.compute_safety_status(severely_injured_player)
        
        assert status == SafetyStatus.RED
        assert any('SEVERE' in f or 'ACL' in f.upper() for f in flags)
    
    def test_critical_acwr_triggers_red_status(self, validator, healthy_player, high_load_context):
        """Critical ACWR (>1.8) should trigger RED status."""
        status, flags = validator.compute_safety_status(healthy_player, high_load_context)
        
        assert status == SafetyStatus.RED
        assert any('ACWR_CRITICAL' in f for f in flags)
    
    def test_high_fatigue_triggers_yellow(self, validator, healthy_player):
        """High fatigue level should trigger YELLOW status."""
        load = LoadContext(fatigue_level=5)
        status, flags = validator.compute_safety_status(healthy_player, load)
        
        assert status == SafetyStatus.YELLOW
        assert 'FATIGUE_LEVEL_HIGH' in flags
    
    def test_acl_injury_triggers_red(self, validator):
        """ACL injury should always trigger RED status."""
        player = PlayerContext(
            player_id="acl-player",
            player_name="ACL Player",
            age=20,
            injury_status=InjuryStatus.MODERATE,
            current_injuries=["acl"]
        )
        
        status, flags = validator.compute_safety_status(player)
        
        assert status == SafetyStatus.RED


# =============================================================================
# ALLOWED ELEMENTS TESTS
# =============================================================================

class TestAllowedElementsGeneration:
    """Tests for allowed elements generation."""
    
    def test_red_status_blocks_high_intensity(self, validator, severely_injured_player):
        """RED status should block all high-intensity activities."""
        elements = validator.generate_allowed_elements(
            SafetyStatus.RED, severely_injured_player
        )
        
        assert elements.max_sprint_days_per_week == 0
        assert elements.max_hard_days_per_week == 0
        assert elements.allow_plyometrics is False
        assert elements.allow_contact is False
        assert elements.allow_max_strength is False
        assert elements.max_intensity == 'low'
    
    def test_yellow_status_limits_training(self, validator, injured_player):
        """YELLOW status should limit but not block training."""
        elements = validator.generate_allowed_elements(
            SafetyStatus.YELLOW, injured_player
        )
        
        assert elements.max_sprint_days_per_week <= 1
        assert elements.max_hard_days_per_week <= 2
        assert elements.allow_plyometrics is False
        assert elements.max_intensity == 'moderate'
    
    def test_green_status_allows_full_training(self, validator, healthy_player):
        """GREEN status should allow full training."""
        elements = validator.generate_allowed_elements(
            SafetyStatus.GREEN, healthy_player
        )
        
        assert elements.max_sprint_days_per_week >= 2
        assert elements.allow_plyometrics is True
        assert elements.allow_contact is True
        assert elements.max_intensity == 'high'
    
    def test_injury_adds_contraindications(self, validator, injured_player):
        """Injuries should add appropriate contraindications."""
        elements = validator.generate_allowed_elements(
            SafetyStatus.YELLOW, injured_player
        )
        
        assert 'hamstring' in elements.excluded_contraindications
        assert 'sprint' in elements.excluded_drill_types or 'plyometrics' in elements.excluded_drill_types


# =============================================================================
# AGE-BASED LIMITS TESTS
# =============================================================================

class TestAgeLimits:
    """Tests for age-based sprint limits."""
    
    def test_under_14_max_1_sprint_day(self, validator, young_player):
        """Players under 14 should have max 1 sprint day/week."""
        elements = validator.generate_allowed_elements(
            SafetyStatus.GREEN, young_player
        )
        
        assert elements.max_sprint_days_per_week <= 1
    
    def test_14_and_over_max_2_sprint_days(self, validator, healthy_player):
        """Players 14+ should have max 2 sprint days/week."""
        elements = validator.generate_allowed_elements(
            SafetyStatus.GREEN, healthy_player
        )
        
        assert elements.max_sprint_days_per_week <= 2
    
    def test_age_limit_enforced_even_in_green(self, validator, young_player):
        """Age limits should be enforced even in GREEN status."""
        context = validator.compute_safety_context(young_player)
        
        assert context.allowed_elements.max_sprint_days_per_week <= 1


# =============================================================================
# COACH OVERRIDE TESTS
# =============================================================================

class TestCoachOverride:
    """Tests for coach override functionality."""
    
    def test_coach_can_make_status_more_restrictive(self, validator, healthy_player):
        """Coach should be able to override GREEN to YELLOW/RED."""
        context = validator.compute_safety_context(
            healthy_player,
            coach_override_status=SafetyStatus.YELLOW,
            coach_override_reason="Player reported discomfort"
        )
        
        effective = context.get_effective_status()
        assert effective == SafetyStatus.YELLOW
    
    def test_coach_cannot_make_status_less_restrictive(self, validator, severely_injured_player):
        """Coach should NOT be able to override RED to GREEN."""
        context = validator.compute_safety_context(
            severely_injured_player,
            coach_override_status=SafetyStatus.GREEN,  # Attempting to make less restrictive
            coach_override_reason="Coach thinks player is fine"
        )
        
        effective = context.get_effective_status()
        # Should remain RED because coach can't make it less restrictive
        assert effective == SafetyStatus.RED
    
    def test_yellow_to_red_override_allowed(self, validator, injured_player):
        """Coach should be able to upgrade YELLOW to RED."""
        context = validator.compute_safety_context(
            injured_player,
            coach_override_status=SafetyStatus.RED,
            coach_override_reason="Extra precaution needed"
        )
        
        effective = context.get_effective_status()
        assert effective == SafetyStatus.RED


# =============================================================================
# POST-GENERATION VALIDATION TESTS
# =============================================================================

class TestPostGenerationValidation:
    """Tests for post-generation validation."""
    
    def test_valid_green_program_passes(self, validator, healthy_player, full_training_program):
        """Valid GREEN program should pass validation."""
        context = validator.compute_safety_context(healthy_player)
        is_valid, violations = validator.validate_program(full_training_program, context)
        
        assert is_valid is True
        assert len([v for v in violations if v.severity in ['error', 'critical']]) == 0
    
    def test_red_status_rejects_full_training(self, validator, severely_injured_player, full_training_program):
        """RED status should reject full training programs."""
        context = validator.compute_safety_context(severely_injured_player)
        is_valid, violations = validator.validate_program(full_training_program, context)
        
        assert is_valid is False
        assert any(v.rule_id == 'RED_STATUS_PLAN_TYPE' for v in violations)
    
    def test_excessive_sprint_days_rejected(self, validator, young_player):
        """Programs with too many sprint days should be rejected."""
        context = validator.compute_safety_context(young_player)  # Age 12, max 1 sprint day
        
        # Create program with 3 sprint days
        days = []
        for i in range(1, 8):
            days.append(DayPlan(
                day_number=i,
                day_type='training' if i <= 5 else 'rest',
                intensity='high' if i <= 3 else 'moderate',
                drills=[DrillSelection(
                    drill_id=f'sprint_{i}',
                    name='Sprint Training',
                    section='speed_agility',
                    intensity='high'
                )] if i <= 3 else [],
                warmup_duration_min=10,
                cooldown_duration_min=6
            ))
        
        program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.GREEN,
            weekly_plan=WeeklyPlan(
                week_number=1,
                days=days,
                sprint_days_count=3,  # Exceeds limit
                hard_days_count=3,
                rest_days_count=2
            ),
            drills_by_section={'speed_agility': []},
            safety_explanation='Test'
        )
        
        is_valid, violations = validator.validate_program(program, context)
        
        assert is_valid is False
        assert any('SPRINT' in v.rule_id for v in violations)
    
    def test_insufficient_warmup_rejected(self, validator, healthy_player):
        """Programs with insufficient warmup should be flagged."""
        context = validator.compute_safety_context(healthy_player)
        
        days = [DayPlan(
            day_number=1,
            day_type='training',
            intensity='moderate',
            drills=[],
            warmup_duration_min=3,  # Too short
            cooldown_duration_min=6
        )]
        
        program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.GREEN,
            weekly_plan=WeeklyPlan(week_number=1, days=days, rest_days_count=6),
            drills_by_section={},
            safety_explanation='Test'
        )
        
        is_valid, violations = validator.validate_program(program, context)
        
        assert any(v.rule_id == 'WARMUP_INSUFFICIENT' for v in violations)


# =============================================================================
# POST-GENERATION SANITIZATION TESTS
# =============================================================================

class TestPostGenerationSanitization:
    """Tests for post-generation sanitization."""
    
    def test_red_status_returns_recovery_only(self, validator, severely_injured_player, full_training_program):
        """RED status sanitization should return recovery-only plan."""
        context = validator.compute_safety_context(severely_injured_player)
        
        sanitized, modifications = validator.sanitize_program(full_training_program, context)
        
        assert sanitized.plan_type == 'recovery_only'
        assert sanitized.safety_status == SafetyStatus.RED
        assert sanitized.weekly_plan.sprint_days_count == 0
        assert sanitized.weekly_plan.hard_days_count == 0
        assert len(modifications) > 0
    
    def test_yellow_status_reduces_intensity(self, validator, injured_player, full_training_program):
        """YELLOW status sanitization should reduce intensity."""
        context = validator.compute_safety_context(injured_player)
        
        # Modify program to have too many hard days
        for day in full_training_program.weekly_plan.days:
            if day.day_type == 'training':
                day.intensity = 'high'
        full_training_program.weekly_plan.hard_days_count = 5
        
        sanitized, modifications = validator.sanitize_program(full_training_program, context)
        
        # Should cap hard days
        assert sanitized.weekly_plan.hard_days_count <= 2
        assert sanitized.is_validated is True
    
    def test_age_limits_enforced_in_sanitization(self, validator, young_player):
        """Sanitization should enforce age-based sprint limits."""
        context = validator.compute_safety_context(young_player)
        
        # Create program with 3 sprint days for 12-year-old
        days = []
        for i in range(1, 8):
            days.append(DayPlan(
                day_number=i,
                day_type='training' if i <= 5 else 'rest',
                intensity='high' if i <= 3 else 'moderate',
                drills=[DrillSelection(
                    drill_id=f'sprint_{i}',
                    name='Sprint Training',
                    section='speed_agility',
                    intensity='high'
                )] if i <= 3 else [],
                warmup_duration_min=10,
                cooldown_duration_min=6
            ))
        
        program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.GREEN,
            weekly_plan=WeeklyPlan(
                week_number=1,
                days=days,
                sprint_days_count=3,
                hard_days_count=3,
                rest_days_count=2
            ),
            drills_by_section={'speed_agility': []},
            safety_explanation='Test'
        )
        
        sanitized, modifications = validator.sanitize_program(program, context)
        
        # Should have max 1 sprint day for under 14
        assert sanitized.weekly_plan.sprint_days_count <= 1
        assert any('AGE_SPRINT_LIMIT' in m.safety_rule_applied for m in modifications)
    
    def test_contraindications_filtered(self, validator, injured_player):
        """Drills matching contraindications should be filtered."""
        context = validator.compute_safety_context(injured_player)  # Has hamstring injury
        
        days = [DayPlan(
            day_number=1,
            day_type='training',
            intensity='moderate',
            drills=[
                DrillSelection(
                    drill_id='sprint_hamstring',
                    name='Hamstring Sprint Drill',  # Should be filtered
                    section='speed_agility'
                ),
                DrillSelection(
                    drill_id='technical_passing',
                    name='Technical Passing Drill',  # Should remain
                    section='technical'
                )
            ],
            warmup_duration_min=10,
            cooldown_duration_min=6
        )]
        
        program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.GREEN,
            weekly_plan=WeeklyPlan(week_number=1, days=days, rest_days_count=6),
            drills_by_section={
                'speed_agility': [DrillSelection(
                    drill_id='sprint_hamstring',
                    name='Hamstring Sprint Drill',
                    section='speed_agility'
                )],
                'technical': [DrillSelection(
                    drill_id='technical_passing',
                    name='Technical Passing Drill',
                    section='technical'
                )]
            },
            safety_explanation='Test'
        )
        
        sanitized, modifications = validator.sanitize_program(program, context)
        
        # Hamstring drill should be filtered
        assert not any(
            'hamstring' in d.name.lower()
            for d in sanitized.weekly_plan.days[0].drills
        )
        assert any('CONTRAINDICATION' in m.safety_rule_applied for m in modifications)
    
    def test_warmup_cooldown_enforced(self, validator, healthy_player):
        """Warmup and cooldown should be enforced in sanitization."""
        context = validator.compute_safety_context(healthy_player)
        
        days = [DayPlan(
            day_number=1,
            day_type='training',
            intensity='moderate',
            drills=[],
            warmup_duration_min=2,  # Too short
            cooldown_duration_min=2  # Too short
        )]
        
        program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.GREEN,
            weekly_plan=WeeklyPlan(week_number=1, days=days, rest_days_count=6),
            drills_by_section={},
            safety_explanation='Test'
        )
        
        sanitized, modifications = validator.sanitize_program(program, context)
        
        training_day = sanitized.weekly_plan.days[0]
        assert training_day.warmup_duration_min >= 8
        assert training_day.cooldown_duration_min >= 5


# =============================================================================
# UNSAFE PLANS CANNOT PASS TESTS
# =============================================================================

class TestUnsafePlansCannotPass:
    """Critical tests proving unsafe plans CANNOT pass the system."""
    
    def test_red_status_cannot_generate_high_intensity(self, validator, severely_injured_player):
        """
        CRITICAL: RED status must NEVER allow high-intensity training.
        """
        context = validator.compute_safety_context(severely_injured_player)
        
        # Attempt to create high-intensity program for RED status
        high_intensity_program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.RED,
            weekly_plan=WeeklyPlan(
                week_number=1,
                days=[DayPlan(
                    day_number=1,
                    day_type='training',
                    intensity='high',
                    drills=[DrillSelection(
                        drill_id='sprint_1',
                        name='High Intensity Sprint',
                        section='speed_agility',
                        intensity='high'
                    )]
                )],
                sprint_days_count=1,
                hard_days_count=1,
                rest_days_count=0
            ),
            drills_by_section={},
            safety_explanation='Unsafe test'
        )
        
        # Validation should fail
        is_valid, violations = validator.validate_program(high_intensity_program, context)
        assert is_valid is False
        
        # Sanitization should convert to recovery only
        sanitized, mods = validator.sanitize_program(high_intensity_program, context)
        assert sanitized.plan_type == 'recovery_only'
        assert sanitized.weekly_plan.hard_days_count == 0
        assert sanitized.weekly_plan.sprint_days_count == 0
    
    def test_acl_injury_blocks_all_high_risk_activities(self, validator):
        """
        CRITICAL: ACL injury must block plyometrics, cutting, jumping, contact, sprints.
        """
        acl_player = PlayerContext(
            player_id="acl-test",
            player_name="ACL Test Player",
            age=20,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        context = validator.compute_safety_context(acl_player)
        
        # Status should be RED
        assert context.get_effective_status() == SafetyStatus.RED
        
        # All high-risk activities should be excluded
        excluded = context.allowed_elements.excluded_drill_types
        assert 'plyometrics' in excluded
        assert 'contact' in excluded
        assert 'sprint' in excluded
    
    def test_under_14_cannot_exceed_sprint_limit(self, validator, young_player):
        """
        CRITICAL: Under 14 players must NEVER have more than 1 sprint day/week.
        """
        context = validator.compute_safety_context(young_player)
        
        # Even in GREEN status, sprint limit should be 1
        assert context.allowed_elements.max_sprint_days_per_week == 1
        
        # Program with 2 sprint days should fail validation
        program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.GREEN,
            weekly_plan=WeeklyPlan(
                week_number=1,
                days=[],
                sprint_days_count=2,  # Exceeds limit
                hard_days_count=2,
                rest_days_count=2
            ),
            drills_by_section={},
            safety_explanation='Test'
        )
        
        is_valid, violations = validator.validate_program(program, context)
        assert is_valid is False
        assert any('AGE_SPRINT_LIMIT' in v.rule_id for v in violations)
    
    def test_coach_cannot_bypass_safety(self, validator, severely_injured_player):
        """
        CRITICAL: Coach override cannot make RED status less restrictive.
        """
        # Coach tries to override RED to GREEN
        context = validator.compute_safety_context(
            severely_injured_player,
            coach_override_status=SafetyStatus.GREEN,
            coach_override_reason="Coach override attempt"
        )
        
        # Effective status should still be RED
        assert context.get_effective_status() == SafetyStatus.RED
        
        # Allowed elements should still be restrictive
        assert context.allowed_elements.max_sprint_days_per_week == 0
        assert context.allowed_elements.allow_plyometrics is False
    
    def test_critical_acwr_triggers_red_regardless_of_injury_status(self, validator, healthy_player):
        """
        CRITICAL: Critical ACWR (>1.8) must trigger RED even for healthy players.
        """
        critical_load = LoadContext(acwr=2.0)  # Critical level
        
        status, flags = validator.compute_safety_status(healthy_player, critical_load)
        
        assert status == SafetyStatus.RED
        assert any('ACWR_CRITICAL' in f for f in flags)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
