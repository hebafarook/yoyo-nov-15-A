"""
Elite Soccer Training & Assessment System
FIFA & Manchester United Edition

Dynamic elite soccer training generator that uses testing data, wellness, and match schedule
to create daily and weekly plans based on FIFA's Four-Corner Model and Manchester United-style
tactical periodisation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from enum import Enum

# ==================== ENUMS ====================

class PlayerLevel(str, Enum):
    ACADEMY = "academy"
    YOUTH = "youth"
    RESERVE = "reserve"
    FIRST_TEAM = "first_team"
    ELITE = "elite"

class InjuryStatus(str, Enum):
    FIT = "fit"
    MINOR_KNOCK = "minor_knock"
    RECOVERING = "recovering"
    INJURED = "injured"
    RETURN_TO_PLAY = "return_to_play"

class LoadStatus(str, Enum):
    UNDERLOAD = "underload"
    OPTIMAL = "optimal"
    OVERLOAD = "overload"

class TacticalDay(str, Enum):
    HIGH_INTENSITY_TRANSITION = "high_intensity_transition"
    STRENGTH_INTEGRATION = "strength_integration"
    TACTICAL_POSITIONAL = "tactical_positional"
    SPEED_PRECISION = "speed_precision"
    ACTIVATION = "activation"
    MATCH_OR_RECOVERY = "match_or_recovery"

class TrainingPhase(str, Enum):
    FOUNDATION = "foundation"
    DEVELOPMENT = "development"
    COMPETITION = "competition"

class RTPStage(str, Enum):
    STAGE_1 = "stage_1"  # pain-free ROM, isometrics, bike
    STAGE_2 = "stage_2"  # linear run progressions, submax COD
    STAGE_3 = "stage_3"  # position-specific drills at 70-80% HSR
    STAGE_4 = "stage_4"  # full team with constraints
    STAGE_5 = "stage_5"  # match return with load monitoring

# ==================== INPUT MODELS ====================

class PlayerProfile(BaseModel):
    name: str
    age: int
    position: str
    level: PlayerLevel
    injury_status: InjuryStatus = InjuryStatus.FIT

class TestingData(BaseModel):
    sprint_10m: Optional[float] = None  # seconds
    sprint_30m: Optional[float] = None  # seconds
    yoyo_ir2: Optional[int] = None      # meters
    cmj: Optional[float] = None         # cm
    test_505: Optional[float] = None    # seconds
    squat_1rm: Optional[float] = None   # kg
    nordic_strength: Optional[float] = None  # kg
    test_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Wellness(BaseModel):
    sleep_hours: float
    soreness_1_5: int = Field(ge=1, le=5)  # 1=very sore, 5=not sore
    mood_1_5: int = Field(ge=1, le=5)      # 1=poor mood, 5=excellent
    stress_1_5: int = Field(ge=1, le=5)    # 1=very stressed, 5=not stressed
    hrv_score: Optional[float] = None       # ms (or normalized)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MatchSchedule(BaseModel):
    days_to_next_match: int
    matches_this_week: int
    opponent: Optional[str] = None
    match_importance: Optional[int] = Field(default=3, ge=1, le=5)  # 1=low, 5=crucial

class TacticalFocus(BaseModel):
    possession: int = Field(default=3, ge=1, le=5)
    transition: int = Field(default=3, ge=1, le=5)
    pressing: int = Field(default=3, ge=1, le=5)
    buildup: int = Field(default=3, ge=1, le=5)
    set_pieces: int = Field(default=3, ge=1, le=5)

class PreviousLoad(BaseModel):
    acwr: float  # Acute:Chronic Workload Ratio
    rpe_avg: float  # Rating of Perceived Exertion (1-10)
    total_distance_m: float
    sprint_count: int
    hsr_m: float  # High-Speed Running meters
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExistingProgram(BaseModel):
    session_library_ids: List[str] = []
    club_periodisation_id: Optional[str] = None
    banned_exercises: List[str] = []
    mandatory_drills: List[str] = []

# ==================== OUTPUT MODELS ====================

class RecoveryDay(BaseModel):
    modalities: List[str]
    nutrition: str
    sleep: str
    field_work: str

class FieldSession(BaseModel):
    duration: str
    warmup: str
    main_block: str
    finisher: str

class GymSession(BaseModel):
    lifts: List[str]
    duration: str = "30-45min"

class CoachChecklist(BaseModel):
    items: List[str] = [
        "first touch direction",
        "press timing (<3s)",
        "communication",
        "decel & hip control",
        "decision speed under fatigue"
    ]

class DayMeta(BaseModel):
    tactical_day: TacticalDay
    load_flag: LoadStatus
    recovery_needed: bool
    date: datetime

class DailyTrainingPlan(BaseModel):
    day_meta: DayMeta
    field_session: FieldSession
    gym_session: GymSession
    recovery_block: RecoveryDay
    coach_checklist: CoachChecklist

class WeeklyMicrocycle(BaseModel):
    week_number: int
    phase: TrainingPhase
    daily_plans: List[DailyTrainingPlan]
    weekly_load_target: Dict[str, float]
    testing_scheduled: bool = False

class RecoveryPlan(BaseModel):
    current_stage: Optional[RTPStage] = None
    modalities: List[str]
    duration_days: int
    restrictions: List[str]

class TestingSummary(BaseModel):
    speed_index: Optional[float] = None
    endurance_index: Optional[float] = None
    power_index: Optional[float] = None
    tests_needed: List[str] = []
    last_test_date: Optional[datetime] = None

class IntegrationSuggestions(BaseModel):
    merge_strategy: str
    mapped_drills: Dict[str, str] = {}
    removed_exercises: List[str] = []
    coach_notes: List[str] = []

class EliteTrainingOutput(BaseModel):
    player_name: str
    daily_training_plan: DailyTrainingPlan
    weekly_microcycle: WeeklyMicrocycle
    recovery_plan: RecoveryPlan
    testing_summary: TestingSummary
    coach_checklist: CoachChecklist
    integration_suggestions: IntegrationSuggestions

# ==================== BENCHMARKS ====================

ELITE_BENCHMARKS = {
    "sprint_10m": {"elite": 1.65, "excellent": 1.75, "good": 1.85, "average": 1.95},
    "sprint_30m": {"elite": 3.90, "excellent": 4.10, "good": 4.30, "average": 4.50},
    "yoyo_ir2": {"elite": 2400, "excellent": 2000, "good": 1700, "average": 1400},
    "cmj": {"elite": 65, "excellent": 60, "good": 55, "average": 50},
    "test_505": {"elite": 2.20, "excellent": 2.30, "good": 2.40, "average": 2.50},
    "squat_1rm": {"elite": 2.0, "excellent": 1.8, "good": 1.6, "average": 1.4}  # x bodyweight
}

# ==================== CORE LOGIC ====================

class EliteTrainingGenerator:
    """Main class for generating elite soccer training programs"""
    
    def __init__(self):
        self.benchmarks = ELITE_BENCHMARKS
        
    def validate_testing_data(self, testing_data: TestingData) -> TestingSummary:
        """Validate testing data and identify gaps"""
        tests_needed = []
        
        # Check if testing is outdated (> 8 weeks)
        if testing_data.test_date:
            days_old = (datetime.now(timezone.utc) - testing_data.test_date).days
            if days_old > 56:  # 8 weeks
                tests_needed.append("Testing data is > 8 weeks old - full retest recommended")
        
        # Check for missing critical tests
        if testing_data.sprint_10m is None:
            tests_needed.append("10m sprint")
        if testing_data.sprint_30m is None:
            tests_needed.append("30m sprint")
        if testing_data.yoyo_ir2 is None:
            tests_needed.append("Yo-Yo IR2")
        if testing_data.cmj is None:
            tests_needed.append("CMJ (Counter Movement Jump)")
        if testing_data.test_505 is None:
            tests_needed.append("505 agility test")
        if testing_data.squat_1rm is None or testing_data.nordic_strength is None:
            tests_needed.append("Strength profile (squat 1RM, nordic strength)")
        
        # Calculate indices
        speed_index = self._calculate_speed_index(testing_data)
        endurance_index = self._benchmark_score(testing_data.yoyo_ir2, "yoyo_ir2") if testing_data.yoyo_ir2 else None
        power_index = self._calculate_power_index(testing_data)
        
        return TestingSummary(
            speed_index=speed_index,
            endurance_index=endurance_index,
            power_index=power_index,
            tests_needed=tests_needed,
            last_test_date=testing_data.test_date
        )
    
    def _calculate_speed_index(self, testing_data: TestingData) -> Optional[float]:
        """Calculate average speed index from sprint times"""
        scores = []
        if testing_data.sprint_10m:
            scores.append(self._benchmark_score(testing_data.sprint_10m, "sprint_10m"))
        if testing_data.sprint_30m:
            scores.append(self._benchmark_score(testing_data.sprint_30m, "sprint_30m"))
        return sum(scores) / len(scores) if scores else None
    
    def _calculate_power_index(self, testing_data: TestingData) -> Optional[float]:
        """Calculate power index from CMJ and squat"""
        scores = []
        if testing_data.cmj:
            scores.append(self._benchmark_score(testing_data.cmj, "cmj"))
        if testing_data.squat_1rm:
            scores.append(self._benchmark_score(testing_data.squat_1rm, "squat_1rm"))
        return sum(scores) / len(scores) if scores else None
    
    def _benchmark_score(self, value: float, test_name: str) -> float:
        """Score a test result against benchmarks (0-100 scale)"""
        if test_name not in self.benchmarks:
            return 50.0
        
        bench = self.benchmarks[test_name]
        
        # For tests where lower is better (sprint times, 505)
        if test_name in ["sprint_10m", "sprint_30m", "test_505"]:
            if value <= bench["elite"]:
                return 100.0
            elif value <= bench["excellent"]:
                return 85.0
            elif value <= bench["good"]:
                return 70.0
            elif value <= bench["average"]:
                return 55.0
            else:
                return 40.0
        # For tests where higher is better (jumps, strength, yoyo)
        else:
            if value >= bench["elite"]:
                return 100.0
            elif value >= bench["excellent"]:
                return 85.0
            elif value >= bench["good"]:
                return 70.0
            elif value >= bench["average"]:
                return 55.0
            else:
                return 40.0
    
    def assess_load_status(self, previous_load: PreviousLoad) -> LoadStatus:
        """Determine load status from ACWR"""
        if previous_load.acwr < 0.8:
            return LoadStatus.UNDERLOAD
        elif previous_load.acwr > 1.5:
            return LoadStatus.OVERLOAD
        else:
            return LoadStatus.OPTIMAL
    
    def assess_recovery_state(self, wellness: Wellness, previous_load: PreviousLoad) -> Dict[str, Any]:
        """Assess recovery state from wellness and HRV"""
        recovery_needed = False
        reasons = []
        
        # Check soreness
        if wellness.soreness_1_5 <= 2:
            recovery_needed = True
            reasons.append("High soreness")
        
        # Check overall wellness
        wellness_avg = (wellness.soreness_1_5 + wellness.mood_1_5 + wellness.stress_1_5) / 3
        if wellness_avg < 3:
            recovery_needed = True
            reasons.append("Low wellness score")
        
        # Check HRV (if available and decreased)
        if wellness.hrv_score and wellness.hrv_score < 50:  # Simplified check
            recovery_needed = True
            reasons.append("Low HRV")
        
        # Check load status
        if previous_load.acwr > 1.5:
            recovery_needed = True
            reasons.append("High ACWR (overload)")
        
        return {
            "recovery_needed": recovery_needed,
            "reasons": reasons,
            "wellness_avg": wellness_avg
        }
    
    def assign_tactical_day(self, match_schedule: MatchSchedule) -> TacticalDay:
        """Assign tactical day based on match proximity"""
        days = match_schedule.days_to_next_match
        
        if days == 6:
            return TacticalDay.HIGH_INTENSITY_TRANSITION
        elif days == 5:
            return TacticalDay.STRENGTH_INTEGRATION
        elif days == 4:
            return TacticalDay.TACTICAL_POSITIONAL
        elif days == 3:
            return TacticalDay.SPEED_PRECISION
        elif days == 2:
            return TacticalDay.ACTIVATION
        else:  # days in [1, 0]
            return TacticalDay.MATCH_OR_RECOVERY
    
    def generate_recovery_plan(
        self,
        load_flag: LoadStatus,
        recovery_state: Dict[str, Any],
        match_schedule: MatchSchedule,
        injury_status: InjuryStatus
    ) -> RecoveryDay:
        """Generate recovery prescription based on current state"""
        
        # Return-to-play protocol
        if injury_status == InjuryStatus.RETURN_TO_PLAY:
            return RecoveryDay(
                modalities=["progressive loading", "position-specific drills at 70-80%", "HRV monitoring"],
                nutrition="Anti-inflammatory focus, 2.5g protein/kg bodyweight",
                sleep="Target 8-9h with quality sleep hygiene",
                field_work="RTP Stage 3-4: position-specific with constraints"
            )
        
        # High load or poor recovery
        if load_flag == LoadStatus.OVERLOAD or recovery_state["recovery_needed"]:
            return RecoveryDay(
                modalities=[
                    "pool/hydro 15-20min",
                    "mobility 15min",
                    "breathing exercises 5min",
                    "soft tissue therapy (if available)"
                ],
                nutrition="3:1 carb:protein within 30min post-training, hydration 35ml/kg",
                sleep="Target 8-9h, no late high-intensity training",
                field_work="Technical only, low intensity (<60% max HR)"
            )
        
        # Match day -1
        elif match_schedule.days_to_next_match == 1:
            return RecoveryDay(
                modalities=["dynamic stretch 10min", "short activation 15min", "video/tactical review"],
                nutrition="Carb loading protocol, hydration check",
                sleep="Early night, 8h minimum",
                field_work="≤30min, sharp technical work, no fatigue"
            )
        
        # Standard recovery
        else:
            return RecoveryDay(
                modalities=["mobility 10-15min", "soft tissue (if available)", "HRV check in AM"],
                nutrition="Balanced meals, maintain hydration",
                sleep="Target 8h with consistent schedule",
                field_work="Normal training load"
            )
    
    def generate_field_session(
        self,
        tactical_day: TacticalDay,
        phase: TrainingPhase,
        tactical_focus: TacticalFocus,
        recovery_needed: bool
    ) -> FieldSession:
        """Generate field session based on tactical day and phase"""
        
        if recovery_needed:
            return FieldSession(
                duration="45-60min",
                warmup="10min dynamic movement with ball",
                main_block="Technical circuits - passing patterns, ball mastery (low intensity)",
                finisher="Small-sided game 4v4 with touch limits"
            )
        
        # Define sessions by tactical day
        sessions = {
            TacticalDay.HIGH_INTENSITY_TRANSITION: FieldSession(
                duration="75-90min",
                warmup="12min dynamic + ball included (passing squares)",
                main_block="Transition game: 8v8 on large pitch, win ball → attack opposite goal in <10s. Focus: counter-pressing and quick transitions.",
                finisher="6x40m repeated sprints with ball (20s rest)"
            ),
            TacticalDay.STRENGTH_INTEGRATION: FieldSession(
                duration="60-75min",
                warmup="10min dynamic + SAQ ladder",
                main_block="Positional play 9v6+3 with physical duels emphasized. Integrate post-gym work.",
                finisher="Acceleration work: 8x15m from various starts"
            ),
            TacticalDay.TACTICAL_POSITIONAL: FieldSession(
                duration="75-90min",
                warmup="10min with directional passing",
                main_block=f"11v11 positional game focusing on {self._get_top_tactical_priorities(tactical_focus)}. Half-pitch or zonal constraints.",
                finisher="Set-piece routines (attacking corners, free kicks)"
            ),
            TacticalDay.SPEED_PRECISION: FieldSession(
                duration="70-80min",
                warmup="12min dynamic + sprint mechanics",
                main_block="Speed endurance: 6x(4x20m) with direction changes. Then small-sided games 5v5 on small pitch.",
                finisher="Technical finisher: 1v1 duels to goal"
            ),
            TacticalDay.ACTIVATION: FieldSession(
                duration="45-60min",
                warmup="10min dynamic stretch + ball rolling",
                main_block="Match preparation: set-pieces, shape review, opposition analysis",
                finisher="Short sharp possession games (10min max)"
            ),
            TacticalDay.MATCH_OR_RECOVERY: FieldSession(
                duration="30-45min",
                warmup="Light dynamic movement",
                main_block="Recovery session: low-intensity technical work or match day",
                finisher="Cool down and stretch"
            )
        }
        
        return sessions.get(tactical_day, sessions[TacticalDay.TACTICAL_POSITIONAL])
    
    def _get_top_tactical_priorities(self, tactical_focus: TacticalFocus) -> str:
        """Get top 2 tactical priorities"""
        priorities = [
            ("possession", tactical_focus.possession),
            ("transition", tactical_focus.transition),
            ("pressing", tactical_focus.pressing),
            ("buildup", tactical_focus.buildup),
            ("set_pieces", tactical_focus.set_pieces)
        ]
        sorted_priorities = sorted(priorities, key=lambda x: x[1], reverse=True)
        return f"{sorted_priorities[0][0]} and {sorted_priorities[1][0]}"
    
    def generate_gym_session(
        self,
        tactical_day: TacticalDay,
        testing_summary: TestingSummary,
        phase: TrainingPhase
    ) -> GymSession:
        """Generate gym session based on tactical day and testing weaknesses"""
        
        if tactical_day == TacticalDay.STRENGTH_INTEGRATION:
            lifts = [
                "Trap bar deadlift or squat pattern: 3x5-6 @ 80-85% 1RM",
                "Single-leg work: Bulgarian split squats 3x8 each",
                "Core anti-rotation: Pallof press 3x10 each side",
                "Nordic hamstrings: 3x5-8 reps"
            ]
        elif tactical_day == TacticalDay.HIGH_INTENSITY_TRANSITION:
            lifts = [
                "Power development: Hex bar jump 4x3 @ 30-40% 1RM",
                "Hamstring eccentric: Nordics 3x6",
                "Hip stability: Single-leg RDL 3x8 each",
                "Core: Dead bugs 3x12"
            ]
        else:
            # Prehab/maintenance
            lifts = [
                "Hamstring prehab: Nordics or eccentric hamstring curls 3x6-8",
                "Calf raises: 3x15 (injury prevention)",
                "Hip abduction/adduction: 3x12 each",
                "Core anti-extension: Plank variations 3x30-45s"
            ]
        
        # Add weakness-specific work
        if testing_summary.power_index and testing_summary.power_index < 60:
            lifts.append("PRIORITY: Power development - CMJ and explosive lifts")
        if testing_summary.speed_index and testing_summary.speed_index < 60:
            lifts.append("PRIORITY: Acceleration mechanics and sprint technique")
        
        return GymSession(
            lifts=lifts,
            duration="30-45min"
        )
    
    def generate_integration_suggestions(
        self,
        existing_program: ExistingProgram,
        suggested_drills: List[str]
    ) -> IntegrationSuggestions:
        """Generate integration suggestions with existing club program"""
        
        if existing_program.club_periodisation_id:
            merge_strategy = "Inherit club periodisation → Merge daily plans with priority: club_mandatory > logic_suggested > optional_extras"
        else:
            merge_strategy = "Use full Elite Training System logic as primary program"
        
        # Map suggested drills to session library
        mapped_drills = {}
        if existing_program.session_library_ids:
            for drill in suggested_drills:
                # Simplified mapping - in production, use tag-based matching
                mapped_drills[drill] = "session_lib_closest_match"
        
        # Remove banned exercises
        removed_exercises = []
        for exercise in existing_program.banned_exercises:
            if any(exercise.lower() in drill.lower() for drill in suggested_drills):
                removed_exercises.append(exercise)
        
        coach_notes = [
            "Integration allows attachment of opposition scouting drills",
            "Set-piece routines can be added to activation days",
            "Academy-specific technical blocks can supplement main sessions"
        ]
        
        return IntegrationSuggestions(
            merge_strategy=merge_strategy,
            mapped_drills=mapped_drills,
            removed_exercises=removed_exercises,
            coach_notes=coach_notes
        )
    
    def generate_daily_plan(
        self,
        player_profile: PlayerProfile,
        testing_data: TestingData,
        wellness: Wellness,
        match_schedule: MatchSchedule,
        tactical_focus: TacticalFocus,
        previous_load: PreviousLoad,
        existing_program: ExistingProgram,
        target_date: Optional[datetime] = None
    ) -> EliteTrainingOutput:
        """Generate complete daily training plan"""
        
        # 1. Validate and analyze testing data
        testing_summary = self.validate_testing_data(testing_data)
        
        # 2. Assess load and recovery
        load_flag = self.assess_load_status(previous_load)
        recovery_state = self.assess_recovery_state(wellness, previous_load)
        
        # 3. Assign tactical day
        tactical_day = self.assign_tactical_day(match_schedule)
        
        # 4. Determine phase (simplified - could be more sophisticated)
        # For now, use a simple heuristic based on match schedule
        if match_schedule.matches_this_week >= 2:
            phase = TrainingPhase.COMPETITION
        elif match_schedule.days_to_next_match <= 7:
            phase = TrainingPhase.DEVELOPMENT
        else:
            phase = TrainingPhase.FOUNDATION
        
        # 5. Generate recovery plan
        recovery_plan_detail = self.generate_recovery_plan(
            load_flag,
            recovery_state,
            match_schedule,
            player_profile.injury_status
        )
        
        # 6. Generate field session
        field_session = self.generate_field_session(
            tactical_day,
            phase,
            tactical_focus,
            recovery_state["recovery_needed"]
        )
        
        # 7. Generate gym session
        gym_session = self.generate_gym_session(
            tactical_day,
            testing_summary,
            phase
        )
        
        # 8. Create day meta
        day_meta = DayMeta(
            tactical_day=tactical_day,
            load_flag=load_flag,
            recovery_needed=recovery_state["recovery_needed"],
            date=target_date or datetime.now(timezone.utc)
        )
        
        # 9. Coach checklist
        coach_checklist = CoachChecklist()
        
        # 10. Daily training plan
        daily_plan = DailyTrainingPlan(
            day_meta=day_meta,
            field_session=field_session,
            gym_session=gym_session,
            recovery_block=recovery_plan_detail,
            coach_checklist=coach_checklist
        )
        
        # 11. Generate weekly microcycle (simplified - single day for now)
        weekly_microcycle = WeeklyMicrocycle(
            week_number=1,
            phase=phase,
            daily_plans=[daily_plan],
            weekly_load_target={
                "total_distance_m": 25000 if phase == TrainingPhase.COMPETITION else 30000,
                "hsr_m": 1500 if phase == TrainingPhase.COMPETITION else 1800,
                "sprints": 25 if phase == TrainingPhase.COMPETITION else 30
            },
            testing_scheduled=False
        )
        
        # 12. Recovery plan summary
        recovery_plan = RecoveryPlan(
            current_stage=None if player_profile.injury_status == InjuryStatus.FIT else RTPStage.STAGE_3,
            modalities=recovery_plan_detail.modalities,
            duration_days=1 if recovery_state["recovery_needed"] else 0,
            restrictions=["No high-intensity if soreness > 3"] if recovery_state["recovery_needed"] else []
        )
        
        # 13. Integration suggestions
        integration_suggestions = self.generate_integration_suggestions(
            existing_program,
            [field_session.main_block, gym_session.lifts[0]]
        )
        
        # 14. Complete output
        return EliteTrainingOutput(
            player_name=player_profile.name,
            daily_training_plan=daily_plan,
            weekly_microcycle=weekly_microcycle,
            recovery_plan=recovery_plan,
            testing_summary=testing_summary,
            coach_checklist=coach_checklist,
            integration_suggestions=integration_suggestions
        )


# ==================== RTP (RETURN TO PLAY) PROTOCOLS ====================

RTP_PROTOCOLS = {
    RTPStage.STAGE_1: {
        "description": "Pain-free ROM, isometrics, bike",
        "duration_days": "2-3 days",
        "criteria_to_progress": [
            "No pain during isometric exercises",
            "Full ROM achieved",
            "Can bike for 20min without discomfort"
        ],
        "sample_protocol": [
            "Isometric holds: 5x10s at multiple angles",
            "Stationary bike: 20min easy",
            "ROM exercises: 3x15 each direction",
            "Ice and elevation post-session"
        ]
    },
    RTPStage.STAGE_2: {
        "description": "Linear run progressions, submax COD",
        "duration_days": "3-5 days",
        "criteria_to_progress": [
            "Can jog 10min continuously pain-free",
            "No swelling post-exercise",
            "Completed 3 sessions without regression"
        ],
        "sample_protocol": [
            "Progressive running: walk→jog→run (15min)",
            "Straight-line running: 8x40m @ 70% speed",
            "Basic change of direction: 45° cuts @ 60%",
            "Gym: Light resistance work for affected area"
        ]
    },
    RTPStage.STAGE_3: {
        "description": "Position-specific drills at 70-80% HSR",
        "duration_days": "4-7 days",
        "criteria_to_progress": [
            "Completed position drills @ 80% without issues",
            "Confident with multi-directional movements",
            "Wellness scores normal (≥4/5)"
        ],
        "sample_protocol": [
            "Position-specific patterns: 15min @ 70-80%",
            "Small-sided games: 5v5 with constraints",
            "Progressive HSR: 6x30m @ 80-85%",
            "Strength: Return to normal gym program"
        ]
    },
    RTPStage.STAGE_4: {
        "description": "Full team with constraints",
        "duration_days": "3-5 days",
        "criteria_to_progress": [
            "Completed full team training without restrictions",
            "Load metrics match pre-injury levels",
            "Medical clearance obtained"
        ],
        "sample_protocol": [
            "Full team training with time constraints",
            "11v11 but limited to 70% of normal duration",
            "All movements unrestricted",
            "Monitor load: ACWR, RPE, GPS metrics"
        ]
    },
    RTPStage.STAGE_5: {
        "description": "Match return with load monitoring",
        "duration_days": "Ongoing",
        "criteria_to_progress": [
            "N/A - back to full training and matches"
        ],
        "sample_protocol": [
            "First match: Sub appearance 20-30min",
            "Second match: Starter but managed minutes",
            "Close HRV and wellness monitoring",
            "Gradual return to full match loads over 3-4 weeks"
        ]
    }
}
