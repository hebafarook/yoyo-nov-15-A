"""
VO2 Max Routes
==============

Thin route handlers that delegate to VO2Service.
Same endpoints, same request/response, same status codes as before.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import logging

from models import VO2MaxBenchmark, VO2MaxBenchmarkCreate
from services.vo2_service import get_vo2_service, VO2ValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/benchmarks", response_model=VO2MaxBenchmark)
async def save_vo2_benchmark(benchmark: VO2MaxBenchmarkCreate):
    """Save a VO2 Max benchmark test result"""
    try:
        service = get_vo2_service()
        return await service.create_benchmark(benchmark)
    except Exception as e:
        logger.error(f"Error saving VO2 benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save VO2 benchmark: {str(e)}"
        )


@router.get("/benchmarks/{player_id}", response_model=List[VO2MaxBenchmark])
async def get_vo2_benchmarks(player_id: str):
    """Get all VO2 Max benchmarks for a player"""
    try:
        service = get_vo2_service()
        return await service.get_benchmarks_by_player(player_id)
    except Exception as e:
        logger.error(f"Error fetching VO2 benchmarks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch VO2 benchmarks"
        )


@router.get("/benchmarks/latest/{player_id}", response_model=Optional[VO2MaxBenchmark])
async def get_latest_vo2_benchmark(player_id: str):
    """Get the latest VO2 Max benchmark for a player"""
    try:
        service = get_vo2_service()
        return await service.get_latest_benchmark(player_id)
    except Exception as e:
        logger.error(f"Error fetching latest VO2 benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest VO2 benchmark"
        )


@router.delete("/benchmarks/{benchmark_id}")
async def delete_vo2_benchmark(benchmark_id: str):
    """Delete a specific VO2 Max benchmark"""
    try:
        service = get_vo2_service()
        deleted = await service.delete_benchmark(benchmark_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benchmark not found"
            )
        
        return {"message": "Benchmark deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting VO2 benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete benchmark"
        )


@router.get("/calculate")
async def calculate_vo2_max(
    age: int,
    gender: str,
    resting_heart_rate: float,
    max_heart_rate: float
):
    """Calculate VO2 Max using ACSM formulas"""
    try:
        service = get_vo2_service()
        return service.calculate_vo2_max(
            age=age,
            gender=gender,
            resting_heart_rate=resting_heart_rate,
            max_heart_rate=max_heart_rate
        )
    except VO2ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating VO2 Max: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate VO2 Max"
        )
