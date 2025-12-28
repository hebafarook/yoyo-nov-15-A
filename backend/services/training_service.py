"""
Training Service
================

Business logic for training program management.
Handles periodized programs, training programs, and adaptive exercises.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from repositories.training_repository import TrainingRepository
from models import (
    PeriodizedProgram, PeriodizedProgramCreate, TrainingProgram, TrainingProgramCreate,
    DailyRoutine, MicroCycle, MacroCycle, Exercise
)
from exercise_database import (
    PERIODIZATION_TEMPLATES, EXERCISE_DATABASE,
    generate_daily_routine, get_intensity_rating, get_focus_areas
)
from utils.llm_integration import generate_training_program, generate_adaptive_exercises
import logging

logger = logging.getLogger(__name__)


class AssessmentNotFoundError(Exception):
    """Raised when no assessment is found for a player."""
    def __init__(self, message: str = "No assessment found for player"):
        self.message = message
        super().__init__(message)


class ProgramNotFoundError(Exception):
    """Raised when no program is found."""
    def __init__(self, message: str = "Program not found"):
        self.message = message
        super().__init__(message)


class TrainingService:
    """Service for training program management."""
    
    def __init__(self):
        self.repository = TrainingRepository()
    
    # =========================================================================
    # WEAKNESS ANALYSIS
    # =========================================================================
    
    def analyze_weaknesses(self, assessment: Dict[str, Any]) -> List[str]:
        """Analyze assessment to identify player weaknesses."""
        weaknesses = []
        
        if assessment.get("sprint_30m", 10) > 4.5:
            weaknesses.append("speed")
        if assessment.get("ball_control", 3) < 4:
            weaknesses.append("ball_control")
        if assessment.get("passing_accuracy", 80) < 75:
            weaknesses.append("passing")
        if assessment.get("game_intelligence", 3) < 4:
            weaknesses.append("tactical")
        
        return weaknesses
    
    def analyze_weaknesses_for_exercises(self, assessment: Dict[str, Any]) -> List[str]:
        """Analyze assessment for adaptive exercise generation."""
        weaknesses = []
        
        if assessment.get("sprint_30m", 10) > 4.5:
            weaknesses.append("speed")
        if assessment.get("ball_control", 3) < 4:
            weaknesses.append("technical")
        if assessment.get("game_intelligence", 3) < 4:
            weaknesses.append("tactical")
        
        return weaknesses
    
    # =========================================================================
    # PERIODIZED PROGRAMS
    # =========================================================================
    
    async def create_periodized_program(
        self,
        program_data: PeriodizedProgramCreate
    ) -> PeriodizedProgram:
        """Create a comprehensive periodized training program."""
        # Get latest assessment for weakness analysis
        assessment = await self.repository.find_latest_assessment(program_data.player_id)
        
        weaknesses = []
        if assessment:
            weaknesses = self.analyze_weaknesses(assessment)
        
        # Create macro cycles
        macro_cycles = []
        current_date = datetime.now(timezone.utc)
        
        phases = ["foundation_building", "development_phase", "peak_performance"]
        total_weeks = 0
        
        for i, phase in enumerate(phases):
            template = PERIODIZATION_TEMPLATES[phase]
            phase_weeks = template["duration_weeks"]
            
            # Create micro cycles (weeks) for this phase
            micro_cycles = []
            for week in range(1, phase_weeks + 1):
                # Create daily routines for this week
                daily_routines = []
                for day in range(1, 6):  # 5 training days per week
                    routine_data = generate_daily_routine(phase, week, day, weaknesses)
                    
                    # Convert exercise data to Exercise objects
                    exercises = []
                    for ex_data in routine_data["exercises"]:
                        exercise = Exercise(
                            name=ex_data["name"],
                            category=ex_data["category"],
                            description=ex_data["description"],
                            instructions=ex_data["instructions"],
                            purpose=ex_data["purpose"],
                            expected_outcome=ex_data["expected_outcome"],
                            duration=ex_data["duration"],
                            intensity=ex_data["intensity"],
                            equipment_needed=ex_data["equipment_needed"],
                            progression=ex_data.get("progression")
                        )
                        exercises.append(exercise)
                    
                    daily_routine = DailyRoutine(
                        day_number=day,
                        phase=phase,
                        exercises=exercises,
                        total_duration=routine_data["total_duration"],
                        intensity_rating=routine_data["intensity_rating"],
                        focus_areas=routine_data["focus_areas"],
                        objectives=routine_data["objectives"]
                    )
                    daily_routines.append(daily_routine)
                
                micro_cycle = MicroCycle(
                    name=f"Week {total_weeks + week}: {template['phase_name']}",
                    cycle_number=total_weeks + week,
                    phase=phase,
                    daily_routines=daily_routines,
                    objectives=template["objectives"],
                    assessment_metrics=["sprint_30m", "ball_control", "passing_accuracy", "game_intelligence"]
                )
                micro_cycles.append(micro_cycle)
            
            # Create macro cycle
            start_date = current_date + timedelta(weeks=total_weeks)
            end_date = start_date + timedelta(weeks=phase_weeks)
            assessment_date = end_date + timedelta(days=1)
            
            macro_cycle = MacroCycle(
                name=f"Phase {i+1}: {template['phase_name']}",
                phase_number=i+1,
                duration_weeks=phase_weeks,
                micro_cycles=micro_cycles,
                start_date=start_date,
                end_date=end_date,
                assessment_date=assessment_date,
                objectives=template["objectives"],
                success_criteria=[
                    f"Improve weak areas by 15%",
                    f"Complete 90% of scheduled training",
                    f"Achieve {template['intensity_progression'][-1]}% intensity capacity"
                ]
            )
            macro_cycles.append(macro_cycle)
            total_weeks += phase_weeks
        
        # Create the full periodized program
        next_assessment = current_date + timedelta(weeks=program_data.assessment_interval_weeks)
        
        periodized_program = PeriodizedProgram(
            player_id=program_data.player_id,
            program_name=program_data.program_name,
            total_duration_weeks=total_weeks,
            macro_cycles=macro_cycles,
            next_assessment_date=next_assessment,
            program_objectives=program_data.program_objectives
        )
        
        # Save to database
        await self.repository.create_periodized_program(periodized_program.dict())
        
        logger.info(f"Periodized program created for player: {program_data.player_id}")
        return periodized_program
    
    async def get_player_periodized_program(
        self,
        player_id: str
    ) -> Optional[PeriodizedProgram]:
        """Get the current periodized program for a player."""
        program = await self.repository.find_periodized_program_by_player(player_id)
        
        if program:
            return PeriodizedProgram(**program)
        return None
    
    async def get_current_routine(self, player_id: str) -> Dict[str, Any]:
        """Get today's training routine for a player."""
        # Get player's current program
        program = await self.repository.find_periodized_program_by_player(player_id)
        
        if not program:
            return {"message": "No training program found", "routine": None}
        
        # Calculate current position in program
        start_date = program.get("program_start_date")
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        current_date = datetime.now(timezone.utc)
        days_elapsed = (current_date - start_date).days
        
        current_week = (days_elapsed // 7) + 1
        current_day = (days_elapsed % 7) + 1
        
        # Find current routine
        current_routine = None
        current_phase = None
        
        week_count = 0
        for macro_cycle in program.get("macro_cycles", []):
            for micro_cycle in macro_cycle.get("micro_cycles", []):
                week_count += 1
                if week_count == current_week:
                    current_phase = macro_cycle.get("phase_number")
                    daily_routines = micro_cycle.get("daily_routines", [])
                    if current_day <= len(daily_routines) and current_day <= 5:  # Only weekdays
                        current_routine = daily_routines[current_day - 1]
                    break
            if current_routine:
                break
        
        if not current_routine:
            return {"message": "Rest day or program completed", "routine": None}
        
        return {
            "routine": current_routine,
            "current_week": current_week,
            "current_day": current_day,
            "current_phase": current_phase,
            "program_name": program.get("program_name")
        }
    
    # =========================================================================
    # TRAINING PROGRAMS (Legacy)
    # =========================================================================
    
    async def create_training_program(
        self,
        program_data: TrainingProgramCreate
    ) -> TrainingProgram:
        """Create AI-generated training program (legacy endpoint)."""
        # Get player's latest assessment for context
        assessment = await self.repository.find_latest_assessment(program_data.player_id)
        
        if not assessment:
            raise AssessmentNotFoundError(
                "No assessment found for player. Please complete assessment first."
            )
        
        # Generate AI training program
        program_content = await generate_training_program(assessment, week_number=1)
        
        # Create training program object
        training_program = TrainingProgram(
            player_id=program_data.player_id,
            program_type=program_data.program_type,
            program_content=program_content,
            weekly_schedule={},
            milestones=[],
            is_group=program_data.is_group or False,
            spotify_playlist=program_data.spotify_playlist
        )
        
        # Save to database
        await self.repository.create_training_program(training_program.dict())
        
        logger.info(f"Training program created for player: {program_data.player_id}")
        return training_program
    
    async def get_player_training_programs(
        self,
        player_id: str
    ) -> List[TrainingProgram]:
        """Get all training programs for a player."""
        programs = await self.repository.find_training_programs_by_player(player_id)
        return [TrainingProgram(**program) for program in programs]
    
    # =========================================================================
    # ADAPTIVE EXERCISES
    # =========================================================================
    
    async def get_adaptive_exercises(
        self,
        player_id: str,
        phase: str = "development",
        week_number: int = 1
    ) -> Dict[str, Any]:
        """Generate adaptive exercises based on player weaknesses."""
        # Get player's latest assessment
        assessment = await self.repository.find_latest_assessment(player_id)
        
        if not assessment:
            raise AssessmentNotFoundError("No assessment found for player")
        
        # Identify weaknesses (using exercise-specific analysis)
        weaknesses = self.analyze_weaknesses_for_exercises(assessment)
        
        # Generate adaptive exercises
        exercises = await generate_adaptive_exercises(weaknesses, phase, week_number)
        
        return {
            "player_id": player_id,
            "phase": phase,
            "week_number": week_number,
            "identified_weaknesses": weaknesses,
            "adaptive_exercises": exercises
        }


# Singleton instance
_training_service: Optional[TrainingService] = None


def get_training_service() -> TrainingService:
    """Get or create the training service singleton."""
    global _training_service
    if _training_service is None:
        _training_service = TrainingService()
    return _training_service
