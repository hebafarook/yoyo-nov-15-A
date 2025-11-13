from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import logging
from models import PlayerAssessment, AssessmentCreate
from utils.database import prepare_for_mongo, parse_from_mongo, db
from utils.assessment_calculator import (
    calculate_overall_score, 
    get_performance_level,
    analyze_strengths_and_weaknesses,
    generate_training_recommendations
)
from datetime import datetime, timezone
from routes.auth_routes import verify_token, verify_token_async

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

async def check_player_access(player_name: str, current_user: dict) -> bool:
    """Check if current user has access to this player's data"""
    role = current_user.get('role')
    username = current_user.get('username')
    user_id = current_user.get('user_id')
    
    # Players can only access their own data
    if role == 'player':
        return player_name == username
    
    # Parents and coaches can access their managed players
    if role in ['parent', 'coach']:
        user = await db.users.find_one({"id": user_id})
        if user:
            managed_players = user.get('managed_players', [])
            return player_name in managed_players
    
    return False

@router.post("/", response_model=PlayerAssessment)
async def create_assessment(
    assessment: AssessmentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new player assessment with automatic scoring"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Check if user has access to create assessment for this player
        if not await check_player_access(assessment.player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to create assessments for this player"
            )
        
        # Calculate overall score and performance level
        assessment_dict = assessment.dict()
        overall_score = calculate_overall_score(assessment_dict)
        performance_level = get_performance_level(overall_score)
        
        # Calculate BMI if height and weight are provided
        bmi = None
        if assessment_dict.get('height_cm') and assessment_dict.get('weight_kg'):
            height_m = assessment_dict['height_cm'] / 100
            bmi = assessment_dict['weight_kg'] / (height_m ** 2)
        
        # Create the assessment object
        player_assessment = PlayerAssessment(
            **assessment_dict,
            overall_score=overall_score,
            performance_level=performance_level,
            bmi=bmi
        )
        
        # Prepare and save to database with user_id
        assessment_data = prepare_for_mongo(player_assessment.dict())
        assessment_data['user_id'] = current_user.get('user_id')  # Link to user
        assessment_data['created_by_username'] = current_user.get('username')
        result = await db.assessments.insert_one(assessment_data)
        
        # Return the created assessment
        player_assessment.id = str(result.inserted_id) if hasattr(result, 'inserted_id') else player_assessment.id
        
        logger.info(f"Assessment created for player: {assessment.player_name}")
        return player_assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )

@router.get("/", response_model=List[PlayerAssessment])
async def get_all_assessments(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all player assessments (coaches only)"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Only coaches can view all assessments
        if current_user.get('role') != 'coach':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Only coaches can view all assessments"
            )
        
        assessments = await db.assessments.find().sort("created_at", -1).to_list(1000)
        return [PlayerAssessment(**parse_from_mongo(assessment)) for assessment in assessments]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessments"
        )

@router.get("/player/{player_name}", response_model=List[PlayerAssessment])
async def get_player_assessments(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all assessments for a specific player"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Check if user has access to this player's data
        if not await check_player_access(player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to view this player's assessments"
            )
        
        assessments = await db.assessments.find(
            {"player_name": player_name}
        ).sort("created_at", -1).to_list(1000)
        
        return [PlayerAssessment(**parse_from_mongo(assessment)) for assessment in assessments]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch player assessments"
        )

@router.get("/player/{player_name}/latest", response_model=Optional[PlayerAssessment])
async def get_latest_assessment(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get the latest assessment for a specific player"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Check if user has access to this player's data
        if not await check_player_access(player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to view this player's assessments"
            )
        
        assessment = await db.assessments.find_one(
            {"player_name": player_name},
            sort=[("created_at", -1)]
        )
        
        if assessment:
            return PlayerAssessment(**parse_from_mongo(assessment))
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest assessment"
        )

