"""Progress service for business logic."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from repositories.progress_repository import ProgressRepository
from models import (
    DailyProgress, DailyProgressCreate, WeeklyProgress, WeeklyProgressCreate,
    PerformanceMetric, ExerciseCompletion
)
import logging

logger = logging.getLogger(__name__)


class ProgressNotFoundError(Exception):
    """Raised when required progress data is not found."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProgressService:
    """Service for player progress tracking and performance metrics."""
    
    def __init__(self):
        self.repository = ProgressRepository()
    
    # =========================================================================
    # DAILY PROGRESS
    # =========================================================================
    
    async def log_daily_progress(
        self,
        progress_data: DailyProgressCreate
    ) -> DailyProgress:
        """Log daily training progress and exercise completions."""
        # Create exercise completions
        completed_exercises = []
        for completion_data in progress_data.completed_exercises:
            completion = ExerciseCompletion(**completion_data.dict())
            completed_exercises.append(completion)
        
        # Create daily progress entry
        daily_progress = DailyProgress(
            player_id=progress_data.player_id,
            routine_id=progress_data.routine_id,
            completed_exercises=completed_exercises,
            overall_rating=progress_data.overall_rating,
            energy_level=progress_data.energy_level,
            motivation_level=progress_data.motivation_level,
            daily_notes=progress_data.daily_notes,
            total_time_spent=progress_data.total_time_spent
        )
        
        # Save to database
        await self.repository.create_daily_progress(daily_progress.dict())
        
        # Update performance metrics based on completed exercises
        await self._update_performance_metrics(progress_data.player_id, completed_exercises)
        
        logger.info(f"Daily progress logged for player: {progress_data.player_id}")
        return daily_progress
    
    async def get_daily_progress(
        self,
        player_id: str,
        days: int = 30
    ) -> List[DailyProgress]:
        """Get daily progress history for a player."""
        entries = await self.repository.find_daily_progress_by_player(player_id, days)
        return [DailyProgress(**entry) for entry in entries]
    
    # =========================================================================
    # WEEKLY PROGRESS
    # =========================================================================
    
    async def log_weekly_progress(
        self,
        progress_data: WeeklyProgressCreate
    ) -> WeeklyProgress:
        """Log weekly training progress."""
        weekly_progress = WeeklyProgress(**progress_data.dict())
        await self.repository.create_weekly_progress(weekly_progress.dict())
        
        logger.info(f"Weekly progress logged for player: {progress_data.player_id}")
        return weekly_progress
    
    async def get_weekly_progress(
        self,
        player_id: str
    ) -> List[WeeklyProgress]:
        """Get weekly progress history for a player."""
        entries = await self.repository.find_weekly_progress_by_player(player_id)
        return [WeeklyProgress(**entry) for entry in entries]
    
    # =========================================================================
    # PERFORMANCE METRICS
    # =========================================================================
    
    async def get_performance_metrics(
        self,
        player_id: str
    ) -> Dict[str, Any]:
        """Get performance metrics and progress tracking."""
        # Get recent performance metrics
        metrics = await self.repository.find_metrics_by_player(player_id)
        
        # Get daily progress for visualization
        progress_entries = await self.repository.find_recent_daily_progress(player_id, limit=30)
        
        # Calculate improvement trends
        improvement_data = self._calculate_improvement_trends(metrics)
        
        # Get next assessment date
        next_assessment = await self._get_next_assessment_date(player_id)
        
        return {
            "metrics": [PerformanceMetric(**metric) for metric in metrics],
            "daily_progress": [DailyProgress(**entry) for entry in progress_entries],
            "improvement_trends": improvement_data,
            "next_assessment": next_assessment
        }
    
    # =========================================================================
    # PROGRESS SUMMARY
    # =========================================================================
    
    async def get_progress_summary(
        self,
        player_id: str
    ) -> Dict[str, Any]:
        """Get a comprehensive progress summary for a player."""
        # Get latest assessment for baseline
        assessment = await self.repository.find_latest_assessment(player_id)
        
        if not assessment:
            raise ProgressNotFoundError("No assessment found for player")
        
        # Get training completion stats (last 30 days)
        daily_sessions = await self.repository.count_daily_progress(player_id, days=30)
        
        # Get performance trends
        metrics = await self.repository.find_metrics_by_player(player_id, limit=100)
        trends = self._calculate_improvement_trends(metrics)
        
        # Calculate training consistency
        training_consistency = min(100, (daily_sessions / 30) * 100)
        
        return {
            "player_id": player_id,
            "assessment_date": assessment.get("created_at"),
            "overall_score": assessment.get("overall_score", 0),
            "performance_level": assessment.get("performance_level", "Developing"),
            "training_sessions_30_days": daily_sessions,
            "training_consistency_percentage": round(training_consistency, 1),
            "improvement_trends": trends,
            "next_assessment_date": await self._get_next_assessment_date(player_id)
        }
    
    # =========================================================================
    # HELPER METHODS (Private)
    # =========================================================================
    
    async def _update_performance_metrics(
        self,
        player_id: str,
        completed_exercises: List[ExerciseCompletion]
    ) -> None:
        """Update performance metrics based on completed exercises."""
        try:
            # Get current program to determine phase and week
            program = await self.repository.find_latest_program(player_id)
            
            if not program:
                return
            
            current_week = self._calculate_current_week(program)
            current_phase = self._calculate_current_phase(program)
            
            # Update metrics based on exercise performance
            for exercise in completed_exercises:
                if exercise.performance_rating and exercise.performance_rating >= 4:
                    # Good performance - create positive metric entry
                    metric = PerformanceMetric(
                        player_id=player_id,
                        metric_name=f"{exercise.exercise_id}_performance",
                        value=exercise.performance_rating,
                        phase_number=current_phase,
                        week_number=current_week
                    )
                    
                    await self.repository.create_performance_metric(metric.dict())
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    @staticmethod
    def _calculate_current_week(program: Dict[str, Any]) -> int:
        """Calculate current week in program."""
        start_date = program.get("program_start_date")
        if not start_date:
            return 1
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        current_date = datetime.now(timezone.utc)
        days_elapsed = (current_date - start_date).days
        return (days_elapsed // 7) + 1
    
    @staticmethod
    def _calculate_current_phase(program: Dict[str, Any]) -> int:
        """Calculate current phase in program."""
        current_week = ProgressService._calculate_current_week(program)
        week_count = 0
        
        macro_cycles = program.get("macro_cycles", [])
        for i, macro_cycle in enumerate(macro_cycles):
            week_count += macro_cycle.get("duration_weeks", 0)
            if current_week <= week_count:
                return i + 1
        
        return len(macro_cycles) if macro_cycles else 1
    
    @staticmethod
    def _calculate_improvement_trends(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate improvement trends from performance metrics."""
        trends = {}
        
        # Group metrics by type
        metric_groups: Dict[str, List[Dict[str, Any]]] = {}
        for metric in metrics:
            metric_type = metric.get("metric_name", "unknown")
            if metric_type not in metric_groups:
                metric_groups[metric_type] = []
            metric_groups[metric_type].append(metric)
        
        # Calculate trends for each metric type
        for metric_type, metric_list in metric_groups.items():
            if len(metric_list) >= 2:
                # Sort by date
                sorted_metrics = sorted(
                    metric_list,
                    key=lambda x: x.get("measurement_date", datetime.min)
                )
                first_value = sorted_metrics[0].get("value", 0)
                last_value = sorted_metrics[-1].get("value", 0)
                
                if first_value > 0:
                    improvement_percentage = ((last_value - first_value) / first_value) * 100
                    trends[metric_type] = {
                        "improvement_percentage": round(improvement_percentage, 2),
                        "trend_direction": "up" if improvement_percentage > 0 else "down",
                        "data_points": len(sorted_metrics)
                    }
        
        return trends
    
    async def _get_next_assessment_date(self, player_id: str) -> Optional[datetime]:
        """Get the next assessment date for a player."""
        try:
            program = await self.repository.find_latest_program(player_id)
            
            if program:
                next_date = program.get("next_assessment_date")
                if isinstance(next_date, str):
                    return datetime.fromisoformat(next_date.replace('Z', '+00:00'))
                return next_date
            
            # Default to 4 weeks from now
            return datetime.now(timezone.utc) + timedelta(weeks=4)
            
        except Exception as e:
            logger.error(f"Error getting next assessment date: {e}")
            return datetime.now(timezone.utc) + timedelta(weeks=4)


# Singleton instance for convenience
_progress_service: Optional[ProgressService] = None


def get_progress_service() -> ProgressService:
    """Get or create the progress service singleton."""
    global _progress_service
    if _progress_service is None:
        _progress_service = ProgressService()
    return _progress_service
