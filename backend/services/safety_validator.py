"""
Safety Validator Service
========================

COMPUTES safety status from player/assessment/load data.
VALIDATES and SANITIZES training programs to ensure safety compliance.

PLAYER SAFETY IS THE TOP PRIORITY.

This service provides:
1. Safety status computation (GREEN/YELLOW/RED)
2. Allowed elements generation
3. Post-generation validation/sanitization
4. Coach override handling (can only make safer)
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
import logging

from data_models.safety_models import (
    SafetyStatus, InjuryStatus, AllowedElements, PlayerContext,
    LoadContext, AssessmentSummary, SafetyContext, PlanModification,
    DrillSelection, DayPlan, WeeklyPlan, TrainingProgramOutput,
    SafetyViolation
)

logger = logging.getLogger(__name__)

# =============================================================================
# SAFETY RULES CONSTANTS
# =============================================================================

# Age-based sprint limits
AGE_SPRINT_LIMITS = {
    'under_14': 1,  # Max 1 sprint day/week for < 14 years
    '14_and_over': 2  # Max 2 sprint days/week for >= 14 years
}

# ACWR thresholds
ACWR_THRESHOLDS = {
    'low': 0.8,      # Below = undertraining
    'optimal_low': 0.8,
    'optimal_high': 1.3,
    'high': 1.5,     # Above = injury risk
    'critical': 1.8  # Above = high injury risk
}

# Injury status to safety status mapping
INJURY_TO_SAFETY = {
    InjuryStatus.HEALTHY: SafetyStatus.GREEN,
    InjuryStatus.MINOR: SafetyStatus.YELLOW,
    InjuryStatus.MODERATE: SafetyStatus.YELLOW,
    InjuryStatus.SEVERE: SafetyStatus.RED,
    InjuryStatus.RETURNING: SafetyStatus.RED  # Until cleared
}

# Body part to contraindication mapping
BODY_PART_CONTRAINDICATIONS = {
    'hamstring': ['sprint', 'plyometrics', 'high_intensity'],
    'knee': ['plyometrics', 'cutting', 'jumping', 'contact'],
    'acl': ['plyometrics', 'cutting', 'jumping', 'contact', 'sprint'],
    'ankle': ['agility', 'cutting', 'lateral_movement'],
    'groin': ['sprint', 'kicking', 'lateral_movement'],
    'back': ['strength', 'lifting', 'plyometrics'],
    'shoulder': ['contact', 'throwing'],
    'calf': ['sprint', 'jumping', 'plyometrics'],
    'quad': ['sprint', 'plyometrics', 'kicking'],
    'hip': ['sprint', 'lateral_movement', 'kicking'],
    'concussion': ['contact', 'heading', 'high_intensity']
}

# Red status - only these elements allowed
RED_ALLOWED_ELEMENTS = AllowedElements(
    max_sprint_days_per_week=0,
    max_hard_days_per_week=0,
    allow_plyometrics=False,
    allow_contact=False,
    allow_max_strength=False,
    max_intensity='low',
    require_warmup=True,
    require_cooldown=True,
    min_rest_days_per_week=3,
    max_session_duration_min=45,
    excluded_drill_types=['sprint', 'plyometrics', 'contact', 'competitive', 'high_intensity']
)

# Yellow status - modified elements
YELLOW_ALLOWED_ELEMENTS = AllowedElements(
    max_sprint_days_per_week=1,
    max_hard_days_per_week=2,
    allow_plyometrics=False,
    allow_contact=False,
    allow_max_strength=False,
    max_intensity='moderate',
    require_warmup=True,
    require_cooldown=True,
    min_rest_days_per_week=2,
    max_session_duration_min=60
)


class SafetyValidator:
    """Service for computing and enforcing training safety."""
    
    def __init__(self):
        pass
    
    # =========================================================================
    # SAFETY STATUS COMPUTATION
    # =========================================================================
    
    def compute_safety_status(
        self,
        player_context: PlayerContext,
        load_context: Optional[LoadContext] = None,
        assessment_summary: Optional[AssessmentSummary] = None
    ) -> Tuple[SafetyStatus, List[str]]:
        """
        Compute safety status from player data.
        
        Returns:
            Tuple of (SafetyStatus, safety_flags)
        """
        safety_flags = []
        status = SafetyStatus.GREEN
        
        # 1. Check injury status (highest priority)
        injury_status = INJURY_TO_SAFETY.get(player_context.injury_status, SafetyStatus.GREEN)
        if injury_status == SafetyStatus.RED:
            status = SafetyStatus.RED
            safety_flags.append(f"INJURY_STATUS_{player_context.injury_status.value.upper()}")
        elif injury_status == SafetyStatus.YELLOW and status != SafetyStatus.RED:
            status = SafetyStatus.YELLOW
            safety_flags.append(f"INJURY_STATUS_{player_context.injury_status.value.upper()}")
        
        # 2. Check current injuries
        if player_context.current_injuries:
            for injury in player_context.current_injuries:
                injury_lower = injury.lower()
                # Severe injuries trigger RED
                if any(severe in injury_lower for severe in ['acl', 'fracture', 'tear', 'rupture', 'severe']):
                    status = SafetyStatus.RED
                    safety_flags.append(f"CURRENT_INJURY_{injury.upper()}")
                elif status != SafetyStatus.RED:
                    status = SafetyStatus.YELLOW
                    safety_flags.append(f"CURRENT_INJURY_{injury.upper()}")
        
        # 3. Check load context
        if load_context:
            # ACWR check
            if load_context.acwr is not None:
                if load_context.acwr > ACWR_THRESHOLDS['critical']:
                    status = SafetyStatus.RED
                    safety_flags.append(f"ACWR_CRITICAL_{load_context.acwr:.2f}")
                elif load_context.acwr > ACWR_THRESHOLDS['high'] and status != SafetyStatus.RED:
                    status = SafetyStatus.YELLOW
                    safety_flags.append(f"ACWR_HIGH_{load_context.acwr:.2f}")
            
            # Fatigue check
            if load_context.fatigue_level is not None:
                if load_context.fatigue_level >= 5:
                    if status != SafetyStatus.RED:
                        status = SafetyStatus.YELLOW
                    safety_flags.append("FATIGUE_LEVEL_HIGH")
            
            # Soreness check
            if load_context.soreness_level is not None:
                if load_context.soreness_level >= 4:
                    if status != SafetyStatus.RED:
                        status = SafetyStatus.YELLOW
                    safety_flags.append("SORENESS_HIGH")
            
            # Consecutive hard days check
            if load_context.consecutive_hard_days >= 3:
                if status != SafetyStatus.RED:
                    status = SafetyStatus.YELLOW
                safety_flags.append(f"CONSECUTIVE_HARD_DAYS_{load_context.consecutive_hard_days}")
            
            # Sleep check
            if load_context.sleep_quality is not None and load_context.sleep_quality <= 2:
                safety_flags.append("POOR_SLEEP")
        
        # 4. Check assessment risk factors
        if assessment_summary and assessment_summary.risk_factors:
            for risk in assessment_summary.risk_factors:
                safety_flags.append(f"RISK_FACTOR_{risk.upper().replace(' ', '_')}")
        
        logger.info(f"Computed safety status: {status.value} with flags: {safety_flags}")
        return status, safety_flags
    
    # =========================================================================
    # ALLOWED ELEMENTS GENERATION
    # =========================================================================
    
    def generate_allowed_elements(
        self,
        safety_status: SafetyStatus,
        player_context: PlayerContext,
        load_context: Optional[LoadContext] = None
    ) -> AllowedElements:
        """
        Generate allowed training elements based on safety status and player context.
        """
        # Start with status-based defaults
        if safety_status == SafetyStatus.RED:
            elements = RED_ALLOWED_ELEMENTS.model_copy()
        elif safety_status == SafetyStatus.YELLOW:
            elements = YELLOW_ALLOWED_ELEMENTS.model_copy()
        else:
            elements = AllowedElements()
        
        # Apply age-based sprint limits
        if player_context.age < 14:
            elements.max_sprint_days_per_week = min(
                elements.max_sprint_days_per_week,
                AGE_SPRINT_LIMITS['under_14']
            )
        else:
            elements.max_sprint_days_per_week = min(
                elements.max_sprint_days_per_week,
                AGE_SPRINT_LIMITS['14_and_over']
            )
        
        # Build contraindication list from injuries
        excluded_contras = set(elements.excluded_contraindications)
        excluded_drill_types = set(elements.excluded_drill_types)
        excluded_body_parts = set(elements.excluded_body_parts)
        
        for injury in player_context.current_injuries:
            injury_lower = injury.lower()
            excluded_body_parts.add(injury_lower)
            
            # Add drill type exclusions based on body part
            for body_part, contras in BODY_PART_CONTRAINDICATIONS.items():
                if body_part in injury_lower:
                    excluded_contras.add(body_part)
                    excluded_drill_types.update(contras)
        
        elements.excluded_contraindications = list(excluded_contras)
        elements.excluded_drill_types = list(excluded_drill_types)
        elements.excluded_body_parts = list(excluded_body_parts)
        
        return elements
    
    # =========================================================================
    # FULL SAFETY CONTEXT COMPUTATION
    # =========================================================================
    
    def compute_safety_context(
        self,
        player_context: PlayerContext,
        load_context: Optional[LoadContext] = None,
        assessment_summary: Optional[AssessmentSummary] = None,
        coach_override_status: Optional[SafetyStatus] = None,
        coach_override_reason: Optional[str] = None
    ) -> SafetyContext:
        """
        Compute complete SafetyContext from inputs.
        
        This is the main entry point for safety computation.
        """
        # Compute base safety status
        safety_status, safety_flags = self.compute_safety_status(
            player_context, load_context, assessment_summary
        )
        
        # Generate allowed elements
        allowed_elements = self.generate_allowed_elements(
            safety_status, player_context, load_context
        )
        
        # Create context
        context = SafetyContext(
            safety_status=safety_status,
            safety_flags=safety_flags,
            allowed_elements=allowed_elements,
            player_context=player_context,
            load_context=load_context,
            assessment_summary=assessment_summary,
            coach_override_status=coach_override_status,
            coach_override_reason=coach_override_reason
        )
        
        logger.info(
            f"Computed SafetyContext for {player_context.player_name}: "
            f"status={context.get_effective_status().value}"
        )
        
        return context
    
    # =========================================================================
    # POST-GENERATION VALIDATION
    # =========================================================================
    
    def validate_program(
        self,
        program: TrainingProgramOutput,
        safety_context: SafetyContext
    ) -> Tuple[bool, List[SafetyViolation]]:
        """
        Validate a generated training program against safety rules.
        
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        effective_status = safety_context.get_effective_status()
        allowed = safety_context.allowed_elements
        
        # Rule 1: RED status must be recovery/RTP only
        if effective_status == SafetyStatus.RED:
            if program.plan_type not in ['recovery_only', 'rtp_guidance']:
                violations.append(SafetyViolation(
                    rule_id="RED_STATUS_PLAN_TYPE",
                    rule_description="RED status requires recovery_only or rtp_guidance plan",
                    violation_details=f"Plan type is {program.plan_type}",
                    severity="critical"
                ))
        
        # Rule 2: Check sprint days
        if program.weekly_plan.sprint_days_count > allowed.max_sprint_days_per_week:
            violations.append(SafetyViolation(
                rule_id="SPRINT_DAYS_EXCEEDED",
                rule_description=f"Max {allowed.max_sprint_days_per_week} sprint days allowed",
                violation_details=f"Plan has {program.weekly_plan.sprint_days_count} sprint days",
                severity="error"
            ))
        
        # Rule 3: Check hard days
        if program.weekly_plan.hard_days_count > allowed.max_hard_days_per_week:
            violations.append(SafetyViolation(
                rule_id="HARD_DAYS_EXCEEDED",
                rule_description=f"Max {allowed.max_hard_days_per_week} hard days allowed",
                violation_details=f"Plan has {program.weekly_plan.hard_days_count} hard days",
                severity="error"
            ))
        
        # Rule 4: Check rest days
        if program.weekly_plan.rest_days_count < allowed.min_rest_days_per_week:
            violations.append(SafetyViolation(
                rule_id="INSUFFICIENT_REST_DAYS",
                rule_description=f"Min {allowed.min_rest_days_per_week} rest days required",
                violation_details=f"Plan has {program.weekly_plan.rest_days_count} rest days",
                severity="error"
            ))
        
        # Rule 5: Check warmup/cooldown
        for day in program.weekly_plan.days:
            if day.day_type == 'training':
                if allowed.require_warmup and day.warmup_duration_min < 8:
                    violations.append(SafetyViolation(
                        rule_id="WARMUP_INSUFFICIENT",
                        rule_description="Warmup must be 8-12 minutes",
                        violation_details=f"Day {day.day_number} has {day.warmup_duration_min} min warmup",
                        severity="error"
                    ))
                if allowed.require_cooldown and day.cooldown_duration_min < 5:
                    violations.append(SafetyViolation(
                        rule_id="COOLDOWN_INSUFFICIENT",
                        rule_description="Cooldown must be 5-8 minutes",
                        violation_details=f"Day {day.day_number} has {day.cooldown_duration_min} min cooldown",
                        severity="error"
                    ))
        
        # Rule 6: Check for excluded drill types
        for section, drills in program.drills_by_section.items():
            for drill in drills:
                # Check intensity
                if drill.intensity and drill.intensity == 'high' and allowed.max_intensity != 'high':
                    violations.append(SafetyViolation(
                        rule_id="INTENSITY_EXCEEDED",
                        rule_description=f"Max intensity allowed is {allowed.max_intensity}",
                        violation_details=f"Drill {drill.drill_id} has intensity {drill.intensity}",
                        severity="error"
                    ))
                
                # Check excluded sections
                if section in allowed.excluded_drill_types:
                    violations.append(SafetyViolation(
                        rule_id="EXCLUDED_DRILL_TYPE",
                        rule_description=f"Drill type {section} is excluded",
                        violation_details=f"Drill {drill.drill_id} is in excluded section {section}",
                        severity="error"
                    ))
        
        # Rule 7: Check age-based sprint limits (redundant but explicit)
        age = safety_context.player_context.age
        max_sprints = AGE_SPRINT_LIMITS['under_14'] if age < 14 else AGE_SPRINT_LIMITS['14_and_over']
        if program.weekly_plan.sprint_days_count > max_sprints:
            violations.append(SafetyViolation(
                rule_id="AGE_SPRINT_LIMIT_EXCEEDED",
                rule_description=f"Age {age}: max {max_sprints} sprint days/week",
                violation_details=f"Plan has {program.weekly_plan.sprint_days_count} sprint days",
                severity="critical"
            ))
        
        is_valid = not any(v.severity in ['error', 'critical'] for v in violations)
        
        logger.info(
            f"Program validation: valid={is_valid}, violations={len(violations)}"
        )
        
        return is_valid, violations
    
    # =========================================================================
    # POST-GENERATION SANITIZATION
    # =========================================================================
    
    def sanitize_program(
        self,
        program: TrainingProgramOutput,
        safety_context: SafetyContext
    ) -> Tuple[TrainingProgramOutput, List[PlanModification]]:
        """
        Sanitize a training program to comply with safety rules.
        
        This is a deterministic post-processor that:
        - RED: Returns recovery/RTP only, ignoring unsafe generated content
        - YELLOW: Auto-modifies to comply with restrictions
        - GREEN: Enforces age limits and rest days
        
        Returns:
            Tuple of (sanitized_program, modifications_made)
        """
        effective_status = safety_context.get_effective_status()
        allowed = safety_context.allowed_elements
        modifications = []
        
        # Make a copy to modify
        sanitized = program.model_copy(deep=True)
        
        # RED STATUS: Return recovery only
        if effective_status == SafetyStatus.RED:
            if sanitized.plan_type not in ['recovery_only', 'rtp_guidance']:
                modifications.append(PlanModification(
                    original_element=f"plan_type:{sanitized.plan_type}",
                    modified_to="recovery_only",
                    reason="RED safety status requires recovery only",
                    safety_rule_applied="RED_STATUS_RECOVERY_ONLY"
                ))
                sanitized = self._generate_recovery_only_plan(safety_context)
                sanitized.modifications_applied = modifications
                sanitized.is_validated = True
                return sanitized, modifications
        
        # YELLOW STATUS: Auto-modify
        if effective_status == SafetyStatus.YELLOW:
            sanitized, yellow_mods = self._apply_yellow_modifications(sanitized, safety_context)
            modifications.extend(yellow_mods)
        
        # ALL STATUSES: Enforce age limits and structure
        sanitized, age_mods = self._enforce_age_limits(sanitized, safety_context)
        modifications.extend(age_mods)
        
        sanitized, structure_mods = self._enforce_structure(sanitized, safety_context)
        modifications.extend(structure_mods)
        
        # Filter drills by contraindications
        sanitized, drill_mods = self._filter_drills(sanitized, safety_context)
        modifications.extend(drill_mods)
        
        # Update counts
        sanitized = self._recount_days(sanitized)
        
        # Mark as validated
        sanitized.modifications_applied = modifications
        sanitized.safety_flags_triggered = safety_context.safety_flags
        sanitized.is_validated = True
        
        logger.info(f"Sanitized program with {len(modifications)} modifications")
        
        return sanitized, modifications
    
    def _generate_recovery_only_plan(self, safety_context: SafetyContext) -> TrainingProgramOutput:
        """Generate a recovery-only plan for RED status."""
        # Create 7-day recovery plan
        days = []
        for i in range(1, 8):
            if i in [1, 4, 7]:  # Rest days
                days.append(DayPlan(
                    day_number=i,
                    day_type='rest',
                    intensity='rest',
                    drills=[],
                    warmup_duration_min=0,
                    cooldown_duration_min=0,
                    notes=['Complete rest day', 'Light walking allowed', 'Focus on nutrition and sleep']
                ))
            else:  # Recovery/mobility days
                days.append(DayPlan(
                    day_number=i,
                    day_type='recovery',
                    intensity='low',
                    drills=[
                        DrillSelection(
                            drill_id='recovery_mobility',
                            name='Mobility & Flexibility',
                            section='mobility',
                            duration_min=15,
                            intensity='low',
                            source='static'
                        ),
                        DrillSelection(
                            drill_id='recovery_breathing',
                            name='Breathing Exercises',
                            section='recovery',
                            duration_min=10,
                            intensity='low',
                            source='static'
                        )
                    ],
                    warmup_duration_min=5,
                    cooldown_duration_min=5,
                    total_duration_min=35,
                    notes=['Low intensity only', 'Stop if any discomfort']
                ))
        
        weekly_plan = WeeklyPlan(
            week_number=1,
            days=days,
            sprint_days_count=0,
            hard_days_count=0,
            rest_days_count=3
        )
        
        return TrainingProgramOutput(
            plan_type='recovery_only',
            safety_status=SafetyStatus.RED,
            safety_flags_triggered=safety_context.safety_flags,
            weekly_plan=weekly_plan,
            drills_by_section={
                'mobility': [d for day in days for d in day.drills if d.section == 'mobility'],
                'recovery': [d for day in days for d in day.drills if d.section == 'recovery']
            },
            safety_explanation=(
                f"RED safety status triggered by: {', '.join(safety_context.safety_flags)}. "
                "High-intensity training is blocked. This plan provides safe recovery activities only. "
                "Medical clearance required to return to full training."
            ),
            user_controls_offered=[
                'Can add light walking',
                'Can adjust rest day timing',
                'Cannot increase intensity'
            ]
        )
    
    def _apply_yellow_modifications(self, program: TrainingProgramOutput, safety_context: SafetyContext):
        """Apply YELLOW status modifications."""
        modifications = []
        allowed = safety_context.allowed_elements
        
        # Cap hard days
        hard_count = 0
        for day in program.weekly_plan.days:
            if day.intensity == 'high':
                hard_count += 1
                if hard_count > allowed.max_hard_days_per_week:
                    modifications.append(PlanModification(
                        original_element=f"day_{day.day_number}_intensity:high",
                        modified_to="moderate",
                        reason=f"YELLOW status caps hard days at {allowed.max_hard_days_per_week}",
                        safety_rule_applied="YELLOW_HARD_DAY_CAP"
                    ))
                    day.intensity = 'moderate'
        
        # Remove plyometrics if not allowed
        if not allowed.allow_plyometrics:
            for section, drills in program.drills_by_section.items():
                if section == 'speed_agility':
                    filtered = []
                    for drill in drills:
                        if 'plyo' in drill.name.lower() or 'jump' in drill.name.lower():
                            modifications.append(PlanModification(
                                original_element=f"drill:{drill.drill_id}",
                                modified_to="removed",
                                reason="Plyometrics not allowed in YELLOW status",
                                safety_rule_applied="YELLOW_NO_PLYOMETRICS"
                            ))
                        else:
                            filtered.append(drill)
                    program.drills_by_section[section] = filtered
        
        # Remove contact drills if not allowed
        if not allowed.allow_contact:
            for section, drills in program.drills_by_section.items():
                filtered = []
                for drill in drills:
                    if 'contact' in drill.name.lower() or 'duel' in drill.name.lower():
                        modifications.append(PlanModification(
                            original_element=f"drill:{drill.drill_id}",
                            modified_to="removed",
                            reason="Contact drills not allowed in YELLOW status",
                            safety_rule_applied="YELLOW_NO_CONTACT"
                        ))
                    else:
                        filtered.append(drill)
                program.drills_by_section[section] = filtered
        
        return program, modifications
    
    def _enforce_age_limits(self, program: TrainingProgramOutput, safety_context: SafetyContext):
        """Enforce age-based limits."""
        modifications = []
        age = safety_context.player_context.age
        max_sprints = AGE_SPRINT_LIMITS['under_14'] if age < 14 else AGE_SPRINT_LIMITS['14_and_over']
        
        # Count and limit sprint days
        sprint_count = 0
        for day in program.weekly_plan.days:
            has_sprint = any(
                'sprint' in d.name.lower() or d.section == 'speed_agility'
                for d in day.drills
            )
            if has_sprint:
                sprint_count += 1
                if sprint_count > max_sprints:
                    # Remove sprint drills from this day
                    day.drills = [d for d in day.drills if 'sprint' not in d.name.lower() and d.section != 'speed_agility']
                    modifications.append(PlanModification(
                        original_element=f"day_{day.day_number}_sprint_drills",
                        modified_to="removed",
                        reason=f"Age {age}: max {max_sprints} sprint days/week",
                        safety_rule_applied="AGE_SPRINT_LIMIT"
                    ))
        
        return program, modifications
    
    def _enforce_structure(self, program: TrainingProgramOutput, safety_context: SafetyContext):
        """Enforce warmup, cooldown, rest days."""
        modifications = []
        allowed = safety_context.allowed_elements
        
        rest_count = sum(1 for d in program.weekly_plan.days if d.day_type == 'rest')
        
        # Add rest days if needed
        if rest_count < allowed.min_rest_days_per_week:
            # Convert lowest intensity training days to rest
            training_days = [(i, d) for i, d in enumerate(program.weekly_plan.days) if d.day_type == 'training']
            training_days.sort(key=lambda x: {'low': 0, 'moderate': 1, 'high': 2}.get(x[1].intensity, 0))
            
            needed = allowed.min_rest_days_per_week - rest_count
            for idx, (i, day) in enumerate(training_days[:needed]):
                program.weekly_plan.days[i].day_type = 'rest'
                program.weekly_plan.days[i].intensity = 'rest'
                program.weekly_plan.days[i].drills = []
                modifications.append(PlanModification(
                    original_element=f"day_{day.day_number}_training",
                    modified_to="rest",
                    reason=f"Min {allowed.min_rest_days_per_week} rest days required",
                    safety_rule_applied="MIN_REST_DAYS"
                ))
        
        # Ensure warmup/cooldown
        for day in program.weekly_plan.days:
            if day.day_type == 'training':
                if allowed.require_warmup and day.warmup_duration_min < 8:
                    modifications.append(PlanModification(
                        original_element=f"day_{day.day_number}_warmup:{day.warmup_duration_min}",
                        modified_to="10",
                        reason="Warmup must be 8-12 minutes",
                        safety_rule_applied="WARMUP_REQUIRED"
                    ))
                    day.warmup_duration_min = 10
                
                if allowed.require_cooldown and day.cooldown_duration_min < 5:
                    modifications.append(PlanModification(
                        original_element=f"day_{day.day_number}_cooldown:{day.cooldown_duration_min}",
                        modified_to="6",
                        reason="Cooldown must be 5-8 minutes",
                        safety_rule_applied="COOLDOWN_REQUIRED"
                    ))
                    day.cooldown_duration_min = 6
        
        return program, modifications
    
    def _filter_drills(self, program: TrainingProgramOutput, safety_context: SafetyContext):
        """Filter out drills that violate contraindications."""
        modifications = []
        excluded = set(safety_context.allowed_elements.excluded_contraindications)
        
        if not excluded:
            return program, modifications
        
        for section, drills in program.drills_by_section.items():
            filtered = []
            for drill in drills:
                # Check if drill violates contraindications
                drill_name_lower = drill.name.lower()
                should_exclude = False
                exclude_reason = ""
                
                for contra in excluded:
                    if contra in drill_name_lower:
                        should_exclude = True
                        exclude_reason = contra
                        break
                
                if should_exclude:
                    modifications.append(PlanModification(
                        original_element=f"drill:{drill.drill_id}",
                        modified_to="removed",
                        reason=f"Contraindicated due to: {exclude_reason}",
                        safety_rule_applied="CONTRAINDICATION_FILTER"
                    ))
                else:
                    filtered.append(drill)
            
            program.drills_by_section[section] = filtered
        
        # Also filter from day drills
        for day in program.weekly_plan.days:
            filtered = []
            for drill in day.drills:
                drill_name_lower = drill.name.lower()
                should_include = True
                
                for contra in excluded:
                    if contra in drill_name_lower:
                        should_include = False
                        break
                
                if should_include:
                    filtered.append(drill)
            
            day.drills = filtered
        
        return program, modifications
    
    def _recount_days(self, program: TrainingProgramOutput) -> TrainingProgramOutput:
        """Recount sprint/hard/rest days after modifications."""
        sprint_count = 0
        hard_count = 0
        rest_count = 0
        
        for day in program.weekly_plan.days:
            if day.day_type == 'rest':
                rest_count += 1
            elif day.intensity == 'high':
                hard_count += 1
            
            # Count sprint days
            has_sprint = any(
                'sprint' in d.name.lower() or d.section == 'speed_agility'
                for d in day.drills
            )
            if has_sprint:
                sprint_count += 1
        
        program.weekly_plan.sprint_days_count = sprint_count
        program.weekly_plan.hard_days_count = hard_count
        program.weekly_plan.rest_days_count = rest_count
        
        return program


# Singleton instance
_safety_validator: Optional[SafetyValidator] = None


def get_safety_validator() -> SafetyValidator:
    """Get or create the safety validator singleton."""
    global _safety_validator
    if _safety_validator is None:
        _safety_validator = SafetyValidator()
    return _safety_validator