@router.get("/player/{player_name}/status")
async def get_assessment_status(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get assessment status including latest assessment and next due date"""
    try:
        from datetime import timedelta
        
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Check if user has access to this player's data
        if not await check_player_access(player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get latest assessment
        assessment = await db.assessments.find_one(
            {"player_name": player_name},
            sort=[("created_at", -1)]
        )
        
        if not assessment:
            return {
                "has_assessment": False,
                "message": "No assessment found. Complete your first assessment to get started."
            }
        
        # Calculate next assessment date (6-8 weeks based on performance level)
        assessment_date = assessment.get('created_at')
        overall_score = assessment.get('overall_score', 0)
        weeks_until_next = 6 if overall_score < 70 else 8
        
        next_date = assessment_date + timedelta(weeks=weeks_until_next)
        is_due = datetime.now(timezone.utc) >= next_date
        
        return {
            "has_assessment": True,
            "latest_assessment_id": assessment.get('id'),
            "latest_assessment_date": assessment_date.isoformat(),
            "overall_score": overall_score,
            "performance_level": assessment.get('performance_level'),
            "next_assessment_due": next_date.isoformat(),
            "is_due": is_due,
            "days_until_due": (next_date - datetime.now(timezone.utc)).days,
            "can_create_new": is_due
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment status"
        )

@router.get("/{assessment_id}", response_model=PlayerAssessment)
async def get_assessment(
    assessment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific assessment by ID"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        assessment = await db.assessments.find_one({"id": assessment_id})
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        # Check if user has access to this player's data
        player_name = assessment.get("player_name")
        if not await check_player_access(player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to view this assessment"
            )
        
        return PlayerAssessment(**parse_from_mongo(assessment))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment"
        )

@router.put("/{assessment_id}", response_model=PlayerAssessment)
async def update_assessment(
    assessment_id: str, 
    assessment_update: AssessmentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update an existing assessment"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Get existing assessment to check permissions
        existing_assessment = await db.assessments.find_one({"id": assessment_id})
        if not existing_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        player_name = existing_assessment.get("player_name")
        if not await check_player_access(player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to update this assessment"
            )
        
        # Calculate new overall score
        assessment_dict = assessment_update.dict()
        overall_score = calculate_overall_score(assessment_dict)
        performance_level = get_performance_level(overall_score)
        
        # Prepare update data
        update_data = {
            **assessment_dict,
            "overall_score": overall_score,
            "performance_level": performance_level,
            "updated_at": datetime.now(timezone.utc)
        }
        
        prepared_data = prepare_for_mongo(update_data)
        
        # Update in database
        result = await db.assessments.update_one(
            {"id": assessment_id},
            {"$set": prepared_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        # Fetch and return updated assessment
        updated_assessment = await db.assessments.find_one({"id": assessment_id})
        return PlayerAssessment(**parse_from_mongo(updated_assessment))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update assessment"
        )

@router.delete("/{assessment_id}")
async def delete_assessment(
    assessment_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an assessment"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Get existing assessment to check permissions
        existing_assessment = await db.assessments.find_one({"id": assessment_id})
        if not existing_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        player_name = existing_assessment.get("player_name")
        if not await check_player_access(player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to delete this assessment"
            )
        
        result = await db.assessments.delete_one({"id": assessment_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        return {"message": "Assessment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete assessment"
        )

@router.get("/player/{player_name}/analysis")
async def get_player_analysis(
    player_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get detailed analysis for a player including strengths, weaknesses, and recommendations"""
    try:
        # Verify token and get user info
        current_user = await verify_token_async(credentials.credentials)
        
        # Check if user has access to this player's data
        if not await check_player_access(player_name, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to view this player's analysis"
            )
        
        # Get latest assessment
        assessment = await db.assessments.find_one(
            {"player_name": player_name},
            sort=[("created_at", -1)]
        )
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No assessment found for player"
            )
        
        assessment_data = parse_from_mongo(assessment)
        
        # Analyze strengths and weaknesses
        analysis = analyze_strengths_and_weaknesses(assessment_data)
        
        # Generate recommendations
        performance_level = assessment_data.get('performance_level', 'Developing')
        recommendations = generate_training_recommendations(analysis, performance_level)
        
        return {
            "player_name": player_name,
            "overall_score": assessment_data.get('overall_score', 0),
            "performance_level": performance_level,
            "strengths": analysis['strengths'],
            "weaknesses": analysis['weaknesses'],
            "recommendations": recommendations,
            "assessment_date": assessment_data.get('created_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating player analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate player analysis"
        )