"""
Elite Training Service
======================

Business logic for elite training operations.
Orchestrates elite training plan generation, wellness tracking, testing data,
load monitoring, and match scheduling.

IMPORTANT: This service delegates to elite_training_system.py for all
training logic and calculations. No training logic is duplicated here.
"""

from typing import Optional, List, Dict, Any
from repositories.elite_training_repository import (
    EliteTrainingRepository,
    get_elite_training_repository
)
from elite_training_system import (
    EliteTrainingGenerator,
    PlayerProfile, TestingData, Wellness, MatchSchedule,
    TacticalFocus, PreviousLoad, ExistingProgram,
    EliteTrainingOutput, RTP_PROTOCOLS, RTPStage
)
import logging

logger = logging.getLogger(__name__)


class TestingDataNotFoundError(Exception):
    """Raised when no testing data is found for a player."""
    def __init__(self, player_name: str):
        self.message = f"No testing data found for {player_name}"
        super().__init__(self.message)


class MatchScheduleNotFoundError(Exception):
    """Raised when no match schedule is found for a player."""
    def __init__(self, player_name: str):
        self.message = f"No match schedule found for {player_name}"
        super().__init__(self.message)


class InvalidRTPStageError(Exception):
    """Raised when an invalid RTP stage is provided."""
    def __init__(self, stage: str, valid_stages: List[str]):
        self.message = f"Invalid stage. Must be one of: {valid_stages}"
        super().__init__(self.message)


class RTPProtocolNotFoundError(Exception):
    """Raised when no RTP protocol is found for a stage."""
    def __init__(self, stage: str):
        self.message = f"No protocol found for stage {stage}"
        super().__init__(self.message)


