"""
API Routes for Elite Soccer Training & Assessment System
FIFA & Manchester United Edition

Thin route handlers that delegate to EliteTrainingService.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from elite_training_system import (
    PlayerProfile, TestingData, Wellness, MatchSchedule,
    TacticalFocus, PreviousLoad, ExistingProgram,
    EliteTrainingOutput
)
from services.elite_training_service import (
    get_elite_training_service,
    TestingDataNotFoundError,
    MatchScheduleNotFoundError,
    InvalidRTPStageError,
    RTPProtocolNotFoundError
)

router = APIRouter(prefix="/elite-training", tags=["Elite Training System"])
logger = logging.getLogger(__name__)


@router.post("/generate-plan", response_model=EliteTrainingOutput)
async def generate_elite_training_plan(
    player_profile: PlayerProfile,
    testing_data: TestingData,
    wellness: Wellness,
    match_schedule: MatchSchedule,
    tactical_focus: TacticalFocus,
    previous_load: PreviousLoad,
    existing_program: Optional[ExistingProgram] = None
):
    """
    Generate comprehensive elite training plan based on FIFA Four-Corner Model
    and Manchester United-style tactical periodisation.
    
    Integrates testing data, wellness, match schedule, and tactical focus
    to create dynamic daily and weekly training plans.
    """
    try:
        service = get_elite_training_service()
        return await service.generate_training_plan(
            player_profile=player_profile,
            testing_data=testing_data,
            wellness=wellness,
            match_schedule=match_schedule,
            tactical_focus=tactical_focus,
            previous_load=previous_load,
            existing_program=existing_program
        )
    except Exception as e:
        logger.error(f"Error generating elite training plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate training plan: {str(e)}")


@router.post("/wellness", status_code=201)
async def log_wellness_data(wellness: Wellness, player_name: str):
    """Log daily wellness data for a player"""
    try:
        service = get_elite_training_service()
        return await service.log_wellness(wellness, player_name)
    except Exception as e:
        logger.error(f"Error logging wellness data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wellness/{player_name}")
async def get_wellness_history(player_name: str, days: int = 7):
    """Get wellness history for a player"""
    try:
        service = get_elite_training_service()
        return await service.get_wellness_history(player_name, days)
    except Exception as e:
        logger.error(f"Error fetching wellness history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/testing-data", status_code=201)
async def log_testing_data(testing_data: TestingData, player_name: str):
    """Log physical testing data for a player"""
    try:
        service = get_elite_training_service()
        return await service.log_testing_data(testing_data, player_name)
    except Exception as e:
        logger.error(f"Error logging testing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/testing-data/{player_name}")
async def get_latest_testing_data(player_name: str):
    """Get latest testing data for a player"""
    try:
        service = get_elite_training_service()
        return await service.get_latest_testing_data(player_name)
    except TestingDataNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching testing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-monitoring", status_code=201)
async def log_load_data(load_data: PreviousLoad, player_name: str):
    """Log training load data for a player"""
    try:
        service = get_elite_training_service()
        return await service.log_load_data(load_data, player_name)
    except Exception as e:
        logger.error(f"Error logging load data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/load-monitoring/{player_name}")
async def get_load_history(player_name: str, days: int = 7):
    """Get load monitoring history for a player"""
    try:
        service = get_elite_training_service()
        return await service.get_load_history(player_name, days)
    except Exception as e:
        logger.error(f"Error fetching load history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rtp-protocol/{stage}")
async def get_rtp_protocol(stage: str):
    """Get Return-to-Play protocol for a specific stage"""
    try:
        service = get_elite_training_service()
        return service.get_rtp_protocol(stage)
    except InvalidRTPStageError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except RTPProtocolNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching RTP protocol: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rtp-protocols")
async def get_all_rtp_protocols():
    """Get all Return-to-Play protocols"""
    try:
        service = get_elite_training_service()
        return service.get_all_rtp_protocols()
    except Exception as e:
        logger.error(f"Error fetching RTP protocols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training-plans/{player_name}")
async def get_training_plans(player_name: str, limit: int = 10):
    """Get recent training plans for a player"""
    try:
        service = get_elite_training_service()
        return await service.get_training_plans(player_name, limit)
    except Exception as e:
        logger.error(f"Error fetching training plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match-schedule", status_code=201)
async def update_match_schedule(match_schedule: MatchSchedule, player_name: str):
    """Update match schedule for a player/team"""
    try:
        service = get_elite_training_service()
        return await service.update_match_schedule(match_schedule, player_name)
    except Exception as e:
        logger.error(f"Error updating match schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/match-schedule/{player_name}")
async def get_match_schedule(player_name: str):
    """Get current match schedule for a player"""
    try:
        service = get_elite_training_service()
        return await service.get_match_schedule(player_name)
    except MatchScheduleNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error fetching match schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))
