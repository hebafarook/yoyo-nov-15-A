"""
Tests for VO2 Service
=====================

Unit tests for VO2 Max calculation and benchmark logic.
Tests the service layer without database dependencies.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.vo2_service import VO2Service, VO2ValidationError, get_vo2_service


# ============================================================================
# TEST: VO2 MAX CALCULATION
# ============================================================================

class TestVO2MaxCalculation:
    """Test VO2 Max calculation using ACSM formulas."""
    
    @pytest.fixture
    def service(self):
        """Create a service instance."""
        return VO2Service()
    
    def test_calculate_male_vo2_max(self, service):
        """Test VO2 Max calculation for male."""
        result = service.calculate_vo2_max(
            age=25,
            gender="male",
            resting_heart_rate=60,
            max_heart_rate=180
        )
        
        assert "vo2_max" in result
        assert "fitness_level" in result
        assert result["inputs"]["gender"] == "male"
        assert result["formula_used"] == "ACSM"
        # Verify formula: (0.21 * 180) - (0.84 * 25) - (0.25 * 60) + 84 = 37.8 + (-21) + (-15) + 84 = 50.8
        expected = round((0.21 * 180) - (0.84 * 25) - (0.25 * 60) + 84, 1)
        assert result["vo2_max"] == expected
    
    def test_calculate_female_vo2_max(self, service):
        """Test VO2 Max calculation for female."""
        result = service.calculate_vo2_max(
            age=25,
            gender="female",
            resting_heart_rate=65,
            max_heart_rate=175
        )
        
        assert "vo2_max" in result
        assert result["inputs"]["gender"] == "female"
        # Verify formula: (0.12 * 175) - (0.64 * 25) - (0.35 * 65) + 65.4
        expected = round((0.12 * 175) - (0.64 * 25) - (0.35 * 65) + 65.4, 1)
        assert result["vo2_max"] == expected
    
    def test_gender_shorthand_m(self, service):
        """Test 'm' shorthand for male."""
        result = service.calculate_vo2_max(
            age=30,
            gender="m",
            resting_heart_rate=60,
            max_heart_rate=180
        )
        assert result["inputs"]["gender"] == "m"
    
    def test_gender_shorthand_f(self, service):
        """Test 'f' shorthand for female."""
        result = service.calculate_vo2_max(
            age=30,
            gender="f",
            resting_heart_rate=60,
            max_heart_rate=175
        )
        assert result["inputs"]["gender"] == "f"
    
    def test_result_has_source(self, service):
        """Test that result includes source URL."""
        result = service.calculate_vo2_max(
            age=25,
            gender="male",
            resting_heart_rate=60,
            max_heart_rate=180
        )
        assert "source" in result
        assert "sporthypnosis" in result["source"]


# ============================================================================
# TEST: INPUT VALIDATION
# ============================================================================

class TestInputValidation:
    """Test input validation for VO2 Max calculation."""
    
    @pytest.fixture
    def service(self):
        return VO2Service()
    
    def test_age_too_low(self, service):
        """Test validation for age below minimum."""
        with pytest.raises(VO2ValidationError) as exc_info:
            service.calculate_vo2_max(
                age=5,  # Too low
                gender="male",
                resting_heart_rate=60,
                max_heart_rate=180
            )
        assert "Age must be between 10 and 80" in str(exc_info.value)
    
    def test_age_too_high(self, service):
        """Test validation for age above maximum."""
        with pytest.raises(VO2ValidationError) as exc_info:
            service.calculate_vo2_max(
                age=85,  # Too high
                gender="male",
                resting_heart_rate=60,
                max_heart_rate=180
            )
        assert "Age must be between 10 and 80" in str(exc_info.value)
    
    def test_invalid_gender(self, service):
        """Test validation for invalid gender."""
        with pytest.raises(VO2ValidationError) as exc_info:
            service.calculate_vo2_max(
                age=25,
                gender="unknown",  # Invalid
                resting_heart_rate=60,
                max_heart_rate=180
            )
        assert "Gender must be" in str(exc_info.value)
    
    def test_resting_hr_too_low(self, service):
        """Test validation for resting heart rate below minimum."""
        with pytest.raises(VO2ValidationError) as exc_info:
            service.calculate_vo2_max(
                age=25,
                gender="male",
                resting_heart_rate=25,  # Too low
                max_heart_rate=180
            )
        assert "Resting heart rate must be between 30 and 120" in str(exc_info.value)
    
    def test_resting_hr_too_high(self, service):
        """Test validation for resting heart rate above maximum."""
        with pytest.raises(VO2ValidationError) as exc_info:
            service.calculate_vo2_max(
                age=25,
                gender="male",
                resting_heart_rate=130,  # Too high
                max_heart_rate=180
            )
        assert "Resting heart rate must be between 30 and 120" in str(exc_info.value)
    
    def test_max_hr_too_low(self, service):
        """Test validation for max heart rate below minimum."""
        with pytest.raises(VO2ValidationError) as exc_info:
            service.calculate_vo2_max(
                age=25,
                gender="male",
                resting_heart_rate=60,
                max_heart_rate=100  # Too low
            )
        assert "Max heart rate must be between 120 and 220" in str(exc_info.value)
    
    def test_max_hr_too_high(self, service):
        """Test validation for max heart rate above maximum."""
        with pytest.raises(VO2ValidationError) as exc_info:
            service.calculate_vo2_max(
                age=25,
                gender="male",
                resting_heart_rate=60,
                max_heart_rate=230  # Too high
            )
        assert "Max heart rate must be between 120 and 220" in str(exc_info.value)
    
    def test_boundary_values_valid(self, service):
        """Test that boundary values are accepted."""
        # Test minimum boundaries
        result = service.calculate_vo2_max(
            age=10,
            gender="male",
            resting_heart_rate=30,
            max_heart_rate=120
        )
        assert "vo2_max" in result
        
        # Test maximum boundaries
        result = service.calculate_vo2_max(
            age=80,
            gender="female",
            resting_heart_rate=120,
            max_heart_rate=220
        )
        assert "vo2_max" in result


# ============================================================================
# TEST: FITNESS LEVEL CLASSIFICATION
# ============================================================================

class TestFitnessLevel:
    """Test fitness level classification."""
    
    @pytest.fixture
    def service(self):
        return VO2Service()
    
    def test_male_young_excellent(self, service):
        """Test excellent fitness for young male."""
        level = service.get_fitness_level(vo2_max=60, age=18, gender="male")
        assert level == "Excellent"
    
    def test_male_young_good(self, service):
        """Test good fitness for young male."""
        level = service.get_fitness_level(vo2_max=50, age=18, gender="male")
        assert level == "Good"
    
    def test_male_young_average(self, service):
        """Test average fitness for young male."""
        level = service.get_fitness_level(vo2_max=40, age=18, gender="male")
        assert level == "Average"
    
    def test_male_young_below_average(self, service):
        """Test below average fitness for young male."""
        level = service.get_fitness_level(vo2_max=30, age=18, gender="male")
        assert level == "Below Average"
    
    def test_female_young_excellent(self, service):
        """Test excellent fitness for young female."""
        level = service.get_fitness_level(vo2_max=50, age=18, gender="female")
        assert level == "Excellent"
    
    def test_male_40_plus(self, service):
        """Test fitness for male 40+."""
        level = service.get_fitness_level(vo2_max=45, age=45, gender="male")
        assert level == "Excellent"
        
        level = service.get_fitness_level(vo2_max=36, age=45, gender="male")
        assert level == "Good"
    
    def test_female_40_plus(self, service):
        """Test fitness for female 40+."""
        level = service.get_fitness_level(vo2_max=37, age=45, gender="female")
        assert level == "Excellent"


# ============================================================================
# TEST: BENCHMARK CRUD (Mocked Repository)
# ============================================================================

class TestBenchmarkCRUD:
    """Test benchmark CRUD operations with mocked repository."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create a mocked repository."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create service with mocked repository."""
        service = VO2Service()
        service.repository = mock_repo
        return service
    
    @pytest.mark.asyncio
    async def test_create_benchmark(self, service, mock_repo):
        """Test creating a benchmark."""
        from models import VO2MaxBenchmarkCreate
        
        mock_repo.create_benchmark = AsyncMock(return_value={
            "id": "test-id",
            "player_id": "player-123",
            "vo2_max": 45.5
        })
        
        benchmark_data = MagicMock(spec=VO2MaxBenchmarkCreate)
        benchmark_data.dict.return_value = {
            "player_id": "player-123",
            "vo2_max": 45.5
        }
        benchmark_data.player_id = "player-123"
        
        result = await service.create_benchmark(benchmark_data)
        
        mock_repo.create_benchmark.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_benchmarks_by_player(self, service, mock_repo):
        """Test getting benchmarks for a player."""
        mock_repo.find_by_player_id = AsyncMock(return_value=[
            {"id": "b1", "player_id": "p1", "vo2_max": 45.0},
            {"id": "b2", "player_id": "p1", "vo2_max": 46.0}
        ])
        
        results = await service.get_benchmarks_by_player("p1")
        
        mock_repo.find_by_player_id.assert_called_once_with("p1")
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_get_latest_benchmark_found(self, service, mock_repo):
        """Test getting latest benchmark when it exists."""
        mock_repo.find_latest_by_player_id = AsyncMock(return_value={
            "id": "b1", "player_id": "p1", "vo2_max": 45.0
        })
        
        result = await service.get_latest_benchmark("p1")
        
        assert result is not None
        mock_repo.find_latest_by_player_id.assert_called_once_with("p1")
    
    @pytest.mark.asyncio
    async def test_get_latest_benchmark_not_found(self, service, mock_repo):
        """Test getting latest benchmark when none exists."""
        mock_repo.find_latest_by_player_id = AsyncMock(return_value=None)
        
        result = await service.get_latest_benchmark("p1")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_benchmark_success(self, service, mock_repo):
        """Test successful benchmark deletion."""
        mock_repo.delete_by_id = AsyncMock(return_value=True)
        
        result = await service.delete_benchmark("b1")
        
        assert result is True
        mock_repo.delete_by_id.assert_called_once_with("b1")
    
    @pytest.mark.asyncio
    async def test_delete_benchmark_not_found(self, service, mock_repo):
        """Test deletion when benchmark not found."""
        mock_repo.delete_by_id = AsyncMock(return_value=False)
        
        result = await service.delete_benchmark("nonexistent")
        
        assert result is False


# ============================================================================
# TEST: SERVICE SINGLETON
# ============================================================================

class TestServiceSingleton:
    """Test service singleton pattern."""
    
    def test_get_vo2_service_returns_same_instance(self):
        """get_vo2_service should return the same instance."""
        service1 = get_vo2_service()
        service2 = get_vo2_service()
        
        assert service1 is service2


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
