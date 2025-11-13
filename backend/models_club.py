from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, date

# ============ CLUB PORTAL MODELS ============

class Club(BaseModel):
    """Main Club/Academy entity"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    club_code: str  # Unique identifier (e.g., "YOYO-001")
    logo_url: Optional[str] = None
    address: Optional[str] = None
    city: str
    country: str
    established_year: Optional[int] = None
    
    # Contact info
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[EmailStr] = None
    primary_contact_phone: Optional[str] = None
    
    # Club settings
    subscription_tier: str = "basic"  # basic, pro, elite
    active: bool = True
    max_players: int = 500
    max_teams: int = 50
    max_coaches: int = 100
    
    # Branding
    primary_color: str = "#4DFF91"  # Neon green
    secondary_color: str = "#0C1A2A"  # Navy
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClubCreate(BaseModel):
    name: str
    club_code: str
    city: str
    country: str
    primary_contact_email: EmailStr

class Team(BaseModel):
    """Team/Squad within a club"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    name: str  # e.g., "U16 Boys Elite"
    team_code: str  # e.g., "U16-ELITE"
    
    # Team classification
    age_group: str  # U8, U10, U12, U14, U16, U18, U21, Senior
    gender: str  # male, female, mixed
    division: str  # elite, competitive, recreational
    season: str  # e.g., "2024-2025"
    
    # Roster
    player_ids: List[str] = Field(default_factory=list)
    coach_ids: List[str] = Field(default_factory=list)
    captain_player_id: Optional[str] = None
    
    # Training schedule
    training_days: List[str] = Field(default_factory=list)  # ["Monday", "Wednesday", "Friday"]
    training_time: Optional[str] = None  # "18:00"
    training_location: Optional[str] = None
    
    # Performance metrics
    team_avg_physical_score: float = 0.0
    team_avg_technical_score: float = 0.0
    team_avg_tactical_score: float = 0.0
    team_avg_mental_score: float = 0.0
    team_overall_score: float = 0.0
    
    # Safety & workload
    team_safety_score: float = 100.0  # 0-100
    weekly_training_load: float = 0.0
    red_flag_count: int = 0
    
    # Status
    active: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TeamCreate(BaseModel):
    club_id: str
    name: str
    team_code: str
    age_group: str
    gender: str
    division: str
    season: str

