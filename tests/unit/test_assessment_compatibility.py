"""
Tests for Assessment Backward Compatibility
===========================================

Tests to verify that:
1. PlayerAssessment model includes assessment_date as alias for created_at
2. Public (unauthenticated) routes work correctly
3. Legacy response schema is preserved
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


# ============================================================================
# TEST: ASSESSMENT_DATE BACKWARD COMPATIBILITY
# ============================================================================

class TestAssessmentDateCompatibility:
    """Test that assessment_date is available as alias for created_at."""
    
    def test_assessment_date_equals_created_at(self):
        """assessment_date should equal created_at."""
        from models import PlayerAssessment
        
        assessment = PlayerAssessment(
            player_name="test_player",
            age=17,
            position="Midfielder",
            sprint_30m=4.5,
            yo_yo_test=1500,
            vo2_max=50.0,
            vertical_jump=45,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=75.0,
            dribbling_success=70.0,
            shooting_accuracy=65.0,
            defensive_duels=60.0,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4
        )
        
        assert assessment.assessment_date == assessment.created_at
    
    def test_assessment_date_in_dict_output(self):
        """assessment_date should be included in model dict/json output."""
        from models import PlayerAssessment
        
        assessment = PlayerAssessment(
            player_name="test_player",
            age=17,
            position="Midfielder",
            sprint_30m=4.5,
            yo_yo_test=1500,
            vo2_max=50.0,
            vertical_jump=45,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=75.0,
            dribbling_success=70.0,
            shooting_accuracy=65.0,
            defensive_duels=60.0,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4
        )
        
        # model_dump() should include assessment_date
        data = assessment.model_dump()
        assert "assessment_date" in data
        assert data["assessment_date"] == data["created_at"]
    
    def test_assessment_date_in_json_schema(self):
        """assessment_date should be in JSON schema for API docs."""
        from models import PlayerAssessment
        
        schema = PlayerAssessment.model_json_schema()
        assert "assessment_date" in schema["properties"]


# ============================================================================
# TEST: LEGACY FIELDS PRESENT
# ============================================================================

class TestLegacyFieldsPresent:
    """Test that legacy fields are present in the model."""
    
    def test_category_scores_field_exists(self):
        """category_scores field should exist and be optional."""
        from models import PlayerAssessment
        
        # Should be able to create without category_scores
        assessment = PlayerAssessment(
            player_name="test_player",
            age=17,
            position="Midfielder",
            sprint_30m=4.5,
            yo_yo_test=1500,
            vo2_max=50.0,
            vertical_jump=45,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=75.0,
            dribbling_success=70.0,
            shooting_accuracy=65.0,
            defensive_duels=60.0,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4
        )
        assert assessment.category_scores is None
        
        # Should be able to set category_scores
        assessment2 = PlayerAssessment(
            player_name="test_player",
            age=17,
            position="Midfielder",
            sprint_30m=4.5,
            yo_yo_test=1500,
            vo2_max=50.0,
            vertical_jump=45,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=75.0,
            dribbling_success=70.0,
            shooting_accuracy=65.0,
            defensive_duels=60.0,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4,
            category_scores={"physical": 80.0, "technical": 75.0}
        )
        assert assessment2.category_scores == {"physical": 80.0, "technical": 75.0}
    
    def test_gamification_fields_exist(self):
        """total_coins and level fields should exist with defaults."""
        from models import PlayerAssessment
        
        assessment = PlayerAssessment(
            player_name="test_player",
            age=17,
            position="Midfielder",
            sprint_30m=4.5,
            yo_yo_test=1500,
            vo2_max=50.0,
            vertical_jump=45,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=75.0,
            dribbling_success=70.0,
            shooting_accuracy=65.0,
            defensive_duels=60.0,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4
        )
        
        assert assessment.total_coins == 0
        assert assessment.level == 1
    
    def test_retest_fields_exist(self):
        """retest_scheduled and previous_assessment_id should exist."""
        from models import PlayerAssessment
        
        assessment = PlayerAssessment(
            player_name="test_player",
            age=17,
            position="Midfielder",
            sprint_30m=4.5,
            yo_yo_test=1500,
            vo2_max=50.0,
            vertical_jump=45,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=75.0,
            dribbling_success=70.0,
            shooting_accuracy=65.0,
            defensive_duels=60.0,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4
        )
        
        assert assessment.retest_scheduled is None
        assert assessment.previous_assessment_id is None
    
    def test_physical_measurement_fields_exist(self):
        """height_cm, weight_kg, bmi fields should exist."""
        from models import PlayerAssessment
        
        assessment = PlayerAssessment(
            player_name="test_player",
            age=17,
            position="Midfielder",
            sprint_30m=4.5,
            yo_yo_test=1500,
            vo2_max=50.0,
            vertical_jump=45,
            body_fat=12.0,
            ball_control=4,
            passing_accuracy=75.0,
            dribbling_success=70.0,
            shooting_accuracy=65.0,
            defensive_duels=60.0,
            game_intelligence=4,
            positioning=4,
            decision_making=4,
            coachability=5,
            mental_toughness=4,
            height_cm=175.0,
            weight_kg=70.0,
            bmi=22.9
        )
        
        assert assessment.height_cm == 175.0
        assert assessment.weight_kg == 70.0
        assert assessment.bmi == 22.9


# ============================================================================
# TEST: PUBLIC ROUTES (NO AUTH)
# ============================================================================

class TestPublicRoutesNoAuth:
    """Test that public routes work without authentication."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.mark.asyncio
    async def test_create_assessment_public_no_auth_required(self, mock_repo):
        """POST /assessments/public should work without JWT."""
        from routes.assessment_routes_public import create_assessment_public, get_repository
        from models import AssessmentCreate
        
        # Mock the repository
        with patch('routes.assessment_routes_public.get_repository', return_value=mock_repo):
            mock_repo.create_assessment = AsyncMock(return_value={})
            
            assessment_data = AssessmentCreate(
                player_name="test_player",
                age=17,
                position="Midfielder",
                sprint_30m=4.5,
                yo_yo_test=1500,
                vo2_max=50.0,
                vertical_jump=45,
                body_fat=12.0,
                ball_control=4,
                passing_accuracy=75.0,
                dribbling_success=70.0,
                shooting_accuracy=65.0,
                defensive_duels=60.0,
                game_intelligence=4,
                positioning=4,
                decision_making=4,
                coachability=5,
                mental_toughness=4
            )
            
            # Should not raise any authentication error
            result = await create_assessment_public(assessment_data)
            
            assert result.player_name == "test_player"
            assert result.overall_score is not None
    
    @pytest.mark.asyncio
    async def test_get_assessments_public_no_auth_required(self, mock_repo):
        """GET /assessments/public should work without JWT."""
        from routes.assessment_routes_public import get_assessments_public
        
        sample_assessment = {
            "id": "test-id",
            "player_name": "test_player",
            "age": 17,
            "position": "Midfielder",
            "sprint_30m": 4.5,
            "yo_yo_test": 1500,
            "vo2_max": 50.0,
            "vertical_jump": 45,
            "body_fat": 12.0,
            "ball_control": 4,
            "passing_accuracy": 75.0,
            "dribbling_success": 70.0,
            "shooting_accuracy": 65.0,
            "defensive_duels": 60.0,
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        with patch('routes.assessment_routes_public.get_repository', return_value=mock_repo):
            mock_repo.find_all = AsyncMock(return_value=[sample_assessment])
            
            # Should not raise any authentication error
            result = await get_assessments_public(user_id=None)
            
            assert len(result) == 1
            assert result[0].player_name == "test_player"
    
    @pytest.mark.asyncio
    async def test_get_player_assessments_public_no_auth_required(self, mock_repo):
        """GET /assessments/public/player/{name} should work without JWT."""
        from routes.assessment_routes_public import get_player_assessments_public
        
        sample_assessment = {
            "id": "test-id",
            "player_name": "john_doe",
            "age": 17,
            "position": "Midfielder",
            "sprint_30m": 4.5,
            "yo_yo_test": 1500,
            "vo2_max": 50.0,
            "vertical_jump": 45,
            "body_fat": 12.0,
            "ball_control": 4,
            "passing_accuracy": 75.0,
            "dribbling_success": 70.0,
            "shooting_accuracy": 65.0,
            "defensive_duels": 60.0,
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        with patch('routes.assessment_routes_public.get_repository', return_value=mock_repo):
            mock_repo.find_by_player_name = AsyncMock(return_value=[sample_assessment])
            
            # Should not raise any authentication error
            result = await get_player_assessments_public("john_doe")
            
            assert len(result) == 1
            assert result[0].player_name == "john_doe"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
