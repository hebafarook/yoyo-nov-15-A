from fastapi import FastAPI, APIRouter, HTTPException, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import random
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models - Complete Youth Handbook Assessment Framework
class PlayerAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    game_intelligence: int  # 1-5 scale - Reading game situations and anticipation
    positioning: int  # 1-5 scale - Off-ball movement and spatial awareness
    decision_making: int  # 1-5 scale - Speed and quality of decisions under pressure
    
    # PSYCHOLOGICAL TRAITS METRICS (10% weight)
    coachability: int  # 1-5 scale - Ability to receive feedback and implement changes
    mental_toughness: int  # 1-5 scale - Composure and resilience under pressure
    
    # Assessment metadata
    assessment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retest_scheduled: Optional[datetime] = None
    previous_assessment_id: Optional[str] = None  # For tracking progress between retests
    overall_score: Optional[float] = None  # Calculated weighted score
    category_scores: Optional[Dict[str, float]] = None  # Physical, Technical, Tactical, Psychological scores
    
    # Gamification
    total_coins: int = Field(default=0)
    level: int = Field(default=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssessmentCreate(BaseModel):
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

class RetestSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    original_assessment_id: str
    retest_date: datetime
    retest_type: str  # "4_week", "8_week", "seasonal", "custom"
    status: str = Field(default="scheduled")  # "scheduled", "completed", "cancelled"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RetestScheduleCreate(BaseModel):
    player_id: str
    original_assessment_id: str
    retest_date: datetime
    retest_type: str = "4_week"

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

class TrainingProgramCreate(BaseModel):
    player_id: str
    program_type: str
    is_group: Optional[bool] = False
    spotify_playlist: Optional[str] = None

class ProgressEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    metric_type: str  # "speed", "agility", "flexibility", "ball_handling"
    metric_name: str
    value: float
    coins_earned: int = Field(default=0)
    achievement_unlocked: Optional[str] = None
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProgressEntryCreate(BaseModel):
    player_id: str
    metric_type: str
    metric_name: str
    value: float

class VoiceNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    note_text: str
    audio_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VoiceNoteCreate(BaseModel):
    player_id: str
    note_text: str
    audio_duration: Optional[float] = None

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

# Enhanced Training Program Models with Periodization
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

class DailyRoutine(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    day_number: int  # Day within the cycle
    phase: str  # "preparation", "development", "peak", "recovery"
    exercises: List[Exercise]
    total_duration: int  # Total minutes for the day
    intensity_rating: str  # Overall day intensity
    focus_areas: List[str]  # Main areas of focus for the day
    
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

# Progress Tracking Models
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

# Create Models
class PeriodizedProgramCreate(BaseModel):
    player_id: str
    program_name: str
    total_duration_weeks: int
    program_objectives: List[str]
    assessment_interval_weeks: int = 4  # Default 4 weeks
    training_frequency: int = 5  # Default 5 days/week (3, 4, or 5)

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

class Trophy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    trophy_name: str
    trophy_type: str  # "speed", "agility", "consistency", "group", "milestone"
    description: str
    coins_reward: int
    icon: str  # emoji or icon name
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroupTraining(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    training_name: str
    description: str
    members: List[str] = Field(default_factory=list)
    invited_members: List[str] = Field(default_factory=list)
    spotify_playlist: Optional[str] = None
    target_date: Optional[datetime] = None
    completion_reward: int = Field(default=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroupTrainingCreate(BaseModel):
    creator_id: str
    training_name: str
    description: str
    invited_members: List[str] = Field(default_factory=list)
    spotify_playlist: Optional[str] = None
    target_date: Optional[datetime] = None

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    title: str
    message: str
    notification_type: str  # "motivation", "wakeup", "achievement", "group"
    spotify_link: Optional[str] = None
    is_read: bool = Field(default=False)
    scheduled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationCreate(BaseModel):
    player_id: str
    title: str
    message: str
    notification_type: str
    spotify_link: Optional[str] = None
    scheduled_at: Optional[datetime] = None

# Youth Handbook Assessment Standards and Evaluation
YOUTH_HANDBOOK_STANDARDS = {
    "12-14": {
        "sprint_30m": {"excellent": 4.5, "good": 4.7, "average": 4.9, "poor": 5.0},
        "yo_yo_test": {"excellent": 1200, "good": 1000, "average": 900, "poor": 800},
        "vo2_max": {"excellent": 52, "good": 50, "average": 49, "poor": 48},
        "vertical_jump": {"excellent": 40, "good": 35, "average": 32, "poor": 30},
        "body_fat": {"excellent": 12, "good": 15, "average": 16, "poor": 18},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 75, "good": 70, "average": 65, "poor": 60},
        "dribbling_success": {"excellent": 55, "good": 50, "average": 45, "poor": 40},
        "shooting_accuracy": {"excellent": 60, "good": 55, "average": 50, "poor": 45},
        "defensive_duels": {"excellent": 70, "good": 65, "average": 60, "poor": 55},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    },
    "15-16": {
        "sprint_30m": {"excellent": 4.2, "good": 4.4, "average": 4.6, "poor": 4.7},
        "yo_yo_test": {"excellent": 1600, "good": 1400, "average": 1300, "poor": 1200},
        "vo2_max": {"excellent": 56, "good": 54, "average": 53, "poor": 52},
        "vertical_jump": {"excellent": 50, "good": 45, "average": 42, "poor": 40},
        "body_fat": {"excellent": 10, "good": 12, "average": 14, "poor": 15},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 85, "good": 80, "average": 75, "poor": 70},
        "dribbling_success": {"excellent": 65, "good": 60, "average": 55, "poor": 50},
        "shooting_accuracy": {"excellent": 70, "good": 65, "average": 60, "poor": 55},
        "defensive_duels": {"excellent": 75, "good": 70, "average": 65, "poor": 60},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    },
    "17-18": {
        "sprint_30m": {"excellent": 4.0, "good": 4.2, "average": 4.4, "poor": 4.5},
        "yo_yo_test": {"excellent": 2000, "good": 1800, "average": 1700, "poor": 1600},
        "vo2_max": {"excellent": 60, "good": 58, "average": 57, "poor": 56},
        "vertical_jump": {"excellent": 60, "good": 55, "average": 52, "poor": 50},
        "body_fat": {"excellent": 8, "good": 10, "average": 11, "poor": 12},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 90, "good": 85, "average": 80, "poor": 75},
        "dribbling_success": {"excellent": 70, "good": 65, "average": 60, "poor": 55},
        "shooting_accuracy": {"excellent": 75, "good": 70, "average": 65, "poor": 60},
        "defensive_duels": {"excellent": 80, "good": 75, "average": 70, "poor": 65},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    },
    "elite": {
        "sprint_30m": {"excellent": 3.8, "good": 3.9, "average": 4.0, "poor": 4.1},
        "yo_yo_test": {"excellent": 2400, "good": 2300, "average": 2200, "poor": 2100},
        "vo2_max": {"excellent": 65, "good": 62, "average": 60, "poor": 58},
        "vertical_jump": {"excellent": 70, "good": 65, "average": 60, "poor": 55},
        "body_fat": {"excellent": 6, "good": 8, "average": 9, "poor": 10},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 95, "good": 90, "average": 85, "poor": 80},
        "dribbling_success": {"excellent": 75, "good": 70, "average": 65, "poor": 60},
        "shooting_accuracy": {"excellent": 85, "good": 80, "average": 75, "poor": 70},
        "defensive_duels": {"excellent": 85, "good": 80, "average": 75, "poor": 70},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    }
}

ASSESSMENT_WEIGHTS = {
    "technical": 0.40,     # 40%
    "tactical": 0.30,      # 30%
    "physical": 0.20,      # 20%
    "psychological": 0.10  # 10%
}

def get_age_category(age: int) -> str:
    """Get age category based on Youth Handbook standards"""
    if age >= 12 and age <= 14:
        return "12-14"
    elif age >= 15 and age <= 16:
        return "15-16"
    elif age >= 17 and age <= 18:
        return "17-18"
    else:
        return "elite"

def evaluate_performance(value: float, metric: str, age_category: str) -> str:
    """Evaluate performance level based on handbook standards"""
    standards = YOUTH_HANDBOOK_STANDARDS.get(age_category, {}).get(metric)
    if not standards:
        return "average"
    
    excellent, good, average, poor = standards["excellent"], standards["good"], standards["average"], standards["poor"]
    
    # Lower is better for these metrics
    lower_is_better = ["sprint_30m", "body_fat"]
    
    if metric in lower_is_better:
        if value <= excellent:
            return "excellent"
        elif value <= good:
            return "good"
        elif value <= average:
            return "average"
        else:
            return "poor"
    else:
        # Higher is better for all other metrics
        if value >= excellent:
            return "excellent"
        elif value >= good:
            return "good"
        elif value >= average:
            return "average"
        else:
            return "poor"

