"""
Tests for Assessment Service
============================

Unit tests for assessment management logic.
Tests the service layer without database dependencies.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.assessment_service import (
    AssessmentService,
    AssessmentNotFoundError,
    AccessDeniedError,
    get_assessment_service
)


# ============================================================================
# TEST: ACCESS CONTROL
# ============================================================================

class TestAccessControl:
    """Test access control logic."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = AssessmentService()
        service.repository = mock_repo
        return service
    
    @pytest.mark.asyncio
    async def test_player_can_access_own_data(self, service):
        """Players should be able to access their own data."""
        current_user = {
            "role": "player",
            "username": "john_doe",
            "user_id": "user-123"
        }
        
        result = await service.check_player_access("john_doe", current_user)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_player_cannot_access_other_player_data(self, service):
        """Players should not be able to access other players' data."""
        current_user = {
            "role": "player",
            "username": "john_doe",
            "user_id": "user-123"
        }
        
        result = await service.check_player_access("jane_doe", current_user)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_coach_can_access_managed_player(self, service, mock_repo):
        """Coaches should be able to access their managed players."""
        mock_repo.find_user_by_id = AsyncMock(return_value={
            "id": "coach-123",
            "managed_players": ["john_doe", "jane_doe"]
        })
        
        current_user = {
            "role": "coach",
            "username": "coach_smith",
            "user_id": "coach-123"
        }
        
        result = await service.check_player_access("john_doe", current_user)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_coach_cannot_access_unmanaged_player(self, service, mock_repo):
        """Coaches should not be able to access unmanaged players."""
        mock_repo.find_user_by_id = AsyncMock(return_value={
            "id": "coach-123",
            "managed_players": ["jane_doe"]
        })
        
        current_user = {
            "role": "coach",
            "username": "coach_smith",
            "user_id": "coach-123"
        }
        
        result = await service.check_player_access("john_doe", current_user)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_parent_can_access_managed_player(self, service, mock_repo):
        """Parents should be able to access their children's data."""
        mock_repo.find_user_by_id = AsyncMock(return_value={
            "id": "parent-123",
            "managed_players": ["child_player"]
        })
        
        current_user = {
            "role": "parent",
            "username": "parent_user",
            "user_id": "parent-123"
        }
        
        result = await service.check_player_access("child_player", current_user)
        
        assert result is True


# ============================================================================
# TEST: ASSESSMENT CRUD (Mocked Repository)
# ============================================================================