class ClubStaff(BaseModel):
    """Staff member at club level (not just coaches)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Links to User in main auth system
    club_id: str
    
    # Personal info
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    
    # Role & permissions
    role: str  # club_admin, technical_director, age_group_lead, head_coach, assistant_coach, medical_staff, analyst
    permissions: List[str] = Field(default_factory=list)
    
    # Assignments
    assigned_team_ids: List[str] = Field(default_factory=list)
    age_group_responsibility: Optional[str] = None  # For age-group leads
    
    # Qualifications
    certifications: List[str] = Field(default_factory=list)
    coaching_license: Optional[str] = None
    years_experience: int = 0
    
    # Status
    active: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClubStaffCreate(BaseModel):
    user_id: str
    club_id: str
    full_name: str
    email: EmailStr
    role: str

class ClubPlayer(BaseModel):
    """Extended player info at club level"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Links to User/Player in main system
    club_id: str
    team_id: Optional[str] = None
    
    # Player info (cached from main system)
    player_name: str
    age: int
    position: str
    dominant_foot: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    
    # Club-specific
    jersey_number: Optional[int] = None
    registration_date: date = Field(default_factory=lambda: date.today())
    contract_end_date: Optional[date] = None
    
    # Guardian info
    parent_name: Optional[str] = None
    parent_email: Optional[str] = None
    parent_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    
    # Performance summary (auto-updated)
    latest_assessment_id: Optional[str] = None
    latest_assessment_date: Optional[datetime] = None
    overall_score: float = 0.0
    physical_score: float = 0.0
    technical_score: float = 0.0
    tactical_score: float = 0.0
    mental_score: float = 0.0
    
    # Training & safety
    total_training_sessions: int = 0
    attendance_rate: float = 0.0
    weekly_training_load: float = 0.0
    safety_status: str = "safe"  # safe, caution, red_flag
    injury_status: str = "healthy"  # healthy, minor_injury, injured, recovering
    
    # Alerts
    has_active_alerts: bool = False
    alert_count: int = 0
    
    # Status
    active: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SafetyAlert(BaseModel):
    """Safety engine alerts for club"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    player_id: str
    team_id: Optional[str] = None
    
    # Alert details
    alert_type: str  # overtraining, fatigue, injury_risk, rapid_load_increase, undertraining
    severity: str  # low, medium, high, critical
    title: str
    description: str
    
    # Metrics
    current_load: Optional[float] = None
    recommended_load: Optional[float] = None
    safety_score: Optional[float] = None
    
    # Actions
    status: str = "active"  # active, acknowledged, resolved, dismissed
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    # Auto-generated recommendations
    ai_recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

class Match(BaseModel):
    """Match/Game event"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    team_id: str
    
    # Match details
    opponent: str
    match_type: str  # league, cup, friendly, tournament
    home_away: str  # home, away, neutral
    
    # Date & time
    match_date: datetime
    match_time: str
    venue: str
    
    # Result (if played)
    played: bool = False
    score_for: Optional[int] = None
    score_against: Optional[int] = None
    result: Optional[str] = None  # win, loss, draw
    
    # Players
    starting_lineup: List[str] = Field(default_factory=list)
    substitutes: List[str] = Field(default_factory=list)
    players_played: List[str] = Field(default_factory=list)
    
    # Analysis
    match_notes: Optional[str] = None
    key_moments: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InjuryRecord(BaseModel):
    """Medical injury tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    player_id: str
    team_id: Optional[str] = None
    
    # Injury details
    injury_type: str
    injury_location: str
    severity: str  # minor, moderate, severe
    diagnosis: str
    
    # Timeline
    injury_date: date
    expected_return_date: Optional[date] = None
    actual_return_date: Optional[date] = None
    days_out: int = 0
    
    # Treatment
    treatment_plan: Optional[str] = None
    rehabilitation_notes: Optional[str] = None
    cleared_for_training: bool = False
    cleared_for_match: bool = False
    
    # Medical staff
    treating_staff: Optional[str] = None
    
    # Status
    status: str = "active"  # active, recovering, cleared
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClubAIInsight(BaseModel):
    """AI-generated insights for club"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    
    # Scope
    insight_type: str  # player, team, club, tactical, safety, performance
    scope: str  # club_wide, team, player
    target_id: Optional[str] = None  # team_id or player_id
    
    # Insight content
    title: str
    description: str
    priority: str  # low, medium, high, critical
    category: str  # development, safety, tactical, technical, injury_prevention
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    
    # Metrics
    confidence_score: float = 0.0
    impact_score: float = 0.0
    
    # Status
    status: str = "active"  # active, acknowledged, implemented, dismissed
    acknowledged_by: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class TrainingSession(BaseModel):
    """Scheduled training session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    team_id: str
    
    # Session details
    session_date: date
    session_time: str
    duration_minutes: int = 90
    session_type: str  # tactical, technical, physical, recovery, match_prep
    
    # Planning
    planned_load: float = 0.0
    planned_intensity: str  # low, medium, high
    focus_areas: List[str] = Field(default_factory=list)
    
    # Execution
    completed: bool = False
    actual_load: Optional[float] = None
    attendance: List[str] = Field(default_factory=list)
    absent_players: List[str] = Field(default_factory=list)
    
    # Coach
    coach_id: str
    session_notes: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClubDrill(BaseModel):
    """Club drill library"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    
    # Drill info
    name: str
    description: str
    category: str  # technical, tactical, physical, warm_up, cool_down
    age_groups: List[str] = Field(default_factory=list)
    
    # Execution
    duration_minutes: int
    players_required: int
    equipment_needed: List[str] = Field(default_factory=list)
    
    # Safety
    intensity_level: str  # low, medium, high
    injury_risk: str  # low, medium, high
    contraindications: List[str] = Field(default_factory=list)
    
    # Media
    video_url: Optional[str] = None
    diagram_url: Optional[str] = None
    
    # Tags
    tags: List[str] = Field(default_factory=list)
    
    # Usage
    times_used: int = 0
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
