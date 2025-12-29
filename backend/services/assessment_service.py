"""Assessment service for business logic."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from repositories.assessment_repository import AssessmentRepository
from models import PlayerAssessment, AssessmentCreate
from utils.assessment_calculator import (
    calculate_overall_score,
    get_performance_level,
    analyze_strengths_and_weaknesses,
    generate_training_recommendations
)
import logging

logger = logging.getLogger(__name__)


class AssessmentNotFoundError(Exception):
    """Raised when an assessment is not found."""
    def __init__(self, message: str = "Assessment not found"):
        self.message = message
        super().__init__(message)


class AccessDeniedError(Exception):
    """Raised when user doesn't have access to a resource."""
    def __init__(self, message: str = "Access denied"):
        self.message = message
        super().__init__(message)


class AssessmentService:
    """Service for player assessment management."""
    
    def __init__(self):
        self.repository = AssessmentRepository()
    
    # =========================================================================
    # ACCESS CONTROL
    # =========================================================================
    
    async def check_player_access(self, player_name: str, current_user: dict) -> bool:
        """Check if current user has access to this player's data."""
        role = current_user.get('role', '').lower()
        username = current_user.get('username', '')
        user_id = current_user.get('user_id')
        player_id = current_user.get('player_id', username)
        
        # Admins have access to all players
        if role == 'admin':
            return True
        
        # Players can only access their own data
        if role == 'player':
            # Check both username and player_id
            return (player_name.lower() == username.lower() or 
                    player_name.lower() == player_id.lower() if player_id else False)
        
        # Parents and coaches can access their managed players
        if role in ['parent', 'coach']:
            # Coaches can create assessments for any player they're assessing
            if role == 'coach':
                return True  # Coaches have broad assessment creation rights
            user = await self.repository.find_user_by_id(user_id)
            if user:
                managed_players = user.get('managed_players', [])
                return player_name in managed_players
        
        return False
    
    # =========================================================================
    # ASSESSMENT CRUD
    # =========================================================================
    
    async def create_assessment(
        self,
        assessment_data: AssessmentCreate,
        current_user: dict
    ) -> PlayerAssessment:
        """Create a new player assessment with automatic scoring.
        
        Args:
            assessment_data: The assessment data from the request
            current_user: Dict containing user info from JWT (user_id, username, role)
        
        Returns:
            PlayerAssessment with user_id properly linked
        """
        # Check access
        if not await self.check_player_access(assessment_data.player_name, current_user):
            raise AccessDeniedError(
                "Access denied: You don't have permission to create assessments for this player"
            )
        
        # Calculate overall score and performance level
        assessment_dict = assessment_data.dict()
        overall_score = calculate_overall_score(assessment_dict)
        performance_level = get_performance_level(overall_score)
        
        # Calculate BMI if height and weight are provided
        bmi = None
        if assessment_dict.get('height_cm') and assessment_dict.get('weight_kg'):
            height_m = assessment_dict['height_cm'] / 100
            bmi = assessment_dict['weight_kg'] / (height_m ** 2)
        
        # Extract user_id from current_user (derived from JWT in route layer)
        # This ensures the assessment is properly linked to the authenticated user
        # We override any user_id from the request payload with the JWT-derived one
        user_id = current_user.get('user_id')
        
        # Override user_id in the dict before creating PlayerAssessment
        assessment_dict['user_id'] = user_id
        
        # Create the assessment object with user_id linked
        player_assessment = PlayerAssessment(
            **assessment_dict,
            overall_score=overall_score,
            performance_level=performance_level,
            bmi=bmi
        )
        
        # Prepare data for database storage
        assessment_data_dict = player_assessment.dict()
        assessment_data_dict['created_by_username'] = current_user.get('username')
        
        # Save to database
        await self.repository.create_assessment(assessment_data_dict)
        
        logger.info(f"Assessment created for player: {assessment_data.player_name} by user: {user_id}")
        return player_assessment
    
    async def get_all_assessments(self, current_user: dict) -> List[PlayerAssessment]:
        """Get all assessments. Only coaches can view all."""
        if current_user.get('role') != 'coach':
            raise AccessDeniedError("Access denied: Only coaches can view all assessments")
        
        assessments = await self.repository.find_all()
        return [PlayerAssessment(**assessment) for assessment in assessments]
    
    async def get_player_assessments(
        self,
        player_name: str,
        current_user: dict
    ) -> List[PlayerAssessment]:
        """Get all assessments for a specific player."""
        if not await self.check_player_access(player_name, current_user):
            raise AccessDeniedError(
                "Access denied: You don't have permission to view this player's assessments"
            )
        
        assessments = await self.repository.find_by_player_name(player_name)
        return [PlayerAssessment(**assessment) for assessment in assessments]
    
    async def get_latest_assessment(
        self,
        player_name: str,
        current_user: dict
    ) -> Optional[PlayerAssessment]:
        """Get the latest assessment for a specific player."""
        if not await self.check_player_access(player_name, current_user):
            raise AccessDeniedError(
                "Access denied: You don't have permission to view this player's assessments"
            )
        
        assessment = await self.repository.find_latest_by_player_name(player_name)
        if assessment:
            return PlayerAssessment(**assessment)
        return None
    
    async def get_assessment_by_id(
        self,
        assessment_id: str,
        current_user: dict
    ) -> PlayerAssessment:
        """Get a specific assessment by ID."""
        assessment = await self.repository.find_by_id(assessment_id)
        
        if not assessment:
            raise AssessmentNotFoundError("Assessment not found")
        
        # Check access
        player_name = assessment.get("player_name")
        if not await self.check_player_access(player_name, current_user):
            raise AccessDeniedError(
                "Access denied: You don't have permission to view this assessment"
            )
        
        return PlayerAssessment(**assessment)
    
    async def update_assessment(
        self,
        assessment_id: str,
        assessment_update: AssessmentCreate,
        current_user: dict
    ) -> PlayerAssessment:
        """Update an existing assessment."""
        # Get existing assessment to check permissions
        existing = await self.repository.find_by_id(assessment_id)
        if not existing:
            raise AssessmentNotFoundError("Assessment not found")
        
        player_name = existing.get("player_name")
        if not await self.check_player_access(player_name, current_user):
            raise AccessDeniedError(
                "Access denied: You don't have permission to update this assessment"
            )
        
        # Calculate new scores
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
        
        # Update in database
        updated = await self.repository.update_assessment(assessment_id, update_data)
        if not updated:
            raise AssessmentNotFoundError("Assessment not found")
        
        return PlayerAssessment(**updated)
    
    async def delete_assessment(
        self,
        assessment_id: str,
        current_user: dict
    ) -> bool:
        """Delete an assessment."""
        # Get existing assessment to check permissions
        existing = await self.repository.find_by_id(assessment_id)
        if not existing:
            raise AssessmentNotFoundError("Assessment not found")
        
        player_name = existing.get("player_name")
        if not await self.check_player_access(player_name, current_user):
            raise AccessDeniedError(
                "Access denied: You don't have permission to delete this assessment"
            )
        
        deleted = await self.repository.delete_assessment(assessment_id)
        if not deleted:
            raise AssessmentNotFoundError("Assessment not found")
        
        return True
    
    # =========================================================================
    # ASSESSMENT STATUS
    # =========================================================================
    
    async def get_assessment_status(
        self,
        player_name: str,
        current_user: dict
    ) -> Dict[str, Any]:
        """Get assessment status including latest assessment and next due date."""
        if not await self.check_player_access(player_name, current_user):
            raise AccessDeniedError("Access denied")
        
        assessment = await self.repository.find_latest_by_player_name(player_name)
        
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
    
    # =========================================================================
    # PLAYER ANALYSIS
    # =========================================================================
    
    async def get_player_analysis(
        self,
        player_name: str,
        current_user: dict
    ) -> Dict[str, Any]:
        """Get detailed analysis for a player."""
        if not await self.check_player_access(player_name, current_user):
            raise AccessDeniedError(
                "Access denied: You don't have permission to view this player's analysis"
            )
        
        assessment = await self.repository.find_latest_by_player_name(player_name)
        
        if not assessment:
            raise AssessmentNotFoundError("No assessment found for player")
        
        # Analyze strengths and weaknesses
        analysis = analyze_strengths_and_weaknesses(assessment)
        
        # Generate recommendations
        performance_level = assessment.get('performance_level', 'Developing')
        recommendations = generate_training_recommendations(analysis, performance_level)
        
        return {
            "player_name": player_name,
            "overall_score": assessment.get('overall_score', 0),
            "performance_level": performance_level,
            "strengths": analysis['strengths'],
            "weaknesses": analysis['weaknesses'],
            "recommendations": recommendations,
            "assessment_date": assessment.get('created_at')
        }


# Singleton instance
_assessment_service: Optional[AssessmentService] = None


def get_assessment_service() -> AssessmentService:
    """Get or create the assessment service singleton."""
    global _assessment_service
    if _assessment_service is None:
        _assessment_service = AssessmentService()
    return _assessment_service
