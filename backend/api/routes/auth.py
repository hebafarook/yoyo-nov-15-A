"""Authentication API routes - thin HTTP layer."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from domain.models import User, UserCreate, UserLogin
from services.auth_service import AuthService
from repositories.assessment_repository import AssessmentRepository
from repositories.report_repository import ReportRepository

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

# Initialize services
auth_service = AuthService()
assessment_repo = AssessmentRepository()
report_repo = ReportRepository()


# Dependency for token verification
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user info."""
    return AuthService.verify_token(credentials.credentials)


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user.
    
    - **username**: Unique username (alphanumeric + underscore)
    - **email**: Valid email address
    - **password**: Minimum 6 characters
    - **role**: player, coach, parent, club, or admin
    - **Additional fields**: Depending on role
    
    Returns user data and JWT token.
    """
    try:
        user, token = await auth_service.register_user(user_data)
        
        return {
            "user": user.dict(exclude={'hashed_password'}),
            "token": token,
            "message": f"User registered successfully as {user.role}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=Dict[str, Any])
async def login(credentials: UserLogin):
    """Authenticate user and return token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns user data and JWT token.
    """
    try:
        user, token = await auth_service.login_user(credentials)
        
        return {
            "user": user.dict(exclude={'hashed_password'}),
            "token": token,
            "message": "Login successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.get("/profile", response_model=Dict[str, Any])
async def get_profile(current_user: dict = Depends(verify_token)):
    """Get current user's profile.
    
    Requires authentication token.
    Returns user data and profile information.
    """
    try:
        user, profile = await auth_service.get_user_profile(current_user['user_id'])
        
        return {
            "user": user.dict(exclude={'hashed_password'}),
            "profile": profile
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )


@router.get("/benchmarks", response_model=list)
async def get_benchmarks(current_user: dict = Depends(verify_token)):
    """Get user's assessment benchmarks.
    
    Requires authentication token.
    Returns list of assessment benchmarks.
    """
    try:
        user_id = current_user['user_id']
        benchmarks = await assessment_repo.find_by_user(user_id)
        return benchmarks
    
    except Exception as e:
        logger.error(f"Benchmark fetch error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch benchmarks"
        )


@router.get("/saved-reports", response_model=list)
async def get_saved_reports(current_user: dict = Depends(verify_token)):
    """Get user's saved reports.
    
    Requires authentication token.
    Returns list of saved reports.
    """
    try:
        user_id = current_user['user_id']
        reports = await report_repo.find_by_user(user_id)
        return reports
    
    except Exception as e:
        logger.error(f"Report fetch error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reports"
        )


@router.get("/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "service": "auth",
        "version": "2.0.0"
    }