def calculate_assessment_scores(assessment_data: dict, age: int) -> dict:
    """Calculate comprehensive assessment scores based on Youth Handbook weighting"""
    age_category = get_age_category(age)
    
    # Define metric categories
    physical_metrics = ["sprint_30m", "yo_yo_test", "vo2_max", "vertical_jump", "body_fat"]
    technical_metrics = ["ball_control", "passing_accuracy", "dribbling_success", "shooting_accuracy", "defensive_duels"]
    tactical_metrics = ["game_intelligence", "positioning", "decision_making"]
    psychological_metrics = ["coachability", "mental_toughness"]
    
    score_map = {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    
    def calculate_category_score(metrics):
        total_score = 0
        valid_metrics = 0
        
        for metric in metrics:
            value = assessment_data.get(metric)
            if value is not None:
                performance = evaluate_performance(value, metric, age_category)
                total_score += score_map.get(performance, 3)
                valid_metrics += 1
        
        return total_score / valid_metrics if valid_metrics > 0 else 3
    
    # Calculate category scores
    physical_score = calculate_category_score(physical_metrics)
    technical_score = calculate_category_score(technical_metrics)
    tactical_score = calculate_category_score(tactical_metrics)
    psychological_score = calculate_category_score(psychological_metrics)
    
    # Calculate weighted overall score
    overall_score = (
        physical_score * ASSESSMENT_WEIGHTS["physical"] +
        technical_score * ASSESSMENT_WEIGHTS["technical"] +
        tactical_score * ASSESSMENT_WEIGHTS["tactical"] +
        psychological_score * ASSESSMENT_WEIGHTS["psychological"]
    )
    
    return {
        "overall": round(overall_score, 2),
        "physical": round(physical_score, 2),
        "technical": round(technical_score, 2),
        "tactical": round(tactical_score, 2),
        "psychological": round(psychological_score, 2)
    }
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

# Helper function to parse data from MongoDB
def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and key.endswith('_at'):
                try:
                    item[key] = datetime.fromisoformat(value)
                except:
                    pass
    return item

# Achievement System
async def check_and_award_achievements(player_id: str, progress_entry: ProgressEntry) -> List[Trophy]:
    """Check for achievements and award trophies and coins"""
    trophies_awarded = []
    
    # Get player's progress history
    progress_history = await db.progress.find({"player_id": player_id}).to_list(1000)
    existing_trophies = await db.trophies.find({"player_id": player_id}).to_list(1000)
    existing_trophy_types = [trophy["trophy_type"] for trophy in existing_trophies]
    
    # Speed Achievement
    if progress_entry.metric_type == "speed" and "speed_master" not in existing_trophy_types:
        if progress_entry.value <= 4.0:  # Under 4 seconds for 40m
            trophy = Trophy(
                player_id=player_id,
                trophy_name="سيد السرعة",
                trophy_type="speed_master",
                description="حقق وقت أقل من 4 ثوان في عدو 40 متر",
                coins_reward=200,
                icon="🏃‍♂️"
            )
            trophies_awarded.append(trophy)
    
    # Consistency Achievement
    speed_entries = [p for p in progress_history if p.get("metric_type") == "speed"]
    if len(speed_entries) >= 5 and "consistency_king" not in existing_trophy_types:
        trophy = Trophy(
            player_id=player_id,
            trophy_name="ملك الثبات",
            trophy_type="consistency_king",
            description="سجل 5 إدخالات تقدم في السرعة",
            coins_reward=150,
            icon="👑"
        )
        trophies_awarded.append(trophy)
    
    # Fire Boy Special Achievement
    if progress_entry.metric_type == "ball_handling" and progress_entry.value >= 95 and "fire_boy" not in existing_trophy_types:
        trophy = Trophy(
            player_id=player_id,
            trophy_name="يويو الفتى الناري",
            trophy_type="fire_boy",
            description="حقق دقة 95% أو أكثر في التحكم بالكرة",
            coins_reward=500,
            icon="🔥"
        )
        trophies_awarded.append(trophy)
    
    # Save trophies and update coins
    total_coins_earned = 0
    for trophy in trophies_awarded:
        trophy_data = prepare_for_mongo(trophy.dict())
        await db.trophies.insert_one(trophy_data)
        total_coins_earned += trophy.coins_reward
    
    # Update player coins
    if total_coins_earned > 0:
        await db.assessments.update_one(
            {"id": player_id},
            {"$inc": {"total_coins": total_coins_earned}}
        )
    
    return trophies_awarded

# Enhanced Weekly Progress Tracking
class WeeklyProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    week_number: int  # 1-4 in the cycle
    program_id: str
    completed_exercises: List[str] = Field(default_factory=list)
    performance_notes: str = ""
    intensity_rating: int = Field(ge=1, le=5)  # 1-5 scale
    fatigue_level: int = Field(ge=1, le=5)  # 1-5 scale
    improvement_areas: List[str] = Field(default_factory=list)
    week_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WeeklyProgressCreate(BaseModel):
    player_id: str
    week_number: int
    program_id: str
    completed_exercises: List[str] = Field(default_factory=list)
    performance_notes: str = ""
    intensity_rating: int = Field(ge=1, le=5)
    fatigue_level: int = Field(ge=1, le=5)
    improvement_areas: List[str] = Field(default_factory=list)
    week_completed: bool = Field(default=False)

# Dynamic Exercise Adjustment System
def adjust_exercises_based_on_progress(player_assessment: dict, weekly_progress_history: List[dict]) -> dict:
    """Dynamically adjust exercises based on player progress and performance"""
    
    # Base exercise library
    base_exercises = {
        "speed": {
            "beginner": ["10x30m sprints", "Hill runs (15 min)", "Acceleration drills"],
            "intermediate": ["8x50m sprints", "Hill runs (20 min)", "Resistance sprints"],
            "advanced": ["6x100m sprints", "Hill runs (25 min)", "Parachute sprints"]
        },
        "technical": {
            "beginner": ["Basic juggling (100 touches)", "Cone dribbling", "Wall passes"],
            "intermediate": ["Advanced juggling (300 touches)", "1v1 dribbling", "Shooting drills"],
            "advanced": ["Elite juggling (500+ touches)", "Competition 1v1", "Precision shooting"]
        },
        "tactical": {
            "beginner": ["Position awareness drills", "Basic passing patterns", "Small-sided games"],
            "intermediate": ["Advanced positioning", "Complex passing", "Tactical scenarios"],
            "advanced": ["Elite game reading", "Advanced tactics", "Match simulation"]
        }
    }
    
    # Analyze progress to determine appropriate level
    if not weekly_progress_history:
        return base_exercises
    
    # Calculate average performance metrics
    avg_intensity = sum([p.get("intensity_rating", 3) for p in weekly_progress_history]) / len(weekly_progress_history)
    avg_fatigue = sum([p.get("fatigue_level", 3) for p in weekly_progress_history]) / len(weekly_progress_history)
    completion_rate = sum([1 for p in weekly_progress_history if p.get("week_completed", False)]) / len(weekly_progress_history)
    
    # Determine player level based on assessment and progress
    overall_score = player_assessment.get("overall_score", 3.0)
    
    if overall_score >= 4.5 and completion_rate >= 0.8 and avg_intensity >= 4:
        level = "advanced"
    elif overall_score >= 3.5 and completion_rate >= 0.6 and avg_intensity >= 3:
        level = "intermediate"
    else:
        level = "beginner"
    
    # Adjust based on fatigue levels
    if avg_fatigue >= 4:
        # High fatigue - reduce intensity
        if level == "advanced":
            level = "intermediate"
        elif level == "intermediate":
            level = "beginner"
    
    # Return adjusted exercises
    adjusted_exercises = {}
    for category in base_exercises:
        adjusted_exercises[category] = base_exercises[category][level]
    
    return {
        "level": level,
        "exercises": adjusted_exercises,
        "reasoning": f"Based on overall score: {overall_score}, completion rate: {completion_rate:.1%}, avg intensity: {avg_intensity}/5, avg fatigue: {avg_fatigue}/5"
    }

# Enhanced AI Training Program Generator with Weekly Adaptation
async def generate_adaptive_training_program(assessment: PlayerAssessment, week_number: int = 1, progress_history: List[dict] = None) -> str:
    """Generate training program that adapts based on weekly progress"""
    try:
        # Get dynamic exercise adjustments
        exercise_adjustment = adjust_exercises_based_on_progress(assessment.dict(), progress_history or [])
        
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"training_{assessment.id}_week_{week_number}",
            system_message="أنت مدرب يويو الفتى الناري النخبوي، خبير تدريب كرة قدم محترف ومتقدم. أنشئ برامج تدريبية نخبوية قابلة للتكيف حسب التقدم الأسبوعي. يجب أن تجيب باللغة العربية فقط مع طاقة عالية وحماس نخبوي."
        ).with_model("openai", "gpt-4o")

        # Create comprehensive assessment summary
        assessment_text = f"""
        بيانات تقييم يويو الفتى الناري النخبوي:
        الاسم: {assessment.player_name}
        العمر: {assessment.age} سنة
        المركز: {assessment.position}
        المستوى: {assessment.level}
        النتيجة الإجمالية: {assessment.overall_score}/5.0
        
        الأسبوع الحالي: {week_number}/4
        مستوى التمارين المُحدد: {exercise_adjustment['level']}
        
        المقاييس البدنية (20%):
        - عدو 30 متر: {assessment.sprint_30m} ثانية
        - اختبار يو-يو: {assessment.yo_yo_test} متر
        - الحد الأقصى لاستهلاك الأكسجين: {assessment.vo2_max} مل/كغ/دقيقة
        - القفز العمودي: {assessment.vertical_jump} سم
        - نسبة الدهون: {assessment.body_fat}%
        
        المهارات التقنية (40%):
        - التحكم بالكرة: {assessment.ball_control}/5
        - دقة التمرير: {assessment.passing_accuracy}%
        - نجاح المراوغة: {assessment.dribbling_success}%
        - دقة التسديد: {assessment.shooting_accuracy}%
        - المبارزات الدفاعية: {assessment.defensive_duels}%
        
        الوعي التكتيكي (30%):
        - ذكاء اللعب: {assessment.game_intelligence}/5
        - تحديد المواقع: {assessment.positioning}/5
        - اتخاذ القرار: {assessment.decision_making}/5
        
        الصفات النفسية (10%):
        - قابلية التدريب: {assessment.coachability}/5
        - الصلابة الذهنية: {assessment.mental_toughness}/5
        
        تمارين مُخصصة للأسبوع {week_number}:
        السرعة: {', '.join(exercise_adjustment['exercises']['speed'])}
        التقنية: {', '.join(exercise_adjustment['exercises']['technical'])}
        التكتيك: {', '.join(exercise_adjustment['exercises']['tactical'])}
        
        سبب اختيار المستوى: {exercise_adjustment['reasoning']}
        """

        prompt = f"""
        أنشئ برنامج تدريبي نخبوي متقدم وقابل للتكيف لـ يويو الفتى الناري للأسبوع {week_number}! 🔥👑

        {assessment_text}

        يرجى إنشاء برنامج نخبوي مليء بالطاقة والحماس يتضمن:
        1. تحليل متقدم لنقاط القوة والضعف مع خطة تطوير نخبوية
        2. برنامج تدريبي يومي مفصل للأسبوع {week_number} مع التمارين المُخصصة
        3. أهداف أسبوعية قابلة للقياس مع مؤشرات الأداء
        4. تعديلات على التمارين بناءً على مستوى اللاعب الحالي
        5. نصائح من نجوم كرة القدم النخبة
        6. مؤشرات التقدم المتوقع والإطار الزمني
        7. تحديات نخبوية للأسبوع القادم

        اجعل البرنامج نخبوياً ومليئاً بالتحفيز الملكي! استخدم الرموز التعبيرية والكلمات المحفزة النخبوية.
        
        يجب أن يكون الرد باللغة العربية فقط ومناسب ليويو الفتى الناري النخبوي!
        """

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response

    except Exception as e:
        logging.error(f"خطأ في إنشاء البرنامج التدريبي التكيفي: {e}")
        return "خطأ في إنشاء البرنامج التدريبي النخبوي. يرجى المحاولة مرة أخرى."

