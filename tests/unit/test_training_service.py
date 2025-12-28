"""
Tests for Training Service
==========================

Unit tests for training program management logic.
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

from services.training_service import (
    TrainingService,
    AssessmentNotFoundError,
    ProgramNotFoundError,
    get_training_service
)


# ============================================================================
# TEST: WEAKNESS ANALYSIS
# ============================================================================

class TestWeaknessAnalysis:
    """Test weakness analysis from assessments."""
    
    @pytest.fixture
    def service(self):
        return TrainingService()
    
    def test_identifies_speed_weakness(self, service):
        """Should identify speed weakness when sprint time > 4.5s."""
        assessment = {"sprint_30m": 5.0, "ball_control": 4, "passing_accuracy": 80, "game_intelligence": 4}
        weaknesses = service.analyze_weaknesses(assessment)
        assert "speed" in weaknesses
    
    def test_identifies_ball_control_weakness(self, service):
        """Should identify ball control weakness when rating < 4."""
        assessment = {"sprint_30m": 4.0, "ball_control": 2, "passing_accuracy": 80, "game_intelligence": 4}
        weaknesses = service.analyze_weaknesses(assessment)
        assert "ball_control" in weaknesses
    
    def test_identifies_passing_weakness(self, service):
        """Should identify passing weakness when accuracy < 75%."""
        assessment = {"sprint_30m": 4.0, "ball_control": 4, "passing_accuracy": 60, "game_intelligence": 4}
        weaknesses = service.analyze_weaknesses(assessment)
        assert "passing" in weaknesses
    
    def test_identifies_tactical_weakness(self, service):
        """Should identify tactical weakness when game intelligence < 4."""
        assessment = {"sprint_30m": 4.0, "ball_control": 4, "passing_accuracy": 80, "game_intelligence": 2}
        weaknesses = service.analyze_weaknesses(assessment)
        assert "tactical" in weaknesses
    
    def test_no_weaknesses_for_strong_player(self, service):
        """Should return empty list for strong player."""
        assessment = {"sprint_30m": 4.0, "ball_control": 5, "passing_accuracy": 85, "game_intelligence": 5}
        weaknesses = service.analyze_weaknesses(assessment)
        assert weaknesses == []
    
    def test_multiple_weaknesses(self, service):
        """Should identify multiple weaknesses."""
        assessment = {"sprint_30m": 5.5, "ball_control": 2, "passing_accuracy": 60, "game_intelligence": 2}
        weaknesses = service.analyze_weaknesses(assessment)
        assert len(weaknesses) == 4
        assert "speed" in weaknesses
        assert "ball_control" in weaknesses
        assert "passing" in weaknesses
        assert "tactical" in weaknesses
    
    def test_exercise_weakness_analysis_different(self, service):
        """Exercise analysis uses 'technical' instead of 'ball_control'."""
        assessment = {"sprint_30m": 5.0, "ball_control": 2, "game_intelligence": 2}
        weaknesses = service.analyze_weaknesses_for_exercises(assessment)
        assert "speed" in weaknesses
        assert "technical" in weaknesses
        assert "tactical" in weaknesses
        assert "ball_control" not in weaknesses  # Uses 'technical' instead


# ============================================================================
# TEST: PERIODIZED PROGRAMS
# ============================================================================

class TestPeriodizedPrograms:
    """Test periodized program operations."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = TrainingService()
        service.repository = mock_repo
        return service
    
    @pytest.fixture
    def sample_program_create(self):
        from models import PeriodizedProgramCreate
        return PeriodizedProgramCreate(
            player_id="test_player",
            program_name="Test Program",
            assessment_interval_weeks=6,
            program_objectives=["Improve speed", "Better passing"]
        )
    
    @pytest.mark.asyncio
    async def test_create_periodized_program_without_assessment(self, service, mock_repo, sample_program_create):
        """Should create program even without assessment (empty weaknesses)."""
        mock_repo.find_latest_assessment = AsyncMock(return_value=None)
        mock_repo.create_periodized_program = AsyncMock(return_value={})
        
        result = await service.create_periodized_program(sample_program_create)
        
        assert result.player_id == "test_player"
        assert result.program_name == "Test Program"
        assert len(result.macro_cycles) == 3  # foundation, development, peak
        mock_repo.create_periodized_program.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_periodized_program_with_assessment(self, service, mock_repo, sample_program_create):
        """Should analyze weaknesses from assessment."""
        mock_repo.find_latest_assessment = AsyncMock(return_value={
            "sprint_30m": 5.5,
            "ball_control": 2,
            "passing_accuracy": 60,
            "game_intelligence": 2
        })
        mock_repo.create_periodized_program = AsyncMock(return_value={})
        
        result = await service.create_periodized_program(sample_program_create)
        
        assert result.player_id == "test_player"
        mock_repo.find_latest_assessment.assert_called_once_with("test_player")
    
    @pytest.mark.asyncio
    async def test_get_player_periodized_program_found(self, service, mock_repo):
        """Should return program when found."""
        mock_repo.find_periodized_program_by_player = AsyncMock(return_value={
            "id": "prog-123",
            "player_id": "test_player",
            "program_name": "Test Program",
            "total_duration_weeks": 12,
            "macro_cycles": [],
            "program_objectives": [],
            "program_start_date": datetime.now(timezone.utc),
            "next_assessment_date": datetime.now(timezone.utc) + timedelta(weeks=6),
            "created_at": datetime.now(timezone.utc)
        })
        
        result = await service.get_player_periodized_program("test_player")
        
        assert result is not None
        assert result.player_id == "test_player"
    
    @pytest.mark.asyncio
    async def test_get_player_periodized_program_not_found(self, service, mock_repo):
        """Should return None when no program found."""
        mock_repo.find_periodized_program_by_player = AsyncMock(return_value=None)
        
        result = await service.get_player_periodized_program("test_player")
        
        assert result is None


