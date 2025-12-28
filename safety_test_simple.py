#!/usr/bin/env python3
"""
Safety System Integration Test
==============================

Simplified test to verify the safety system is working correctly.
Uses the same approach as the working unit tests.
"""

import sys
import os
import importlib.util

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Direct import safety_models
_models_spec = importlib.util.spec_from_file_location(
    'safety_models',
    os.path.join(os.path.dirname(__file__), 'backend', 'models', 'safety_models.py')
)
_models_module = importlib.util.module_from_spec(_models_spec)
_models_spec.loader.exec_module(_models_module)

# Import classes
SafetyStatus = _models_module.SafetyStatus
InjuryStatus = _models_module.InjuryStatus
PlayerContext = _models_module.PlayerContext
LoadContext = _models_module.LoadContext
TrainingProgramOutput = _models_module.TrainingProgramOutput
WeeklyPlan = _models_module.WeeklyPlan
DayPlan = _models_module.DayPlan
DrillSelection = _models_module.DrillSelection

# Direct import safety_validator
_validator_spec = importlib.util.spec_from_file_location(
    'safety_validator',
    os.path.join(os.path.dirname(__file__), 'backend', 'services', 'safety_validator.py')
)
_validator_module = importlib.util.module_from_spec(_validator_spec)
_validator_spec.loader.exec_module(_validator_module)
SafetyValidator = _validator_module.SafetyValidator

