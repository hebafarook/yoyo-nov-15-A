"""Report domain models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class SavedReportCreate(BaseModel):
    """Saved report creation model."""
    title: str = Field(..., min_length=1, max_length=200)
    content: Dict[str, Any] = Field(...)
    report_type: str = Field(default="assessment")
    player_name: Optional[str] = None


class SavedReport(SavedReportCreate):
    """Complete saved report model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user123",
                "title": "Assessment Report",
                "content": {},
                "report_type": "assessment"
            }
        }
