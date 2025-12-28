"""
Safety Models
=============

Models for training program safety enforcement.
PLAYER SAFETY IS THE TOP PRIORITY and overrides performance, goals, or user requests.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum


class SafetyStatus(str, Enum):
    """Safety status levels - determines training restrictions."""
    GREEN = "GREEN"   # Full training allowed
    YELLOW = "YELLOW" # Modified training required
    RED = "RED"       # Recovery/RTP only


class InjuryStatus(str, Enum):
    """Player injury status."""
    HEALTHY = "healthy"
    MINOR = "minor"           # Minor discomfort, can train with modifications
    MODERATE = "moderate"     # Injury requiring restrictions
    SEVERE = "severe"         # Requires recovery only
    RETURNING = "returning"   # Return-to-play protocol


class AllowedElements(BaseModel):
    """
    Strict schema defining permitted training components.
    Generated deterministically from SafetyContext.
    """
    max_sprint_days_per_week: int = Field(default=2, ge=0, le=3, description="Max sprint training days")
    max_hard_days_per_week: int = Field(default=3, ge=0, le=5, description="Max high-intensity days")
    allow_plyometrics: bool = Field(default=True, description="Plyometric exercises allowed")
    allow_contact: bool = Field(default=True, description="Contact/competitive drills allowed")
    allow_max_strength: bool = Field(default=True, description="Maximal strength work allowed")
    max_intensity: str = Field(default="high", description="Maximum allowed intensity: low/moderate/high")
    require_warmup: bool = Field(default=True, description="Warmup required (8-12 min)")
    require_cooldown: bool = Field(default=True, description="Cooldown required (5-8 min)")
    min_rest_days_per_week: int = Field(default=1, ge=1, le=3, description="Minimum rest days")
    max_session_duration_min: int = Field(default=90, ge=30, le=120, description="Max session duration")
    
    # Injury-specific restrictions
    excluded_body_parts: List[str] = Field(default_factory=list, description="Body parts to avoid")
    excluded_drill_types: List[str] = Field(default_factory=list, description="Drill types to exclude")
    excluded_contraindications: List[str] = Field(default_factory=list, description="Injury flags to exclude")

    @field_validator('max_intensity')
    @classmethod
    def validate_intensity(cls, v):
        if v not in ['low', 'moderate', 'high']:
            raise ValueError("max_intensity must be 'low', 'moderate', or 'high'")
        return v


class PlayerContext(BaseModel):
    """Player information for safety assessment."""
    player_id: str
    player_name: str
    age: int = Field(..., ge=5, le=50, description="Player age")
    sex: str = Field(default="any", description="male/female/any")
    position: str = Field(default="any", description="Player position")
    injury_status: InjuryStatus = Field(default=InjuryStatus.HEALTHY)
    current_injuries: List[str] = Field(default_factory=list, description="Active injury types")
    injury_history: List[str] = Field(default_factory=list, description="Past injuries")
    
    @field_validator('sex')
    @classmethod
    def validate_sex(cls, v):
        if v not in ['male', 'female', 'any']:
            return 'any'
        return v


class LoadContext(BaseModel):
    """Training load context for safety assessment."""
    acwr: Optional[float] = Field(default=None, ge=0, le=3, description="Acute:Chronic Workload Ratio")
    weekly_load: Optional[float] = Field(default=None, ge=0, description="Weekly training load")
    fatigue_level: Optional[int] = Field(default=None, ge=1, le=5, description="1-5 fatigue scale")
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=5, description="1-5 sleep quality")
    soreness_level: Optional[int] = Field(default=None, ge=1, le=5, description="1-5 soreness scale")
    days_since_last_match: Optional[int] = Field(default=None, ge=0)
    days_to_next_match: Optional[int] = Field(default=None, ge=0)
    consecutive_hard_days: int = Field(default=0, ge=0, le=7)


class AssessmentSummary(BaseModel):
    """Summary of player's assessment for safety context."""
    overall_score: Optional[float] = None
    performance_level: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    vo2_max: Optional[float] = None
    sprint_30m: Optional[float] = None


