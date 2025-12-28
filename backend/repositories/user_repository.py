"""User repository for data access."""

from typing import Optional, List
from .base import BaseRepository
from utils.database import db


class UserRepository(BaseRepository):
    """Repository for user data access."""
    
    def __init__(self):
        super().__init__(db.users)
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email."""
        return await self.find_one({"email": email})
    
    async def find_by_username(self, username: str) -> Optional[dict]:
        """Find user by username."""
        return await self.find_one({"username": username})
    
    async def find_by_role(self, role: str, limit: Optional[int] = None) -> List[dict]:
        """Find users by role."""
        return await self.find_many({"role": role}, limit=limit)
    
    async def update_last_login(self, user_id: str, timestamp: str) -> bool:
        """Update user's last login timestamp."""
        return await self.update(user_id, {"last_login": timestamp})
    
    async def is_email_taken(self, email: str) -> bool:
        """Check if email is already registered."""
        count = await self.count({"email": email})
        return count > 0
    
    async def is_username_taken(self, username: str) -> bool:
        """Check if username is already taken."""
        count = await self.count({"username": username})
        return count > 0


class UserProfileRepository(BaseRepository):
    """Repository for user profiles."""
    
    def __init__(self):
        super().__init__(db.user_profiles)
    
    async def find_by_user_id(self, user_id: str) -> Optional[dict]:
        """Find profile by user ID."""
        return await self.find_one({"user_id": user_id})
    
    async def create_default_profile(self, user_id: str) -> dict:
        """Create default profile for new user."""
        profile_data = {
            "user_id": user_id,
            "players_managed": [],
            "saved_reports": [],
            "benchmarks": [],
            "coaching_level": None,
            "organization": None,
            "preferences": {}
        }
        return await self.create(profile_data)


class RelationshipRepository(BaseRepository):
    """Repository for parent-player and coach-player relationships."""
    
    def __init__(self, collection_name: str):
        super().__init__(getattr(db, collection_name))
    
    async def find_by_player(self, player_id: str) -> List[dict]:
        """Find all relationships for a player."""
        return await self.find_many({"player_id": player_id})
    
    async def find_by_parent(self, parent_id: str) -> List[dict]:
        """Find all relationships for a parent."""
        return await self.find_many({"parent_id": parent_id})
    
    async def find_by_coach(self, coach_id: str) -> List[dict]:
        """Find all relationships for a coach."""
        return await self.find_many({"coach_id": coach_id})


class InvitationRepository(BaseRepository):
    """Repository for pending invitations."""
    
    def __init__(self):
        super().__init__(db.pending_invitations)
    
    async def find_pending_by_email(self, email: str) -> List[dict]:
        """Find pending invitations by email."""
        return await self.find_many({"email": email, "status": "pending"})
    
    async def mark_as_processed(self, invitation_id: str) -> bool:
        """Mark invitation as processed."""
        return await self.update(invitation_id, {"status": "processed"})
