"""Progress repository for database operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from repositories.base import BaseRepository
from utils.database import db, prepare_for_mongo, parse_from_mongo
import logging

logger = logging.getLogger(__name__)


class ProgressRepository:
    """Repository for progress-related database operations."""
    
    def __init__(self):
        self.daily_progress = db.daily_progress
        self.weekly_progress = db.weekly_progress
        self.performance_metrics = db.performance_metrics
        self.assessments = db.assessments
        self.periodized_programs = db.periodized_programs
    
    # =========================================================================
    # DAILY PROGRESS
    # =========================================================================
    
    async def create_daily_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new daily progress entry."""
        prepared_data = prepare_for_mongo(data)
        await self.daily_progress.insert_one(prepared_data)
        logger.info(f"Daily progress created for player: {data.get('player_id')}")
        return data
    
    async def find_daily_progress_by_player(
        self,
        player_id: str,
        days: int = 30,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find daily progress entries for a player within a date range."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        cursor = self.daily_progress.find(
            {
                "player_id": player_id,
                "date": {"$gte": start_date}
            }
        ).sort("date", -1).limit(limit)
        
        docs = await cursor.to_list(length=limit)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def find_recent_daily_progress(
        self,
        player_id: str,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Find recent daily progress entries for a player."""
        cursor = self.daily_progress.find(
            {"player_id": player_id}
        ).sort("date", -1).limit(limit)
        
        docs = await cursor.to_list(length=limit)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def count_daily_progress(
        self,
        player_id: str,
        days: int = 30
    ) -> int:
        """Count daily progress entries for a player within a date range."""
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        return await self.daily_progress.count_documents(
            {
                "player_id": player_id,
                "date": {"$gte": start_date}
            }
        )
    
    # =========================================================================
    # WEEKLY PROGRESS
    # =========================================================================
    
    async def create_weekly_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new weekly progress entry."""
        prepared_data = prepare_for_mongo(data)
        await self.weekly_progress.insert_one(prepared_data)
        logger.info(f"Weekly progress created for player: {data.get('player_id')}")
        return data
    
    async def find_weekly_progress_by_player(
        self,
        player_id: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find weekly progress entries for a player."""
        cursor = self.weekly_progress.find(
            {"player_id": player_id}
        ).sort("created_at", -1).limit(limit)
        
        docs = await cursor.to_list(length=limit)
        return [parse_from_mongo(doc) for doc in docs]
    
    # =========================================================================
    # PERFORMANCE METRICS
    # =========================================================================
    
    async def create_performance_metric(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new performance metric entry."""
        prepared_data = prepare_for_mongo(data)
        await self.performance_metrics.insert_one(prepared_data)
        return data
    
    async def find_metrics_by_player(
        self,
        player_id: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find performance metrics for a player."""
        cursor = self.performance_metrics.find(
            {"player_id": player_id}
        ).sort("measurement_date", -1).limit(limit)
        
        docs = await cursor.to_list(length=limit)
        return [parse_from_mongo(doc) for doc in docs]
    
    # =========================================================================
    # ASSESSMENTS & PROGRAMS
    # =========================================================================
    
    async def find_latest_assessment(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Find the latest assessment for a player."""
        doc = await self.assessments.find_one(
            {"player_name": player_id},
            sort=[("created_at", -1)]
        )
        return parse_from_mongo(doc) if doc else None
    
    async def find_latest_program(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Find the latest periodized program for a player."""
        doc = await self.periodized_programs.find_one(
            {"player_id": player_id},
            sort=[("created_at", -1)]
        )
        return parse_from_mongo(doc) if doc else None
