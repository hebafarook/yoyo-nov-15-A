"""
Tests for Progress Service
==========================

Unit tests for progress tracking and performance metrics.
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

from services.progress_service import (
    ProgressService,
    ProgressNotFoundError,
    get_progress_service
)


# ============================================================================
# TEST: IMPROVEMENT TRENDS CALCULATION
# ============================================================================

class TestImprovementTrends:
    """Test improvement trend calculations."""
    
    def test_calculates_positive_trend(self):
        """Test calculation of positive improvement trend."""
        metrics = [
            {"metric_name": "speed", "value": 10, "measurement_date": datetime(2024, 1, 1)},
            {"metric_name": "speed", "value": 15, "measurement_date": datetime(2024, 1, 15)},
        ]
        
        trends = ProgressService._calculate_improvement_trends(metrics)
        
        assert "speed" in trends
        assert trends["speed"]["improvement_percentage"] == 50.0
        assert trends["speed"]["trend_direction"] == "up"
        assert trends["speed"]["data_points"] == 2
    
    def test_calculates_negative_trend(self):
        """Test calculation of negative improvement trend."""
        metrics = [
            {"metric_name": "reaction_time", "value": 100, "measurement_date": datetime(2024, 1, 1)},
            {"metric_name": "reaction_time", "value": 80, "measurement_date": datetime(2024, 1, 15)},
        ]
        
        trends = ProgressService._calculate_improvement_trends(metrics)
        
        assert "reaction_time" in trends
        assert trends["reaction_time"]["improvement_percentage"] == -20.0
        assert trends["reaction_time"]["trend_direction"] == "down"
    
    def test_groups_metrics_by_type(self):
        """Test that metrics are grouped by type correctly."""
        metrics = [
            {"metric_name": "speed", "value": 10, "measurement_date": datetime(2024, 1, 1)},
            {"metric_name": "speed", "value": 12, "measurement_date": datetime(2024, 1, 15)},
            {"metric_name": "strength", "value": 50, "measurement_date": datetime(2024, 1, 1)},
            {"metric_name": "strength", "value": 60, "measurement_date": datetime(2024, 1, 15)},
        ]
        
        trends = ProgressService._calculate_improvement_trends(metrics)
        
        assert "speed" in trends
        assert "strength" in trends
    
    def test_requires_at_least_two_data_points(self):
        """Test that trends require at least 2 data points."""
        metrics = [
            {"metric_name": "speed", "value": 10, "measurement_date": datetime(2024, 1, 1)},
        ]
        
        trends = ProgressService._calculate_improvement_trends(metrics)
        
        assert "speed" not in trends  # Not enough data points
    
    def test_handles_zero_first_value(self):
        """Test handling of zero first value (avoid division by zero)."""
        metrics = [
            {"metric_name": "errors", "value": 0, "measurement_date": datetime(2024, 1, 1)},
            {"metric_name": "errors", "value": 5, "measurement_date": datetime(2024, 1, 15)},
        ]
        
        trends = ProgressService._calculate_improvement_trends(metrics)
        
        # Should not crash, and should not include trend (can't calculate % from 0)
        assert "errors" not in trends
    
    def test_empty_metrics_returns_empty_trends(self):
        """Test that empty metrics returns empty trends."""
        trends = ProgressService._calculate_improvement_trends([])
        
        assert trends == {}


# ============================================================================
# TEST: CURRENT WEEK CALCULATION
# ============================================================================

class TestCurrentWeekCalculation:
    """Test current week calculation from program start date."""
    
    def test_first_week(self):
        """Test that day 1 is week 1."""
        program = {
            "program_start_date": datetime.now(timezone.utc)
        }
        
        week = ProgressService._calculate_current_week(program)
        
        assert week == 1
    
    def test_second_week(self):
        """Test that day 8 is week 2."""
        program = {
            "program_start_date": datetime.now(timezone.utc) - timedelta(days=8)
        }
        
        week = ProgressService._calculate_current_week(program)
        
        assert week == 2
    
    def test_handles_string_date(self):
        """Test handling of ISO string date."""
        start = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
        program = {
            "program_start_date": start
        }
        
        week = ProgressService._calculate_current_week(program)
        
        assert week == 3
    
    def test_missing_start_date_returns_1(self):
        """Test that missing start date returns week 1."""
        program = {}
        
        week = ProgressService._calculate_current_week(program)
        
        assert week == 1


# ============================================================================
# TEST: CURRENT PHASE CALCULATION
# ============================================================================

class TestCurrentPhaseCalculation:
    """Test current phase calculation."""
    
    def test_first_phase(self):
        """Test first phase detection."""
        program = {
            "program_start_date": datetime.now(timezone.utc),
            "macro_cycles": [
                {"duration_weeks": 4},
                {"duration_weeks": 4},
            ]
        }
        
        phase = ProgressService._calculate_current_phase(program)
        
        assert phase == 1
    
    def test_second_phase(self):
        """Test second phase detection after first phase duration."""
        program = {
            "program_start_date": datetime.now(timezone.utc) - timedelta(weeks=5),
            "macro_cycles": [
                {"duration_weeks": 4},
                {"duration_weeks": 4},
            ]
        }
        
        phase = ProgressService._calculate_current_phase(program)
        
        assert phase == 2
    
    def test_empty_macro_cycles_returns_1(self):
        """Test that empty macro_cycles returns phase 1."""
        program = {
            "program_start_date": datetime.now(timezone.utc),
            "macro_cycles": []
        }
        
        phase = ProgressService._calculate_current_phase(program)
        
        assert phase == 1


# ============================================================================
# TEST: DAILY PROGRESS CRUD (Mocked Repository)
# ============================================================================

class TestDailyProgressCRUD:
    """Test daily progress CRUD operations with mocked repository."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create a mocked repository."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create service with mocked repository."""
        service = ProgressService()
        service.repository = mock_repo
        return service
    
    @pytest.mark.asyncio
    async def test_log_daily_progress(self, service, mock_repo):
        """Test logging daily progress."""
        from models import DailyProgressCreate, ExerciseCompletionCreate
        
        mock_repo.create_daily_progress = AsyncMock(return_value={})
        mock_repo.find_latest_program = AsyncMock(return_value=None)
        
        progress_data = MagicMock(spec=DailyProgressCreate)
        progress_data.player_id = "player-123"
        progress_data.routine_id = "routine-1"
        progress_data.completed_exercises = []
        progress_data.overall_rating = 4
        progress_data.energy_level = 4
        progress_data.motivation_level = 4
        progress_data.daily_notes = "Good session"
        progress_data.total_time_spent = 60
        
        result = await service.log_daily_progress(progress_data)
        
        mock_repo.create_daily_progress.assert_called_once()
        assert result.player_id == "player-123"
    
    @pytest.mark.asyncio
    async def test_get_daily_progress(self, service, mock_repo):
        """Test getting daily progress."""
        mock_repo.find_daily_progress_by_player = AsyncMock(return_value=[
            {
                "id": "dp1",
                "player_id": "p1",
                "routine_id": "r1",
                "completed_exercises": [],
                "overall_rating": 4,
                "energy_level": 4,
                "motivation_level": 4
            }
        ])
        
        results = await service.get_daily_progress("p1", days=30)
        
        mock_repo.find_daily_progress_by_player.assert_called_once_with("p1", 30)
        assert len(results) == 1


# ============================================================================
# TEST: WEEKLY PROGRESS CRUD (Mocked Repository)
# ============================================================================

class TestWeeklyProgressCRUD:
    """Test weekly progress CRUD operations with mocked repository."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = ProgressService()
        service.repository = mock_repo
        return service
    
    @pytest.fixture
    def sample_weekly_progress_dict(self):
        """Sample weekly progress data matching model requirements."""
        return {
            "id": "wp1",
            "player_id": "player-123",
            "week_number": 1,
            "program_id": "program-1",
            "completed_exercises": ["ex1", "ex2"],
            "performance_notes": "Good week",
            "intensity_rating": 4,
            "fatigue_level": 3,
            "improvement_areas": ["speed", "agility"],
            "week_completed": True,
            "created_at": datetime.now(timezone.utc)
        }
    
    @pytest.mark.asyncio
    async def test_log_weekly_progress(self, service, mock_repo, sample_weekly_progress_dict):
        """Test logging weekly progress."""
        from models import WeeklyProgressCreate
        
        mock_repo.create_weekly_progress = AsyncMock(return_value={})
        
        progress_data = MagicMock(spec=WeeklyProgressCreate)
        progress_data.dict.return_value = sample_weekly_progress_dict
        progress_data.player_id = "player-123"
        
        result = await service.log_weekly_progress(progress_data)
        
        mock_repo.create_weekly_progress.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_weekly_progress(self, service, mock_repo, sample_weekly_progress_dict):
        """Test getting weekly progress."""
        mock_repo.find_weekly_progress_by_player = AsyncMock(return_value=[
            sample_weekly_progress_dict
        ])
        
        results = await service.get_weekly_progress("p1")
        
        mock_repo.find_weekly_progress_by_player.assert_called_once_with("p1")
        assert len(results) == 1


