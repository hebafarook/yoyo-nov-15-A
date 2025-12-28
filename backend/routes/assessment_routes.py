"""
Assessment Routes
=================

Thin route handlers that delegate to AssessmentService.
Same endpoints, same request/response, same status codes as before.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import logging

from models import PlayerAssessment, AssessmentCreate
from services.assessment_service import (
    get_assessment_service,
    AssessmentNotFoundError,
    AccessDeniedError
)
from routes.auth_routes import verify_token_async

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()


@router.post("/", response_model=PlayerAssessment)
async def create_assessment(
    assessment: AssessmentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new player assessment with automatic scoring"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.create_assessment(assessment, current_user)
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )


@router.get("/", response_model=List[PlayerAssessment])
async def get_all_assessments(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all player assessments (coaches only)"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.get_all_assessments(current_user)
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessments"
        )


@router.get("/player/{player_name}", response_model=List[PlayerAssessment])
async def get_player_assessments(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all assessments for a specific player"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.get_player_assessments(player_name, current_user)
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player assessments"
        )


@router.get("/player/{player_name}/latest", response_model=Optional[PlayerAssessment])
async def get_latest_assessment(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get the latest assessment for a specific player"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.get_latest_assessment(player_name, current_user)
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest assessment"
        )


@router.get("/player/{player_name}/status")
async def get_assessment_status(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get assessment status including latest assessment and next due date"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.get_assessment_status(player_name, current_user)
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment status"
        )


@router.get("/player/{player_name}/analysis")
async def get_player_analysis(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get detailed analysis for a player including strengths, weaknesses, and recommendations"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.get_player_analysis(player_name, current_user)
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except AssessmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating player analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate player analysis"
        )


@router.get("/{assessment_id}", response_model=PlayerAssessment)
async def get_assessment(
    assessment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific assessment by ID"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.get_assessment_by_id(assessment_id, current_user)
    except AssessmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment"
        )


@router.put("/{assessment_id}", response_model=PlayerAssessment)
async def update_assessment(
    assessment_id: str,
    assessment_update: AssessmentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update an existing assessment"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        return await service.update_assessment(assessment_id, assessment_update, current_user)
    except AssessmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update assessment"
        )


@router.delete("/{assessment_id}")
async def delete_assessment(
    assessment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an assessment"""
    try:
        current_user = await verify_token_async(credentials.credentials)
        service = get_assessment_service()
        await service.delete_assessment(assessment_id, current_user)
        return {"message": "Assessment deleted successfully"}
    except AssessmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete assessment"
        )