# AI Training Program Generator in Arabic
async def generate_ai_training_program(assessment: PlayerAssessment) -> str:
    try:
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"training_{assessment.id}",
            system_message="أنت مدرب يويو الفتى الناري، خبير تدريب كرة قدم محترف ومحفز. أنشئ برامج تدريبية ممتعة ومحفزة للشباب. يجب أن تجيب باللغة العربية فقط مع طاقة عالية وحماس."
        ).with_model("openai", "gpt-4o")

        # Create assessment summary in Arabic using Youth Handbook fields
        assessment_text = f"""
        بيانات تقييم يويو الفتى الناري:
        الاسم: {assessment.player_name}
        العمر: {assessment.age} سنة
        المركز: {assessment.position}
        المستوى: {assessment.level}
        العملات المجمعة: {assessment.total_coins}
        النتيجة الإجمالية: {assessment.overall_score}
        
        المقاييس البدنية (20%):
        - عدو 30 متر: {assessment.sprint_30m} ثانية
        - اختبار يو-يو: {assessment.yo_yo_test} متر
        - الحد الأقصى لاستهلاك الأكسجين: {assessment.vo2_max} مل/كغ/دقيقة
        - القفز العمودي: {assessment.vertical_jump} سم
        - نسبة الدهون: {assessment.body_fat}%
        
        المهارات التقنية (40%):
        - التحكم بالكرة: {assessment.ball_control}/5
        - دقة التمرير: {assessment.passing_accuracy}%
        - نجاح المراوغة: {assessment.dribbling_success}%
        - دقة التسديد: {assessment.shooting_accuracy}%
        - المبارزات الدفاعية: {assessment.defensive_duels}%
        
        الوعي التكتيكي (30%):
        - ذكاء اللعب: {assessment.game_intelligence}/5
        - تحديد المواقع: {assessment.positioning}/5
        - اتخاذ القرار: {assessment.decision_making}/5
        
        الصفات النفسية (10%):
        - قابلية التدريب: {assessment.coachability}/5
        - الصلابة الذهنية: {assessment.mental_toughness}/5
        """

        prompt = f"""
        أنشئ برنامج تدريبي ناري ومحفز لـ يويو الفتى الناري لمدة 8 أسابيع! 🔥

        {assessment_text}

        يرجى إنشاء برنامج مليء بالطاقة والحماس يتضمن:
        1. تحليل نقاط القوة والضعف بطريقة محفزة
        2. تمارين ممتعة ومتحدية لكل نقطة ضعف
        3. أهداف أسبوعية قابلة للتحقيق مع مكافآت
        4. تحديات يومية صغيرة
        5. نصائح من أساطير كرة القدم
        6. كلمات تحفيزية قوية

        اجعل البرنامج مليئاً بالحماس والتشجيع! استخدم الرموز التعبيرية والكلمات المحفزة.
        
        يجب أن يكون الرد باللغة العربية فقط ومناسب ليويو الفتى الناري الشجاع!
        """

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response

    except Exception as e:
        logging.error(f"خطأ في إنشاء برنامج التدريب بالذكاء الاصطناعي: {e}")
        return "خطأ في إنشاء برنامج التدريب. يرجى المحاولة مرة أخرى."
    try:
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"training_{assessment.id}",
            system_message="أنت مدرب يويو الفتى الناري، خبير تدريب كرة قدم محترف ومحفز. أنشئ برامج تدريبية ممتعة ومحفزة للشباب. يجب أن تجيب باللغة العربية فقط مع طاقة عالية وحماس."
        ).with_model("openai", "gpt-4o")

        # Create assessment summary in Arabic using Youth Handbook fields
        assessment_text = f"""
        بيانات تقييم يويو الفتى الناري:
        الاسم: {assessment.player_name}
        العمر: {assessment.age} سنة
        المركز: {assessment.position}
        المستوى: {assessment.level}
        العملات المجمعة: {assessment.total_coins}
        النتيجة الإجمالية: {assessment.overall_score}
        
        المقاييس البدنية (20%):
        - عدو 30 متر: {assessment.sprint_30m} ثانية
        - اختبار يو-يو: {assessment.yo_yo_test} متر
        - الحد الأقصى لاستهلاك الأكسجين: {assessment.vo2_max} مل/كغ/دقيقة
        - القفز العمودي: {assessment.vertical_jump} سم
        - نسبة الدهون: {assessment.body_fat}%
        
        المهارات التقنية (40%):
        - التحكم بالكرة: {assessment.ball_control}/5
        - دقة التمرير: {assessment.passing_accuracy}%
        - نجاح المراوغة: {assessment.dribbling_success}%
        - دقة التسديد: {assessment.shooting_accuracy}%
        - المبارزات الدفاعية: {assessment.defensive_duels}%
        
        الوعي التكتيكي (30%):
        - ذكاء اللعب: {assessment.game_intelligence}/5
        - تحديد المواقع: {assessment.positioning}/5
        - اتخاذ القرار: {assessment.decision_making}/5
        
        الصفات النفسية (10%):
        - قابلية التدريب: {assessment.coachability}/5
        - الصلابة الذهنية: {assessment.mental_toughness}/5
        """

        prompt = f"""
        أنشئ برنامج تدريبي ناري ومحفز لـ يويو الفتى الناري لمدة 8 أسابيع! 🔥

        {assessment_text}

        يرجى إنشاء برنامج مليء بالطاقة والحماس يتضمن:
        1. تحليل نقاط القوة والضعف بطريقة محفزة
        2. تمارين ممتعة ومتحدية لكل نقطة ضعف
        3. أهداف أسبوعية قابلة للتحقيق مع مكافآت
        4. تحديات يومية صغيرة
        5. نصائح من أساطير كرة القدم
        6. كلمات تحفيزية قوية

        اجعل البرنامج مليئاً بالحماس والتشجيع! استخدم الرموز التعبيرية والكلمات المحفزة.
        
        يجب أن يكون الرد باللغة العربية فقط ومناسب ليويو الفتى الناري الشجاع!
        """

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response

    except Exception as e:
        logging.error(f"خطأ في إنشاء برنامج التدريب بالذكاء الاصطناعي: {e}")
        return "خطأ في إنشاء برنامج التدريب. يرجى المحاولة مرة أخرى."

# Routes
@api_router.get("/")
async def root():
    return {"message": "مرحباً بك في عالم يويو الفتى الناري! 🔥⚽"}

@api_router.post("/assessments", response_model=PlayerAssessment)
async def create_assessment(assessment: AssessmentCreate):
    try:
        assessment_dict = assessment.dict()
        
        # Calculate comprehensive scores based on Youth Handbook standards
        scores = calculate_assessment_scores(assessment_dict, assessment.age)
        assessment_dict["overall_score"] = scores["overall"]
        assessment_dict["category_scores"] = {
            "physical": scores["physical"],
            "technical": scores["technical"],
            "tactical": scores["tactical"],
            "psychological": scores["psychological"]
        }
        
        assessment_obj = PlayerAssessment(**assessment_dict)
        assessment_data = prepare_for_mongo(assessment_obj.dict())
        await db.assessments.insert_one(assessment_data)
        
        # CRITICAL FIX: Also save as benchmark for data persistence across logins
        # This ensures users can see their data when they log back in
        try:
            # Check if user has benchmarks already
            existing_benchmarks = await db.benchmarks.find(
                {"player_name": assessment_obj.player_name}
            ).to_list(length=1000)
            
            is_baseline = len(existing_benchmarks) == 0  # First assessment is baseline
            
            benchmark_data = {
                "id": str(uuid.uuid4()),
                "user_id": assessment_obj.user_id if hasattr(assessment_obj, 'user_id') and assessment_obj.user_id else None,
                "player_name": assessment_obj.player_name,
                "assessment_id": assessment_obj.id,
                "age": assessment_obj.age,
                "position": assessment_obj.position,
                # Physical metrics
                "sprint_30m": assessment_obj.sprint_30m,
                "yo_yo_test": assessment_obj.yo_yo_test,
                "vo2_max": assessment_obj.vo2_max,
                "vertical_jump": assessment_obj.vertical_jump,
                "body_fat": assessment_obj.body_fat,
                # Technical metrics
                "ball_control": assessment_obj.ball_control,
                "passing_accuracy": assessment_obj.passing_accuracy,
                "dribbling_success": assessment_obj.dribbling_success,
                "shooting_accuracy": assessment_obj.shooting_accuracy,
                "defensive_duels": assessment_obj.defensive_duels,
                # Tactical metrics
                "game_intelligence": assessment_obj.game_intelligence,
                "positioning": assessment_obj.positioning,
                "decision_making": assessment_obj.decision_making,
                # Psychological metrics
                "coachability": assessment_obj.coachability,
                "mental_toughness": assessment_obj.mental_toughness,
                # Calculated metrics
                "overall_score": assessment_obj.overall_score,
                "performance_level": "Average",  # Default, can be calculated
                "is_baseline": is_baseline,
                "benchmark_type": "baseline" if is_baseline else "regular",
                "benchmark_date": datetime.now(timezone.utc).isoformat(),
                "notes": f"Auto-saved from assessment on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
            }
            
            await db.benchmarks.insert_one(benchmark_data)
            logger.info(f"✅ Auto-saved assessment as benchmark for {assessment_obj.player_name} (baseline: {is_baseline})")
        except Exception as bench_error:
            logger.warning(f"Could not auto-save benchmark: {bench_error}")
            # Don't fail the assessment creation if benchmark save fails
        
        return assessment_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessments", response_model=List[PlayerAssessment])
