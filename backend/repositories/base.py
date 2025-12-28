"""Base repository with common CRUD operations."""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from utils.database import prepare_for_mongo, parse_from_mongo
import uuid


class BaseRepository:
    """Base repository with generic CRUD operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document."""
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        prepared_data = prepare_for_mongo(data)
        await self.collection.insert_one(prepared_data)
        return data
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID."""
        doc = await self.collection.find_one({"id": id})
        return parse_from_mongo(doc) if doc else None
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching query."""
        doc = await self.collection.find_one(query)
        return parse_from_mongo(doc) if doc else None
    
    async def find_many(self, query: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find multiple documents matching query."""
        cursor = self.collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        docs = await cursor.to_list(length=None)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def update(self, id: str, data: Dict[str, Any]) -> bool:
        """Update document by ID."""
        prepared_data = prepare_for_mongo(data)
        result = await self.collection.update_one(
            {"id": id},
            {"$set": prepared_data}
        )
        return result.modified_count > 0
    
    async def delete(self, id: str) -> bool:
        """Delete document by ID."""
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def count(self, query: Dict[str, Any]) -> int:
        """Count documents matching query."""
        return await self.collection.count_documents(query)
