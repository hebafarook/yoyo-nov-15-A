"""
API Routes for Elite Soccer Training & Assessment System
FIFA & Manchester United Edition
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone
import logging

from elite_training_system import (
    EliteTrainingGenerator,
    PlayerProfile, TestingData, Wellness, MatchSchedule,
    TacticalFocus, PreviousLoad, ExistingProgram,
    EliteTrainingOutput, RTP_PROTOCOLS
)
from utils.database import get_database

router = APIRouter(prefix="/elite-training", tags=["Elite Training System"])
logger = logging.getLogger(__name__)

# Initialize generator
elite_generator = EliteTrainingGenerator()

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
        logger.info(f"Generating elite training plan for {player_profile.name}")
        
        # Use empty existing program if not provided
        if existing_program is None:
            existing_program = ExistingProgram()
        
        # Generate plan
        output = elite_generator.generate_daily_plan(
            player_profile=player_profile,
            testing_data=testing_data,
            wellness=wellness,
            match_schedule=match_schedule,
            tactical_focus=tactical_focus,
            previous_load=previous_load,
            existing_program=existing_program
        )
        
        # Store in database
        db = await get_db()
        plan_data = output.dict()
        plan_data["created_at"] = datetime.now(timezone.utc).isoformat()
        await db.elite_training_plans.insert_one(plan_data)
        
        logger.info(f"✅ Elite training plan generated successfully for {player_profile.name}")
        return output
        
    except Exception as e:
        logger.error(f"Error generating elite training plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate training plan: {str(e)}")


@router.post("/wellness", status_code=201)
async def log_wellness_data(wellness: Wellness, player_name: str):
    """Log daily wellness data for a player"""
    try:
        db = await get_db()
        wellness_data = wellness.dict()
        wellness_data["player_name"] = player_name
        wellness_data["logged_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.wellness_logs.insert_one(wellness_data)
        
        return {
            "success": True,
            "wellness_id": str(result.inserted_id),
            "message": f"Wellness data logged for {player_name}"
        }
        
    except Exception as e:
        logger.error(f"Error logging wellness data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wellness/{player_name}")
async def get_wellness_history(player_name: str, days: int = 7):
    """Get wellness history for a player"""
    try:
        db = await get_db()
        
        # Get recent wellness logs
        wellness_logs = await db.wellness_logs.find(
            {"player_name": player_name}
        ).sort("date", -1).limit(days).to_list(length=days)
        
        if not wellness_logs:
            return {
                "player_name": player_name,
                "wellness_logs": [],
                "message": "No wellness data found"
            }
        
        return {
            "player_name": player_name,
            "wellness_logs": wellness_logs,
            "average_sleep": sum(log.get("sleep_hours", 0) for log in wellness_logs) / len(wellness_logs),
            "average_soreness": sum(log.get("soreness_1_5", 0) for log in wellness_logs) / len(wellness_logs),
            "average_mood": sum(log.get("mood_1_5", 0) for log in wellness_logs) / len(wellness_logs)
        }
        
    except Exception as e:
        logger.error(f"Error fetching wellness history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/testing-data", status_code=201)
async def log_testing_data(testing_data: TestingData, player_name: str):
    """Log physical testing data for a player"""
    try:
        db = await get_db()
        test_data = testing_data.dict()
        test_data["player_name"] = player_name
        test_data["logged_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.testing_data.insert_one(test_data)
        
        # Also generate testing summary
        testing_summary = elite_generator.validate_testing_data(testing_data)
        
        return {
            "success": True,
            "testing_id": str(result.inserted_id),
            "testing_summary": testing_summary.dict(),
            "message": f"Testing data logged for {player_name}"
        }
        
    except Exception as e:
        logger.error(f"Error logging testing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/testing-data/{player_name}")
async def get_latest_testing_data(player_name: str):
    """Get latest testing data for a player"""
    try:
        db = await get_db()
        
        testing_data = await db.testing_data.find_one(
            {"player_name": player_name},
            sort=[("test_date", -1)]
        )
        
        if not testing_data:
            raise HTTPException(status_code=404, detail=f"No testing data found for {player_name}")
        
        # Generate testing summary
        test_obj = TestingData(**testing_data)
        testing_summary = elite_generator.validate_testing_data(test_obj)
        
        return {
            "player_name": player_name,
            "testing_data": testing_data,
            "testing_summary": testing_summary.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching testing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-monitoring", status_code=201)
async def log_load_data(load_data: PreviousLoad, player_name: str):
    """Log training load data for a player"""
    try:
        db = await get_db()
        load_dict = load_data.dict()
        load_dict["player_name"] = player_name
        load_dict["logged_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.load_monitoring.insert_one(load_dict)
        
        # Assess load status
        load_status = elite_generator.assess_load_status(load_data)
        
        return {
            "success": True,
            "load_id": str(result.inserted_id),
            "load_status": load_status.value,
            "message": f"Load data logged for {player_name}",
            "warning": "OVERLOAD - Consider recovery day" if load_status.value == "overload" else None
        }
        
    except Exception as e:
        logger.error(f"Error logging load data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/load-monitoring/{player_name}")
async def get_load_history(player_name: str, days: int = 7):
    """Get load monitoring history for a player"""
    try:
        db = await get_db()
        
        load_logs = await db.load_monitoring.find(
            {"player_name": player_name}
        ).sort("date", -1).limit(days).to_list(length=days)
        
        if not load_logs:
            return {
                "player_name": player_name,
                "load_logs": [],
                "message": "No load data found"
            }
        
        return {
            "player_name": player_name,
            "load_logs": load_logs,
            "average_acwr": sum(log.get("acwr", 0) for log in load_logs) / len(load_logs),
            "average_rpe": sum(log.get("rpe_avg", 0) for log in load_logs) / len(load_logs),
            "total_distance": sum(log.get("total_distance_m", 0) for log in load_logs)
        }
        
    except Exception as e:
        logger.error(f"Error fetching load history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rtp-protocol/{stage}")
async def get_rtp_protocol(stage: str):
    """Get Return-to-Play protocol for a specific stage"""
    try:
        from elite_training_system import RTPStage
        
        # Convert string to enum
        try:
            rtp_stage = RTPStage(stage)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stage. Must be one of: {[s.value for s in RTPStage]}"
            )
        
        protocol = RTP_PROTOCOLS.get(rtp_stage)
        
        if not protocol:
            raise HTTPException(status_code=404, detail=f"No protocol found for stage {stage}")
        
        return {
            "stage": rtp_stage.value,
            "protocol": protocol
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching RTP protocol: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rtp-protocols")
async def get_all_rtp_protocols():
    """Get all Return-to-Play protocols"""
    try:
        from elite_training_system import RTPStage
        
        all_protocols = {}
        for stage in RTPStage:
            all_protocols[stage.value] = RTP_PROTOCOLS.get(stage)
        
        return {
            "protocols": all_protocols,
            "total_stages": len(RTPStage)
        }
        
    except Exception as e:
        logger.error(f"Error fetching RTP protocols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training-plans/{player_name}")
async def get_training_plans(player_name: str, limit: int = 10):
    """Get recent training plans for a player"""
    try:
        db = await get_db()
        
        plans = await db.elite_training_plans.find(
            {"player_name": player_name}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        if not plans:
            return {
                "player_name": player_name,
                "plans": [],
                "message": "No training plans found"
            }
        
        return {
            "player_name": player_name,
            "plans": plans,
            "count": len(plans)
        }
        
    except Exception as e:
        logger.error(f"Error fetching training plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match-schedule", status_code=201)
async def update_match_schedule(match_schedule: MatchSchedule, player_name: str):
    """Update match schedule for a player/team"""
    try:
        db = await get_db()
        schedule_data = match_schedule.dict()
        schedule_data["player_name"] = player_name
        schedule_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Upsert - update if exists, insert if not
        result = await db.match_schedules.update_one(
            {"player_name": player_name},
            {"$set": schedule_data},
            upsert=True
        )
        
        return {
            "success": True,
            "message": f"Match schedule updated for {player_name}",
            "days_to_match": match_schedule.days_to_next_match
        }
        
    except Exception as e:
        logger.error(f"Error updating match schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/match-schedule/{player_name}")
async def get_match_schedule(player_name: str):
    """Get current match schedule for a player"""
    try:
        db = await get_db()
        
        schedule = await db.match_schedules.find_one({"player_name": player_name})
        
        if not schedule:
            raise HTTPException(status_code=404, detail=f"No match schedule found for {player_name}")
        
        return {
            "player_name": player_name,
            "schedule": schedule
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching match schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))