async def get_assessments(user_id: Optional[str] = None):
    try:
        query = {}
        if user_id:
            query["user_id"] = user_id
            
        assessments = await db.assessments.find(query).to_list(1000)
        valid_assessments = []
        
        for assessment in assessments:
            try:
                # Only include assessments that have the new Youth Handbook fields
                parsed_assessment = parse_from_mongo(assessment)
                if all(field in parsed_assessment for field in ['sprint_30m', 'yo_yo_test', 'vo2_max', 'ball_control', 'game_intelligence', 'coachability']):
                    valid_assessments.append(PlayerAssessment(**parsed_assessment))
            except Exception as e:
                # Skip assessments that don't match the new format
                continue
                
        return valid_assessments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessments/player/{player_name}", response_model=List[PlayerAssessment])
async def get_assessments_by_player(player_name: str):
    """Get all assessments for a specific player by player name"""
    try:
        assessments = await db.assessments.find({"player_name": player_name}).sort("created_at", -1).to_list(1000)
        valid_assessments = []
        
        for assessment in assessments:
            try:
                parsed_assessment = parse_from_mongo(assessment)
                if all(field in parsed_assessment for field in ['sprint_30m', 'yo_yo_test', 'vo2_max', 'ball_control', 'game_intelligence', 'coachability']):
                    valid_assessments.append(PlayerAssessment(**parsed_assessment))
            except Exception as e:
                continue
                
        return valid_assessments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessments/{player_id}", response_model=PlayerAssessment)