class EliteTrainingService:
    """Service for elite training operations."""
    
    def __init__(self):
        self.repository = get_elite_training_repository()
        self.generator = EliteTrainingGenerator()
    
    # =========================================================================
    # ELITE TRAINING PLAN GENERATION
    # =========================================================================
    
    async def generate_training_plan(
        self,
        player_profile: PlayerProfile,
        testing_data: TestingData,
        wellness: Wellness,
        match_schedule: MatchSchedule,
        tactical_focus: TacticalFocus,
        previous_load: PreviousLoad,
        existing_program: Optional[ExistingProgram] = None
    ) -> EliteTrainingOutput:
        """
        Generate comprehensive elite training plan.
        
        Delegates to EliteTrainingGenerator for all training logic.
        """
        logger.info(f"Generating elite training plan for {player_profile.name}")
        
        # Use empty existing program if not provided
        if existing_program is None:
            existing_program = ExistingProgram()
        
        # Generate plan using the elite training engine
        output = self.generator.generate_daily_plan(
            player_profile=player_profile,
            testing_data=testing_data,
            wellness=wellness,
            match_schedule=match_schedule,
            tactical_focus=tactical_focus,
            previous_load=previous_load,
            existing_program=existing_program
        )
        
        # Store in database
        plan_data = output.dict()
        plan_data["player_name"] = player_profile.name
        await self.repository.create_training_plan(plan_data)
        
        logger.info(f"✅ Elite training plan generated successfully for {player_profile.name}")
        return output
    
    async def get_training_plans(
        self,
        player_name: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get recent training plans for a player."""
        plans = await self.repository.find_training_plans_by_player(player_name, limit)
        
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
    
    # =========================================================================
    # WELLNESS
    # =========================================================================
    
    async def log_wellness(
        self,
        wellness: Wellness,
        player_name: str
    ) -> Dict[str, Any]:
        """Log daily wellness data for a player."""
        wellness_data = wellness.dict()
        wellness_data["player_name"] = player_name
        
        wellness_id = await self.repository.create_wellness_log(wellness_data)
        
        return {
            "success": True,
            "wellness_id": wellness_id,
            "message": f"Wellness data logged for {player_name}"
        }
    
    async def get_wellness_history(
        self,
        player_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get wellness history for a player."""
        wellness_logs = await self.repository.find_wellness_logs_by_player(player_name, days)
        
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
    
    # =========================================================================
    # TESTING DATA
    # =========================================================================
    
    async def log_testing_data(
        self,
        testing_data: TestingData,
        player_name: str
    ) -> Dict[str, Any]:
        """Log physical testing data for a player."""
        test_data = testing_data.dict()
        test_data["player_name"] = player_name
        
        testing_id = await self.repository.create_testing_data(test_data)
        
        # Generate testing summary using the elite training engine
        testing_summary = self.generator.validate_testing_data(testing_data)
        
        return {
            "success": True,
            "testing_id": testing_id,
            "testing_summary": testing_summary.dict(),
            "message": f"Testing data logged for {player_name}"
        }
    
    async def get_latest_testing_data(
        self,
        player_name: str
    ) -> Dict[str, Any]:
        """Get latest testing data for a player."""
        testing_data = await self.repository.find_latest_testing_data(player_name)
        
        if not testing_data:
            raise TestingDataNotFoundError(player_name)
        
        # Generate testing summary using the elite training engine
        test_obj = TestingData(**testing_data)
        testing_summary = self.generator.validate_testing_data(test_obj)
        
        return {
            "player_name": player_name,
            "testing_data": testing_data,
            "testing_summary": testing_summary.dict()
        }
    
    # =========================================================================
    # LOAD MONITORING
    # =========================================================================
    
    async def log_load_data(
        self,
        load_data: PreviousLoad,
        player_name: str
    ) -> Dict[str, Any]:
        """Log training load data for a player."""
        load_dict = load_data.dict()
        load_dict["player_name"] = player_name
        
        load_id = await self.repository.create_load_log(load_dict)
        
        # Assess load status using the elite training engine
        load_status = self.generator.assess_load_status(load_data)
        
        return {
            "success": True,
            "load_id": load_id,
            "load_status": load_status.value,
            "message": f"Load data logged for {player_name}",
            "warning": "OVERLOAD - Consider recovery day" if load_status.value == "overload" else None
        }
    
    async def get_load_history(
        self,
        player_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get load monitoring history for a player."""
        load_logs = await self.repository.find_load_logs_by_player(player_name, days)
        
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
    
    # =========================================================================
    # RTP PROTOCOLS
    # =========================================================================
    
    def get_rtp_protocol(self, stage: str) -> Dict[str, Any]:
        """Get Return-to-Play protocol for a specific stage."""
        # Validate stage
        try:
            rtp_stage = RTPStage(stage)
        except ValueError:
            raise InvalidRTPStageError(stage, [s.value for s in RTPStage])
        
        protocol = RTP_PROTOCOLS.get(rtp_stage)
        
        if not protocol:
            raise RTPProtocolNotFoundError(stage)
        
        return {
            "stage": rtp_stage.value,
            "protocol": protocol
        }
    
    def get_all_rtp_protocols(self) -> Dict[str, Any]:
        """Get all Return-to-Play protocols."""
        all_protocols = {}
        for stage in RTPStage:
            all_protocols[stage.value] = RTP_PROTOCOLS.get(stage)
        
        return {
            "protocols": all_protocols,
            "total_stages": len(RTPStage)
        }
    
    # =========================================================================
    # MATCH SCHEDULES
    # =========================================================================
    
    async def update_match_schedule(
        self,
        match_schedule: MatchSchedule,
        player_name: str
    ) -> Dict[str, Any]:
        """Update match schedule for a player/team."""
        schedule_data = match_schedule.dict()
        schedule_data["player_name"] = player_name
        
        await self.repository.upsert_match_schedule(player_name, schedule_data)
        
        return {
            "success": True,
            "message": f"Match schedule updated for {player_name}",
            "days_to_match": match_schedule.days_to_next_match
        }
    
    async def get_match_schedule(self, player_name: str) -> Dict[str, Any]:
        """Get current match schedule for a player."""
        schedule = await self.repository.find_match_schedule(player_name)
        
        if not schedule:
            raise MatchScheduleNotFoundError(player_name)
        
        return {
            "player_name": player_name,
            "schedule": schedule
        }


# Singleton instance
_elite_training_service: Optional[EliteTrainingService] = None


def get_elite_training_service() -> EliteTrainingService:
    """Get or create the elite training service singleton."""
    global _elite_training_service
    if _elite_training_service is None:
        _elite_training_service = EliteTrainingService()
    return _elite_training_service
