from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

# ============ CORE ASSESSMENT MODELS ============
class PlayerAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None  # User who created this assessment
    player_name: str
    age: int
    position: str
    
    # PHYSICAL PERFORMANCE METRICS (20% weight)
    sprint_30m: float  # seconds - 30m sprint test
    yo_yo_test: int  # meters - Yo-Yo Intermittent Recovery Test  
    vo2_max: float  # ml/kg/min - Maximum oxygen uptake
    vertical_jump: int  # cm - Countermovement jump height
    body_fat: float  # percentage - Body fat percentage
    
    # TECHNICAL SKILLS METRICS (40% weight)
    ball_control: int  # 1-5 scale - First touch and ball manipulation under pressure
    passing_accuracy: float  # percentage - Successful passes to target under pressure
    dribbling_success: float  # percentage - Successful 1v1 dribbling attempts
    shooting_accuracy: float  # percentage - Shots on target from various positions
    defensive_duels: float  # percentage - Defensive actions won
    
    # TACTICAL AWARENESS METRICS (30% weight)
    game_intelligence: int  # 1-5 scale - Reading game situations and making smart decisions
    positioning: int  # 1-5 scale - Proper positioning for role
    decision_making: int  # 1-5 scale - Quality of decisions under pressure
    
    # PSYCHOLOGICAL METRICS (10% weight)
    coachability: int  # 1-5 scale - Willingness to learn and apply feedback
    mental_toughness: int  # 1-5 scale - Performance under pressure
    
    # METADATA
    overall_score: Optional[float] = None
    performance_level: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssessmentCreate(BaseModel):
    user_id: Optional[str] = None  # User creating this assessment
    player_name: str
    age: int
    position: str
    # Physical metrics
    sprint_30m: float
    yo_yo_test: int
    vo2_max: float
    vertical_jump: int
    body_fat: float
    # Technical metrics
    ball_control: int
    passing_accuracy: float
    dribbling_success: float
    shooting_accuracy: float
    defensive_duels: float
    # Tactical metrics
    game_intelligence: int
    positioning: int
    decision_making: int
    # Psychological metrics
    coachability: int
    mental_toughness: int

