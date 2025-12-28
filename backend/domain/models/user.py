"""User domain model with validation and business rules."""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import uuid
import re


class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="player", pattern="^(player|coach|parent|club|admin)$")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric (underscores allowed)')
        return v


class UserCreate(UserBase):
    """User creation model with validation."""
    password: str = Field(..., min_length=6)
    is_coach: Optional[bool] = False
    
    # Player-specific fields
    age: Optional[int] = Field(None, ge=10, le=30)
    position: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    height: Optional[str] = None
    weight: Optional[str] = None
    height_unit: Optional[str] = Field("metric", pattern="^(metric|imperial)$")
    weight_unit: Optional[str] = Field("metric", pattern="^(metric|imperial)$")
    dominant_foot: Optional[str] = Field(None, pattern="^(Left|Right|Both)$")
    current_injuries: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    coach_email: Optional[EmailStr] = None

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "player123",
                "email": "player@example.com",
                "full_name": "John Doe",
                "password": "securepass123",
                "role": "player",
                "age": 17,
                "position": "Forward"
            }
        }


class UserLogin(BaseModel):
    """User login credentials."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class User(UserBase):
    """Complete user model with all fields."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str
    is_active: bool = True
    is_coach: bool = False
    
    # Player-specific fields
    player_id: Optional[str] = None
    age: Optional[int] = None
    position: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    height_unit: Optional[str] = "metric"
    weight_unit: Optional[str] = "metric"
    dominant_foot: Optional[str] = None
    current_injuries: Optional[str] = None
    parent_email: Optional[str] = None
    coach_email: Optional[str] = None
    
    # Metadata
    profile_picture: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "player123",
                "email": "player@example.com",
                "full_name": "John Doe",
                "role": "player",
                "is_active": True
            }
        }


class UserProfile(BaseModel):
    """User profile with additional data."""
    players_managed: List[str] = Field(default_factory=list)
    saved_reports: List[dict] = Field(default_factory=list)
    benchmarks: List[dict] = Field(default_factory=list)
    coaching_level: Optional[str] = None
    organization: Optional[str] = None
    preferences: dict = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "players_managed": [],
                "saved_reports": [],
                "benchmarks": [],
                "preferences": {}
            }
        }
