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
    
    async def upsert_drill(self, drill_data: Dict[str, Any], admin_id: Optional[str] = None) -> Dict[str, str]:
        """
        Insert or update a drill by drill_id.
        
        Returns:
            Dict with 'action' ('inserted' or 'updated') and 'drill_id'
        """
        drill_id = drill_data['drill_id']
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if drill exists
        existing = await self.collection.find_one({"drill_id": drill_id})
        
        if existing:
            # Update existing drill
            drill_data['updated_at'] = now
            # Preserve original created_at and created_by
            drill_data['created_at'] = existing.get('created_at', now)
            drill_data['created_by'] = existing.get('created_by', admin_id)
            
            await self.collection.update_one(
                {"drill_id": drill_id},
                {"$set": drill_data}
            )
            logger.info(f"Updated drill: {drill_id}")
            return {"action": "updated", "drill_id": drill_id}
        else:
            # Insert new drill
            drill_data['created_at'] = now
            drill_data['updated_at'] = now
            drill_data['created_by'] = admin_id
            
            await self.collection.insert_one(drill_data)
            logger.info(f"Inserted drill: {drill_id}")
            return {"action": "inserted", "drill_id": drill_id}
    
    async def upsert_many(self, drills: List[Dict[str, Any]], admin_id: Optional[str] = None) -> Dict[str, int]:
        """
        Upsert multiple drills atomically.
        
        Returns:
            Dict with 'inserted' and 'updated' counts
        """
        inserted = 0
        updated = 0
        
        for drill_data in drills:
            result = await self.upsert_drill(drill_data, admin_id)
            if result['action'] == 'inserted':
                inserted += 1
            else:
                updated += 1
        
        logger.info(f"Upserted {len(drills)} drills: {inserted} inserted, {updated} updated")
        return {"inserted": inserted, "updated": updated}
    
    async def find_by_id(self, drill_id: str) -> Optional[Dict[str, Any]]:
        """Find a drill by its drill_id."""
        doc = await self.collection.find_one(
            {"drill_id": drill_id, "is_active": True},
            {"_id": 0}
        )
        return doc
    
    async def find_by_section(self, section: str) -> List[Dict[str, Any]]:
        """Find all active drills in a section."""
        cursor = self.collection.find(
            {"section": section, "is_active": True},
            {"_id": 0}
        )
        return await cursor.to_list(length=1000)
    
    async def find_all(
        self,
        include_inactive: bool = False,
        section: Optional[str] = None,
        tag: Optional[str] = None,
        age: Optional[int] = None,
        position: Optional[str] = None,
        skip: int = 0,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find all drills with optional filters."""
        query: Dict[str, Any] = {}
        
        if not include_inactive:
            query["is_active"] = True
        
        if section:
            query["section"] = section
        
        if tag:
            query["tags"] = {"$in": [tag]}
        
        if age is not None:
            query["$or"] = [
                {"age_min": {"$exists": False}},
                {"age_min": None},
                {"age_min": {"$lte": age}}
            ]
            query["$and"] = [
                {"$or": [
                    {"age_max": {"$exists": False}},
                    {"age_max": None},
                    {"age_max": {"$gte": age}}
                ]}
            ]
        
        if position:
            query["$or"] = query.get("$or", []) + [
                {"positions": {"$in": [position]}},
                {"positions": {"$in": ["any"]}}
            ]
        
        cursor = self.collection.find(query, {"_id": 0}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def count_drills(self, include_inactive: bool = False) -> int:
        """Count total drills in database."""
        query = {} if include_inactive else {"is_active": True}
        return await self.collection.count_documents(query)
    
    async def count_by_section(self) -> Dict[str, int]:
        """Count drills grouped by section."""
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$section", "count": {"$sum": 1}}}
        ]
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=100)
        return {item["_id"]: item["count"] for item in results if item["_id"]}
    
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
                {"$set": {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            return result.modified_count > 0
        else:
            result = await self.collection.delete_one({"drill_id": drill_id})
            return result.deleted_count > 0
    
    async def search_drills(
        self,
        query: Optional[str] = None,
        section: Optional[str] = None,
        intensity: Optional[str] = None,
        tags: Optional[List[str]] = None,
        contraindications_exclude: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search drills with various filters.
        
        Args:
            query: Text search in name
            section: Filter by section
            intensity: Filter by intensity
            tags: Filter by any of these tags
            contraindications_exclude: Exclude drills with these contraindications
        """
        filter_query: Dict[str, Any] = {"is_active": True}
        
        if query:
            filter_query["name"] = {"$regex": query, "$options": "i"}
        
        if section:
            filter_query["section"] = section
        
        if intensity:
            filter_query["intensity"] = intensity
        
        if tags:
            filter_query["tags"] = {"$in": tags}
        
        if contraindications_exclude:
            filter_query["contraindications"] = {"$nin": contraindications_exclude}
        
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
