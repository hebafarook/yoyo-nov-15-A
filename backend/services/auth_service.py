"""Authentication and authorization service."""

import hashlib
import jwt
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status

from domain.models import User, UserCreate, UserLogin
from repositories.user_repository import (
    UserRepository,
    UserProfileRepository,
    RelationshipRepository,
    InvitationRepository
)
import logging
import uuid

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


class AuthService:
    """Service for authentication and user management."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = UserProfileRepository()
        self.parent_relationship_repo = RelationshipRepository("parent_player_relationships")
        self.coach_relationship_repo = RelationshipRepository("coach_player_relationships")
        self.invitation_repo = InvitationRepository()
    
    # Password management
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password
    
    # Token management
    @staticmethod
    def create_access_token(user_id: str, username: str, role: str = "player") -> str:
        """Create JWT access token."""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    # User registration
    async def register_user(self, user_data: UserCreate) -> Tuple[User, str]:
        """Register a new user.
        
        Returns:
            Tuple of (User, token)
        
        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        if await self.user_repo.is_email_taken(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if await self.user_repo.is_username_taken(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = self.hash_password(user_data.password)
        
        # Generate player_id for players
        player_id = None
        if user_data.role == "player":
            player_id = f"{user_data.username}_{user_data.age}_{user_data.position or 'unknown'}".replace(" ", "_")
        
        # Create user
        user_dict = user_data.dict(exclude={'password'})
        user_dict['hashed_password'] = hashed_password
        user_dict['player_id'] = player_id
        user_dict['is_coach'] = user_data.is_coach or (user_data.role == "coach")
        user_dict['created_at'] = datetime.now(timezone.utc).isoformat()
        user_dict['last_login'] = datetime.now(timezone.utc).isoformat()
        
        created_user = await self.user_repo.create(user_dict)
        
        # Create default profile
        await self.profile_repo.create_default_profile(created_user['id'])
        
        # Handle relationships
        if user_data.role == "player":
            if user_data.parent_email:
                await self._create_parent_relationship(created_user['id'], user_data.parent_email)
            if user_data.coach_email:
                await self._create_coach_relationship(created_user['id'], user_data.coach_email)
        
        # Process pending invitations
        if user_data.role in ["parent", "coach"]:
            await self._process_pending_invitations(created_user['id'], user_data.email, user_data.role)
        
        # Create token
        token = self.create_access_token(
            created_user['id'],
            created_user['username'],
            created_user['role']
        )
        
        # Convert to User model
        user = User(**created_user)
        
        logger.info(f"User registered successfully: {user.email} (role: {user.role})")
        
        return user, token
    
    async def login_user(self, credentials: UserLogin) -> Tuple[User, str]:
        """Authenticate user and return user data with token.
        
        Returns:
            Tuple of (User, token)
        
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user_dict = await self.user_repo.find_by_email(credentials.email)
        
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not self.verify_password(credentials.password, user_dict['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        await self.user_repo.update_last_login(
            user_dict['id'],
            datetime.now(timezone.utc).isoformat()
        )
        
        # Create token
        token = self.create_access_token(
            user_dict['id'],
            user_dict['username'],
            user_dict['role']
        )
        
        # Convert to User model
        user = User(**user_dict)
        
        logger.info(f"User logged in: {user.email}")
        
        return user, token
    
    async def get_user_profile(self, user_id: str) -> Tuple[User, dict]:
        """Get user data and profile.
        
        Returns:
            Tuple of (User, profile_dict)
        
        Raises:
            HTTPException: If user not found
        """
        user_dict = await self.user_repo.find_by_id(user_id)
        
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        profile_dict = await self.profile_repo.find_by_user_id(user_id)
        
        if not profile_dict:
            # Create default profile if it doesn't exist
            profile_dict = await self.profile_repo.create_default_profile(user_id)
        
        user = User(**user_dict)
        
        return user, profile_dict
    
    # Private helper methods
    async def _create_parent_relationship(self, player_id: str, parent_email: str):
        """Create or queue parent-player relationship."""
        parent = await self.user_repo.find_by_email(parent_email)
        
        if parent and parent['role'] == 'parent':
            # Parent exists, create relationship
            relationship = {
                "parent_id": parent['id'],
                "player_id": player_id,
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.parent_relationship_repo.create(relationship)
            logger.info(f"Parent relationship created: {parent_email} -> {player_id}")
        else:
            # Queue invitation
            invitation = {
                "email": parent_email,
                "player_id": player_id,
                "type": "parent",
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.invitation_repo.create(invitation)
            logger.info(f"Parent invitation queued: {parent_email}")
    
    async def _create_coach_relationship(self, player_id: str, coach_email: str):
        """Create or queue coach-player relationship."""
        coach = await self.user_repo.find_by_email(coach_email)
        
        if coach and coach['role'] == 'coach':
            # Coach exists, create relationship
            relationship = {
                "coach_id": coach['id'],
                "player_id": player_id,
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.coach_relationship_repo.create(relationship)
            logger.info(f"Coach relationship created: {coach_email} -> {player_id}")
        else:
            # Queue invitation
            invitation = {
                "email": coach_email,
                "player_id": player_id,
                "type": "coach",
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.invitation_repo.create(invitation)
            logger.info(f"Coach invitation queued: {coach_email}")
    
    async def _process_pending_invitations(self, user_id: str, email: str, role: str):
        """Process pending invitations when user registers."""
        invitations = await self.invitation_repo.find_pending_by_email(email)
        
        for invitation in invitations:
            if invitation['type'] == role:
                # Create relationship
                if role == 'parent':
                    relationship = {
                        "parent_id": user_id,
                        "player_id": invitation['player_id'],
                        "status": "active",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    await self.parent_relationship_repo.create(relationship)
                elif role == 'coach':
                    relationship = {
                        "coach_id": user_id,
                        "player_id": invitation['player_id'],
                        "status": "active",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    await self.coach_relationship_repo.create(relationship)
                
                # Mark invitation as processed
                await self.invitation_repo.mark_as_processed(invitation['id'])
                logger.info(f"Processed pending invitation: {email} -> {invitation['player_id']}")
