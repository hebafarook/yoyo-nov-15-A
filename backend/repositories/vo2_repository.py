"""VO2 Max repository for database operations."""

from typing import Optional, List, Dict, Any
from repositories.base import BaseRepository
from utils.database import db, prepare_for_mongo, parse_from_mongo
import logging

logger = logging.getLogger(__name__)


class VO2Repository(BaseRepository):
    """Repository for VO2 Max benchmark database operations."""
    
    def __init__(self):
        super().__init__(db.vo2_benchmarks)
    
    async def create_benchmark(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new VO2 benchmark."""
        prepared_data = prepare_for_mongo(data)
        await self.collection.insert_one(prepared_data)
        logger.info(f"VO2 benchmark created for player: {data.get('player_id')}")
        return data
    
    async def find_by_player_id(
        self, 
        player_id: str, 
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find all benchmarks for a player, sorted by test_date descending."""
        cursor = self.collection.find(
            {"player_id": player_id}
        ).sort("test_date", -1).limit(limit)
        
        docs = await cursor.to_list(length=limit)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def find_latest_by_player_id(
        self, 
        player_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find the latest benchmark for a player."""
        doc = await self.collection.find_one(
            {"player_id": player_id},
            sort=[("test_date", -1)]
        )
        return parse_from_mongo(doc) if doc else None
    
    async def delete_by_id(self, benchmark_id: str) -> bool:
        """Delete a benchmark by ID. Returns True if deleted."""
        result = await self.collection.delete_one({"id": benchmark_id})
        return result.deleted_count > 0
