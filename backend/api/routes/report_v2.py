"""
YoYo Report v2 API Routes
=========================

New endpoint for the presentation-layer YoYo Report v2.
This is a READ-ONLY endpoint that formats existing data.
Does NOT modify any existing endpoints or calculations.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
import logging
from datetime import datetime, timezone

from utils.database import db
from routes.auth_routes import verify_token
from reporting.yoyo_report_v2 import format_yoyo_report_v2, validate_report_structure

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/yoyo/{player_id}")
async def get_yoyo_report_v2(
    player_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get YoYo Report v2 for a player.
    
    This is a presentation-only endpoint that:
    - Reads existing data from database
    - Formats it into the standardized 11-section report
    - Returns machine-readable JSON object
    
    NO NEW CALCULATIONS. NO DATA MODIFICATIONS.
    
    Args:
        player_id: The player/user ID to generate report for
    
    Returns:
        YoYo Report v2 with:
        - report_sections: List of 11 sections in fixed order
        - report_json: Machine-readable JSON with required schema
        - meta: Report metadata
    """
    try:
        user_id = current_user.get('user_id') or current_user.get('id')
        
        logger.info(f"Generating YoYo Report v2 for player_id: {player_id}")
        
        # Fetch user profile
        user = await db.users.find_one(
            {"$or": [{"id": player_id}, {"id": user_id}]},
            {"_id": 0}
        )
        
        # Fetch latest assessment
        assessment = await db.assessments.find_one(
            {"$or": [
                {"user_id": player_id},
                {"user_id": user_id},
                {"id": player_id}
            ]},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        
        # Fetch latest benchmark
        benchmark = await db.benchmarks.find_one(
            {"$or": [
                {"user_id": player_id},
                {"user_id": user_id},
                {"player_name": assessment.get('player_name') if assessment else None}
            ]},
            {"_id": 0},
            sort=[("benchmark_date", -1)]
        )
        
        # Fetch training program if exists
        training_program = await db.training_programs.find_one(
            {"$or": [
                {"player_id": player_id},
                {"player_id": user_id}
            ]},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        
        # Fetch comprehensive report if exists (has AI analysis)
        generated_report = await db.comprehensive_reports.find_one(
            {"$or": [
                {"user_id": player_id},
                {"user_id": user_id}
            ]},
            {"_id": 0},
            sort=[("generated_at", -1)]
        )
        
        # Fetch match history if exists
        match_history = await db.matches.find(
            {"$or": [
                {"player_id": player_id},
                {"player_id": user_id}
            ]},
            {"_id": 0}
        ).sort("date", -1).limit(10).to_list(10)
        
        # Check if we have minimum data (at least assessment or user)
        if not assessment and not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No assessment or user data found for player_id: {player_id}"
            )
        
        # Generate the report
        report = format_yoyo_report_v2(
            user=user,
            assessment=assessment,
            benchmark=benchmark,
            training_program=training_program,
            injury_data=None,  # Can be added if injury collection exists
            match_history=match_history,
            generated_report=generated_report
        )
        
        # Validate report structure
        validation = validate_report_structure(report)
        if not validation['valid']:
            logger.warning(f"Report validation warnings: {validation['errors']}")
        
        logger.info(f"Successfully generated YoYo Report v2 for player_id: {player_id}")
        
        return {
            "success": True,
            "player_id": player_id,
            "report": report,
            "validation": validation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating YoYo Report v2: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate YoYo Report v2: {str(e)}"
        )


@router.get("/yoyo/{player_id}/sections")
async def get_yoyo_report_sections_only(
    player_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get only the 11 sections of YoYo Report v2 (without full JSON).
    Lighter payload for frontend rendering.
    """
    result = await get_yoyo_report_v2(player_id, current_user)
    
    return {
        "success": True,
        "player_id": player_id,
        "sections": result['report']['report_sections'],
        "meta": result['report']['meta']
    }


@router.get("/yoyo/{player_id}/json")
async def get_yoyo_report_json_only(
    player_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get only the JSON object of YoYo Report v2.
    Machine-readable data for integrations.
    """
    result = await get_yoyo_report_v2(player_id, current_user)
    
    return {
        "success": True,
        "player_id": player_id,
        "json": result['report']['report_json'],
        "meta": result['report']['meta']
    }
