"""
Tests for Elite Training Service
================================

Unit tests for elite training service operations.
Tests the service layer without database dependencies.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.elite_training_service import (
    EliteTrainingService,
    TestingDataNotFoundError,
    MatchScheduleNotFoundError,
    InvalidRTPStageError,
    RTPProtocolNotFoundError,
    get_elite_training_service
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def mock_generator():
    return MagicMock()


@pytest.fixture
def service(mock_repo, mock_generator):
    service = EliteTrainingService()
    service.repository = mock_repo
    service.generator = mock_generator
    return service


@pytest.fixture
def sample_wellness_data():
    """Sample wellness data from the engine."""
    from elite_training_system import Wellness
    return Wellness(
        sleep_hours=7.5,
        sleep_quality=4,
        soreness_1_5=2,
        fatigue_1_5=2,
        stress_1_5=2,
        mood_1_5=4,
        resting_hr=60,
        hrv=65.0,
        hydration_status="good",
        nutrition_compliance=True
    )


@pytest.fixture
def sample_testing_data():
    """Sample testing data from the engine."""
    from elite_training_system import TestingData
    return TestingData(
        yo_yo_level=18.5,
        sprint_10m=1.75,
        sprint_30m=4.2,
        cmj_height=42.0,
        rsa_mean=7.2,
        rsa_fatigue_index=5.0,
        agility_505=2.3,
        max_hr=195,
        resting_hr=55,
        hrv_rmssd=65.0,
        test_date=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_previous_load():
    """Sample previous load data from the engine."""
    from elite_training_system import PreviousLoad
    return PreviousLoad(
        acwr=1.1,
        rpe_avg=6.5,
        total_distance_m=8500,
        sprint_count=25,
        hsr_m=850
    )


@pytest.fixture
def sample_match_schedule():
    """Sample match schedule from the engine."""
    from elite_training_system import MatchSchedule
    return MatchSchedule(
        days_to_next_match=4,
        matches_this_week=2,
        opponent="Team A",
        match_importance=4
    )


# ============================================================================
# TEST: WELLNESS OPERATIONS
# ============================================================================

class TestWellnessOperations:
    """Test wellness logging and retrieval."""
    
    @pytest.mark.asyncio
    async def test_log_wellness_success(self, service, mock_repo, sample_wellness_data):
        """Should log wellness data and return success response."""
        mock_repo.create_wellness_log = AsyncMock(return_value="wellness-123")
        
        result = await service.log_wellness(sample_wellness_data, "test_player")
        
        assert result["success"] is True
        assert result["wellness_id"] == "wellness-123"
        assert result["message"] == "Wellness data logged for test_player"
        mock_repo.create_wellness_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_wellness_history_with_data(self, service, mock_repo):
        """Should return wellness history with averages."""
        mock_repo.find_wellness_logs_by_player = AsyncMock(return_value=[
            {"sleep_hours": 7, "soreness_1_5": 2, "mood_1_5": 4},
            {"sleep_hours": 8, "soreness_1_5": 3, "mood_1_5": 3}
        ])
        
        result = await service.get_wellness_history("test_player", days=7)
        
        assert result["player_name"] == "test_player"
        assert len(result["wellness_logs"]) == 2
        assert result["average_sleep"] == 7.5
        assert result["average_soreness"] == 2.5
        assert result["average_mood"] == 3.5
    
    @pytest.mark.asyncio
    async def test_get_wellness_history_no_data(self, service, mock_repo):
        """Should return empty message when no data."""
        mock_repo.find_wellness_logs_by_player = AsyncMock(return_value=[])
        
        result = await service.get_wellness_history("test_player", days=7)
        
        assert result["wellness_logs"] == []
        assert result["message"] == "No wellness data found"


# ============================================================================
# TEST: TESTING DATA OPERATIONS
# ============================================================================

class TestTestingDataOperations:
    """Test testing data logging and retrieval."""
    
    @pytest.mark.asyncio
    async def test_log_testing_data_success(self, service, mock_repo, mock_generator, sample_testing_data):
        """Should log testing data and return summary."""
        mock_repo.create_testing_data = AsyncMock(return_value="testing-123")
        mock_summary = MagicMock()
        mock_summary.dict.return_value = {"aerobic": "good", "speed": "excellent"}
        mock_generator.validate_testing_data.return_value = mock_summary
        
        result = await service.log_testing_data(sample_testing_data, "test_player")
        
        assert result["success"] is True
        assert result["testing_id"] == "testing-123"
        assert result["testing_summary"] == {"aerobic": "good", "speed": "excellent"}
        mock_generator.validate_testing_data.assert_called_once_with(sample_testing_data)
    
    @pytest.mark.asyncio
    async def test_get_latest_testing_data_found(self, service, mock_repo, mock_generator):
        """Should return testing data with summary when found."""
        mock_repo.find_latest_testing_data = AsyncMock(return_value={
            "yo_yo_level": 18.5,
            "sprint_10m": 1.75,
            "sprint_30m": 4.2,
            "cmj_height": 42.0,
            "rsa_mean": 7.2,
            "rsa_fatigue_index": 5.0,
            "agility_505": 2.3,
            "max_hr": 195,
            "resting_hr": 55,
            "hrv_rmssd": 65.0,
            "test_date": datetime.now(timezone.utc).isoformat()
        })
        mock_summary = MagicMock()
        mock_summary.dict.return_value = {"aerobic": "good"}
        mock_generator.validate_testing_data.return_value = mock_summary
        
        result = await service.get_latest_testing_data("test_player")
        
        assert result["player_name"] == "test_player"
        assert "testing_data" in result
        assert result["testing_summary"] == {"aerobic": "good"}
    
    @pytest.mark.asyncio
    async def test_get_latest_testing_data_not_found(self, service, mock_repo):
        """Should raise error when no testing data found."""
        mock_repo.find_latest_testing_data = AsyncMock(return_value=None)
        
        with pytest.raises(TestingDataNotFoundError) as exc_info:
            await service.get_latest_testing_data("test_player")
        
        assert "No testing data found for test_player" in str(exc_info.value)


# ============================================================================
# TEST: LOAD MONITORING OPERATIONS
# ============================================================================

class TestLoadMonitoringOperations:
    """Test load monitoring logging and retrieval."""
    
    @pytest.mark.asyncio
    async def test_log_load_data_success(self, service, mock_repo, mock_generator, sample_previous_load):
        """Should log load data and assess status."""
        mock_repo.create_load_log = AsyncMock(return_value="load-123")
        mock_status = MagicMock()
        mock_status.value = "optimal"
        mock_generator.assess_load_status.return_value = mock_status
        
        result = await service.log_load_data(sample_previous_load, "test_player")
        
        assert result["success"] is True
        assert result["load_id"] == "load-123"
        assert result["load_status"] == "optimal"
        assert result["warning"] is None
    
    @pytest.mark.asyncio
    async def test_log_load_data_overload_warning(self, service, mock_repo, mock_generator, sample_previous_load):
        """Should return warning when overload detected."""
        mock_repo.create_load_log = AsyncMock(return_value="load-123")
        mock_status = MagicMock()
        mock_status.value = "overload"
        mock_generator.assess_load_status.return_value = mock_status
        
        result = await service.log_load_data(sample_previous_load, "test_player")
        
        assert result["load_status"] == "overload"
        assert result["warning"] == "OVERLOAD - Consider recovery day"
    
    @pytest.mark.asyncio
    async def test_get_load_history_with_data(self, service, mock_repo):
        """Should return load history with aggregates."""
        mock_repo.find_load_logs_by_player = AsyncMock(return_value=[
            {"acwr": 1.0, "rpe_avg": 6.0, "total_distance_m": 8000},
            {"acwr": 1.2, "rpe_avg": 7.0, "total_distance_m": 9000}
        ])
        
        result = await service.get_load_history("test_player", days=7)
        
        assert result["player_name"] == "test_player"
        assert len(result["load_logs"]) == 2
        assert result["average_acwr"] == 1.1
        assert result["average_rpe"] == 6.5
        assert result["total_distance"] == 17000
    
    @pytest.mark.asyncio
    async def test_get_load_history_no_data(self, service, mock_repo):
        """Should return empty message when no data."""
        mock_repo.find_load_logs_by_player = AsyncMock(return_value=[])
        
        result = await service.get_load_history("test_player", days=7)
        
        assert result["load_logs"] == []
        assert result["message"] == "No load data found"


# ============================================================================
# TEST: RTP PROTOCOLS
# ============================================================================

class TestRTPProtocols:
    """Test Return-to-Play protocol operations."""
    
    def test_get_rtp_protocol_valid_stage(self, service):
        """Should return protocol for valid stage."""
        result = service.get_rtp_protocol("phase_1")
        
        assert result["stage"] == "phase_1"
        assert "protocol" in result
    
    def test_get_rtp_protocol_invalid_stage(self, service):
        """Should raise error for invalid stage."""
        with pytest.raises(InvalidRTPStageError) as exc_info:
            service.get_rtp_protocol("invalid_stage")
        
        assert "Invalid stage" in str(exc_info.value)
    
    def test_get_all_rtp_protocols(self, service):
        """Should return all protocols."""
        result = service.get_all_rtp_protocols()
        
        assert "protocols" in result
        assert "total_stages" in result
        assert result["total_stages"] > 0


# ============================================================================
# TEST: MATCH SCHEDULE OPERATIONS
# ============================================================================

class TestMatchScheduleOperations:
    """Test match schedule operations."""
    
    @pytest.mark.asyncio
    async def test_update_match_schedule_success(self, service, mock_repo, sample_match_schedule):
        """Should update match schedule."""
        mock_repo.upsert_match_schedule = AsyncMock()
        
        result = await service.update_match_schedule(sample_match_schedule, "test_player")
        
        assert result["success"] is True
        assert result["message"] == "Match schedule updated for test_player"
        assert result["days_to_match"] == 4
        mock_repo.upsert_match_schedule.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_match_schedule_found(self, service, mock_repo):
        """Should return schedule when found."""
        mock_repo.find_match_schedule = AsyncMock(return_value={
            "days_to_next_match": 3,
            "opponent_quality": "medium"
        })
        
        result = await service.get_match_schedule("test_player")
        
        assert result["player_name"] == "test_player"
        assert result["schedule"]["days_to_next_match"] == 3
    
    @pytest.mark.asyncio
    async def test_get_match_schedule_not_found(self, service, mock_repo):
        """Should raise error when not found."""
        mock_repo.find_match_schedule = AsyncMock(return_value=None)
        
        with pytest.raises(MatchScheduleNotFoundError) as exc_info:
            await service.get_match_schedule("test_player")
        
        assert "No match schedule found for test_player" in str(exc_info.value)


# ============================================================================
# TEST: TRAINING PLANS
# ============================================================================

class TestTrainingPlans:
    """Test training plan operations."""
    
    @pytest.mark.asyncio
    async def test_get_training_plans_with_data(self, service, mock_repo):
        """Should return training plans."""
        mock_repo.find_training_plans_by_player = AsyncMock(return_value=[
            {"id": "plan-1", "created_at": "2025-01-01"},
            {"id": "plan-2", "created_at": "2025-01-02"}
        ])
        
        result = await service.get_training_plans("test_player", limit=10)
        
        assert result["player_name"] == "test_player"
        assert result["count"] == 2
        assert len(result["plans"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_training_plans_no_data(self, service, mock_repo):
        """Should return empty message when no plans."""
        mock_repo.find_training_plans_by_player = AsyncMock(return_value=[])
        
        result = await service.get_training_plans("test_player", limit=10)
        
        assert result["plans"] == []
        assert result["message"] == "No training plans found"


# ============================================================================
# TEST: SERVICE SINGLETON
# ============================================================================

class TestServiceSingleton:
    """Test service singleton pattern."""
    
    def test_get_elite_training_service_returns_same_instance(self):
        """get_elite_training_service should return the same instance."""
        service1 = get_elite_training_service()
        service2 = get_elite_training_service()
        
        assert service1 is service2


# ============================================================================
# TEST: INTEGRATION (FastAPI TestClient)
# ============================================================================

class TestEliteTrainingEndpoints:
    """Integration tests using FastAPI TestClient."""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from routes.elite_training_routes import router
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_get_rtp_protocols_endpoint(self, client):
        """Test GET /elite-training/rtp-protocols returns expected shape."""
        response = client.get("/elite-training/rtp-protocols")
        
        assert response.status_code == 200
        data = response.json()
        assert "protocols" in data
        assert "total_stages" in data
        assert isinstance(data["protocols"], dict)
        assert isinstance(data["total_stages"], int)
    
    def test_get_rtp_protocol_valid_stage(self, client):
        """Test GET /elite-training/rtp-protocol/{stage} with valid stage."""
        response = client.get("/elite-training/rtp-protocol/phase_1")
        
        assert response.status_code == 200
        data = response.json()
        assert "stage" in data
        assert "protocol" in data
        assert data["stage"] == "phase_1"
    
    def test_get_rtp_protocol_invalid_stage(self, client):
        """Test GET /elite-training/rtp-protocol/{stage} with invalid stage returns 400."""
        response = client.get("/elite-training/rtp-protocol/invalid_stage")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid stage" in data["detail"]
    
    def test_get_wellness_history_endpoint_shape(self, client):
        """Test GET /elite-training/wellness/{player_name} returns expected shape."""
        with patch('services.elite_training_service.get_elite_training_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_wellness_history = AsyncMock(return_value={
                "player_name": "test_player",
                "wellness_logs": [],
                "message": "No wellness data found"
            })
            mock_get_service.return_value = mock_service
            
            response = client.get("/elite-training/wellness/test_player")
            
            assert response.status_code == 200
            data = response.json()
            assert "player_name" in data
            assert "wellness_logs" in data
    
    def test_get_load_history_endpoint_shape(self, client):
        """Test GET /elite-training/load-monitoring/{player_name} returns expected shape."""
        with patch('services.elite_training_service.get_elite_training_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_load_history = AsyncMock(return_value={
                "player_name": "test_player",
                "load_logs": [],
                "message": "No load data found"
            })
            mock_get_service.return_value = mock_service
            
            response = client.get("/elite-training/load-monitoring/test_player")
            
            assert response.status_code == 200
            data = response.json()
            assert "player_name" in data
            assert "load_logs" in data
    
    def test_get_training_plans_endpoint_shape(self, client):
        """Test GET /elite-training/training-plans/{player_name} returns expected shape."""
        with patch('services.elite_training_service.get_elite_training_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.get_training_plans = AsyncMock(return_value={
                "player_name": "test_player",
                "plans": [],
                "message": "No training plans found"
            })
            mock_get_service.return_value = mock_service
            
            response = client.get("/elite-training/training-plans/test_player")
            
            assert response.status_code == 200
            data = response.json()
            assert "player_name" in data
            assert "plans" in data


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
