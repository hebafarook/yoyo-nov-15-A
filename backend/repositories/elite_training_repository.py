"""
Elite Training Repository
=========================

Database access layer for elite training operations.
Handles all MongoDB interactions for elite training plans, wellness, testing data,
load monitoring, and match schedules.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from utils.database import get_database
import logging

logger = logging.getLogger(__name__)


class EliteTrainingRepository:
    """Repository for elite training database operations."""
    
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        """Lazy load database connection."""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    # =========================================================================
    # ELITE TRAINING PLANS
    # =========================================================================
    
    async def create_training_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new elite training plan."""
        plan_data["created_at"] = datetime.now(timezone.utc).isoformat()
        await self.db.elite_training_plans.insert_one(plan_data)
        logger.info(f"Elite training plan created for player: {plan_data.get('player_name')}")
        return plan_data
    
    async def find_training_plans_by_player(
        self, 
        player_name: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find recent training plans for a player."""
        cursor = self.db.elite_training_plans.find(
            {"player_name": player_name}
        ).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # =========================================================================
    # WELLNESS
    # =========================================================================
    
    async def create_wellness_log(self, wellness_data: Dict[str, Any]) -> str:
        """Create a new wellness log entry. Returns inserted_id as string."""
        wellness_data["logged_at"] = datetime.now(timezone.utc).isoformat()
        result = await self.db.wellness_logs.insert_one(wellness_data)
        return str(result.inserted_id)
    
    async def find_wellness_logs_by_player(
        self, 
        player_name: str, 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Find recent wellness logs for a player."""
        cursor = self.db.wellness_logs.find(
            {"player_name": player_name}
        ).sort("date", -1).limit(days)
        return await cursor.to_list(length=days)
    
    # =========================================================================
    # TESTING DATA
    # =========================================================================
    
    async def create_testing_data(self, testing_data: Dict[str, Any]) -> str:
        """Create a new testing data entry. Returns inserted_id as string."""
        testing_data["logged_at"] = datetime.now(timezone.utc).isoformat()
        result = await self.db.testing_data.insert_one(testing_data)
        return str(result.inserted_id)
    
    async def find_latest_testing_data(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Find the latest testing data for a player."""
        return await self.db.testing_data.find_one(
            {"player_name": player_name},
            sort=[("test_date", -1)]
        )
    
    # =========================================================================
    # LOAD MONITORING
    # =========================================================================
    
    async def create_load_log(self, load_data: Dict[str, Any]) -> str:
        """Create a new load monitoring entry. Returns inserted_id as string."""
        load_data["logged_at"] = datetime.now(timezone.utc).isoformat()
        result = await self.db.load_monitoring.insert_one(load_data)
        return str(result.inserted_id)
    
    async def find_load_logs_by_player(
        self, 
        player_name: str, 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Find recent load monitoring logs for a player."""
        cursor = self.db.load_monitoring.find(
            {"player_name": player_name}
        ).sort("date", -1).limit(days)
        return await cursor.to_list(length=days)
    
    # =========================================================================
    # MATCH SCHEDULES
    # =========================================================================
    
    async def upsert_match_schedule(
        self, 
        player_name: str, 
        schedule_data: Dict[str, Any]
    ) -> None:
        """Update or insert match schedule for a player."""
        schedule_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.db.match_schedules.update_one(
            {"player_name": player_name},
            {"$set": schedule_data},
            upsert=True
        )
    
    async def find_match_schedule(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Find match schedule for a player."""
        return await self.db.match_schedules.find_one({"player_name": player_name})


# Singleton instance
_elite_training_repository: Optional[EliteTrainingRepository] = None


def get_elite_training_repository() -> EliteTrainingRepository:
    """Get or create the elite training repository singleton."""
    global _elite_training_repository
    if _elite_training_repository is None:
        _elite_training_repository = EliteTrainingRepository()
    return _elite_training_repository
