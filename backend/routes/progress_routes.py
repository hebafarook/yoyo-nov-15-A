"""
Progress Routes
===============

Thin route handlers that delegate to ProgressService.
Same endpoints, same request/response, same status codes as before.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from models import (
    DailyProgress, DailyProgressCreate, WeeklyProgress, WeeklyProgressCreate
)
from services.progress_service import get_progress_service, ProgressNotFoundError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/daily", response_model=DailyProgress)
async def log_daily_progress(progress: DailyProgressCreate):
    """Log daily training progress and exercise completions"""
    try:
        service = get_progress_service()
        return await service.log_daily_progress(progress)
    except Exception as e:
        logger.error(f"Error logging daily progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log daily progress: {str(e)}"
        )


@router.get("/daily/{player_id}", response_model=List[DailyProgress])
async def get_daily_progress(player_id: str, days: int = 30):
    """Get daily progress history for a player"""
    try:
        service = get_progress_service()
        return await service.get_daily_progress(player_id, days)
    except Exception as e:
        logger.error(f"Error fetching daily progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch daily progress"
        )


@router.post("/weekly", response_model=WeeklyProgress)
async def log_weekly_progress(progress: WeeklyProgressCreate):
    """Log weekly training progress"""
    try:
        service = get_progress_service()
        return await service.log_weekly_progress(progress)
    except Exception as e:
        logger.error(f"Error logging weekly progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log weekly progress: {str(e)}"
        )


@router.get("/weekly/{player_id}", response_model=List[WeeklyProgress])
async def get_weekly_progress(player_id: str):
    """Get weekly progress history for a player"""
    try:
        service = get_progress_service()
        return await service.get_weekly_progress(player_id)
    except Exception as e:
        logger.error(f"Error fetching weekly progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch weekly progress"
        )


@router.get("/metrics/{player_id}")
async def get_performance_metrics(player_id: str):
    """Get performance metrics and progress tracking"""
    try:
        service = get_progress_service()
        return await service.get_performance_metrics(player_id)
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch performance metrics"
        )


@router.get("/summary/{player_id}")
async def get_progress_summary(player_id: str):
    """Get a comprehensive progress summary for a player"""
    try:
        service = get_progress_service()
        return await service.get_progress_summary(player_id)
    except ProgressNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error generating progress summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate progress summary"
        )
