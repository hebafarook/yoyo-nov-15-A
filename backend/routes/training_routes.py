"""
Training Routes
===============

Thin route handlers that delegate to TrainingService.
Same endpoints, same request/response, same status codes as before.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import logging

from models import (
    PeriodizedProgram, PeriodizedProgramCreate,
    TrainingProgram, TrainingProgramCreate
)
from services.training_service import (
    get_training_service,
    AssessmentNotFoundError,
    ProgramNotFoundError
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/periodized-programs", response_model=PeriodizedProgram)
async def create_periodized_program(program: PeriodizedProgramCreate):
    """Create a comprehensive periodized training program"""
    try:
        service = get_training_service()
        return await service.create_periodized_program(program)
    except Exception as e:
        logger.error(f"Error creating periodized program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create periodized program: {str(e)}"
        )


@router.get("/periodized-programs/{player_id}", response_model=Optional[PeriodizedProgram])
async def get_player_program(player_id: str):
    """Get the current periodized program for a player"""
    try:
        service = get_training_service()
        return await service.get_player_periodized_program(player_id)
    except Exception as e:
        logger.error(f"Error fetching player program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player program"
        )


@router.get("/current-routine/{player_id}")
async def get_current_routine(player_id: str):
    """Get today's training routine for a player"""
    try:
        service = get_training_service()
        return await service.get_current_routine(player_id)
    except Exception as e:
        logger.error(f"Error fetching current routine: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch current routine"
        )


@router.post("/programs", response_model=TrainingProgram)
async def create_training_program(program: TrainingProgramCreate):
    """Create AI-generated training program (legacy endpoint)"""
    try:
        service = get_training_service()
        return await service.create_training_program(program)
    except AssessmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error creating training program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create training program: {str(e)}"
        )


@router.get("/programs/{player_id}", response_model=List[TrainingProgram])
async def get_player_programs(player_id: str):
    """Get all training programs for a player"""
    try:
        service = get_training_service()
        return await service.get_player_training_programs(player_id)
    except Exception as e:
        logger.error(f"Error fetching player programs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player programs"
        )


@router.post("/adaptive-exercises")
async def get_adaptive_exercises(
    player_id: str,
    phase: str = "development",
    week_number: int = 1
):
    """Generate adaptive exercises based on player weaknesses"""
    try:
        service = get_training_service()
        return await service.get_adaptive_exercises(player_id, phase, week_number)
    except AssessmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error generating adaptive exercises: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate adaptive exercises"
        )