# ============================================================================
# TEST: PROGRESS SUMMARY
# ============================================================================

class TestProgressSummary:
    """Test progress summary generation."""
    
    @pytest.fixture
    def mock_repo(self):
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        service = ProgressService()
        service.repository = mock_repo
        return service
    
    @pytest.mark.asyncio
    async def test_raises_not_found_when_no_assessment(self, service, mock_repo):
        """Test that ProgressNotFoundError is raised when no assessment exists."""
        mock_repo.find_latest_assessment = AsyncMock(return_value=None)
        
        with pytest.raises(ProgressNotFoundError) as exc_info:
            await service.get_progress_summary("player-123")
        
        assert "No assessment found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_calculates_training_consistency(self, service, mock_repo):
        """Test training consistency calculation."""
        mock_repo.find_latest_assessment = AsyncMock(return_value={
            "created_at": datetime.now(timezone.utc),
            "overall_score": 75,
            "performance_level": "Developing"
        })
        mock_repo.count_daily_progress = AsyncMock(return_value=15)  # 15 sessions in 30 days
        mock_repo.find_metrics_by_player = AsyncMock(return_value=[])
        mock_repo.find_latest_program = AsyncMock(return_value=None)
        
        result = await service.get_progress_summary("player-123")
        
        assert result["training_sessions_30_days"] == 15
        assert result["training_consistency_percentage"] == 50.0  # 15/30 * 100
    
    @pytest.mark.asyncio
    async def test_caps_consistency_at_100(self, service, mock_repo):
        """Test that training consistency is capped at 100%."""
        mock_repo.find_latest_assessment = AsyncMock(return_value={
            "created_at": datetime.now(timezone.utc),
            "overall_score": 75,
            "performance_level": "Developing"
        })
        mock_repo.count_daily_progress = AsyncMock(return_value=45)  # More than 30 sessions
        mock_repo.find_metrics_by_player = AsyncMock(return_value=[])
        mock_repo.find_latest_program = AsyncMock(return_value=None)
        
        result = await service.get_progress_summary("player-123")
        
        assert result["training_consistency_percentage"] == 100.0


# ============================================================================
# TEST: SERVICE SINGLETON
# ============================================================================

class TestServiceSingleton:
    """Test service singleton pattern."""
    
    def test_get_progress_service_returns_same_instance(self):
        """get_progress_service should return the same instance."""
        service1 = get_progress_service()
        service2 = get_progress_service()
        
        assert service1 is service2


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
