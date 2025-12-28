"""
Models Package - Re-exports from root models.py
"""

# Import specific models needed by routes
# Using relative import to avoid circular issues
try:
    import importlib
    _models = importlib.import_module('models')
    
    # Export all needed classes
    User = _models.User
    UserCreate = _models.UserCreate
    UserLogin = _models.UserLogin
    PlayerAssessment = _models.PlayerAssessment
    AssessmentCreate = _models.AssessmentCreate
    VO2MaxBenchmark = _models.VO2MaxBenchmark
    VO2MaxBenchmarkCreate = _models.VO2MaxBenchmarkCreate
    PeriodizedProgram = _models.PeriodizedProgram
    DailyProgress = _models.DailyProgress
    NotificationPreferences = _models.NotificationPreferences
    SavedReport = _models.SavedReport
    SavedReportCreate = _models.SavedReportCreate
    TrainingProgram = _models.TrainingProgram
    Exercise = _models.Exercise
    DailyRoutine = _models.DailyRoutine
    ExerciseCompletion = _models.ExerciseCompletion
    MicroCycle = _models.MicroCycle
    MacroCycle = _models.MacroCycle
    PerformanceMetric = _models.PerformanceMetric
    WeeklyProgress = _models.WeeklyProgress
    RetestSchedule = _models.RetestSchedule
    UserProfile = _models.UserProfile
    CheckInOut = _models.CheckInOut
    AssessmentBenchmark = _models.AssessmentBenchmark
    
except Exception as e:
    # If import fails, don't break everything
    import logging
    logging.warning(f"Could not import from root models: {e}")
