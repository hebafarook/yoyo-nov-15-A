"""Assessment repository for data access."""

from typing import Optional, List
from .base import BaseRepository
from utils.database import db


class AssessmentRepository(BaseRepository):
    """Repository for assessment/benchmark data access."""
    
    def __init__(self):
        super().__init__(db.benchmarks)
    
    async def find_by_user(self, user_id: str) -> List[dict]:
        """Find all assessments for a user."""
        return await self.find_many({"user_id": user_id})
    
    async def find_baseline(self, user_id: str) -> Optional[dict]:
        """Find baseline assessment for a user."""
        assessments = await self.find_many({"user_id": user_id, "is_baseline": True}, limit=1)
        return assessments[0] if assessments else None
    
    async def find_latest(self, user_id: str) -> Optional[dict]:
        """Find latest assessment for a user."""
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        return docs[0] if docs else None
    
    async def count_user_assessments(self, user_id: str) -> int:
        """Count total assessments for a user."""
        return await self.count({"user_id": user_id})
