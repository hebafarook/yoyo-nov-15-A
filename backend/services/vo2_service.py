"""VO2 Max service for business logic."""

from typing import Optional, List, Dict, Any
from repositories.vo2_repository import VO2Repository
from models import VO2MaxBenchmark, VO2MaxBenchmarkCreate
import logging

logger = logging.getLogger(__name__)


class VO2ValidationError(Exception):
    """Custom exception for VO2 validation errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class VO2Service:
    """Service for VO2 Max calculations and benchmark management."""
    
    def __init__(self):
        self.repository = VO2Repository()
    
    # =========================================================================
    # BENCHMARK CRUD OPERATIONS
    # =========================================================================
    
    async def create_benchmark(
        self, 
        benchmark_data: VO2MaxBenchmarkCreate
    ) -> VO2MaxBenchmark:
        """Create a new VO2 benchmark."""
        benchmark_obj = VO2MaxBenchmark(**benchmark_data.dict())
        await self.repository.create_benchmark(benchmark_obj.dict())
        logger.info(f"VO2 Max benchmark saved for player: {benchmark_data.player_id}")
        return benchmark_obj
    
    async def get_benchmarks_by_player(
        self, 
        player_id: str
    ) -> List[VO2MaxBenchmark]:
        """Get all VO2 benchmarks for a player."""
        benchmarks = await self.repository.find_by_player_id(player_id)
        return [VO2MaxBenchmark(**b) for b in benchmarks]
    
    async def get_latest_benchmark(
        self, 
        player_id: str
    ) -> Optional[VO2MaxBenchmark]:
        """Get the latest VO2 benchmark for a player."""
        benchmark = await self.repository.find_latest_by_player_id(player_id)
        if benchmark:
            return VO2MaxBenchmark(**benchmark)
        return None
    
    async def delete_benchmark(self, benchmark_id: str) -> bool:
        """Delete a benchmark. Returns True if found and deleted."""
        return await self.repository.delete_by_id(benchmark_id)
    
    # =========================================================================
    # VO2 MAX CALCULATION (ACSM FORMULAS)
    # =========================================================================
    
    def validate_calculation_inputs(
        self,
        age: int,
        gender: str,
        resting_heart_rate: float,
        max_heart_rate: float
    ) -> None:
        """
        Validate inputs for VO2 Max calculation.
        Raises VO2ValidationError if any input is invalid.
        """
        if age < 10 or age > 80:
            raise VO2ValidationError("Age must be between 10 and 80 years")
        
        if gender.lower() not in ['male', 'female', 'm', 'f']:
            raise VO2ValidationError("Gender must be 'male' or 'female'")
        
        if resting_heart_rate < 30 or resting_heart_rate > 120:
            raise VO2ValidationError("Resting heart rate must be between 30 and 120 bpm")
        
        if max_heart_rate < 120 or max_heart_rate > 220:
            raise VO2ValidationError("Max heart rate must be between 120 and 220 bpm")
    
    def calculate_vo2_max(
        self,
        age: int,
        gender: str,
        resting_heart_rate: float,
        max_heart_rate: float
    ) -> Dict[str, Any]:
        """
        Calculate VO2 Max using ACSM formulas.
        
        Args:
            age: Age in years (10-80)
            gender: 'male'/'m' or 'female'/'f'
            resting_heart_rate: Resting heart rate in bpm (30-120)
            max_heart_rate: Maximum heart rate in bpm (120-220)
        
        Returns:
            Dict with vo2_max, fitness_level, inputs, formula_used, source
        
        Raises:
            VO2ValidationError: If any input is invalid
        """
        # Validate inputs
        self.validate_calculation_inputs(age, gender, resting_heart_rate, max_heart_rate)
        
        normalized_gender = gender.lower()
        
        # ACSM Formulas
        if normalized_gender in ['male', 'm']:
            # For males: VO2 Max = (0.21 * Max Heart Rate) – (0.84 * Age) – (0.25 * Resting Heart Rate) + 84
            vo2_max = (0.21 * max_heart_rate) - (0.84 * age) - (0.25 * resting_heart_rate) + 84
        else:
            # For females: VO2 Max = (0.12 * Max Heart Rate) – (0.64 * Age) – (0.35 * Resting Heart Rate) + 65.4
            vo2_max = (0.12 * max_heart_rate) - (0.64 * age) - (0.35 * resting_heart_rate) + 65.4
        
        # Round to 1 decimal place
        vo2_max = round(vo2_max, 1)
        
        # Determine fitness level
        fitness_level = self.get_fitness_level(vo2_max, age, normalized_gender)
        
        return {
            "vo2_max": vo2_max,
            "fitness_level": fitness_level,
            "inputs": {
                "age": age,
                "gender": normalized_gender,
                "resting_heart_rate": resting_heart_rate,
                "max_heart_rate": max_heart_rate
            },
            "formula_used": "ACSM",
            "source": "https://sporthypnosis.net/elementor-1032/"
        }
    
    @staticmethod
    def get_fitness_level(vo2_max: float, age: int, gender: str) -> str:
        """Determine fitness level based on VO2 Max, age, and gender."""
        if gender in ['male', 'm']:
            if age <= 19:
                if vo2_max >= 56: return 'Excellent'
                if vo2_max >= 47: return 'Good'
                if vo2_max >= 37: return 'Average'
                return 'Below Average'
            elif age <= 29:
                if vo2_max >= 52: return 'Excellent'
                if vo2_max >= 43: return 'Good'
                if vo2_max >= 33: return 'Average'
                return 'Below Average'
            elif age <= 39:
                if vo2_max >= 48: return 'Excellent'
                if vo2_max >= 39: return 'Good'
                if vo2_max >= 29: return 'Average'
                return 'Below Average'
            else:  # 40+
                if vo2_max >= 44: return 'Excellent'
                if vo2_max >= 35: return 'Good'
                if vo2_max >= 25: return 'Average'
                return 'Below Average'
        else:  # female
            if age <= 19:
                if vo2_max >= 48: return 'Excellent'
                if vo2_max >= 39: return 'Good'
                if vo2_max >= 29: return 'Average'
                return 'Below Average'
            elif age <= 29:
                if vo2_max >= 44: return 'Excellent'
                if vo2_max >= 35: return 'Good'
                if vo2_max >= 25: return 'Average'
                return 'Below Average'
            elif age <= 39:
                if vo2_max >= 40: return 'Excellent'
                if vo2_max >= 31: return 'Good'
                if vo2_max >= 21: return 'Average'
                return 'Below Average'
            else:  # 40+
                if vo2_max >= 36: return 'Excellent'
                if vo2_max >= 27: return 'Good'
                if vo2_max >= 17: return 'Average'
                return 'Below Average'


# Singleton instance for convenience
_vo2_service: Optional[VO2Service] = None


def get_vo2_service() -> VO2Service:
    """Get or create the VO2 service singleton."""
    global _vo2_service
    if _vo2_service is None:
        _vo2_service = VO2Service()
    return _vo2_service
