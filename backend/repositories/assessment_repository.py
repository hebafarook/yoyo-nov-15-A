"""Assessment repository for database operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from repositories.base import BaseRepository
from utils.database import db, prepare_for_mongo, parse_from_mongo
import logging

logger = logging.getLogger(__name__)


class AssessmentRepository(BaseRepository):
    """Repository for assessment-related database operations."""
    
    def __init__(self):
        super().__init__(db.assessments)
        self.users = db.users
    
    # =========================================================================
    # ASSESSMENT CRUD
    # =========================================================================
    
    async def create_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assessment."""
        prepared_data = prepare_for_mongo(assessment_data)
        await self.collection.insert_one(prepared_data)
        logger.info(f"Assessment created for player: {assessment_data.get('player_name')}")
        return assessment_data
    
    async def find_by_id(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Find an assessment by ID."""
        doc = await self.collection.find_one({"id": assessment_id})
        return parse_from_mongo(doc) if doc else None
    
    async def find_all(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Find all assessments, sorted by created_at descending."""
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def find_by_player_name(
        self,
        player_name: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find all assessments for a player, sorted by created_at descending."""
        cursor = self.collection.find(
            {"player_name": player_name}
        ).sort("created_at", -1).limit(limit)
        
        docs = await cursor.to_list(length=limit)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def find_latest_by_player_name(
        self,
        player_name: str
    ) -> Optional[Dict[str, Any]]:
        """Find the latest assessment for a player."""
        doc = await self.collection.find_one(
            {"player_name": player_name},
            sort=[("created_at", -1)]
        )
        return parse_from_mongo(doc) if doc else None
    
    async def update_assessment(
        self,
        assessment_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an assessment. Returns updated doc or None if not found."""
        prepared_data = prepare_for_mongo(update_data)
        
        result = await self.collection.update_one(
            {"id": assessment_id},
            {"$set": prepared_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.find_by_id(assessment_id)
    
    async def delete_assessment(self, assessment_id: str) -> bool:
        """Delete an assessment. Returns True if deleted."""
        result = await self.collection.delete_one({"id": assessment_id})
        return result.deleted_count > 0
    
    # =========================================================================
    # USER ACCESS
    # =========================================================================
    
    async def find_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find a user by ID for access checks."""
        doc = await self.users.find_one({"id": user_id})
        return parse_from_mongo(doc) if doc else None
    
    # =========================================================================
    # LEGACY METHODS (for backward compatibility)
    # =========================================================================
    
    async def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Find all assessments for a user by user_id."""
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=1000)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def find_baseline(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find baseline assessment for a user."""
        doc = await self.collection.find_one({"user_id": user_id, "is_baseline": True})
        return parse_from_mongo(doc) if doc else None
    
    async def find_latest(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find latest assessment for a user by user_id."""
        doc = await self.collection.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        return parse_from_mongo(doc) if doc else None
    
    async def count_user_assessments(self, user_id: str) -> int:
        """Count total assessments for a user."""
        return await self.collection.count_documents({"user_id": user_id})
