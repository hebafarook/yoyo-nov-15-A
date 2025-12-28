"""
Drill Models
============

Pydantic models for drill validation and storage.
Clean DrillItem schema as specified for admin drill uploads.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum


class DrillSection(str, Enum):
    """Valid drill sections."""
    TECHNICAL = "technical"
    TACTICAL = "tactical"
    POSSESSION = "possession"
    SPEED_AGILITY = "speed_agility"
    CARDIO = "cardio"
    GYM = "gym"
    MOBILITY = "mobility"
    RECOVERY = "recovery"
    PREHAB = "prehab"


class DrillIntensity(str, Enum):
    """Valid intensity levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class DrillSex(str, Enum):
    """Valid sex filter values."""
    MALE = "male"
    FEMALE = "female"
    ANY = "any"


class DrillItem(BaseModel):
    """
    Clean DrillItem schema for admin drill uploads.
    
    Required fields:
    - drill_id: unique identifier (used for upsert)
    - name: display name
    - section: one of the valid drill sections
    
    Optional fields:
    - tags: keywords for matching weaknesses/focus areas
    - age_min, age_max: age filters
    - sex: male/female/any (default: any)
    - positions: list of positions or ["any"]
    - intensity: low/moderate/high
    - duration_min: duration in minutes
    - sets, reps: alternative to duration
    - equipment: required equipment
    - coaching_points: key coaching instructions
    - contraindications: injury flags (hamstring, knee, etc.)
    - progressions, regressions: drill variations
    """
    # Required fields
    drill_id: str = Field(..., min_length=1, description="Unique drill identifier")
    name: str = Field(..., min_length=1, description="Display name")
    section: DrillSection = Field(..., description="Drill section category")
    
    # Optional fields
    tags: List[str] = Field(default_factory=list, description="Keywords for matching weaknesses/focus areas")
    age_min: Optional[int] = Field(default=None, ge=5, le=100, description="Minimum age")
    age_max: Optional[int] = Field(default=None, ge=5, le=100, description="Maximum age")
    sex: DrillSex = Field(default=DrillSex.ANY, description="Sex filter")
    positions: List[str] = Field(default_factory=lambda: ["any"], description="Applicable positions")
    intensity: Optional[DrillIntensity] = Field(default=None, description="Intensity level")
    duration_min: Optional[int] = Field(default=None, ge=1, le=180, description="Duration in minutes")
    sets: Optional[int] = Field(default=None, ge=1, le=20, description="Number of sets")
    reps: Optional[int] = Field(default=None, ge=1, le=100, description="Number of reps per set")
    equipment: List[str] = Field(default_factory=list, description="Required equipment")
    coaching_points: List[str] = Field(default_factory=list, description="Key coaching instructions")
    contraindications: List[str] = Field(default_factory=list, description="Injury flags (hamstring, knee, etc.)")
    progressions: List[str] = Field(default_factory=list, description="Harder variations")
    regressions: List[str] = Field(default_factory=list, description="Easier variations")
    
    # Metadata (set by system)
    is_active: bool = Field(default=True, description="Whether drill is available for selection")
    created_at: Optional[str] = Field(default=None, description="ISO timestamp of creation")
    updated_at: Optional[str] = Field(default=None, description="ISO timestamp of last update")
    created_by: Optional[str] = Field(default=None, description="Admin user ID who created/uploaded")
    
    @field_validator('age_max')
    @classmethod
    def validate_age_range(cls, v, info):
        """Ensure age_max >= age_min if both are provided."""
        if v is not None and info.data.get('age_min') is not None:
            if v < info.data['age_min']:
                raise ValueError('age_max must be >= age_min')
        return v
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "drill_id": "tech_passing_triangle",
                "name": "Triangle Passing Drill",
                "section": "technical",
                "tags": ["passing", "first_touch", "awareness"],
                "age_min": 10,
                "age_max": 18,
                "sex": "any",
                "positions": ["any"],
                "intensity": "moderate",
                "duration_min": 15,
                "equipment": ["cones", "balls"],
                "coaching_points": ["Soft first touch", "Body position open", "Communication"],
                "contraindications": [],
                "progressions": ["One-touch passing", "Add defender"],
                "regressions": ["Larger triangle", "Two-touch minimum"]
            }
        }


class DrillUploadRequest(BaseModel):
    """Request model for bulk drill upload."""
    drills: List[DrillItem] = Field(..., min_length=1, description="List of drills to upload")
    
    @field_validator('drills')
    @classmethod
    def validate_unique_ids(cls, drills: List[DrillItem]) -> List[DrillItem]:
        """Ensure all drill_ids are unique within the upload."""
        ids = [d.drill_id for d in drills]
        if len(ids) != len(set(ids)):
            duplicates = list(set([id for id in ids if ids.count(id) > 1]))
            raise ValueError(f"Duplicate drill_ids in upload: {duplicates}")
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
    drills: List[DrillItem]
    total: int
    source: str  # 'database', 'static', or 'auto'
    page: Optional[int] = None
    page_size: Optional[int] = None


class DrillStatsResponse(BaseModel):
    """Response model for drill statistics."""
    db_count: int
    static_count: int
    source_mode: str  # 'auto', 'db', 'static'
    active_source: str  # 'database' or 'static' (which one is currently being used)
    db_available: bool
    sections: dict  # Count per section
