"""
Drill Candidate Models
======================

Models for PDF drill parsing preview (candidates before confirmation).
These are NOT written to DB until confirmed.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class DrillItemCandidate(BaseModel):
    """
    Candidate drill item parsed from PDF.
    Used for preview before confirmation - NOT written to DB.
    
    Fields may be incomplete/uncertain - coach reviews and edits before confirm.
    """
    # Optional fields that may be inferred from PDF
    drill_id: Optional[str] = Field(default=None, description="Inferred drill ID or null")
    name: Optional[str] = Field(default=None, description="Inferred drill name or null")
    section: Optional[str] = Field(default=None, description="Inferred section or null")
    tags: List[str] = Field(default_factory=list, description="Inferred tags")
    duration_min: Optional[int] = Field(default=None, description="Duration in minutes")
    sets: Optional[int] = Field(default=None, description="Number of sets")
    reps: Optional[int] = Field(default=None, description="Number of reps")
    intensity: Optional[str] = Field(default=None, description="Intensity level")
    equipment: List[str] = Field(default_factory=list, description="Equipment needed")
    coaching_points: List[str] = Field(default_factory=list, description="Coaching points")
    contraindications: List[str] = Field(default_factory=list, description="Injury contraindications")
    
    # Required fields for candidate
    raw_text: str = Field(..., description="Raw text extracted from PDF")
    needs_review: bool = Field(default=True, description="True if human review needed")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Parsing confidence 0-1")
    
    # Metadata
    page_number: Optional[int] = Field(default=None, description="PDF page number")
    parse_warnings: List[str] = Field(default_factory=list, description="Parsing warnings")


class PDFUploadResponse(BaseModel):
    """Response from PDF upload (preview only, no DB writes)."""
    parsed: List[DrillItemCandidate] = Field(..., description="Parsed drill candidates")
    errors: List[str] = Field(default_factory=list, description="Parsing errors")
    meta: dict = Field(default_factory=dict, description="PDF metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parsed": [
                    {
                        "drill_id": "TECH01",
                        "name": "Triangle Passing Drill",
                        "section": "technical",
                        "tags": ["passing", "first_touch"],
                        "raw_text": "Triangle Passing Drill - Setup 3 cones...",
                        "needs_review": False,
                        "confidence": 0.85
                    }
                ],
                "errors": [],
                "meta": {"pages": 2, "filename": "drills.pdf"}
            }
        }


class DrillConfirmRequest(BaseModel):
    """Request to confirm and save drills to database."""
    drills: List[dict] = Field(..., min_length=1, description="Drills to confirm (as DrillItem)")


class DrillConfirmResponse(BaseModel):
    """Response from drill confirmation."""
    success: bool
    inserted: int
    updated: int
    total: int
    drill_ids: List[str]
