"""Assessment domain models."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class AssessmentBenchmarkCreate(BaseModel):
    """Assessment benchmark creation model."""
    player_name: str = Field(..., min_length=1)
    age: int = Field(..., ge=10, le=30)
    position: str
    assessment_date: str
    
    # Physical metrics
    sprint_30m: Optional[float] = Field(None, ge=0)
    yo_yo_test: Optional[float] = Field(None, ge=0)
    vo2_max: Optional[float] = Field(None, ge=0)
    vertical_jump: Optional[float] = Field(None, ge=0)
    body_fat: Optional[float] = Field(None, ge=0, le=100)
    
    # Technical metrics
    ball_control: Optional[int] = Field(None, ge=1, le=5)
    passing_accuracy: Optional[float] = Field(None, ge=0, le=100)
    dribbling_success: Optional[float] = Field(None, ge=0, le=100)
    shooting_accuracy: Optional[float] = Field(None, ge=0, le=100)
    defensive_duels: Optional[float] = Field(None, ge=0, le=100)
    
    # Tactical metrics
    game_intelligence: Optional[int] = Field(None, ge=1, le=5)
    positioning: Optional[int] = Field(None, ge=1, le=5)
    decision_making: Optional[int] = Field(None, ge=1, le=5)
    
    # Psychological metrics
    coachability: Optional[int] = Field(None, ge=1, le=5)
    mental_toughness: Optional[int] = Field(None, ge=1, le=5)


class AssessmentBenchmark(AssessmentBenchmarkCreate):
    """Complete assessment benchmark model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    overall_score: Optional[float] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    is_baseline: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user123",
                "player_name": "John Doe",
                "age": 17,
                "position": "Forward",
                "sprint_30m": 4.2,
                "ball_control": 4,
                "is_baseline": True
            }
        }