class TestAssessmentCRUD:
    """Test assessment CRUD operations with mocked repository."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = AssessmentService()
        service.repository = mock_repo
        return service
    
    @pytest.fixture
    def sample_assessment_dict(self):
        """Sample assessment data."""
        return {
            "id": "assess-123",
            "player_name": "john_doe",
            "age": 17,
            "position": "Midfielder",
            "assessment_date": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "overall_score": 75.5,
            "performance_level": "Intermediate",
            "sprint_30m": 4.2,
            "yo_yo_test": 1800,
            "vo2_max": 55.0,
            "vertical_jump": 50,
            "body_fat": 12.0,
            "ball_control": 4,
            "passing_accuracy": 80,
            "dribbling_success": 75,
            "shooting_accuracy": 70,
            "defensive_duels": 65,
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4
        }
    
    @pytest.fixture
    def current_user(self):
        return {
            "role": "player",
            "username": "john_doe",
            "user_id": "user-123"
        }
    
    @pytest.mark.asyncio
    async def test_get_all_assessments_coach_only(self, service, mock_repo, sample_assessment_dict):
        """Only coaches should be able to get all assessments."""
        mock_repo.find_all = AsyncMock(return_value=[sample_assessment_dict])
        
        coach_user = {
            "role": "coach",
            "username": "coach_smith",
            "user_id": "coach-123"
        }
        
        results = await service.get_all_assessments(coach_user)
        
        assert len(results) == 1
        mock_repo.find_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_assessments_denied_for_player(self, service, current_user):
        """Players should not be able to get all assessments."""
        with pytest.raises(AccessDeniedError) as exc_info:
            await service.get_all_assessments(current_user)
        
        assert "Only coaches" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_player_assessments(self, service, mock_repo, sample_assessment_dict, current_user):
        """Should return assessments for a player."""
        mock_repo.find_by_player_name = AsyncMock(return_value=[sample_assessment_dict])
        
        results = await service.get_player_assessments("john_doe", current_user)
        
        assert len(results) == 1
        mock_repo.find_by_player_name.assert_called_once_with("john_doe")
    
    @pytest.mark.asyncio
    async def test_get_player_assessments_access_denied(self, service, current_user):
        """Should deny access to other player's assessments."""
        with pytest.raises(AccessDeniedError):
            await service.get_player_assessments("other_player", current_user)
    
    @pytest.mark.asyncio
    async def test_get_assessment_by_id(self, service, mock_repo, sample_assessment_dict, current_user):
        """Should return assessment by ID."""
        mock_repo.find_by_id = AsyncMock(return_value=sample_assessment_dict)
        
        result = await service.get_assessment_by_id("assess-123", current_user)
        
        assert result.id == "assess-123"
        mock_repo.find_by_id.assert_called_once_with("assess-123")
    
    @pytest.mark.asyncio
    async def test_get_assessment_by_id_not_found(self, service, mock_repo, current_user):
        """Should raise error when assessment not found."""
        mock_repo.find_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(AssessmentNotFoundError):
            await service.get_assessment_by_id("nonexistent", current_user)
    
    @pytest.mark.asyncio
    async def test_delete_assessment_success(self, service, mock_repo, sample_assessment_dict, current_user):
        """Should delete assessment successfully."""
        mock_repo.find_by_id = AsyncMock(return_value=sample_assessment_dict)
        mock_repo.delete_assessment = AsyncMock(return_value=True)
        
        result = await service.delete_assessment("assess-123", current_user)
        
        assert result is True
        mock_repo.delete_assessment.assert_called_once_with("assess-123")
    
    @pytest.mark.asyncio
    async def test_delete_assessment_not_found(self, service, mock_repo, current_user):
        """Should raise error when deleting non-existent assessment."""
        mock_repo.find_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(AssessmentNotFoundError):
            await service.delete_assessment("nonexistent", current_user)


# ============================================================================
# TEST: ASSESSMENT STATUS
# ============================================================================

class TestAssessmentStatus:
    """Test assessment status logic."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = AssessmentService()
        service.repository = mock_repo
        return service
    
    @pytest.fixture
    def current_user(self):
        return {
            "role": "player",
            "username": "john_doe",
            "user_id": "user-123"
        }
    
    @pytest.mark.asyncio
    async def test_no_assessment_returns_message(self, service, mock_repo, current_user):
        """Should return appropriate message when no assessment exists."""
        mock_repo.find_latest_by_player_name = AsyncMock(return_value=None)
        
        result = await service.get_assessment_status("john_doe", current_user)
        
        assert result["has_assessment"] is False
        assert "No assessment found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_assessment_due_calculated_correctly(self, service, mock_repo, current_user):
        """Should calculate next assessment date correctly."""
        # Assessment from 8 weeks ago with high score
        assessment_date = datetime.now(timezone.utc) - timedelta(weeks=8)
        mock_repo.find_latest_by_player_name = AsyncMock(return_value={
            "id": "assess-123",
            "created_at": assessment_date,
            "overall_score": 85,
            "performance_level": "Advanced"
        })
        
        result = await service.get_assessment_status("john_doe", current_user)
        
        assert result["has_assessment"] is True
        assert result["is_due"] is True  # 8 weeks for high score
    
    @pytest.mark.asyncio
    async def test_assessment_not_due_yet(self, service, mock_repo, current_user):
        """Should show not due when assessment is recent."""
        # Assessment from 2 weeks ago
        assessment_date = datetime.now(timezone.utc) - timedelta(weeks=2)
        mock_repo.find_latest_by_player_name = AsyncMock(return_value={
            "id": "assess-123",
            "created_at": assessment_date,
            "overall_score": 75,
            "performance_level": "Intermediate"
        })
        
        result = await service.get_assessment_status("john_doe", current_user)
        
        assert result["has_assessment"] is True
        assert result["is_due"] is False


# ============================================================================
# TEST: PLAYER ANALYSIS
# ============================================================================

class TestPlayerAnalysis:
    """Test player analysis generation."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = AssessmentService()
        service.repository = mock_repo
        return service
    
    @pytest.fixture
    def current_user(self):
        return {
            "role": "player",
            "username": "john_doe",
            "user_id": "user-123"
        }
    
    @pytest.mark.asyncio
    async def test_analysis_not_found(self, service, mock_repo, current_user):
        """Should raise error when no assessment found for analysis."""
        mock_repo.find_latest_by_player_name = AsyncMock(return_value=None)
        
        with pytest.raises(AssessmentNotFoundError) as exc_info:
            await service.get_player_analysis("john_doe", current_user)
        
        assert "No assessment found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_analysis_access_denied(self, service, current_user):
        """Should deny access to other player's analysis."""
        with pytest.raises(AccessDeniedError):
            await service.get_player_analysis("other_player", current_user)