# ============ VO2 MAX BENCHMARK MODELS ============
class VO2MaxBenchmark(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    vo2_max: float  # ml/kg/min
    calculation_inputs: Dict[str, Any]  # stores age, gender, heart rates, etc.
    calculation_method: str = "ACSM"  # ACSM formula or other methods
    test_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None
    fitness_level: Optional[str] = None

class VO2MaxBenchmarkCreate(BaseModel):
    player_id: str
    vo2_max: float
    calculation_inputs: Dict[str, Any]
    calculation_method: str = "ACSM"
    notes: Optional[str] = None
    fitness_level: Optional[str] = None

# ============ ENHANCED TRAINING MODELS ============
class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # "speed", "technical", "tactical", "physical", "psychological"
    description: str  # What the exercise is
    instructions: List[str]  # Step-by-step how to do it
    purpose: str  # Why this exercise is important
    expected_outcome: str  # What should be achieved
    duration: int  # in minutes
    intensity: str  # "low", "medium", "high", "maximum"
    equipment_needed: List[str] = Field(default_factory=list)
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    progression: Optional[Dict[str, Any]] = None

class DailyRoutine(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    day_number: int  # Day within the cycle
    phase: str  # "preparation", "development", "peak", "recovery"
    exercises: List[Exercise]
    total_duration: int  # Total minutes for the day
    intensity_rating: str  # Overall day intensity
    focus_areas: List[str]  # Main areas of focus for the day
    objectives: List[str] = Field(default_factory=list)
    
class ExerciseCompletion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    exercise_id: str
    routine_id: str
    completed: bool = False
    completion_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    feedback: Optional[str] = None  # Player's feedback on the exercise
    difficulty_rating: Optional[int] = None  # 1-5 scale
    performance_rating: Optional[int] = None  # 1-5 scale
    notes: Optional[str] = None
    time_taken: Optional[int] = None  # Actual time taken in minutes

class MicroCycle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "Week 1: Foundation Building"
    cycle_number: int  # Week number
    phase: str  # "preparation", "development", "peak", "recovery"
    daily_routines: List[DailyRoutine]
    objectives: List[str]  # What should be achieved this week
    assessment_metrics: List[str]  # What to track/measure
    
class MacroCycle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "Phase 1: Foundation Building"
    phase_number: int
    duration_weeks: int  # Usually 4-6 weeks
    micro_cycles: List[MicroCycle]
    start_date: datetime
    end_date: datetime
    assessment_date: datetime  # When to reassess
    objectives: List[str]  # Phase objectives
    success_criteria: List[str]  # How to measure success
    
class PeriodizedProgram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    user_id: Optional[str] = None  # Link to user who created the program
    program_name: str
    total_duration_weeks: int
    macro_cycles: List[MacroCycle]
    current_phase: int = 1
    current_week: int = 1
    current_day: int = 1
    program_start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    next_assessment_date: datetime
    program_objectives: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ PROGRESS TRACKING MODELS ============
class DailyProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    routine_id: str
    completed_exercises: List[ExerciseCompletion]
    overall_rating: Optional[int] = None  # 1-5 scale for the day
    energy_level: Optional[int] = None  # 1-5 scale
    motivation_level: Optional[int] = None  # 1-5 scale
    daily_notes: Optional[str] = None
    total_time_spent: Optional[int] = None  # Total minutes

class PerformanceMetric(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    metric_name: str  # e.g., "sprint_30m", "ball_control_rating"
    value: float
    measurement_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    phase_number: int
    week_number: int
    baseline_value: Optional[float] = None  # Starting value
    target_value: Optional[float] = None  # Goal value
    improvement_percentage: Optional[float] = None

class WeeklyProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    week_number: int
    program_id: str
    completed_exercises: List[str]
    performance_notes: str
    intensity_rating: int  # 1-5 scale
    fatigue_level: int  # 1-5 scale
    improvement_areas: List[str]
    week_completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ LEGACY TRAINING MODELS ============
class TrainingProgram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    program_type: str  # "AI_Generated", "Ronaldo_Template", "Custom"
    program_content: str
    weekly_schedule: Dict[str, Any]
    milestones: List[Dict[str, Any]]
    is_group: bool = Field(default=False)
    group_members: List[str] = Field(default_factory=list)
    spotify_playlist: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RetestSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    original_assessment_id: str
    retest_date: datetime
    retest_type: str  # "4_week", "8_week", "seasonal", "custom"
    status: str = "scheduled"  # "scheduled", "completed", "missed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ CREATE MODELS ============
class PeriodizedProgramCreate(BaseModel):
    player_id: str
    program_name: str
    total_duration_weeks: int
    program_objectives: List[str]
    assessment_interval_weeks: int = 4  # Default 4 weeks

class ExerciseCompletionCreate(BaseModel):
    player_id: str
    exercise_id: str
    routine_id: str
    completed: bool = True
    feedback: Optional[str] = None
    difficulty_rating: Optional[int] = None
    performance_rating: Optional[int] = None
    notes: Optional[str] = None
    time_taken: Optional[int] = None

class DailyProgressCreate(BaseModel):
    player_id: str
    routine_id: str
    completed_exercises: List[ExerciseCompletionCreate]
    overall_rating: Optional[int] = None
    energy_level: Optional[int] = None
    motivation_level: Optional[int] = None
    daily_notes: Optional[str] = None
    total_time_spent: Optional[int] = None

# ============ USER PROFILE & AUTH MODELS ============
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True
    role: str = "parent"  # "coach", "parent", "player"
    is_coach: bool = False  # Deprecated - use role instead
    # Player-specific fields (when role="player")
    player_id: Optional[str] = None  # Links to player_name in assessments
    age: Optional[int] = None
    position: Optional[str] = None
    height: Optional[str] = None  # e.g., "175cm"
    weight: Optional[str] = None  # e.g., "68kg"
    dominant_foot: Optional[str] = None  # "Left", "Right", "Both"
    # Coach/Parent management
    managed_players: List[str] = Field(default_factory=list)  # List of player_names or player_ids they can access
    profile_picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    # Password reset fields
    reset_token: Optional[str] = None
    reset_token_expiry: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "parent"  # "coach", "parent", "player"
    is_coach: Optional[bool] = False  # Deprecated
    # Player-specific fields (optional, for when role="player")
    age: Optional[int] = None
    position: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    dominant_foot: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class SavedReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    player_name: str
    assessment_id: str
    report_data: Dict[str, Any]  # Complete report data
    report_type: str  # "startup", "milestone", "manual"
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    title: Optional[str] = None
    notes: Optional[str] = None

class SavedReportCreate(BaseModel):
    player_name: str
    assessment_id: str
    report_data: Dict[str, Any]
    report_type: str = "manual"
    title: Optional[str] = None
    notes: Optional[str] = None

# ============ ASSESSMENT BENCHMARK MODELS ============
class AssessmentBenchmark(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    player_name: str
    assessment_id: str
    
    # Complete assessment data
    age: int
    position: str
    
    # Physical Performance (20%)
    sprint_30m: float
    yo_yo_test: int
    vo2_max: float
    vertical_jump: int
    body_fat: float
    
    # Technical Skills (40%)
    ball_control: int
    passing_accuracy: float
    dribbling_success: float
    shooting_accuracy: float
    defensive_duels: float
    
    # Tactical Awareness (30%)
    game_intelligence: int
    positioning: int
    decision_making: int
    
    # Psychological (10%)
    coachability: int
    mental_toughness: int
    
    # Calculated metrics
    overall_score: float
    performance_level: str
    
    # Benchmark metadata
    benchmark_type: str = "regular"  # "baseline", "regular", "milestone"
    is_baseline: bool = False
    benchmark_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None
    
    # Progress tracking
    improvement_from_baseline: Optional[Dict[str, float]] = None
    previous_benchmark_id: Optional[str] = None

class AssessmentBenchmarkCreate(BaseModel):
    user_id: str
    player_name: str
    assessment_id: str
    age: int
    position: str
    sprint_30m: float
    yo_yo_test: int
    vo2_max: float
    vertical_jump: int
    body_fat: float
    ball_control: int
    passing_accuracy: float
    dribbling_success: float
    shooting_accuracy: float
    defensive_duels: float
    game_intelligence: int
    positioning: int
    decision_making: int
    coachability: int
    mental_toughness: int
    overall_score: float
    performance_level: str
    benchmark_type: str = "regular"
    notes: Optional[str] = None

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    players_managed: List[str] = Field(default_factory=list)  # List of player names
    saved_reports: List[str] = Field(default_factory=list)  # List of saved report IDs
    benchmarks: List[str] = Field(default_factory=list)  # List of benchmark IDs
    baseline_benchmark_id: Optional[str] = None  # First benchmark as baseline
    preferences: Dict[str, Any] = Field(default_factory=dict)
    coaching_level: Optional[str] = None
    organization: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationPreferences(BaseModel):
    user_id: str
    email_notifications: bool = True
    push_notifications: bool = True
    daily_reminders: bool = True
    check_in_reminders: bool = True
    weekly_summaries: bool = True
    achievement_alerts: bool = True
    reminder_time: str = "08:00"  # Default 8 AM
    fcm_token: Optional[str] = None

class CheckInOut(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    player_name: str
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    session_type: str = "training"  # training, match, practice
    notes: Optional[str] = None
    completed: bool = False

class TrainingProgramCreate(BaseModel):
    player_id: str
    program_type: str
    is_group: Optional[bool] = False
    spotify_playlist: Optional[str] = None

class WeeklyProgressCreate(BaseModel):
    player_id: str
    week_number: int
    program_id: str
    completed_exercises: List[str]
    performance_notes: str
    intensity_rating: int
    fatigue_level: int
    improvement_areas: List[str]
    week_completed: bool = False