# ============================================================================
# TEST: CURRENT ROUTINE
# ============================================================================

class TestCurrentRoutine:
    """Test current routine retrieval."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = TrainingService()
        service.repository = mock_repo
        return service
    
    @pytest.mark.asyncio
    async def test_no_program_returns_message(self, service, mock_repo):
        """Should return message when no program exists."""
        mock_repo.find_periodized_program_by_player = AsyncMock(return_value=None)
        
        result = await service.get_current_routine("test_player")
        
        assert result["message"] == "No training program found"
        assert result["routine"] is None
    
    @pytest.mark.asyncio
    async def test_rest_day_returns_message(self, service, mock_repo):
        """Should return rest day message when current day is weekend."""
        # Program with no matching routine for current day
        mock_repo.find_periodized_program_by_player = AsyncMock(return_value={
            "program_start_date": datetime.now(timezone.utc) - timedelta(days=6),  # Started 6 days ago (weekend)
            "macro_cycles": [{
                "phase_number": 1,
                "micro_cycles": [{
                    "daily_routines": []  # Empty routines
                }]
            }],
            "program_name": "Test Program"
        })
        
        result = await service.get_current_routine("test_player")
        
        assert "routine" in result
    
    @pytest.mark.asyncio
    async def test_valid_routine_returned(self, service, mock_repo):
        """Should return valid routine for current day."""
        sample_routine = {
            "day_number": 1,
            "phase": "foundation_building",
            "exercises": [],
            "total_duration": 60
        }
        
        mock_repo.find_periodized_program_by_player = AsyncMock(return_value={
            "program_start_date": datetime.now(timezone.utc),  # Started today
            "macro_cycles": [{
                "phase_number": 1,
                "micro_cycles": [{
                    "daily_routines": [sample_routine, sample_routine, sample_routine, sample_routine, sample_routine]
                }]
            }],
            "program_name": "Test Program"
        })
        
        result = await service.get_current_routine("test_player")
        
        assert result["current_week"] == 1
        assert result["program_name"] == "Test Program"


# ============================================================================
# TEST: TRAINING PROGRAMS (Legacy)
# ============================================================================

class TestTrainingPrograms:
    """Test legacy training program operations."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = TrainingService()
        service.repository = mock_repo
        return service
    
    @pytest.fixture
    def sample_program_create(self):
        from models import TrainingProgramCreate
        return TrainingProgramCreate(
            player_id="test_player",
            program_type="AI_Generated"
        )
    
    @pytest.mark.asyncio
    async def test_create_training_program_no_assessment(self, service, mock_repo, sample_program_create):
        """Should raise error when no assessment found."""
        mock_repo.find_latest_assessment = AsyncMock(return_value=None)
        
        with pytest.raises(AssessmentNotFoundError) as exc_info:
            await service.create_training_program(sample_program_create)
        
        assert "No assessment found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_training_program_with_assessment(self, service, mock_repo, sample_program_create):
        """Should create program when assessment exists."""
        mock_repo.find_latest_assessment = AsyncMock(return_value={
            "player_name": "test_player",
            "sprint_30m": 4.5,
            "ball_control": 4,
            "overall_score": 75
        })
        mock_repo.create_training_program = AsyncMock(return_value={})
        
        with patch('services.training_service.generate_training_program', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Generated training content"
            
            result = await service.create_training_program(sample_program_create)
            
            assert result.player_id == "test_player"
            assert result.program_type == "AI_Generated"
            mock_repo.create_training_program.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_player_training_programs(self, service, mock_repo):
        """Should return list of programs."""
        mock_repo.find_training_programs_by_player = AsyncMock(return_value=[
            {
                "id": "prog-1",
                "player_id": "test_player",
                "program_type": "AI_Generated",
                "program_content": "Content 1",
                "weekly_schedule": {},
                "milestones": [],
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": "prog-2",
                "player_id": "test_player",
                "program_type": "Custom",
                "program_content": "Content 2",
                "weekly_schedule": {},
                "milestones": [],
                "created_at": datetime.now(timezone.utc)
            }
        ])
        
        result = await service.get_player_training_programs("test_player")
        
        assert len(result) == 2
        assert result[0].program_type == "AI_Generated"
        assert result[1].program_type == "Custom"


# ============================================================================
# TEST: ADAPTIVE EXERCISES
# ============================================================================

class TestAdaptiveExercises:
    """Test adaptive exercise generation."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = TrainingService()
        service.repository = mock_repo
        return service
    
    @pytest.mark.asyncio
    async def test_no_assessment_raises_error(self, service, mock_repo):
        """Should raise error when no assessment found."""
        mock_repo.find_latest_assessment = AsyncMock(return_value=None)
        
        with pytest.raises(AssessmentNotFoundError):
            await service.get_adaptive_exercises("test_player")
    
    @pytest.mark.asyncio
    async def test_generates_exercises_with_assessment(self, service, mock_repo):
        """Should generate exercises when assessment exists."""
        mock_repo.find_latest_assessment = AsyncMock(return_value={
            "sprint_30m": 5.0,
            "ball_control": 2,
            "game_intelligence": 2
        })
        
        with patch('services.training_service.generate_adaptive_exercises', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = ["Exercise 1", "Exercise 2"]
            
            result = await service.get_adaptive_exercises("test_player", "development", 2)
            
            assert result["player_id"] == "test_player"
            assert result["phase"] == "development"
            assert result["week_number"] == 2
            assert "speed" in result["identified_weaknesses"]
            assert "technical" in result["identified_weaknesses"]
            assert "tactical" in result["identified_weaknesses"]


# ============================================================================
# TEST: SERVICE SINGLETON
# ============================================================================

class TestServiceSingleton:
    """Test service singleton pattern."""
    
    def test_get_training_service_returns_same_instance(self):
        """get_training_service should return the same instance."""
        service1 = get_training_service()
        service2 = get_training_service()
        
        assert service1 is service2


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
