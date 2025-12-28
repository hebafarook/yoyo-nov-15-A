"""Report repository for data access."""

from typing import List, Optional
from .base import BaseRepository
from utils.database import db


class ReportRepository(BaseRepository):
    """Repository for saved reports data access."""
    
    def __init__(self):
        super().__init__(db.saved_reports)
    
    async def find_by_user(self, user_id: str, limit: Optional[int] = None) -> List[dict]:
        """Find all reports for a user."""
        return await self.find_many({"user_id": user_id}, limit=limit)
    
    async def find_by_type(self, user_id: str, report_type: str) -> List[dict]:
        """Find reports by type for a user."""
        return await self.find_many({"user_id": user_id, "report_type": report_type})
