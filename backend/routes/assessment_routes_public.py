"""
Assessment Routes (Public/Legacy)
=================================

These routes maintain backward compatibility with the legacy API that did NOT
require JWT authentication. They are intentionally unauthenticated to preserve
existing client integrations.

DEPRECATION NOTICE: These routes are deprecated and will be removed in a future
version. Please migrate to the authenticated routes in assessment_routes.py.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
import logging

from models import PlayerAssessment, AssessmentCreate
from repositories.assessment_repository import AssessmentRepository
from utils.assessment_calculator import (
    calculate_overall_score,
    get_performance_level
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Singleton repository for public routes
_repository: Optional[AssessmentRepository] = None


def get_repository() -> AssessmentRepository:
    """Get or create the repository singleton."""
    global _repository
    if _repository is None:
        _repository = AssessmentRepository()
    return _repository


@router.post("/public", response_model=PlayerAssessment, tags=["assessments-public"])
async def create_assessment_public(assessment: AssessmentCreate):
    """
    Create a new player assessment (NO AUTHENTICATION REQUIRED).
    
    DEPRECATED: Use POST /api/assessments/ with JWT authentication instead.
    This endpoint is maintained for backward compatibility only.
    """
    try:
        repository = get_repository()
        
        # Calculate overall score and performance level
        assessment_dict = assessment.dict()
        overall_score = calculate_overall_score(assessment_dict)
        performance_level = get_performance_level(overall_score)
        
        # Calculate BMI if height and weight are provided
        bmi = None
        if assessment_dict.get('height_cm') and assessment_dict.get('weight_kg'):
            height_m = assessment_dict['height_cm'] / 100
            bmi = assessment_dict['weight_kg'] / (height_m ** 2)
        
        # Create the assessment object (no user_id since unauthenticated)
        player_assessment = PlayerAssessment(
            **assessment_dict,
            overall_score=overall_score,
            performance_level=performance_level,
            bmi=bmi
        )
        
        # Save to database
        await repository.create_assessment(player_assessment.dict())
        
        logger.info(f"[PUBLIC] Assessment created for player: {assessment.player_name}")
        return player_assessment
        
    except Exception as e:
        logger.error(f"Error creating assessment (public): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/public", response_model=List[PlayerAssessment], tags=["assessments-public"])
async def get_assessments_public(user_id: Optional[str] = Query(None)):
    """
    Get all assessments, optionally filtered by user_id (NO AUTHENTICATION REQUIRED).
    
    DEPRECATED: Use GET /api/assessments/ with JWT authentication instead.
    This endpoint is maintained for backward compatibility only.
    """
    try:
        repository = get_repository()
        
        if user_id:
            assessments = await repository.find_by_user(user_id)
        else:
            assessments = await repository.find_all()
        
        return [PlayerAssessment(**a) for a in assessments]
        
    except Exception as e:
        logger.error(f"Error fetching assessments (public): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessments"
        )


@router.get("/public/player/{player_name}", response_model=List[PlayerAssessment], tags=["assessments-public"])
async def get_player_assessments_public(player_name: str):
    """
    Get all assessments for a specific player (NO AUTHENTICATION REQUIRED).
    
    DEPRECATED: Use GET /api/assessments/player/{player_name} with JWT instead.
    This endpoint is maintained for backward compatibility only.
    """
    try:
        repository = get_repository()
        assessments = await repository.find_by_player_name(player_name)
        return [PlayerAssessment(**a) for a in assessments]
        
    except Exception as e:
        logger.error(f"Error fetching player assessments (public): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player assessments"
        )


@router.get("/public/{assessment_id}", response_model=PlayerAssessment, tags=["assessments-public"])
async def get_assessment_public(assessment_id: str):
    """
    Get a specific assessment by ID (NO AUTHENTICATION REQUIRED).
    
    DEPRECATED: Use GET /api/assessments/{id} with JWT authentication instead.
    This endpoint is maintained for backward compatibility only.
    """
    try:
        repository = get_repository()
        assessment = await repository.find_by_id(assessment_id)
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        return PlayerAssessment(**assessment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessment (public): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment"
        )
