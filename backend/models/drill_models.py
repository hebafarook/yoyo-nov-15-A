"""
Drill Models
============

Pydantic models for drill validation and storage.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class DrillProgression(BaseModel):
    """Drill progression configuration."""
    week_1_2: Optional[Dict[str, Any]] = None
    week_3_4: Optional[Dict[str, Any]] = None
    week_5_6: Optional[Dict[str, Any]] = None


class Drill(BaseModel):
    """
    Drill model matching the structure in exercise_database.py.
    
    All drills must have:
    - drill_id: unique identifier (used for upsert)
    - name: display name
    - category: classification (speed, agility, technical, tactical, etc.)
    - description: brief description
    - instructions: list of step-by-step instructions
    - purpose: why this drill is useful
    - expected_outcome: what to expect from doing this drill
    - duration: estimated duration in minutes
    - intensity: low/medium/high/maximum
    """
    drill_id: str = Field(..., min_length=1, description="Unique drill identifier")
    name: str = Field(..., min_length=1, description="Display name")
    category: str = Field(..., min_length=1, description="Drill category")
    description: str = Field(..., min_length=1, description="Brief description")
    instructions: List[str] = Field(..., min_length=1, description="Step-by-step instructions")
    purpose: str = Field(..., min_length=1, description="Why this drill is useful")
    expected_outcome: str = Field(..., min_length=1, description="Expected results")
    duration: int = Field(..., ge=1, le=120, description="Duration in minutes")
    intensity: str = Field(..., description="Intensity level")
    equipment_needed: List[str] = Field(default_factory=list, description="Required equipment")
    progression: Optional[DrillProgression] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # Admin user ID
    is_active: bool = Field(default=True, description="Whether drill is available for selection")
    tags: List[str] = Field(default_factory=list, description="Additional tags for filtering")
    
    @field_validator('intensity')
    @classmethod
    def validate_intensity(cls, v: str) -> str:
        valid = ['low', 'medium', 'high', 'maximum']
        if v.lower() not in valid:
            raise ValueError(f"intensity must be one of: {valid}")
        return v.lower()
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = [
            'speed', 'agility', 'technical', 'tactical', 'possession',
            'shooting', 'passing', 'defending', 'conditioning', 'warmup',
            'cooldown', 'strength', 'flexibility', 'recovery', 'goalkeeper'
        ]
        if v.lower() not in valid:
            raise ValueError(f"category must be one of: {valid}")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "drill_id": "sprint_30m_custom",
                "name": "Custom 30m Sprint",
                "category": "speed",
                "description": "High-intensity sprint drill",
                "instructions": ["Set up cones", "Sprint at max effort", "Rest and repeat"],
                "purpose": "Develop maximum speed",
                "expected_outcome": "Improved sprint times",
                "duration": 20,
                "intensity": "maximum",
                "equipment_needed": ["cones"],
                "tags": ["speed", "acceleration"]
            }
        }


class DrillUpload(BaseModel):
    """Model for bulk drill upload request."""
    drills: List[Drill] = Field(..., min_length=1, description="List of drills to upload")
    
    @field_validator('drills')
    @classmethod
    def validate_unique_ids(cls, drills: List[Drill]) -> List[Drill]:
        """Ensure all drill_ids are unique within the upload."""
        ids = [d.drill_id for d in drills]
        if len(ids) != len(set(ids)):
            duplicates = [id for id in ids if ids.count(id) > 1]
            raise ValueError(f"Duplicate drill_ids in upload: {set(duplicates)}")
        return drills


class DrillUploadResponse(BaseModel):
    """Response model for drill upload."""
    success: bool
    message: str
    uploaded_count: int
    updated_count: int
    drill_ids: List[str]


class DrillListResponse(BaseModel):
    """Response model for listing drills."""
    drills: List[Drill]
    total: int
    source: str  # 'database' or 'static'
