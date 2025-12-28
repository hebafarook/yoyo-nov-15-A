"""
Drill Repository
================

Database access layer for drill operations.
Handles MongoDB interactions for drill storage and retrieval.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from utils.database import get_database
import logging

logger = logging.getLogger(__name__)


class DrillRepository:
    """Repository for drill database operations."""
    
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        """Lazy load database connection."""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def collection(self):
        """Get drills collection."""
        return self.db.drills
    
    async def upsert_drill(self, drill_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Insert or update a drill by drill_id.
        
        Returns:
            Dict with 'action' ('inserted' or 'updated') and 'drill_id'
        """
        drill_id = drill_data['drill_id']
        
        # Check if drill exists
        existing = await self.collection.find_one({"drill_id": drill_id})
        
        if existing:
            # Update existing drill
            drill_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            await self.collection.update_one(
                {"drill_id": drill_id},
                {"$set": drill_data}
            )
            logger.info(f"Updated drill: {drill_id}")
            return {"action": "updated", "drill_id": drill_id}
        else:
            # Insert new drill
            drill_data['created_at'] = datetime.now(timezone.utc).isoformat()
            drill_data['updated_at'] = drill_data['created_at']
            await self.collection.insert_one(drill_data)
            logger.info(f"Inserted drill: {drill_id}")
            return {"action": "inserted", "drill_id": drill_id}
    
    async def upsert_many(self, drills: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Upsert multiple drills.
        
        Returns:
            Dict with 'inserted' and 'updated' counts
        """
        inserted = 0
        updated = 0
        
        for drill_data in drills:
            result = await self.upsert_drill(drill_data)
            if result['action'] == 'inserted':
                inserted += 1
            else:
                updated += 1
        
        return {"inserted": inserted, "updated": updated}
    
    async def find_by_id(self, drill_id: str) -> Optional[Dict[str, Any]]:
        """Find a drill by its drill_id."""
        doc = await self.collection.find_one(
            {"drill_id": drill_id, "is_active": True},
            {"_id": 0}
        )
        return doc
    
    async def find_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Find all active drills in a category."""
        cursor = self.collection.find(
            {"category": category, "is_active": True},
            {"_id": 0}
        )
        return await cursor.to_list(length=1000)
    
    async def find_by_categories(self, categories: List[str]) -> List[Dict[str, Any]]:
        """Find all active drills in multiple categories."""
        cursor = self.collection.find(
            {"category": {"$in": categories}, "is_active": True},
            {"_id": 0}
        )
        return await cursor.to_list(length=1000)
    
    async def find_all(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Find all drills."""
        query = {} if include_inactive else {"is_active": True}
        cursor = self.collection.find(query, {"_id": 0})
        return await cursor.to_list(length=5000)
    
    async def count_drills(self, include_inactive: bool = False) -> int:
        """Count total drills in database."""
        query = {} if include_inactive else {"is_active": True}
        return await self.collection.count_documents(query)
    
    async def delete_drill(self, drill_id: str, soft_delete: bool = True) -> bool:
        """
        Delete a drill by drill_id.
        
        Args:
            drill_id: The drill ID to delete
            soft_delete: If True, mark as inactive; if False, hard delete
        
        Returns:
            True if drill was found and deleted/deactivated
        """
        if soft_delete:
            result = await self.collection.update_one(
                {"drill_id": drill_id},
                {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
        else:
            result = await self.collection.delete_one({"drill_id": drill_id})
        
        return result.modified_count > 0 or result.deleted_count > 0
    
    async def search_drills(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        intensity: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search drills with various filters.
        """
        filter_query = {"is_active": True}
        
        if query:
            filter_query["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"purpose": {"$regex": query, "$options": "i"}}
            ]
        
        if category:
            filter_query["category"] = category
        
        if intensity:
            filter_query["intensity"] = intensity
        
        if tags:
            filter_query["tags"] = {"$in": tags}
        
        cursor = self.collection.find(filter_query, {"_id": 0})
        return await cursor.to_list(length=1000)


# Singleton instance
_drill_repository: Optional[DrillRepository] = None


def get_drill_repository() -> DrillRepository:
    """Get or create the drill repository singleton."""
    global _drill_repository
    if _drill_repository is None:
        _drill_repository = DrillRepository()
    return _drill_repository
