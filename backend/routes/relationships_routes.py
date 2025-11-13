from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel
import logging
from utils.database import db
from routes.auth_routes import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

class PlayerRelationship(BaseModel):
    player_username: str

class BulkPlayerRelationship(BaseModel):
    player_usernames: List[str]

@router.post("/parent/add-child")
async def add_child_to_parent(
    relationship: PlayerRelationship,
    current_user: dict = Depends(verify_token)
):
    """Allow parents to link their child players"""
    try:
        user_id = current_user.get('user_id')
        role = current_user.get('role')
        
        if role != 'parent':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents can add children"
            )
        
        # Verify the player exists
        player = await db.users.find_one({
            "username": relationship.player_username,
            "role": "player"
        })
        
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        # Add player to parent's managed_players list
        result = await db.users.update_one(
            {"id": user_id},
            {"$addToSet": {"managed_players": relationship.player_username}}
        )
        
        if result.modified_count == 0:
            return {"message": "Player already linked to your account"}
        
        return {
            "message": f"Successfully linked {relationship.player_username} to your account",
            "player_name": relationship.player_username
        }
    
    except Exception as e:
        logger.error(f"Error adding child: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add child: {str(e)}"
        )

@router.post("/coach/assign-player")
async def assign_player_to_coach(
    relationship: PlayerRelationship,
    current_user: dict = Depends(verify_token)
):
    """Allow coaches to assign players to their roster"""
    try:
        user_id = current_user.get('user_id')
        role = current_user.get('role')
        
        if role != 'coach':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only coaches can assign players"
            )
        
        # Verify the player exists
        player = await db.users.find_one({
            "username": relationship.player_username,
            "role": "player"
        })
        
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        # Add player to coach's managed_players list
        result = await db.users.update_one(
            {"id": user_id},
            {"$addToSet": {"managed_players": relationship.player_username}}
        )
        
        if result.modified_count == 0:
            return {"message": "Player already assigned to you"}
        
        return {
            "message": f"Successfully assigned {relationship.player_username} to your roster",
            "player_name": relationship.player_username
        }
    
    except Exception as e:
        logger.error(f"Error assigning player: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign player: {str(e)}"
        )

@router.delete("/remove-player/{player_username}")
async def remove_player_relationship(
    player_username: str,
    current_user: dict = Depends(verify_token)
):
    """Remove a player from parent/coach's managed list"""
    try:
        user_id = current_user.get('user_id')
        role = current_user.get('role')
        
        if role not in ['parent', 'coach']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents and coaches can remove relationships"
            )
        
        # Remove player from managed_players list
        result = await db.users.update_one(
            {"id": user_id},
            {"$pull": {"managed_players": player_username}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found in your managed list"
            )
        
        return {
            "message": f"Successfully removed {player_username} from your list"
        }
    
    except Exception as e:
        logger.error(f"Error removing player: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove player: {str(e)}"
        )

@router.get("/my-players")
async def get_my_players(
    current_user: dict = Depends(verify_token)
):
    """Get list of players managed by current user"""
    try:
        user_id = current_user.get('user_id')
        username = current_user.get('username')
        role = current_user.get('role')
        
        # Get current user's managed_players list
        user = await db.users.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        managed_players = user.get('managed_players', [])
        
        # If player role, return their own username
        if role == 'player':
            player_data = {
                "username": username,
                "full_name": user.get('full_name', username),
                "age": user.get('age'),
                "position": user.get('position')
            }
            return {
                "players": [player_data],
                "count": 1
            }
        
        # For parents and coaches, return their managed players
        if not managed_players:
            return {
                "players": [],
                "count": 0,
                "message": "No players linked yet"
            }
        
        # Fetch player details
        players = await db.users.find({
            "username": {"$in": managed_players},
            "role": "player"
        }).to_list(length=100)
        
        player_list = []
        for player in players:
            player_list.append({
                "username": player.get('username'),
                "full_name": player.get('full_name', player.get('username')),
                "age": player.get('age'),
                "position": player.get('position')
            })
        
        return {
            "players": player_list,
            "count": len(player_list)
        }
    
    except Exception as e:
        logger.error(f"Error fetching players: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch players: {str(e)}"
        )

@router.get("/search-players")
async def search_players(
    query: str = "",
    current_user: dict = Depends(verify_token)
):
    """Search for players by username or name (for adding relationships)"""
    try:
        role = current_user.get('role')
        
        if role not in ['parent', 'coach']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parents and coaches can search for players"
            )
        
        # Search for players
        players = await db.users.find({
            "role": "player",
            "$or": [
                {"username": {"$regex": query, "$options": "i"}},
                {"full_name": {"$regex": query, "$options": "i"}}
            ]
        }).to_list(length=20)
        
        player_list = []
        for player in players:
            player_list.append({
                "username": player.get('username'),
                "full_name": player.get('full_name', player.get('username')),
                "age": player.get('age'),
                "position": player.get('position')
            })
        
        return {
            "players": player_list,
            "count": len(player_list)
        }
    
    except Exception as e:
        logger.error(f"Error searching players: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search players: {str(e)}"
        )
