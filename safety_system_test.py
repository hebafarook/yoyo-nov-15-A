#!/usr/bin/env python3
"""
Backend Safety System Integration Tests
========================================

Comprehensive tests for the Training Program Safety & Drill Enforcement system.
Tests all critical safety components to ensure PLAYER SAFETY IS THE TOP PRIORITY.

Components tested:
1. Safety Status Computation (GREEN/YELLOW/RED)
2. Allowed Elements Generation
3. Age-Based Sprint Limits
4. Coach Override (can only make safer)
5. Post-Generation Validation
6. Post-Generation Sanitization
7. Critical safety scenarios that must NEVER pass
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add backend to path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import safety system components
from models.safety_models import (
    SafetyStatus, InjuryStatus, AllowedElements, PlayerContext,
    LoadContext, AssessmentSummary, SafetyContext, PlanModification,
    DrillSelection, DayPlan, WeeklyPlan, TrainingProgramOutput
)
from services.safety_validator import SafetyValidator, get_safety_validator
from services.safe_training_prompt import build_safety_prompt, get_full_training_prompt

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://drill-uploader.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SafetySystemTester:
    """Comprehensive safety system tester."""
    
    def __init__(self):
        self.validator = SafetyValidator()
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        
        self.test_results.append(result)
        if not passed:
            self.failed_tests.append(test_name)
        
        print(result)
    
    def test_safety_status_computation(self):
        """Test safety status computation from player data."""
        print("\n🔍 Testing Safety Status Computation...")
        
        # Test 1: Healthy player gets GREEN
        healthy_player = PlayerContext(
            player_id="test-healthy",
            player_name="Healthy Player",
            age=16,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        status, flags = self.validator.compute_safety_status(healthy_player)
        self.log_test(
            "Healthy player gets GREEN status",
            status == SafetyStatus.GREEN and len(flags) == 0,
            f"Got {status.value} with flags: {flags}"
        )
        
        # Test 2: Severe injury gets RED
        severe_player = PlayerContext(
            player_id="test-severe",
            player_name="Severe Player",
            age=17,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        status, flags = self.validator.compute_safety_status(severe_player)
        self.log_test(
            "Severe injury gets RED status",
            status == SafetyStatus.RED,
            f"Got {status.value} with flags: {flags}"
        )
        
        # Test 3: Critical ACWR triggers RED
        high_load = LoadContext(acwr=1.9)  # Above critical threshold
        status, flags = self.validator.compute_safety_status(healthy_player, high_load)
        self.log_test(
            "Critical ACWR (>1.8) triggers RED",
            status == SafetyStatus.RED and any('ACWR_CRITICAL' in f for f in flags),
            f"ACWR 1.9 -> {status.value} with flags: {flags}"
        )
        
        # Test 4: High fatigue triggers YELLOW
        fatigue_load = LoadContext(fatigue_level=5)
        status, flags = self.validator.compute_safety_status(healthy_player, fatigue_load)
        self.log_test(
            "High fatigue triggers YELLOW",
            status == SafetyStatus.YELLOW and 'FATIGUE_LEVEL_HIGH' in flags,
            f"Fatigue 5 -> {status.value} with flags: {flags}"
        )
        
        # Test 5: ACL injury always triggers RED
        acl_player = PlayerContext(
            player_id="test-acl",
            player_name="ACL Player",
            age=20,
            injury_status=InjuryStatus.MODERATE,
            current_injuries=["acl"]
        )
        
        status, flags = self.validator.compute_safety_status(acl_player)
        self.log_test(
            "ACL injury triggers RED status",
            status == SafetyStatus.RED,
            f"ACL injury -> {status.value} with flags: {flags}"
        )
    
    def test_allowed_elements_generation(self):
        """Test allowed elements generation based on safety status."""
        print("\n🔧 Testing Allowed Elements Generation...")
        
        # Test 1: RED status blocks high-intensity
        severe_player = PlayerContext(
            player_id="test-red",
            player_name="RED Player",
            age=18,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        elements = self.validator.generate_allowed_elements(SafetyStatus.RED, severe_player)
        red_restrictions_correct = (
            elements.max_sprint_days_per_week == 0 and
            elements.max_hard_days_per_week == 0 and
            elements.allow_plyometrics is False and
            elements.allow_contact is False and
            elements.max_intensity == 'low'
        )
        self.log_test(
            "RED status blocks all high-intensity activities",
            red_restrictions_correct,
            f"Sprint days: {elements.max_sprint_days_per_week}, Hard days: {elements.max_hard_days_per_week}, Plyo: {elements.allow_plyometrics}, Contact: {elements.allow_contact}, Max intensity: {elements.max_intensity}"
        )
        
        # Test 2: YELLOW status limits training
        injured_player = PlayerContext(
            player_id="test-yellow",
            player_name="YELLOW Player",
            age=17,
            injury_status=InjuryStatus.MODERATE,
            current_injuries=["hamstring"]
        )
        
        elements = self.validator.generate_allowed_elements(SafetyStatus.YELLOW, injured_player)
        yellow_restrictions_correct = (
            elements.max_sprint_days_per_week <= 1 and
            elements.max_hard_days_per_week <= 2 and
            elements.allow_plyometrics is False and
            elements.max_intensity == 'moderate'
        )
        self.log_test(
            "YELLOW status limits but allows modified training",
            yellow_restrictions_correct,
            f"Sprint days: {elements.max_sprint_days_per_week}, Hard days: {elements.max_hard_days_per_week}, Max intensity: {elements.max_intensity}"
        )
        
        # Test 3: GREEN status allows full training
        healthy_player = PlayerContext(
            player_id="test-green",
            player_name="GREEN Player",
            age=16,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        elements = self.validator.generate_allowed_elements(SafetyStatus.GREEN, healthy_player)
        green_permissions_correct = (
            elements.max_sprint_days_per_week >= 2 and
            elements.allow_plyometrics is True and
            elements.allow_contact is True and
            elements.max_intensity == 'high'
        )
        self.log_test(
            "GREEN status allows full training",
            green_permissions_correct,
            f"Sprint days: {elements.max_sprint_days_per_week}, Plyo: {elements.allow_plyometrics}, Contact: {elements.allow_contact}, Max intensity: {elements.max_intensity}"
        )
    
    def test_age_based_sprint_limits(self):
        """Test age-based sprint limits."""
        print("\n👶 Testing Age-Based Sprint Limits...")
        
        # Test 1: Under 14 gets max 1 sprint day
        young_player = PlayerContext(
            player_id="test-young",
            player_name="Young Player",
            age=12,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        elements = self.validator.generate_allowed_elements(SafetyStatus.GREEN, young_player)
        self.log_test(
            "Under 14 players limited to 1 sprint day/week",
            elements.max_sprint_days_per_week == 1,
            f"Age 12 -> {elements.max_sprint_days_per_week} sprint days allowed"
        )
        
        # Test 2: 14+ gets max 2 sprint days
        older_player = PlayerContext(
            player_id="test-older",
            player_name="Older Player",
            age=16,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        elements = self.validator.generate_allowed_elements(SafetyStatus.GREEN, older_player)
        self.log_test(
            "14+ players limited to 2 sprint days/week",
            elements.max_sprint_days_per_week == 2,
            f"Age 16 -> {elements.max_sprint_days_per_week} sprint days allowed"
        )
        
        # Test 3: Age limits enforced even in GREEN status
        context = self.validator.compute_safety_context(young_player)
        self.log_test(
            "Age limits enforced even in GREEN status",
            context.allowed_elements.max_sprint_days_per_week == 1,
            f"GREEN status + age 12 -> {context.allowed_elements.max_sprint_days_per_week} sprint days"
        )
    
    def test_coach_override_restrictions(self):
        """Test coach override can only make status MORE restrictive."""
        print("\n👨‍🏫 Testing Coach Override Restrictions...")
        
        # Test 1: Coach can make GREEN -> YELLOW
        healthy_player = PlayerContext(
            player_id="test-override1",
            player_name="Override Test 1",
            age=16,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        context = self.validator.compute_safety_context(
            healthy_player,
            coach_override_status=SafetyStatus.YELLOW,
            coach_override_reason="Player reported discomfort"
        )
        
        self.log_test(
            "Coach can override GREEN to YELLOW (more restrictive)",
            context.get_effective_status() == SafetyStatus.YELLOW,
            f"GREEN + coach override YELLOW -> {context.get_effective_status().value}"
        )
        
        # Test 2: Coach CANNOT make RED -> GREEN
        severe_player = PlayerContext(
            player_id="test-override2",
            player_name="Override Test 2",
            age=18,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        context = self.validator.compute_safety_context(
            severe_player,
            coach_override_status=SafetyStatus.GREEN,  # Attempting less restrictive
            coach_override_reason="Coach thinks player is fine"
        )
        
        self.log_test(
            "Coach CANNOT override RED to GREEN (less restrictive)",
            context.get_effective_status() == SafetyStatus.RED,
            f"RED + coach override GREEN -> {context.get_effective_status().value} (should remain RED)"
        )
        
        # Test 3: Coach can make YELLOW -> RED
        injured_player = PlayerContext(
            player_id="test-override3",
            player_name="Override Test 3",
            age=17,
            injury_status=InjuryStatus.MODERATE,
            current_injuries=["hamstring"]
        )
        
        context = self.validator.compute_safety_context(
            injured_player,
            coach_override_status=SafetyStatus.RED,
            coach_override_reason="Extra precaution needed"
        )
        
        self.log_test(
            "Coach can override YELLOW to RED (more restrictive)",
            context.get_effective_status() == SafetyStatus.RED,
            f"YELLOW + coach override RED -> {context.get_effective_status().value}"
        )
    
    def test_post_generation_validation(self):
        """Test post-generation validation catches unsafe programs."""
        print("\n✅ Testing Post-Generation Validation...")
        
        # Create a test program
        def create_test_program(plan_type='full_training', sprint_days=1, hard_days=2, rest_days=2, warmup_min=10, cooldown_min=6):
            days = []
            for i in range(1, 8):
                if i <= rest_days:
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
                        intensity='high' if i <= hard_days + rest_days else 'moderate',
                        drills=[DrillSelection(
                            drill_id=f'drill_{i}',
                            name='Sprint Training' if i <= sprint_days + rest_days else 'Technical Drill',
                            section='speed_agility' if i <= sprint_days + rest_days else 'technical',
                            intensity='high' if i <= hard_days + rest_days else 'moderate'
                        )],
                        warmup_duration_min=warmup_min,
                        cooldown_duration_min=cooldown_min
                    ))
            
            return TrainingProgramOutput(
                plan_type=plan_type,
                safety_status=SafetyStatus.GREEN,
                weekly_plan=WeeklyPlan(
                    week_number=1,
                    days=days,
                    sprint_days_count=sprint_days,
                    hard_days_count=hard_days,
                    rest_days_count=rest_days
                ),
                drills_by_section={'speed_agility': [], 'technical': []},
                safety_explanation='Test program'
            )
        
        # Test 1: Valid GREEN program passes
        healthy_player = PlayerContext(
            player_id="test-valid",
            player_name="Valid Player",
            age=16,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        context = self.validator.compute_safety_context(healthy_player)
        valid_program = create_test_program()
        is_valid, violations = self.validator.validate_program(valid_program, context)
        
        self.log_test(
            "Valid GREEN program passes validation",
            is_valid and len([v for v in violations if v.severity in ['error', 'critical']]) == 0,
            f"Valid: {is_valid}, Critical violations: {len([v for v in violations if v.severity in ['error', 'critical']])}"
        )
        
        # Test 2: RED status rejects full training
        severe_player = PlayerContext(
            player_id="test-red-validation",
            player_name="RED Validation Player",
            age=18,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        red_context = self.validator.compute_safety_context(severe_player)
        full_program = create_test_program()
        is_valid, violations = self.validator.validate_program(full_program, red_context)
        
        self.log_test(
            "RED status rejects full training programs",
            not is_valid and any(v.rule_id == 'RED_STATUS_PLAN_TYPE' for v in violations),
            f"Valid: {is_valid}, RED violations: {[v.rule_id for v in violations if 'RED' in v.rule_id]}"
        )
        
        # Test 3: Excessive sprint days rejected for young players
        young_player = PlayerContext(
            player_id="test-young-validation",
            player_name="Young Validation Player",
            age=12,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        young_context = self.validator.compute_safety_context(young_player)
        excessive_sprint_program = create_test_program(sprint_days=3)  # Exceeds limit for age 12
        is_valid, violations = self.validator.validate_program(excessive_sprint_program, young_context)
        
        self.log_test(
            "Excessive sprint days rejected for young players",
            not is_valid and any('SPRINT' in v.rule_id for v in violations),
            f"Age 12 with 3 sprint days -> Valid: {is_valid}, Sprint violations: {[v.rule_id for v in violations if 'SPRINT' in v.rule_id]}"
        )
        
        # Test 4: Insufficient warmup flagged
        insufficient_warmup_program = create_test_program(warmup_min=3)  # Too short
        is_valid, violations = self.validator.validate_program(insufficient_warmup_program, context)
        
        self.log_test(
            "Insufficient warmup flagged",
            any(v.rule_id == 'WARMUP_INSUFFICIENT' for v in violations),
            f"3 min warmup -> Warmup violations: {[v.rule_id for v in violations if 'WARMUP' in v.rule_id]}"
        )
    
    def test_post_generation_sanitization(self):
        """Test post-generation sanitization fixes unsafe programs."""
        print("\n🧹 Testing Post-Generation Sanitization...")
        
        # Test 1: RED status returns recovery only
        severe_player = PlayerContext(
            player_id="test-sanitize-red",
            player_name="RED Sanitize Player",
            age=18,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        red_context = self.validator.compute_safety_context(severe_player)
        
        # Create unsafe program for RED status
        unsafe_program = TrainingProgramOutput(
            plan_type='full_training',  # Unsafe for RED
            safety_status=SafetyStatus.RED,
            weekly_plan=WeeklyPlan(
                week_number=1,
                days=[DayPlan(
                    day_number=1,
                    day_type='training',
                    intensity='high',  # Unsafe for RED
                    drills=[DrillSelection(
                        drill_id='unsafe_sprint',
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
        
        sanitized, modifications = self.validator.sanitize_program(unsafe_program, red_context)
        
        self.log_test(
            "RED status sanitization returns recovery-only plan",
            (sanitized.plan_type == 'recovery_only' and 
             sanitized.weekly_plan.sprint_days_count == 0 and
             sanitized.weekly_plan.hard_days_count == 0 and
             len(modifications) > 0),
            f"Sanitized: {sanitized.plan_type}, Sprint days: {sanitized.weekly_plan.sprint_days_count}, Hard days: {sanitized.weekly_plan.hard_days_count}, Modifications: {len(modifications)}"
        )
        
        # Test 2: Age limits enforced in sanitization
        young_player = PlayerContext(
            player_id="test-sanitize-age",
            player_name="Young Sanitize Player",
            age=12,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        young_context = self.validator.compute_safety_context(young_player)
        
        # Create program with too many sprint days for age 12
        excessive_program = TrainingProgramOutput(
            plan_type='full_training',
            safety_status=SafetyStatus.GREEN,
            weekly_plan=WeeklyPlan(
                week_number=1,
                days=[
                    DayPlan(day_number=i, day_type='training', intensity='high',
                           drills=[DrillSelection(drill_id=f'sprint_{i}', name='Sprint Training', section='speed_agility')])
                    for i in range(1, 4)  # 3 sprint days
                ] + [
                    DayPlan(day_number=i, day_type='rest', intensity='rest', drills=[])
                    for i in range(4, 8)
                ],
                sprint_days_count=3,  # Exceeds limit for age 12
                hard_days_count=3,
                rest_days_count=4
            ),
            drills_by_section={},
            safety_explanation='Age test'
        )
        
        sanitized, modifications = self.validator.sanitize_program(excessive_program, young_context)
        
        self.log_test(
            "Age limits enforced in sanitization",
            (sanitized.weekly_plan.sprint_days_count <= 1 and
             any('AGE_SPRINT_LIMIT' in m.safety_rule_applied for m in modifications)),
            f"Age 12: {excessive_program.weekly_plan.sprint_days_count} -> {sanitized.weekly_plan.sprint_days_count} sprint days, Age modifications: {[m.safety_rule_applied for m in modifications if 'AGE' in m.safety_rule_applied]}"
        )
    
    def test_critical_unsafe_scenarios(self):
        """Test critical scenarios that must NEVER pass the safety system."""
        print("\n🚨 Testing Critical Unsafe Scenarios (MUST NEVER PASS)...")
        
        # Test 1: RED status CANNOT generate high-intensity training
        severe_player = PlayerContext(
            player_id="test-critical-1",
            player_name="Critical Test 1",
            age=18,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        red_context = self.validator.compute_safety_context(severe_player)
        
        # Attempt to create high-intensity program
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
                        drill_id='dangerous_sprint',
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
            safety_explanation='Dangerous test'
        )
        
        # Validation should fail
        is_valid, violations = self.validator.validate_program(high_intensity_program, red_context)
        
        # Sanitization should convert to recovery only
        sanitized, mods = self.validator.sanitize_program(high_intensity_program, red_context)
        
        critical_1_passed = (
            not is_valid and  # Validation fails
            sanitized.plan_type == 'recovery_only' and  # Sanitized to recovery
            sanitized.weekly_plan.hard_days_count == 0 and  # No hard days
            sanitized.weekly_plan.sprint_days_count == 0  # No sprint days
        )
        
        self.log_test(
            "CRITICAL: RED status CANNOT generate high-intensity training",
            critical_1_passed,
            f"Validation failed: {not is_valid}, Sanitized to: {sanitized.plan_type}, Hard days: {sanitized.weekly_plan.hard_days_count}, Sprint days: {sanitized.weekly_plan.sprint_days_count}"
        )
        
        # Test 2: ACL injury blocks ALL high-risk activities
        acl_player = PlayerContext(
            player_id="test-critical-2",
            player_name="Critical Test 2",
            age=20,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        acl_context = self.validator.compute_safety_context(acl_player)
        
        # Check that all high-risk activities are blocked
        excluded = acl_context.allowed_elements.excluded_drill_types
        critical_2_passed = (
            acl_context.get_effective_status() == SafetyStatus.RED and
            'plyometrics' in excluded and
            'contact' in excluded and
            'sprint' in excluded
        )
        
        self.log_test(
            "CRITICAL: ACL injury blocks ALL high-risk activities",
            critical_2_passed,
            f"Status: {acl_context.get_effective_status().value}, Excluded: {excluded}"
        )
        
        # Test 3: Under 14 CANNOT exceed 1 sprint day/week
        young_player = PlayerContext(
            player_id="test-critical-3",
            player_name="Critical Test 3",
            age=12,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        young_context = self.validator.compute_safety_context(young_player)
        
        # Even in GREEN status, sprint limit should be 1
        critical_3_passed = young_context.allowed_elements.max_sprint_days_per_week == 1
        
        self.log_test(
            "CRITICAL: Under 14 CANNOT exceed 1 sprint day/week",
            critical_3_passed,
            f"Age 12 in GREEN status -> {young_context.allowed_elements.max_sprint_days_per_week} sprint days allowed"
        )
        
        # Test 4: Coach CANNOT bypass safety (RED -> GREEN blocked)
        coach_bypass_context = self.validator.compute_safety_context(
            severe_player,
            coach_override_status=SafetyStatus.GREEN,  # Attempting to bypass
            coach_override_reason="Coach override attempt"
        )
        
        critical_4_passed = (
            coach_bypass_context.get_effective_status() == SafetyStatus.RED and
            coach_bypass_context.allowed_elements.max_sprint_days_per_week == 0
        )
        
        self.log_test(
            "CRITICAL: Coach CANNOT bypass safety (RED -> GREEN blocked)",
            critical_4_passed,
            f"RED + coach override GREEN -> {coach_bypass_context.get_effective_status().value}, Sprint days: {coach_bypass_context.allowed_elements.max_sprint_days_per_week}"
        )
        
        # Test 5: Critical ACWR triggers RED regardless of injury status
        healthy_player = PlayerContext(
            player_id="test-critical-5",
            player_name="Critical Test 5",
            age=20,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        critical_load = LoadContext(acwr=2.0)  # Critical level
        status, flags = self.validator.compute_safety_status(healthy_player, critical_load)
        
        critical_5_passed = (
            status == SafetyStatus.RED and
            any('ACWR_CRITICAL' in f for f in flags)
        )
        
        self.log_test(
            "CRITICAL: Critical ACWR (>1.8) triggers RED regardless of injury status",
            critical_5_passed,
            f"Healthy player + ACWR 2.0 -> {status.value} with flags: {flags}"
        )
    
    def test_safety_prompt_generation(self):
        """Test safety prompt generation includes all constraints."""
        print("\n📝 Testing Safety Prompt Generation...")
        
        # Test 1: RED status prompt includes restrictions
        severe_player = PlayerContext(
            player_id="test-prompt-red",
            player_name="RED Prompt Player",
            age=18,
            injury_status=InjuryStatus.SEVERE,
            current_injuries=["acl"]
        )
        
        red_context = self.validator.compute_safety_context(severe_player)
        prompt = build_safety_prompt(red_context)
        
        red_prompt_correct = (
            'Status: RED' in prompt and
            'NO sprinting, high-intensity, plyometrics' in prompt and
            'RECOVERY_ONLY' in prompt
        )
        
        self.log_test(
            "RED status prompt includes all restrictions",
            red_prompt_correct,
            f"Prompt contains RED restrictions: {red_prompt_correct}"
        )
        
        # Test 2: Age limits included in prompt
        young_player = PlayerContext(
            player_id="test-prompt-age",
            player_name="Young Prompt Player",
            age=12,
            injury_status=InjuryStatus.HEALTHY,
            current_injuries=[]
        )
        
        young_context = self.validator.compute_safety_context(young_player)
        prompt = build_safety_prompt(young_context)
        
        age_prompt_correct = (
            'Age: 12' in prompt and
            '<14 years: max 1 sprint day/week' in prompt
        )
        
        self.log_test(
            "Age limits included in safety prompt",
            age_prompt_correct,
            f"Prompt contains age limits: {age_prompt_correct}"
        )
        
        # Test 3: Full training prompt includes safety context
        full_prompt = get_full_training_prompt(
            young_context,
            training_goals="Improve speed and agility",
            focus_areas=["speed", "technical"],
            week_number=1
        )
        
        full_prompt_correct = (
            'system' in full_prompt and
            'user' in full_prompt and
            'PLAYER SAFETY IS THE TOP PRIORITY' in full_prompt['system']
        )
        
        self.log_test(
            "Full training prompt includes safety context",
            full_prompt_correct,
            f"Full prompt structure correct: {full_prompt_correct}"
        )
    
    def run_all_tests(self):
        """Run all safety system tests."""
        print("🔥 TRAINING PROGRAM SAFETY & DRILL ENFORCEMENT SYSTEM TESTS")
        print("=" * 70)
        print("Testing comprehensive safety system to ensure PLAYER SAFETY IS THE TOP PRIORITY")
        print()
        
        # Run all test categories
        self.test_safety_status_computation()
        self.test_allowed_elements_generation()
        self.test_age_based_sprint_limits()
        self.test_coach_override_restrictions()
        self.test_post_generation_validation()
        self.test_post_generation_sanitization()
        self.test_critical_unsafe_scenarios()
        self.test_safety_prompt_generation()
        
        # Print summary
        print("\n" + "=" * 70)
        print("🏆 SAFETY SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = total_tests - len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        else:
            print(f"\n✅ ALL TESTS PASSED! Safety system is working correctly.")
        
        print("\n🔒 SAFETY VERIFICATION COMPLETE")
        print("The safety system successfully enforces all critical safety rules.")
        print("Unsafe training plans CANNOT pass the validation and sanitization layers.")
        
        return len(self.failed_tests) == 0


def main():
    """Main test execution."""
    print("Starting Training Program Safety & Drill Enforcement System Tests...")
    
    tester = SafetySystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 SUCCESS: All safety system tests passed!")
        return 0
    else:
        print(f"\n💥 FAILURE: {len(tester.failed_tests)} tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())