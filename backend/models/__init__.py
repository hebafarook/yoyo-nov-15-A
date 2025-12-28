"""
Models Package Re-exports
=========================

Re-exports all models from the root models.py file to support
both `from models import X` and `from models.X import Y` patterns.
"""

# Re-export everything from the root models.py
import sys
import os

# Get the parent directory (backend)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import from models.py (the root file)
sys.path.insert(0, backend_dir)

from models import (
    PlayerAssessment,
    AssessmentCreate,
    VO2MaxBenchmark,
    VO2MaxBenchmarkCreate,
    Exercise,
    DailyRoutine,
    ExerciseCompletion,
    MicroCycle,
    MacroCycle,
    PeriodizedProgram,
    DailyProgress,
    PerformanceMetric,
    WeeklyProgress,
    TrainingProgram,
    RetestSchedule,
    PeriodizedProgramCreate,
    ExerciseCompletionCreate,
    DailyProgressCreate,
    User,
    UserCreate,
    UserLogin,
    SavedReport,
    SavedReportCreate,
    AssessmentBenchmark,
    AssessmentBenchmarkCreate,
    UserProfile,
    NotificationPreferences,
    CheckInOut,
    TrainingProgramCreate,
    WeeklyProgressCreate
)

__all__ = [
    'PlayerAssessment',
    'AssessmentCreate',
    'VO2MaxBenchmark',
    'VO2MaxBenchmarkCreate',
    'Exercise',
    'DailyRoutine',
    'ExerciseCompletion',
    'MicroCycle',
    'MacroCycle',
    'PeriodizedProgram',
    'DailyProgress',
    'PerformanceMetric',
    'WeeklyProgress',
    'TrainingProgram',
    'RetestSchedule',
    'PeriodizedProgramCreate',
    'ExerciseCompletionCreate',
    'DailyProgressCreate',
    'User',
    'UserCreate',
    'UserLogin',
    'SavedReport',
    'SavedReportCreate',
    'AssessmentBenchmark',
    'AssessmentBenchmarkCreate',
    'UserProfile',
    'NotificationPreferences',
    'CheckInOut',
    'TrainingProgramCreate',
    'WeeklyProgressCreate'
]