class SafetyContext(BaseModel):
    """
    Complete safety context for training program generation.
    This MUST be provided to all training generation functions.
    """
    # Core safety status (computed or overridden)
    safety_status: SafetyStatus = Field(default=SafetyStatus.GREEN)
    safety_flags: List[str] = Field(default_factory=list, description="Active safety flags")
    
    # Allowed training elements (generated from context)
    allowed_elements: AllowedElements = Field(default_factory=AllowedElements)
    
    # Context inputs
    player_context: PlayerContext
    load_context: Optional[LoadContext] = None
    assessment_summary: Optional[AssessmentSummary] = None
    
    # Coach override (can only make SAFER, never less safe)
    coach_override_status: Optional[SafetyStatus] = Field(
        default=None,
        description="Coach can override to make status MORE restrictive only"
    )
    coach_override_reason: Optional[str] = None
    
    # Clearance workflow (required to upgrade from RED)
    clearance_granted: bool = Field(default=False, description="Medical clearance for RED->GREEN")
    clearance_date: Optional[datetime] = None
    clearance_provider: Optional[str] = None  # Who provided clearance
    
    # Metadata
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_effective_status(self) -> SafetyStatus:
        """
        Get effective safety status considering coach override.
        Coach can only make it MORE restrictive, never less.
        """
        if self.coach_override_status is None:
            return self.safety_status
        
        # Priority order: RED > YELLOW > GREEN
        priority = {SafetyStatus.RED: 2, SafetyStatus.YELLOW: 1, SafetyStatus.GREEN: 0}
        
        computed_priority = priority[self.safety_status]
        override_priority = priority[self.coach_override_status]
        
        # Coach can only make it MORE restrictive (higher priority)
        if override_priority > computed_priority:
            return self.coach_override_status
        
        return self.safety_status


class PlanModification(BaseModel):
    """Record of a modification made to a training plan for safety."""
    original_element: str
    modified_to: str
    reason: str
    safety_rule_applied: str


class DrillSelection(BaseModel):
    """A drill selected for the training program."""
    drill_id: str
    name: str
    section: str
    duration_min: Optional[int] = None
    intensity: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    source: str = Field(default="database", description="database or static")


class DayPlan(BaseModel):
    """Training plan for a single day."""
    day_number: int
    day_type: str = Field(description="training/rest/recovery/match")
    intensity: str = Field(description="low/moderate/high/rest")
    drills: List[DrillSelection] = Field(default_factory=list)
    warmup_duration_min: int = Field(default=10)
    cooldown_duration_min: int = Field(default=6)
    total_duration_min: int = Field(default=0)
    notes: List[str] = Field(default_factory=list)


class WeeklyPlan(BaseModel):
    """Training plan for a week."""
    week_number: int
    days: List[DayPlan] = Field(default_factory=list)
    sprint_days_count: int = Field(default=0)
    hard_days_count: int = Field(default=0)
    rest_days_count: int = Field(default=0)
    total_load_estimate: float = Field(default=0)


class TrainingProgramOutput(BaseModel):
    """
    MANDATORY OUTPUT FORMAT for all training programs.
    Any output that doesn't include all fields is INVALID.
    """
    # Required fields
    plan_type: str = Field(..., description="full_training/modified_training/recovery_only/rtp_guidance")
    safety_status: SafetyStatus
    safety_flags_triggered: List[str] = Field(default_factory=list)
    
    # Training content
    weekly_plan: WeeklyPlan
    drills_by_section: Dict[str, List[DrillSelection]] = Field(default_factory=dict)
    
    # Safety documentation
    modifications_applied: List[PlanModification] = Field(default_factory=list)
    safety_explanation: str = Field(..., description="Why this plan is safe")
    
    # User controls
    user_controls_offered: List[str] = Field(
        default_factory=list,
        description="Options user can adjust within safe limits"
    )
    
    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generator_version: str = Field(default="1.0.0")
    
    # Validation flag
    is_validated: bool = Field(default=False, description="Post-generation validation passed")


class SafetyViolation(BaseModel):
    """Record of a safety rule violation detected during validation."""
    rule_id: str
    rule_description: str
    violation_details: str
    severity: str = Field(description="warning/error/critical")
    auto_corrected: bool = False
    correction_applied: Optional[str] = None