# ============================================================================
# TEST: SERVICE SINGLETON
# ============================================================================

class TestServiceSingleton:
    """Test service singleton pattern."""
    
    def test_get_assessment_service_returns_same_instance(self):
        """get_assessment_service should return the same instance."""
        service1 = get_assessment_service()
        service2 = get_assessment_service()
        
        assert service1 is service2


# ============================================================================
# TEST: USER_ID LINKING (Bug Fix Verification)
# ============================================================================

class TestUserIdLinking:
    """Test that assessments are properly linked to user_id from JWT."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = AssessmentService()
        service.repository = mock_repo
        return service
    
    @pytest.fixture
    def sample_assessment_create(self):
        """Sample assessment creation data."""
        from models import AssessmentCreate
        return AssessmentCreate(
            player_name="john_doe",
            age=17,
            position="Midfielder",
            sprint_30m=4.2,
            yo_yo_test=1800,
            vo2_max=55.0,
            vertical_jump=50,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=80,
            dribbling_success=75,
            shooting_accuracy=70,
            defensive_duels=65,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4
        )
    
    @pytest.fixture
    def current_user_player(self):
        """Current user as player (JWT-derived)."""
        return {
            "role": "player",
            "username": "john_doe",
            "user_id": "user-abc-123"
        }
    
    @pytest.fixture
    def current_user_coach(self):
        """Current user as coach (JWT-derived)."""
        return {
            "role": "coach",
            "username": "coach_smith",
            "user_id": "coach-xyz-789"
        }
    
    @pytest.mark.asyncio
    async def test_assessment_created_with_user_id(self, service, mock_repo, sample_assessment_create, current_user_player):
        """Assessment should be created with user_id from JWT-derived current_user."""
        mock_repo.create_assessment = AsyncMock(return_value={})
        
        result = await service.create_assessment(sample_assessment_create, current_user_player)
        
        # The returned PlayerAssessment should have user_id set
        assert result.user_id == "user-abc-123"
    
    @pytest.mark.asyncio
    async def test_assessment_saved_to_db_with_user_id(self, service, mock_repo, sample_assessment_create, current_user_player):
        """The data saved to database should include user_id."""
        mock_repo.create_assessment = AsyncMock(return_value={})
        
        await service.create_assessment(sample_assessment_create, current_user_player)
        
        # Verify the repository was called with data including user_id
        call_args = mock_repo.create_assessment.call_args
        saved_data = call_args[0][0]
        
        assert saved_data['user_id'] == "user-abc-123"
        assert saved_data['created_by_username'] == "john_doe"
    
    @pytest.mark.asyncio
    async def test_coach_creating_assessment_links_their_user_id(self, service, mock_repo, sample_assessment_create, current_user_coach):
        """When coach creates assessment, their user_id should be linked."""
        # Coach needs to have managed_players
        mock_repo.find_user_by_id = AsyncMock(return_value={
            "id": "coach-xyz-789",
            "managed_players": ["john_doe"]
        })
        mock_repo.create_assessment = AsyncMock(return_value={})
        
        result = await service.create_assessment(sample_assessment_create, current_user_coach)
        
        # The coach's user_id should be linked
        assert result.user_id == "coach-xyz-789"
    
    @pytest.mark.asyncio
    async def test_missing_user_id_handled_gracefully(self, service, mock_repo, sample_assessment_create):
        """Should handle missing user_id gracefully (backward compatibility)."""
        mock_repo.create_assessment = AsyncMock(return_value={})
        
        # current_user without user_id (edge case)
        current_user_no_id = {
            "role": "player",
            "username": "john_doe"
            # user_id missing
        }
        
        result = await service.create_assessment(sample_assessment_create, current_user_no_id)
        
        # Should still create assessment, user_id will be None
        assert result.user_id is None
        assert result.player_name == "john_doe"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