def test_safety_system():
    """Test the safety system components."""
    print("🔥 TESTING TRAINING PROGRAM SAFETY & DRILL ENFORCEMENT SYSTEM")
    print("=" * 65)
    
    validator = SafetyValidator()
    test_results = []
    
    def log_test(name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {name}"
        if details:
            result += f": {details}"
        test_results.append((name, passed, details))
        print(result)
    
    print("\n🔍 Testing Safety Status Computation...")
    
    # Test 1: Healthy player gets GREEN
    healthy_player = PlayerContext(
        player_id="test-healthy",
        player_name="Healthy Player",
        age=16,
        injury_status=InjuryStatus.HEALTHY,
        current_injuries=[]
    )
    
    status, flags = validator.compute_safety_status(healthy_player)
    log_test(
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
    
    status, flags = validator.compute_safety_status(severe_player)
    log_test(
        "Severe injury gets RED status",
        status == SafetyStatus.RED,
        f"Got {status.value} with flags: {flags}"
    )
    
    # Test 3: Critical ACWR triggers RED
    high_load = LoadContext(acwr=1.9)
    status, flags = validator.compute_safety_status(healthy_player, high_load)
    log_test(
        "Critical ACWR (>1.8) triggers RED",
        status == SafetyStatus.RED and any('ACWR_CRITICAL' in f for f in flags),
        f"ACWR 1.9 -> {status.value} with flags: {flags}"
    )
    
    # Test 4: ACL injury always triggers RED
    acl_player = PlayerContext(
        player_id="test-acl",
        player_name="ACL Player",
        age=20,
        injury_status=InjuryStatus.MODERATE,
        current_injuries=["acl"]
    )
    
    status, flags = validator.compute_safety_status(acl_player)
    log_test(
        "ACL injury triggers RED status",
        status == SafetyStatus.RED,
        f"ACL injury -> {status.value} with flags: {flags}"
    )
    
    print("\n🔧 Testing Allowed Elements Generation...")
    
    # Test 5: RED status blocks high-intensity
    elements = validator.generate_allowed_elements(SafetyStatus.RED, severe_player)
    red_restrictions_correct = (
        elements.max_sprint_days_per_week == 0 and
        elements.max_hard_days_per_week == 0 and
        elements.allow_plyometrics is False and
        elements.allow_contact is False and
        elements.max_intensity == 'low'
    )
    log_test(
        "RED status blocks all high-intensity activities",
        red_restrictions_correct,
        f"Sprint days: {elements.max_sprint_days_per_week}, Hard days: {elements.max_hard_days_per_week}, Plyo: {elements.allow_plyometrics}, Contact: {elements.allow_contact}, Max intensity: {elements.max_intensity}"
    )
    
    # Test 6: GREEN status allows full training
    elements = validator.generate_allowed_elements(SafetyStatus.GREEN, healthy_player)
    green_permissions_correct = (
        elements.max_sprint_days_per_week >= 2 and
        elements.allow_plyometrics is True and
        elements.allow_contact is True and
        elements.max_intensity == 'high'
    )
    log_test(
        "GREEN status allows full training",
        green_permissions_correct,
        f"Sprint days: {elements.max_sprint_days_per_week}, Plyo: {elements.allow_plyometrics}, Contact: {elements.allow_contact}, Max intensity: {elements.max_intensity}"
    )
    
    print("\n👶 Testing Age-Based Sprint Limits...")
    
    # Test 7: Under 14 gets max 1 sprint day
    young_player = PlayerContext(
        player_id="test-young",
        player_name="Young Player",
        age=12,
        injury_status=InjuryStatus.HEALTHY,
        current_injuries=[]
    )
    
    elements = validator.generate_allowed_elements(SafetyStatus.GREEN, young_player)
    log_test(
        "Under 14 players limited to 1 sprint day/week",
        elements.max_sprint_days_per_week == 1,
        f"Age 12 -> {elements.max_sprint_days_per_week} sprint days allowed"
    )
    
    # Test 8: 14+ gets max 2 sprint days
    elements = validator.generate_allowed_elements(SafetyStatus.GREEN, healthy_player)
    log_test(
        "14+ players limited to 2 sprint days/week",
        elements.max_sprint_days_per_week == 2,
        f"Age 16 -> {elements.max_sprint_days_per_week} sprint days allowed"
    )
    
    print("\n🚨 Testing Critical Safety Scenarios...")
    
    # Test 9: ACL injury blocks ALL high-risk activities
    acl_context = validator.compute_safety_context(acl_player)
    excluded = acl_context.allowed_elements.excluded_drill_types
    critical_acl_passed = (
        acl_context.get_effective_status() == SafetyStatus.RED and
        'plyometrics' in excluded and
        'contact' in excluded and
        'sprint' in excluded
    )
    log_test(
        "CRITICAL: ACL injury blocks ALL high-risk activities",
        critical_acl_passed,
        f"Status: {acl_context.get_effective_status().value}, Excluded: {excluded}"
    )
    
    # Test 10: Coach CANNOT bypass safety (RED -> GREEN blocked)
    coach_bypass_context = validator.compute_safety_context(
        severe_player,
        coach_override_status=SafetyStatus.GREEN,
        coach_override_reason="Coach override attempt"
    )
    
    critical_coach_passed = (
        coach_bypass_context.get_effective_status() == SafetyStatus.RED and
        coach_bypass_context.allowed_elements.max_sprint_days_per_week == 0
    )
    log_test(
        "CRITICAL: Coach CANNOT bypass safety (RED -> GREEN blocked)",
        critical_coach_passed,
        f"RED + coach override GREEN -> {coach_bypass_context.get_effective_status().value}, Sprint days: {coach_bypass_context.allowed_elements.max_sprint_days_per_week}"
    )
    
    print("\n✅ Testing Post-Generation Validation...")
    
    # Test 11: RED status rejects full training
    red_context = validator.compute_safety_context(severe_player)
    
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
    
    is_valid, violations = validator.validate_program(unsafe_program, red_context)
    log_test(
        "RED status rejects full training programs",
        not is_valid and any(v.rule_id == 'RED_STATUS_PLAN_TYPE' for v in violations),
        f"Valid: {is_valid}, RED violations: {[v.rule_id for v in violations if 'RED' in v.rule_id]}"
    )
    
    print("\n🧹 Testing Post-Generation Sanitization...")
    
    # Test 12: RED status sanitization returns recovery only
    sanitized, modifications = validator.sanitize_program(unsafe_program, red_context)
    
    sanitization_passed = (
        sanitized.plan_type == 'recovery_only' and 
        sanitized.weekly_plan.sprint_days_count == 0 and
        sanitized.weekly_plan.hard_days_count == 0 and
        len(modifications) > 0
    )
    log_test(
        "RED status sanitization returns recovery-only plan",
        sanitization_passed,
        f"Sanitized: {sanitized.plan_type}, Sprint days: {sanitized.weekly_plan.sprint_days_count}, Hard days: {sanitized.weekly_plan.hard_days_count}, Modifications: {len(modifications)}"
    )
    
    # Print summary
    print("\n" + "=" * 65)
    print("🏆 SAFETY SYSTEM TEST SUMMARY")
    print("=" * 65)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed, _ in test_results if passed)
    failed_tests = [name for name, passed, _ in test_results if not passed]
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"  - {test}")
        return False
    else:
        print(f"\n✅ ALL TESTS PASSED! Safety system is working correctly.")
        print("\n🔒 SAFETY VERIFICATION COMPLETE")
        print("The safety system successfully enforces all critical safety rules.")
        print("Unsafe training plans CANNOT pass the validation and sanitization layers.")
        return True

if __name__ == "__main__":
    success = test_safety_system()
    if success:
        print("\n🎉 SUCCESS: All safety system tests passed!")
        exit(0)
    else:
        print("\n💥 FAILURE: Some tests failed!")
        exit(1)