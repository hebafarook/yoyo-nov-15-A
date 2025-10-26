from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import logging
import hashlib
import jwt
import os
from datetime import datetime, timezone, timedelta
from models import User, UserCreate, UserLogin, SavedReport, SavedReportCreate, UserProfile
from utils.database import prepare_for_mongo, parse_from_mongo, db

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password

def create_access_token(user_id: str, username: str) -> str:
    """Create JWT access token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    \"\"\"Verify JWT token and return user info\"\"\"\n    try:\n        token = credentials.credentials\n        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])\n        return payload\n    except jwt.ExpiredSignatureError:\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail=\"Token has expired\"\n        )\n    except jwt.JWTError:\n        raise HTTPException(\n            status_code=status.HTTP_401_UNAUTHORIZED,\n            detail=\"Invalid token\"\n        )

@router.post(\"/register\", response_model=dict)
async def register_user(user_data: UserCreate):
    \"\"\"Register a new user\"\"\"
    try:
        # Check if username already exists
        existing_user = await db.users.find_one({\"username\": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=\"Username already registered\"
            )
        
        # Check if email already exists
        existing_email = await db.users.find_one({\"email\": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=\"Email already registered\"
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_coach=user_data.is_coach or False
        )
        
        # Save user to database
        user_data_dict = prepare_for_mongo(user.dict())
        result = await db.users.insert_one(user_data_dict)
        
        # Create user profile
        profile = UserProfile(user_id=user.id)
        profile_data = prepare_for_mongo(profile.dict())
        await db.user_profiles.insert_one(profile_data)
        
        # Create access token
        access_token = create_access_token(user.id, user.username)
        
        logger.info(f\"User registered: {user.username}\")
        return {
            \"message\": \"User registered successfully\",
            \"access_token\": access_token,
            \"user\": {
                \"id\": user.id,
                \"username\": user.username,
                \"email\": user.email,
                \"full_name\": user.full_name,
                \"is_coach\": user.is_coach
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f\"Error registering user: {e}\")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=\"Failed to register user\"
        )

@router.post(\"/login\", response_model=dict)
async def login_user(login_data: UserLogin):
    \"\"\"Login user and return access token\"\"\"
    try:
        # Find user by username
        user_doc = await db.users.find_one({\"username\": login_data.username})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=\"Invalid username or password\"
            )
        
        user = User(**parse_from_mongo(user_doc))
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=\"Invalid username or password\"
            )
        
        # Update last login
        await db.users.update_one(
            {\"id\": user.id},
            {\"$set\": {\"last_login\": datetime.now(timezone.utc)}}
        )
        
        # Create access token
        access_token = create_access_token(user.id, user.username)
        
        logger.info(f\"User logged in: {user.username}\")
        return {
            \"message\": \"Login successful\",
            \"access_token\": access_token,
            \"user\": {
                \"id\": user.id,
                \"username\": user.username,
                \"email\": user.email,
                \"full_name\": user.full_name,
                \"is_coach\": user.is_coach
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f\"Error logging in user: {e}\")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=\"Failed to login\"
        )

@router.get(\"/profile\", response_model=dict)
async def get_user_profile(current_user: dict = Depends(verify_token)):
    \"\"\"Get user profile information\"\"\"
    try:
        user_doc = await db.users.find_one({\"id\": current_user[\"user_id\"]})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=\"User not found\"
            )
        
        user = User(**parse_from_mongo(user_doc))
        
        # Get user profile
        profile_doc = await db.user_profiles.find_one({\"user_id\": user.id})
        if profile_doc:
            profile = UserProfile(**parse_from_mongo(profile_doc))
        else:
            # Create profile if it doesn't exist
            profile = UserProfile(user_id=user.id)
            profile_data = prepare_for_mongo(profile.dict())
            await db.user_profiles.insert_one(profile_data)
        
        return {
            \"user\": {
                \"id\": user.id,
                \"username\": user.username,
                \"email\": user.email,
                \"full_name\": user.full_name,
                \"is_coach\": user.is_coach,
                \"profile_picture\": user.profile_picture,
                \"created_at\": user.created_at,
                \"last_login\": user.last_login
            },
            \"profile\": {
                \"players_managed\": profile.players_managed,
                \"saved_reports_count\": len(profile.saved_reports),
                \"coaching_level\": profile.coaching_level,
                \"organization\": profile.organization,
                \"preferences\": profile.preferences
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f\"Error fetching user profile: {e}\")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=\"Failed to fetch user profile\"
        )

@router.post(\"/save-report\", response_model=SavedReport)
async def save_assessment_report(
    report_data: SavedReportCreate, 
    current_user: dict = Depends(verify_token)
):
    \"\"\"Save assessment report to user profile\"\"\"
    try:
        # Verify user owns this report or is a coach
        user_doc = await db.users.find_one({\"id\": current_user[\"user_id\"]})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=\"User not found\"
            )
        
        # Create saved report
        saved_report = SavedReport(
            user_id=current_user[\"user_id\"],
            player_name=report_data.player_name,
            assessment_id=report_data.assessment_id,
            report_data=report_data.report_data,
            report_type=report_data.report_type,
            title=report_data.title or f\"Assessment Report - {report_data.player_name}\",
            notes=report_data.notes
        )
        
        # Save to database
        report_dict = prepare_for_mongo(saved_report.dict())
        await db.saved_reports.insert_one(report_dict)
        
        # Update user profile
        await db.user_profiles.update_one(
            {\"user_id\": current_user[\"user_id\"]},
            {
                \"$addToSet\": {
                    \"saved_reports\": saved_report.id,
                    \"players_managed\": report_data.player_name
                },
                \"$set\": {\"updated_at\": datetime.now(timezone.utc)}
            }
        )
        
        logger.info(f\"Report saved for user {current_user['username']}: {saved_report.id}\")
        return saved_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f\"Error saving report: {e}\")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=\"Failed to save report\"
        )

@router.get(\"/saved-reports\", response_model=List[SavedReport])
async def get_saved_reports(current_user: dict = Depends(verify_token)):
    \"\"\"Get all saved reports for the current user\"\"\"
    try:
        reports = await db.saved_reports.find(
            {\"user_id\": current_user[\"user_id\"]}
        ).sort(\"saved_at\", -1).to_list(1000)
        
        return [SavedReport(**parse_from_mongo(report)) for report in reports]
        
    except Exception as e:
        logger.error(f\"Error fetching saved reports: {e}\")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=\"Failed to fetch saved reports\"
        )

@router.get(\"/saved-reports/{report_id}\", response_model=SavedReport)
async def get_saved_report(report_id: str, current_user: dict = Depends(verify_token)):
    \"\"\"Get a specific saved report\"\"\"
    try:
        report = await db.saved_reports.find_one({
            \"id\": report_id,
            \"user_id\": current_user[\"user_id\"]
        })
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=\"Report not found\"
            )
        
        return SavedReport(**parse_from_mongo(report))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f\"Error fetching saved report: {e}\")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=\"Failed to fetch saved report\"
        )

@router.delete(\"/saved-reports/{report_id}\")
async def delete_saved_report(report_id: str, current_user: dict = Depends(verify_token)):
    \"\"\"Delete a saved report\"\"\"
    try:
        result = await db.saved_reports.delete_one({
            \"id\": report_id,
            \"user_id\": current_user[\"user_id\"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=\"Report not found\"
            )
        
        # Update user profile
        await db.user_profiles.update_one(\n            {\"user_id\": current_user[\"user_id\"]},\n            {\"$pull\": {\"saved_reports\": report_id}}\n        )\n        \n        return {\"message\": \"Report deleted successfully\"}\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f\"Error deleting saved report: {e}\")\n        raise HTTPException(\n            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n            detail=\"Failed to delete report\"\n        )"