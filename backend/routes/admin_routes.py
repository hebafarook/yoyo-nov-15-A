from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from models import User, UserCreate
from utils.database import prepare_for_mongo, parse_from_mongo
import bcrypt

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['soccer_coach_db']

# Helper function to verify admin role
async def verify_admin(user_id: str) -> bool:
    """Verify user is admin"""
    user = await db.users.find_one({"id": user_id})
    return user and user.get("role") == "admin"

# ============ USER MANAGEMENT ============

@router.get("/users/all")
async def get_all_users(
    role: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all users in the system (Admin only)"""
    try:
        query = {}
        
        if role:
            query["role"] = role
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"username": {"$regex": search, "$options": "i"}}
            ]
        
        users = await db.users.find(query).to_list(1000)
        
        # Remove sensitive data
        for user in users:
            if "hashed_password" in user:
                del user["hashed_password"]
        
        return {
            "success": True,
            "count": len(users),
            "users": users
        }
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}")
async def get_user_by_id(user_id: str):
    """Get user details by ID (Admin only)"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove sensitive data
        if "hashed_password" in user:
            del user["hashed_password"]
        
        return {
            "success": True,
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/create")
async def admin_create_user(user: UserCreate):
    """Create new user (Admin only)"""
    try:
        # Check if user already exists
        existing = await db.users.find_one({
            "$or": [
                {"email": user.email},
                {"username": user.username}
            ]
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="User with this email or username already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user object
        new_user = User(
            username=user.username,
            email=user.email,
            name=user.name,
            hashed_password=hashed_password.decode('utf-8'),
            role=user.role,
            age=user.age,
            position=user.position
        )
        
        user_data = prepare_for_mongo(new_user.dict())
        await db.users.insert_one(user_data)
        
        logger.info(f"✅ Admin created user: {new_user.email} (role: {new_user.role})")
        
        # Return user without password
        user_response = new_user.dict()
        del user_response["hashed_password"]
        
        return {
            "success": True,
            "message": "User created successfully",
            "user": user_response
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/update")
async def admin_update_user(
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
    age: Optional[int] = None,
    position: Optional[str] = None,
    active: Optional[bool] = None
):
    """Update user details (Admin only)"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        if name is not None:
            update_data["name"] = name
        if email is not None:
            # Check email uniqueness
            existing = await db.users.find_one({"email": email, "id": {"$ne": user_id}})
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")
            update_data["email"] = email
        if role is not None:
            update_data["role"] = role
        if age is not None:
            update_data["age"] = age
        if position is not None:
            update_data["position"] = position
        if active is not None:
            update_data["active"] = active
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        logger.info(f"✅ Admin updated user {user_id}")
        
        return {
            "success": True,
            "message": "User updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}/delete")
async def admin_delete_user(user_id: str):
    """Delete user (Admin only)"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting admin users
        if user.get("role") == "admin":
            raise HTTPException(status_code=403, detail="Cannot delete admin users")
        
        # Delete user
        await db.users.delete_one({"id": user_id})
        
        # Also delete related data
        # Delete assessments
        await db.assessments.delete_many({"user_id": user_id})
        await db.assessment_benchmarks.delete_many({"user_id": user_id})
        
        # Delete training programs
        player_name = user.get("username") or user.get("name")
        if player_name:
            await db.periodized_programs.delete_many({"player_name": player_name})
            await db.training_programs.delete_many({"player_name": player_name})
        
        # Delete relationships
        await db.relationships.delete_many({
            "$or": [
                {"parent_id": user_id},
                {"child_id": user_id},
                {"coach_id": user_id},
                {"player_id": user_id}
            ]
        })
        
        logger.info(f"✅ Admin deleted user {user_id} and all related data")
        
        return {
            "success": True,
            "message": f"User {user.get('email')} and all related data deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(user_id: str, new_password: str):
    """Reset user password (Admin only)"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "hashed_password": hashed_password.decode('utf-8'),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        logger.info(f"✅ Admin reset password for user {user_id}")
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ SYSTEM STATISTICS ============

@router.get("/stats/overview")
async def get_system_stats():
    """Get system-wide statistics (Admin only)"""
    try:
        # Count users by role
        total_users = await db.users.count_documents({})
        players = await db.users.count_documents({"role": "player"})
        coaches = await db.users.count_documents({"role": "coach"})
        parents = await db.users.count_documents({"role": "parent"})
        clubs = await db.users.count_documents({"role": "club"})
        admins = await db.users.count_documents({"role": "admin"})
        
        # Count assessments
        total_assessments = await db.assessment_benchmarks.count_documents({})
        
        # Count training programs
        total_programs = await db.training_programs.count_documents({})
        
        # Count clubs and teams
        total_clubs = await db.clubs.count_documents({})
        total_teams = await db.teams.count_documents({})
        
        # Recent registrations (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_users = await db.users.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        return {
            "success": True,
            "stats": {
                "users": {
                    "total": total_users,
                    "players": players,
                    "coaches": coaches,
                    "parents": parents,
                    "clubs": clubs,
                    "admins": admins,
                    "recent_7_days": recent_users
                },
                "content": {
                    "assessments": total_assessments,
                    "programs": total_programs,
                    "clubs": total_clubs,
                    "teams": total_teams
                }
            }
        }
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity/recent")
async def get_recent_activity():
    """Get recent system activity (Admin only)"""
    try:
        # Get recent users
        recent_users = await db.users.find({}).sort("created_at", -1).limit(10).to_list(10)
        
        # Get recent assessments
        recent_assessments = await db.assessment_benchmarks.find({}).sort("saved_at", -1).limit(10).to_list(10)
        
        # Remove sensitive data
        for user in recent_users:
            if "hashed_password" in user:
                del user["hashed_password"]
        
        return {
            "success": True,
            "recent_users": recent_users,
            "recent_assessments": recent_assessments
        }
    except Exception as e:
        logger.error(f"Error fetching recent activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))