async def get_assessment(player_id: str):
    try:
        assessment = await db.assessments.find_one({"id": player_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="لم يتم العثور على تقييم يويو")
        return PlayerAssessment(**parse_from_mongo(assessment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/training-programs", response_model=TrainingProgram)
async def create_training_program(program: TrainingProgramCreate):
    try:
        # Get player assessment
        assessment = await db.assessments.find_one({"id": program.player_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="لم يتم العثور على تقييم يويو")
        
        assessment_obj = PlayerAssessment(**parse_from_mongo(assessment))
        
        # Generate program content based on type
        if program.program_type == "AI_Generated":
            program_content = await generate_ai_training_program(assessment_obj)
            weekly_schedule = {
                "Monday": "تدريب السرعة الناري 🔥",
                "Tuesday": "تحدي التحكم بالكرة ⚽",
                "Wednesday": "يوم المرونة والتعافي 🧘‍♂️",
                "Thursday": "مهارات يويو الفنية ✨",
                "Friday": "معركة محاكاة المباراة ⚔️",
                "Saturday": "تحدي نقاط الضعف 💪",
                "Sunday": "يوم راحة المحارب 😴"
            }
            milestones = [
                {"week": 2, "target": "فتح إنجاز السرعة الأولى 🏃‍♂️", "coins": 50},
                {"week": 4, "target": "كسب لقب محارب الرشاقة ⚡", "coins": 100},
                {"week": 6, "target": "إتقان مهارات يويو الناري 🔥", "coins": 150},
                {"week": 8, "target": "أن تصبح أسطورة يويو 👑", "coins": 300}
            ]
        elif program.program_type == "Ronaldo_Template":
            program_content = """
            🔥 برنامج يويو الفتى الناري المستوحى من رونالدو الأسطورة! 🔥
            
            هذا البرنامج الناري مبني على أسرار تدريب رونالدو:
            - الطاقة الانفجارية والسرعة البرقية ⚡
            - قوة العضلات الأساسية والمرونة المذهلة 💪
            - الدقة الفنية الساحرة ✨
            - العقلية الفولاذية 🧠
            
            🌟 الأسبوع 1-2: بناء أساسات المحارب الناري
            - تمارين القلب النارية يومياً لمدة ساعة 🏃‍♂️
            - تقوية العضلات الأساسية (200 تمرين معدة، بلانك ناري) 🔥
            - تدريبات التحكم بالكرة السحرية (1000 لمسة يومياً) ⚽
            - روتين المرونة الذهبية (30 دقيقة يوغا) 🧘‍♂️
            
            ⚡ الأسبوع 3-4: إشعال الطاقة الكامنة
            - فترات العدو الصاروخية (10x100 متر) 🚀
            - تمارين البليومتريك المتفجرة 💥
            - مهارات الكرة الأسطورية 🌟
            - تدريب الأثقال الناري (التركيز على الساقين) 🦵
            
            🎯 الأسبوع 5-6: إتقان فنون الساحر
            - تمرين الضربات الحرة الذهبية (50 محاولة يومياً) ⚽
            - تدريبات دقة التسديد القاتلة 🎯
            - التمرير والإنهاء الساحر ✨
            - معارك محاكاة المباراة الحقيقية ⚔️
            
            👑 الأسبوع 7-8: تحقيق المجد الأسطوري
            - تدريب الوحش عالي الكثافة 🔥
            - الإعداد النهائي للمنافسة 🏆
            - قوة التصور الذهني الفولاذية 🧠
            - تحسين التعافي الذهبي ✨
            """
            weekly_schedule = {
                "Monday": "يوم القوة والسرعة الناري 🔥",
                "Tuesday": "تحدي المهارات الفنية ✨",
                "Wednesday": "يوم العضلات الأساسية والمرونة 💪",
                "Thursday": "إتقان سحر الكرة ⚽",
                "Friday": "الإعداد الناري للمعركة ⚔️",
                "Saturday": "يوم المجد والمنافسة 🏆",
                "Sunday": "التعافي الذهبي للمحارب ✨"
            }
            milestones = [
                {"week": 2, "target": "إتقان 1000 لمسة سحرية ⚽", "coins": 100},
                {"week": 4, "target": "تحطيم الرقم القياسي في العدو ⚡", "coins": 150},
                {"week": 6, "target": "إتقان 80% من الضربات الحرة 🎯", "coins": 200},
                {"week": 8, "target": "أن تصبح أسطورة مثل رونالدو 👑", "coins": 500}
            ]
        else:
            program_content = "برنامج تدريب يويو المخصص سيتم تحديده قريباً! 🔥"
            weekly_schedule = {}
            milestones = []

        program_obj = TrainingProgram(
            player_id=program.player_id,
            program_type=program.program_type,
            program_content=program_content,
            weekly_schedule=weekly_schedule,
            milestones=milestones,
            is_group=program.is_group or False,
            spotify_playlist=program.spotify_playlist
        )
        
        program_data = prepare_for_mongo(program_obj.dict())
        await db.training_programs.insert_one(program_data)
        return program_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/training-programs/{player_id}", response_model=List[TrainingProgram])
async def get_training_programs(player_id: str):
    try:
        programs = await db.training_programs.find({"player_id": player_id}).to_list(1000)
        return [TrainingProgram(**parse_from_mongo(program)) for program in programs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/progress", response_model=Dict[str, Any])
async def add_progress_entry(progress: ProgressEntryCreate):
    try:
        # Calculate coins based on improvement
        coins_earned = random.randint(10, 50)  # Base coins
        
        progress_obj = ProgressEntry(**progress.dict(), coins_earned=coins_earned)
        progress_data = prepare_for_mongo(progress_obj.dict())
        await db.progress.insert_one(progress_data)
        
        # Check for achievements
        trophies = await check_and_award_achievements(progress.player_id, progress_obj)
        
        return {
            "progress": progress_obj,
            "coins_earned": coins_earned,
            "trophies_unlocked": trophies,
            "message": f"مبروك يويو! حصلت على {coins_earned} عملة ذهبية! 🔥"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/progress/{player_id}", response_model=List[ProgressEntry])
async def get_progress(player_id: str):
    try:
        progress_entries = await db.progress.find({"player_id": player_id}).sort("date", -1).to_list(1000)
        return [ProgressEntry(**parse_from_mongo(entry)) for entry in progress_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trophies/{player_id}", response_model=List[Trophy])
async def get_player_trophies(player_id: str):
    try:
        trophies = await db.trophies.find({"player_id": player_id}).sort("unlocked_at", -1).to_list(1000)
        return [Trophy(**parse_from_mongo(trophy)) for trophy in trophies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Weekly Progress Tracking Endpoints
@api_router.post("/weekly-progress", response_model=WeeklyProgress)
async def create_weekly_progress(progress: WeeklyProgressCreate):
    try:
        progress_obj = WeeklyProgress(**progress.dict())
        progress_data = prepare_for_mongo(progress_obj.dict())
        await db.weekly_progress.insert_one(progress_data)
        return progress_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/weekly-progress/{player_id}", response_model=List[WeeklyProgress])
async def get_weekly_progress(player_id: str):
    try:
        progress_entries = await db.weekly_progress.find({"player_id": player_id}).sort("created_at", -1).to_list(1000)
        return [WeeklyProgress(**parse_from_mongo(entry)) for entry in progress_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/weekly-progress/{player_id}/{program_id}", response_model=List[WeeklyProgress])
async def get_weekly_progress_by_program(player_id: str, program_id: str):
    try:
        progress_entries = await db.weekly_progress.find({
            "player_id": player_id, 
            "program_id": program_id
        }).sort("week_number", 1).to_list(1000)
        return [WeeklyProgress(**parse_from_mongo(entry)) for entry in progress_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/weekly-progress/{progress_id}", response_model=WeeklyProgress)
async def update_weekly_progress(progress_id: str, progress_update: WeeklyProgressCreate):
    try:
        update_data = prepare_for_mongo(progress_update.dict())
        result = await db.weekly_progress.update_one(
            {"id": progress_id},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Weekly progress not found")
        
        updated_progress = await db.weekly_progress.find_one({"id": progress_id})
        return WeeklyProgress(**parse_from_mongo(updated_progress))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Training Program Generation with Weekly Adaptation
@api_router.post("/training-programs/adaptive", response_model=Dict[str, Any])
async def create_adaptive_training_program(request: Dict[str, Any]):
    try:
        player_id = request.get("player_id")
        week_number = request.get("week_number", 1)
        
        # Get player assessment
        assessment = await db.assessments.find_one({"id": player_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="لم يتم العثور على تقييم يويو")
        
        assessment_obj = PlayerAssessment(**parse_from_mongo(assessment))
        
        # Get weekly progress history
        progress_history = await db.weekly_progress.find({"player_id": player_id}).to_list(1000)
        progress_history_dicts = [parse_from_mongo(p) for p in progress_history]
        
        # Generate adaptive program
        program_content = await generate_adaptive_training_program(
            assessment_obj, 
            week_number, 
            progress_history_dicts
        )
        
        return {
            "program_content": program_content,
            "week_number": week_number,
            "player_id": player_id,
            "adaptation_level": "نخبوي متقدم",
            "message": f"تم إنشاء برنامج تدريبي نخبوي للأسبوع {week_number}! 🔥👑"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/group-training", response_model=GroupTraining)
async def create_group_training(group: GroupTrainingCreate):
    try:
        group_obj = GroupTraining(**group.dict())
        group_data = prepare_for_mongo(group_obj.dict())
        await db.group_trainings.insert_one(group_data)
        
        # Send invitations to members
        for member_id in group.invited_members:
            notification = Notification(
                player_id=member_id,
                title="دعوة للتدريب الجماعي! 🔥",
                message=f"يويو يدعوك للانضمام إلى '{group.training_name}'",
                notification_type="group",
                spotify_link=group.spotify_playlist
            )
            notification_data = prepare_for_mongo(notification.dict())
            await db.notifications.insert_one(notification_data)
            
        return group_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/group-training/{player_id}", response_model=List[GroupTraining])
async def get_group_trainings(player_id: str):
    try:
        groups = await db.group_trainings.find({
            "$or": [
                {"creator_id": player_id},
                {"members": player_id},
                {"invited_members": player_id}
            ]
        }).to_list(1000)
        return [GroupTraining(**parse_from_mongo(group)) for group in groups]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications", response_model=Notification)
async def create_notification(notification: NotificationCreate):
    try:
        notification_obj = Notification(**notification.dict())
        notification_data = prepare_for_mongo(notification_obj.dict())
        await db.notifications.insert_one(notification_data)
        return notification_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications/{player_id}", response_model=List[Notification])
async def get_notifications(player_id: str):
    try:
        notifications = await db.notifications.find({"player_id": player_id}).sort("created_at", -1).to_list(1000)
        return [Notification(**parse_from_mongo(notification)) for notification in notifications]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/retests/schedule", response_model=RetestSchedule)
async def schedule_retest(retest: RetestScheduleCreate):
    try:
        retest_obj = RetestSchedule(**retest.dict())
        retest_data = prepare_for_mongo(retest_obj.dict())
        await db.retest_schedules.insert_one(retest_data)
        
        # Create notification for retest
        notification = Notification(
            player_id=retest.player_id,
            title="🔥 Retest Scheduled - Time to Show Your Progress!",
            message=f"Your retest is scheduled for {retest.retest_date.strftime('%B %d, %Y')}. Time to demonstrate your improvements!",
            notification_type="retest",
            scheduled_at=retest.retest_date
        )
        notification_data = prepare_for_mongo(notification.dict())
        await db.notifications.insert_one(notification_data)
        
        return retest_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/retests/{player_id}", response_model=List[RetestSchedule])
async def get_scheduled_retests(player_id: str):
    try:
        retests = await db.retest_schedules.find({"player_id": player_id}).to_list(1000)
        return [RetestSchedule(**parse_from_mongo(retest)) for retest in retests]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/assessments/{assessment_id}/retest")
async def create_retest_assessment(assessment_id: str, assessment: AssessmentCreate):
    try:
        # Get original assessment
        original = await db.assessments.find_one({"id": assessment_id})
        if not original:
            raise HTTPException(status_code=404, detail="Original assessment not found")
        
        assessment_dict = assessment.dict()
        
        # Calculate scores
        scores = calculate_assessment_scores(assessment_dict, assessment.age)
        assessment_dict["overall_score"] = scores["overall"]
        assessment_dict["category_scores"] = scores
        assessment_dict["previous_assessment_id"] = assessment_id
        
        # Create new assessment
        assessment_obj = PlayerAssessment(**assessment_dict)
        assessment_data = prepare_for_mongo(assessment_obj.dict())
        await db.assessments.insert_one(assessment_data)
        
        # Compare with original and create progress notification
        original_score = original.get("overall_score", 0)
        new_score = scores["overall"]
        improvement = new_score - original_score
        
        improvement_message = f"Overall score: {original_score} → {new_score} "
        if improvement > 0:
            improvement_message += f"(+{improvement:.2f} improvement! 🎉)"
        elif improvement < 0:
            improvement_message += f"({improvement:.2f} - keep working! 💪)"
        else:
            improvement_message += "(maintained level 👍)"
        
        notification = Notification(
            player_id=assessment.player_id if hasattr(assessment, 'player_id') else assessment_obj.id,
            title="🏆 Retest Results - Progress Update!",
            message=f"Retest completed! {improvement_message}",
            notification_type="progress"
        )
        notification_data = prepare_for_mongo(notification.dict())
        await db.notifications.insert_one(notification_data)
        
        return assessment_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessments/{player_id}/progress")
async def get_assessment_progress(player_id: str):
    try:
        # Get all assessments for player, ordered by date
        assessments = await db.assessments.find({"player_name": player_id}).sort("assessment_date", 1).to_list(1000)
        
        if not assessments:
            raise HTTPException(status_code=404, detail="No assessments found")
        
        progress_data = []
        for assessment in assessments:
            progress_data.append({
                "date": assessment.get("assessment_date"),
                "overall_score": assessment.get("overall_score", 0),
                "category_scores": assessment.get("category_scores", {}),
                "is_retest": assessment.get("previous_assessment_id") is not None
            })
        
        return {
            "player_id": player_id,
            "assessments": progress_data,
            "total_assessments": len(assessments),
            "latest_score": progress_data[-1]["overall_score"] if progress_data else 0,
            "improvement": progress_data[-1]["overall_score"] - progress_data[0]["overall_score"] if len(progress_data) > 1 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@api_router.post("/weekly-progress", response_model=WeeklyProgress)
async def create_weekly_progress(progress: WeeklyProgressCreate):
    try:
        progress_dict = progress.dict()
        progress_obj = WeeklyProgress(**progress_dict)
        progress_data = prepare_for_mongo(progress_obj.dict())
        await db.weekly_progress.insert_one(progress_data)
        return progress_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/weekly-progress/{player_id}", response_model=List[WeeklyProgress])
async def get_weekly_progress(player_id: str):
    try:
        progress_entries = await db.weekly_progress.find({"player_id": player_id}).sort("created_at", -1).to_list(1000)
        return [WeeklyProgress(**parse_from_mongo(entry)) for entry in progress_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/weekly-progress/{player_id}/{program_id}", response_model=List[WeeklyProgress])
async def get_program_weekly_progress(player_id: str, program_id: str):
    try:
        progress_entries = await db.weekly_progress.find({
            "player_id": player_id, 
            "program_id": program_id
        }).sort("week_number", 1).to_list(1000)
        return [WeeklyProgress(**parse_from_mongo(entry)) for entry in progress_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/weekly-progress/{progress_id}", response_model=WeeklyProgress)
async def update_weekly_progress(progress_id: str, progress: WeeklyProgressCreate):
    try:
        progress_dict = progress.dict()
        progress_dict["id"] = progress_id
        
        await db.weekly_progress.update_one(
            {"id": progress_id},
            {"$set": prepare_for_mongo(progress_dict)}
        )
        
        updated_progress = await db.weekly_progress.find_one({"id": progress_id})
        if not updated_progress:
            raise HTTPException(status_code=404, detail="Weekly progress not found")
        
        return WeeklyProgress(**parse_from_mongo(updated_progress))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/training-programs/adaptive")
async def create_adaptive_training_program(player_id: str, week_number: int = 1):
    try:
        # Get player assessment
        assessment = await db.assessments.find_one({"id": player_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Player assessment not found")
        
        assessment_obj = PlayerAssessment(**parse_from_mongo(assessment))
        
        # Get weekly progress history
        progress_history = await db.weekly_progress.find({"player_id": player_id}).to_list(1000)
        
        # Generate adaptive program
        program_content = await generate_adaptive_training_program(
            assessment_obj, 
            week_number, 
            progress_history
        )
        
        # Create program with adaptive content
        program_obj = TrainingProgram(
            player_id=player_id,
            program_type="Elite_Adaptive_AI",
            program_content=program_content,
            weekly_schedule={
                "Monday": f"النخبة: التركيز الأسبوعي رقم {week_number} - اليوم الأول 🔥",
                "Tuesday": f"النخبة: التقنيات المتقدمة - الأسبوع {week_number} ⚽",
                "Wednesday": f"النخبة: التكتيكات الذكية - الأسبوع {week_number} 🧠",
                "Thursday": f"النخبة: القوة والسرعة - الأسبوع {week_number} ⚡",
                "Friday": f"النخبة: الإنهاء الاحترافي - الأسبوع {week_number} 🎯",
                "Saturday": f"النخبة: محاكاة المباراة - الأسبوع {week_number} 🏆",
                "Sunday": f"النخبة: التعافي والتحليل - الأسبوع {week_number} 🧘‍♂️"
            },
            milestones=[
                {"week": week_number, "target": f"إتقان تحديات الأسبوع {week_number} النخبوية", "coins": 100 + (week_number * 50)}
            ]
        )
        
        program_data = prepare_for_mongo(program_obj.dict())
        await db.training_programs.insert_one(program_data)
        return program_obj
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/voice-notes", response_model=VoiceNote)
async def add_voice_note(note: VoiceNoteCreate):
    try:
        note_obj = VoiceNote(**note.dict())
        note_data = prepare_for_mongo(note_obj.dict())
        await db.voice_notes.insert_one(note_data)
        return note_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/voice-notes/{player_id}", response_model=List[VoiceNote])
async def get_voice_notes(player_id: str):
    try:
        notes = await db.voice_notes.find({"player_id": player_id}).sort("created_at", -1).to_list(1000)
        return [VoiceNote(**parse_from_mongo(note)) for note in notes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# VO2 Max Benchmark Endpoints
@api_router.post("/vo2-benchmarks", response_model=VO2MaxBenchmark)
async def save_vo2_benchmark(benchmark: VO2MaxBenchmarkCreate):
    """Save a VO2 Max benchmark test result"""
    try:
        benchmark_obj = VO2MaxBenchmark(**benchmark.dict())
        benchmark_data = prepare_for_mongo(benchmark_obj.dict())
        await db.vo2_benchmarks.insert_one(benchmark_data)
        return benchmark_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/vo2-benchmarks/{player_id}", response_model=List[VO2MaxBenchmark])
async def get_vo2_benchmarks(player_id: str):
    """Get all VO2 Max benchmarks for a player"""
    try:
        benchmarks = await db.vo2_benchmarks.find({"player_id": player_id}).sort("test_date", -1).to_list(1000)
        return [VO2MaxBenchmark(**parse_from_mongo(benchmark)) for benchmark in benchmarks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/vo2-benchmarks/latest/{player_id}", response_model=Optional[VO2MaxBenchmark])
async def get_latest_vo2_benchmark(player_id: str):
    """Get the latest VO2 Max benchmark for a player"""
    try:
        benchmark = await db.vo2_benchmarks.find_one(
            {"player_id": player_id}, 
            sort=[("test_date", -1)]
        )
        if benchmark:
            return VO2MaxBenchmark(**parse_from_mongo(benchmark))
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/vo2-benchmarks/{benchmark_id}")
async def delete_vo2_benchmark(benchmark_id: str):
    """Delete a specific VO2 Max benchmark"""
    try:
        result = await db.vo2_benchmarks.delete_one({"id": benchmark_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Benchmark not found")
        return {"message": "Benchmark deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Training Program Endpoints with Periodization
@api_router.post("/periodized-programs", response_model=PeriodizedProgram)
async def create_periodized_program(program: PeriodizedProgramCreate):
    """Create a comprehensive personalized training program based on player assessment"""
    try:
        from exercise_database import PERIODIZATION_TEMPLATES, generate_daily_routine
        
        # Get the latest assessment for this player
        assessment = await db.assessments.find_one(
            {"player_name": program.player_id}, 
            sort=[("created_at", -1)]
        )
        
        if not assessment:
            raise HTTPException(status_code=404, detail="No assessment found for this player. Please complete an assessment first.")
        
        # ENHANCED YOUTH HANDBOOK STANDARDS-BASED WEAKNESS ANALYSIS
        age = assessment.get("age", 17)
        position = assessment.get("position", "Midfielder")
        
        # Age-based standards (simplified - using 15-16 age group as baseline)
        STANDARDS = {
            "sprint_30m": {"excellent": 4.0, "good": 4.3, "average": 4.6, "needs_improvement": 5.0},
            "yo_yo_test": {"excellent": 2000, "good": 1700, "average": 1400, "needs_improvement": 1000},
            "vo2_max": {"excellent": 58, "good": 54, "average": 50, "needs_improvement": 45},
            "vertical_jump": {"excellent": 60, "good": 55, "average": 50, "needs_improvement": 45},
            "body_fat": {"excellent": 10, "good": 12, "average": 14, "needs_improvement": 16},
            "ball_control": {"excellent": 5, "good": 4, "average": 3, "needs_improvement": 2},
            "passing_accuracy": {"excellent": 85, "good": 75, "average": 65, "needs_improvement": 55},
            "dribbling_success": {"excellent": 80, "good": 70, "average": 60, "needs_improvement": 50},
            "shooting_accuracy": {"excellent": 75, "good": 65, "average": 55, "needs_improvement": 45},
            "defensive_duels": {"excellent": 75, "good": 65, "average": 55, "needs_improvement": 45},
            "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "needs_improvement": 2},
            "positioning": {"excellent": 5, "good": 4, "average": 3, "needs_improvement": 2},
            "decision_making": {"excellent": 5, "good": 4, "average": 3, "needs_improvement": 2},
            "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "needs_improvement": 2},
            "coachability": {"excellent": 5, "good": 4, "average": 3, "needs_improvement": 2}
        }
        
        # Analyze weaknesses with priority scoring
        weakness_analysis = {
            "critical": [],  # Needs immediate attention
            "moderate": [],  # Should be improved
            "minor": []      # Can be refined
        }
        
        # Physical Analysis (20% weight)
        if assessment.get("sprint_30m", 5.0) > STANDARDS["sprint_30m"]["average"]:
            weakness_analysis["critical" if assessment["sprint_30m"] > STANDARDS["sprint_30m"]["needs_improvement"] else "moderate"].append("speed")
        
        if assessment.get("yo_yo_test", 1000) < STANDARDS["yo_yo_test"]["average"]:
            weakness_analysis["critical" if assessment["yo_yo_test"] < STANDARDS["yo_yo_test"]["needs_improvement"] else "moderate"].append("endurance")
        
        if assessment.get("vertical_jump", 45) < STANDARDS["vertical_jump"]["average"]:
            weakness_analysis["critical" if assessment["vertical_jump"] < STANDARDS["vertical_jump"]["needs_improvement"] else "moderate"].append("power")
        
        if assessment.get("vo2_max", 45) < STANDARDS["vo2_max"]["average"]:
            weakness_analysis["moderate"].append("aerobic_capacity")
        
        # Technical Analysis (40% weight - highest priority)
        if assessment.get("ball_control", 2) < STANDARDS["ball_control"]["average"]:
            weakness_analysis["critical" if assessment["ball_control"] < STANDARDS["ball_control"]["needs_improvement"] else "moderate"].append("ball_control")
        
        if assessment.get("passing_accuracy", 50) < STANDARDS["passing_accuracy"]["average"]:
            weakness_analysis["critical" if assessment["passing_accuracy"] < STANDARDS["passing_accuracy"]["needs_improvement"] else "moderate"].append("passing")
        
        if assessment.get("dribbling_success", 50) < STANDARDS["dribbling_success"]["average"]:
            weakness_analysis["moderate"].append("dribbling")
        
        if assessment.get("shooting_accuracy", 45) < STANDARDS["shooting_accuracy"]["average"]:
            weakness_analysis["critical" if assessment["shooting_accuracy"] < STANDARDS["shooting_accuracy"]["needs_improvement"] else "moderate"].append("shooting")
        
        if assessment.get("defensive_duels", 45) < STANDARDS["defensive_duels"]["average"]:
            weakness_analysis["moderate"].append("defending")
        
        # Tactical Analysis (30% weight)
        if assessment.get("game_intelligence", 2) < STANDARDS["game_intelligence"]["average"]:
            weakness_analysis["moderate"].append("tactical_awareness")
        
        if assessment.get("positioning", 2) < STANDARDS["positioning"]["average"]:
            weakness_analysis["critical" if assessment["positioning"] < STANDARDS["positioning"]["needs_improvement"] else "moderate"].append("positioning")
        
        if assessment.get("decision_making", 2) < STANDARDS["decision_making"]["average"]:
            weakness_analysis["moderate"].append("decision_making")
        
        # Psychological Analysis (10% weight)
        if assessment.get("mental_toughness", 2) < STANDARDS["mental_toughness"]["average"]:
            weakness_analysis["minor"].append("mental_strength")
        
        # Flatten weaknesses with priority order
        weaknesses = weakness_analysis["critical"] + weakness_analysis["moderate"] + weakness_analysis["minor"]
        
        # Ensure variety if player is already strong
        if not weaknesses:
            weaknesses = ["technical_refinement", "tactical_mastery", "physical_conditioning"]
        
        logger.info(f"Player {program.player_id} weakness analysis: Critical={weakness_analysis['critical']}, Moderate={weakness_analysis['moderate']}, Minor={weakness_analysis['minor']}")
        
        # Create macro cycles
        macro_cycles = []
        current_date = datetime.now(timezone.utc)
        
        phases = ["foundation_building", "development_phase", "peak_performance"]
        
        # DYNAMIC DURATION CALCULATION based on total_duration_weeks from request
        # Default template proportions: 4:6:4 = 28.6%:42.9%:28.6%
        requested_duration = program.total_duration_weeks
        logger.info(f"Requested program duration: {requested_duration} weeks")
        
        # Calculate phase durations proportionally
        # Foundation: ~29% of total, Development: ~43% of total, Peak: ~29% of total
        phase_durations = {
            "foundation_building": max(2, int(requested_duration * 0.29)),  # At least 2 weeks
            "development_phase": max(3, int(requested_duration * 0.43)),    # At least 3 weeks
            "peak_performance": max(2, int(requested_duration * 0.29))      # At least 2 weeks
        }
        
        # Adjust to match exact total (account for rounding)
        calculated_total = sum(phase_durations.values())
        if calculated_total < requested_duration:
            # Add extra weeks to development phase (most critical)
            phase_durations["development_phase"] += (requested_duration - calculated_total)
        elif calculated_total > requested_duration:
            # Remove weeks from development phase
            phase_durations["development_phase"] -= (calculated_total - requested_duration)
        
        logger.info(f"Dynamic phase durations - Foundation: {phase_durations['foundation_building']}w, Development: {phase_durations['development_phase']}w, Peak: {phase_durations['peak_performance']}w")
        
        total_weeks = 0
        
        for i, phase in enumerate(phases):
            template = PERIODIZATION_TEMPLATES[phase]
            # Use dynamic duration instead of template duration
            phase_weeks = phase_durations[phase]
            
            # Create micro cycles (weeks) for this phase
            micro_cycles = []
            for week in range(1, phase_weeks + 1):
                # Create daily routines for this week based on training frequency
                daily_routines = []
                training_days = program.training_frequency  # 3, 4, or 5 days per week
                for day in range(1, training_days + 1):
                    routine_data = generate_daily_routine(phase, week, day, weaknesses)
                    daily_routine = DailyRoutine(**routine_data)
                    daily_routines.append(daily_routine)
                
                micro_cycle = MicroCycle(
                    name=f"Week {total_weeks + week}: {template['phase_name']}",
                    cycle_number=total_weeks + week,
                    phase=phase,
                    daily_routines=daily_routines,
                    objectives=template["objectives"],
                    assessment_metrics=["sprint_30m", "ball_control", "passing_accuracy", "game_intelligence"]
                )
                micro_cycles.append(micro_cycle)
            
            # Create macro cycle
            start_date = current_date + timedelta(weeks=total_weeks)
            end_date = start_date + timedelta(weeks=phase_weeks)
            assessment_date = end_date + timedelta(days=1)
            
            macro_cycle = MacroCycle(
                name=f"Phase {i+1}: {template['phase_name']}",
                phase_number=i+1,
                duration_weeks=phase_weeks,
                micro_cycles=micro_cycles,
                start_date=start_date,
                end_date=end_date,
                assessment_date=assessment_date,
                objectives=template["objectives"],
                success_criteria=[
                    f"Improve weak areas by 15%",
                    f"Complete 90% of scheduled training",
                    f"Achieve {template['intensity_progression'][-1]}% intensity capacity"
                ]
            )
            macro_cycles.append(macro_cycle)
            total_weeks += phase_weeks
        
        # Create the full periodized program
        next_assessment = current_date + timedelta(weeks=program.assessment_interval_weeks)
        
        periodized_program = PeriodizedProgram(
            player_id=program.player_id,
            program_name=program.program_name,
            total_duration_weeks=total_weeks,
            macro_cycles=macro_cycles,
            next_assessment_date=next_assessment,
            program_objectives=program.program_objectives
        )
        
        # Save to database
        program_data = prepare_for_mongo(periodized_program.dict())
        await db.periodized_programs.insert_one(program_data)
        
        return periodized_program
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analyze-assessment/{player_name}")
async def analyze_player_assessment(player_name: str):
    """Analyze player assessment and provide training recommendations"""
    try:
        # Get the latest assessment
        assessment = await db.assessments.find_one(
            {"player_name": player_name}, 
            sort=[("created_at", -1)]
        )
        
        if not assessment:
            raise HTTPException(status_code=404, detail="No assessment found for this player")
        
        # Standards for comparison
        STANDARDS = {
            "sprint_30m": {"excellent": 4.0, "good": 4.3, "average": 4.6},
            "yo_yo_test": {"excellent": 2000, "good": 1700, "average": 1400},
            "ball_control": {"excellent": 5, "good": 4, "average": 3},
            "passing_accuracy": {"excellent": 85, "good": 75, "average": 65},
            "shooting_accuracy": {"excellent": 75, "good": 65, "average": 55},
            "positioning": {"excellent": 5, "good": 4, "average": 3}
        }
        
        # Analyze each category
        analysis = {
            "player_name": player_name,
            "overall_score": assessment.get("overall_score", 0),
            "performance_level": assessment.get("performance_level", "Average"),
            "strengths": [],
            "weaknesses": [],
            "recommendations": {
                "suggested_frequency": 5,  # Default
                "program_duration": 14,    # weeks
                "focus_areas": []
            }
        }
        
        # Physical Analysis
        sprint = assessment.get("sprint_30m", 5.0)
        if sprint <= STANDARDS["sprint_30m"]["good"]:
            analysis["strengths"].append({"area": "Speed", "level": "Good"})
        elif sprint > STANDARDS["sprint_30m"]["average"]:
            analysis["weaknesses"].append({"area": "Speed", "current": f"{sprint}s", "target": "4.3s", "priority": "High"})
            analysis["recommendations"]["focus_areas"].append("Sprint Development")
        
        endurance = assessment.get("yo_yo_test", 1000)
        if endurance >= STANDARDS["yo_yo_test"]["good"]:
            analysis["strengths"].append({"area": "Endurance", "level": "Good"})
        elif endurance < STANDARDS["yo_yo_test"]["average"]:
            analysis["weaknesses"].append({"area": "Endurance", "current": f"{endurance}m", "target": "1700m", "priority": "High"})
            analysis["recommendations"]["focus_areas"].append("Aerobic Capacity")
        
        # Technical Analysis
        ball_control = assessment.get("ball_control", 2)
        if ball_control >= STANDARDS["ball_control"]["good"]:
            analysis["strengths"].append({"area": "Ball Control", "level": "Good"})
        elif ball_control < STANDARDS["ball_control"]["average"]:
            analysis["weaknesses"].append({"area": "Ball Control", "current": f"{ball_control}/5", "target": "4/5", "priority": "Critical"})
            analysis["recommendations"]["focus_areas"].append("Technical Skills")
        
        passing = assessment.get("passing_accuracy", 50)
        if passing >= STANDARDS["passing_accuracy"]["good"]:
            analysis["strengths"].append({"area": "Passing", "level": "Good"})
        elif passing < STANDARDS["passing_accuracy"]["average"]:
            analysis["weaknesses"].append({"area": "Passing", "current": f"{passing}%", "target": "75%", "priority": "High"})
            analysis["recommendations"]["focus_areas"].append("Passing Accuracy")
        
        shooting = assessment.get("shooting_accuracy", 45)
        if shooting >= STANDARDS["shooting_accuracy"]["good"]:
            analysis["strengths"].append({"area": "Shooting", "level": "Good"})
        elif shooting < STANDARDS["shooting_accuracy"]["average"]:
            analysis["weaknesses"].append({"area": "Shooting", "current": f"{shooting}%", "target": "65%", "priority": "High"})
            analysis["recommendations"]["focus_areas"].append("Shooting Accuracy")
        
        # Tactical Analysis
        positioning = assessment.get("positioning", 2)
        if positioning >= STANDARDS["positioning"]["good"]:
            analysis["strengths"].append({"area": "Positioning", "level": "Good"})
        elif positioning < STANDARDS["positioning"]["average"]:
            analysis["weaknesses"].append({"area": "Positioning", "current": f"{positioning}/5", "target": "4/5", "priority": "Moderate"})
            analysis["recommendations"]["focus_areas"].append("Tactical Awareness")
        
        # CALCULATE DYNAMIC PROGRAM DURATION based on gaps and training frequency
        # Improvement rates per month based on training science
        IMPROVEMENT_RATES = {
            "sprint_30m": 0.08,  # seconds per month (with 5 days/week)
            "yo_yo_test": 80,    # meters per month
            "ball_control": 0.4,  # points per month (1-5 scale)
            "passing_accuracy": 4,  # percentage points per month
            "shooting_accuracy": 3.5,  # percentage points per month
            "positioning": 0.4   # points per month (1-5 scale)
        }
        
        # Calculate required months for each weakness
        months_needed = []
        for weakness in analysis["weaknesses"]:
            area = weakness["area"]
            
            if area == "Speed":
                current = assessment.get("sprint_30m", 5.0)
                target = STANDARDS["sprint_30m"]["good"]
                gap = current - target  # e.g., 5.0 - 4.3 = 0.7s
                months = gap / IMPROVEMENT_RATES["sprint_30m"]  # 0.7 / 0.08 = 8.75 months
                months_needed.append(months)
                weakness["estimated_months"] = round(months, 1)
                
            elif area == "Endurance":
                current = assessment.get("yo_yo_test", 1000)
                target = STANDARDS["yo_yo_test"]["good"]
                gap = target - current  # e.g., 1700 - 1200 = 500m
                months = gap / IMPROVEMENT_RATES["yo_yo_test"]  # 500 / 80 = 6.25 months
                months_needed.append(months)
                weakness["estimated_months"] = round(months, 1)
                
            elif area == "Ball Control":
                current = assessment.get("ball_control", 2)
                target = STANDARDS["ball_control"]["good"]
                gap = target - current
                months = gap / IMPROVEMENT_RATES["ball_control"]
                months_needed.append(months)
                weakness["estimated_months"] = round(months, 1)
                
            elif area == "Passing":
                current = assessment.get("passing_accuracy", 50)
                target = STANDARDS["passing_accuracy"]["good"]
                gap = target - current
                months = gap / IMPROVEMENT_RATES["passing_accuracy"]
                months_needed.append(months)
                weakness["estimated_months"] = round(months, 1)
                
            elif area == "Shooting":
                current = assessment.get("shooting_accuracy", 45)
                target = STANDARDS["shooting_accuracy"]["good"]
                gap = target - current
                months = gap / IMPROVEMENT_RATES["shooting_accuracy"]
                months_needed.append(months)
                weakness["estimated_months"] = round(months, 1)
                
            elif area == "Positioning":
                current = assessment.get("positioning", 2)
                target = STANDARDS["positioning"]["good"]
                gap = target - current
                months = gap / IMPROVEMENT_RATES["positioning"]
                months_needed.append(months)
                weakness["estimated_months"] = round(months, 1)
        
        # Calculate base program duration (months)
        if months_needed:
            # Use the longest time needed (can't rush weakest area)
            base_months = max(months_needed)
            # Add buffer for consolidation and multiple weaknesses
            if len(months_needed) > 3:
                base_months = base_months * 1.2  # 20% longer for multiple weaknesses
        else:
            base_months = 3  # Default 3 months for maintenance
        
        # Adjust based on training frequency (5 days is baseline)
        # 3 days/week = 60% volume → takes ~67% longer
        # 4 days/week = 80% volume → takes ~25% longer
        # 5 days/week = 100% volume → baseline
        
        # This will be applied when user selects frequency
        frequency_multipliers = {3: 1.67, 4: 1.25, 5: 1.0}
        
        # Store durations for each frequency option
        analysis["recommendations"]["program_duration_options"] = {
            "3_days": {
                "weeks": int(base_months * frequency_multipliers[3] * 4.33),  # months to weeks
                "months": round(base_months * frequency_multipliers[3], 1),
                "description": "Slower progress - Good for beginners or busy schedules"
            },
            "4_days": {
                "weeks": int(base_months * frequency_multipliers[4] * 4.33),
                "months": round(base_months * frequency_multipliers[4], 1),
                "description": "Balanced progress - Recommended for most players"
            },
            "5_days": {
                "weeks": int(base_months * frequency_multipliers[5] * 4.33),
                "months": round(base_months * frequency_multipliers[5], 1),
                "description": "Fastest progress - For dedicated athletes"
            }
        }
        
        # Determine suggested training frequency based on weaknesses
        weakness_count = len(analysis["weaknesses"])
        if weakness_count >= 5:
            analysis["recommendations"]["suggested_frequency"] = 5
            analysis["recommendations"]["intensity"] = "High - Multiple areas need development"
            analysis["recommendations"]["program_duration"] = analysis["recommendations"]["program_duration_options"]["5_days"]["weeks"]
        elif weakness_count >= 3:
            analysis["recommendations"]["suggested_frequency"] = 4
            analysis["recommendations"]["intensity"] = "Moderate - Several areas to improve"
            analysis["recommendations"]["program_duration"] = analysis["recommendations"]["program_duration_options"]["4_days"]["weeks"]
        else:
            analysis["recommendations"]["suggested_frequency"] = 3
            analysis["recommendations"]["intensity"] = "Standard - Maintenance and refinement"
            analysis["recommendations"]["program_duration"] = analysis["recommendations"]["program_duration_options"]["3_days"]["weeks"]
        
        # Add summary message
        analysis["recommendations"]["duration_explanation"] = f"Based on your current performance and {weakness_count} areas for improvement, you need approximately {analysis['recommendations']['program_duration']} weeks with {analysis['recommendations']['suggested_frequency']} days/week training to reach your target goals."
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/periodized-programs/{player_id}", response_model=Optional[PeriodizedProgram])
async def get_player_program(player_id: str):
    """Get the current periodized program for a player"""
    try:
        program = await db.periodized_programs.find_one(
            {"player_id": player_id}, 
            sort=[("created_at", -1)]
        )
        if program:
            return PeriodizedProgram(**parse_from_mongo(program))
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/daily-progress", response_model=DailyProgress)
async def log_daily_progress(progress: DailyProgressCreate):
    """Log daily training progress and exercise completions"""
    try:
        # Create exercise completions
        completed_exercises = []
        for completion_data in progress.completed_exercises:
            completion = ExerciseCompletion(**completion_data.dict())
            completed_exercises.append(completion)
        
        # Create daily progress entry
        daily_progress = DailyProgress(
            player_id=progress.player_id,
            routine_id=progress.routine_id,
            completed_exercises=completed_exercises,
            overall_rating=progress.overall_rating,
            energy_level=progress.energy_level,
            motivation_level=progress.motivation_level,
            daily_notes=progress.daily_notes,
            total_time_spent=progress.total_time_spent
        )
        
        # Save to database
        progress_data = prepare_for_mongo(daily_progress.dict())
        await db.daily_progress.insert_one(progress_data)
        
        # Update performance metrics based on completed exercises
        await update_performance_metrics(progress.player_id, completed_exercises)
        
        return daily_progress
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/daily-progress/{player_id}")
async def get_daily_progress(player_id: str, days: int = 30):
    """Get daily progress history for a player"""
    try:
        # Get all entries for the player first, then filter by date in Python
        # This handles the string vs datetime comparison issue
        progress_entries = await db.daily_progress.find(
            {"player_id": player_id}
        ).sort("date", -1).to_list(1000)
        
        # Filter by date in Python after parsing
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        filtered_entries = []
        
        for entry in progress_entries:
            # Parse the entry and convert date string to datetime
            parsed_entry = parse_from_mongo(entry)
            
            # Handle date field conversion (not just _at fields)
            if 'date' in parsed_entry and isinstance(parsed_entry['date'], str):
                try:
                    parsed_entry['date'] = datetime.fromisoformat(parsed_entry['date'])
                except:
                    # If date parsing fails, include the entry anyway
                    pass
            
            # Filter by date if we have a valid datetime
            if isinstance(parsed_entry.get('date'), datetime):
                if parsed_entry['date'] >= start_date:
                    filtered_entries.append(parsed_entry)
            else:
                # Include entries with invalid dates
                filtered_entries.append(parsed_entry)
        
        return [DailyProgress(**entry) for entry in filtered_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/current-routine/{player_id}")
async def get_current_routine(player_id: str):
    """Get today's training routine for a player"""
    try:
        # Get player's current program
        program = await db.periodized_programs.find_one(
            {"player_id": player_id}, 
            sort=[("created_at", -1)]
        )
        
        if not program:
            return {"message": "No training program found", "routine": None}
        
        # Calculate current position in program
        start_date = program["program_start_date"]
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        current_date = datetime.now(timezone.utc)
        days_elapsed = (current_date - start_date).days
        
        current_week = (days_elapsed // 7) + 1
        current_day = (days_elapsed % 7) + 1
        
        # Find current routine
        current_routine = None
        current_phase = None
        
        week_count = 0
        for macro_cycle in program["macro_cycles"]:
            for micro_cycle in macro_cycle["micro_cycles"]:
                week_count += 1
                if week_count == current_week:
                    current_phase = macro_cycle["phase_number"]
                    if current_day <= len(micro_cycle["daily_routines"]):
                        current_routine = micro_cycle["daily_routines"][current_day - 1]
                    break
            if current_routine:
                break
        
        if not current_routine:
            return {"message": "Rest day or program completed", "routine": None}
        
        return {
            "routine": current_routine,
            "current_week": current_week,
            "current_day": current_day,
            "current_phase": current_phase,
            "program_name": program["program_name"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/performance-metrics/{player_id}")
async def get_performance_metrics(player_id: str):
    """Get performance metrics and progress tracking"""
    try:
        # Get recent performance metrics
        metrics = await db.performance_metrics.find(
            {"player_id": player_id}
        ).sort("measurement_date", -1).to_list(1000)
        
        # Get daily progress for visualization
        progress_entries = await db.daily_progress.find(
            {"player_id": player_id}
        ).sort("date", -1).limit(30).to_list(1000)
        
        # Calculate improvement trends
        improvement_data = calculate_improvement_trends(metrics)
        
        return {
            "metrics": [PerformanceMetric(**parse_from_mongo(metric)) for metric in metrics],
            "daily_progress": [DailyProgress(**parse_from_mongo(entry)) for entry in progress_entries],
            "improvement_trends": improvement_data,
            "next_assessment": get_next_assessment_date(player_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_performance_metrics(player_id: str, completed_exercises: List[ExerciseCompletion]):
    """Update performance metrics based on completed exercises"""
    try:
        # Get current program to determine phase and week
        program = await db.periodized_programs.find_one(
            {"player_id": player_id}, 
            sort=[("created_at", -1)]
        )
        
        if not program:
            return
        
        current_week = calculate_current_week(program)
        current_phase = calculate_current_phase(program)
        
        # Update metrics based on exercise performance
        for exercise in completed_exercises:
            if exercise.performance_rating and exercise.performance_rating >= 4:
                # Good performance - create positive metric entry
                metric = PerformanceMetric(
                    player_id=player_id,
                    metric_name=f"{exercise.exercise_id}_performance",
                    value=exercise.performance_rating,
                    phase_number=current_phase,
                    week_number=current_week
                )
                
                metric_data = prepare_for_mongo(metric.dict())
                await db.performance_metrics.insert_one(metric_data)
        
    except Exception as e:
        print(f"Error updating performance metrics: {e}")

def calculate_current_week(program):
    """Calculate current week in program"""
    start_date = program["program_start_date"]
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    current_date = datetime.now(timezone.utc)
    days_elapsed = (current_date - start_date).days
    return (days_elapsed // 7) + 1

def calculate_current_phase(program):
    """Calculate current phase in program"""
    current_week = calculate_current_week(program)
    week_count = 0
    
    for i, macro_cycle in enumerate(program["macro_cycles"]):
        week_count += macro_cycle["duration_weeks"]
        if current_week <= week_count:
            return i + 1
    
    return len(program["macro_cycles"])

def calculate_improvement_trends(metrics):
    """Calculate improvement trends from performance metrics"""
    trends = {}
    
    # Group metrics by type
    metric_groups = {}
    for metric in metrics:
        metric_type = metric["metric_name"]
        if metric_type not in metric_groups:
            metric_groups[metric_type] = []
        metric_groups[metric_type].append(metric)
    
    # Calculate trends for each metric type
    for metric_type, metric_list in metric_groups.items():
        if len(metric_list) >= 2:
            # Sort by date
            sorted_metrics = sorted(metric_list, key=lambda x: x["measurement_date"])
            first_value = sorted_metrics[0]["value"]
            last_value = sorted_metrics[-1]["value"]
            
            if first_value > 0:
                improvement_percentage = ((last_value - first_value) / first_value) * 100
                trends[metric_type] = {
                    "improvement_percentage": round(improvement_percentage, 2),
                    "trend_direction": "up" if improvement_percentage > 0 else "down",
                    "data_points": len(sorted_metrics)
                }
    
    return trends

def get_next_assessment_date(player_id: str):
    """Get the next assessment date for a player"""
    # This would get the next assessment date from the program
    # For now, return a default 4 weeks from now
    return datetime.now(timezone.utc) + timedelta(weeks=4)

# Import auth routes
try:
    from routes.auth_routes import router as auth_router
    api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
    logging.info("Auth routes loaded successfully")
except ImportError as e:
    logging.warning(f"Could not import auth routes: {e}")

# Import notification routes
try:
    from routes.notification_routes import router as notification_router
    api_router.include_router(notification_router, tags=["notifications"])
    logging.info("Notification routes loaded successfully")
except ImportError as e:
    logging.warning(f"Could not import notification routes: {e}")

# Import Elite Training System routes
try:
    from routes.elite_training_routes import router as elite_training_router
    api_router.include_router(elite_training_router, tags=["elite-training"])
    logging.info("✅ Elite Training System routes loaded successfully (FIFA & Manchester United Edition)")
except ImportError as e:
    logging.warning(f"Could not import elite training routes: {e}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelevel)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()