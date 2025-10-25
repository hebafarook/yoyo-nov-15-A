# Comprehensive Soccer Exercise Database with Detailed Instructions
# Each exercise includes: instructions, purpose, expected outcomes, and progression

from typing import Dict, Any, List

EXERCISE_DATABASE = {
    # ========== SPEED & AGILITY EXERCISES ==========
    "sprint_intervals_30m": {
        "name": "30m Sprint Intervals",
        "category": "speed",
        "description": "High-intensity sprints over 30 meters to develop maximum speed and acceleration.",
        "instructions": [
            "Set up two cones 30 meters apart on a flat surface",
            "Start in a 3-point stance (one hand down, opposite foot forward)",
            "On signal, sprint at maximum effort to the far cone",
            "Focus on driving arms and maintaining forward lean",
            "Walk back slowly to starting position for recovery",
            "Repeat for specified number of sets"
        ],
        "purpose": "Develops maximum running speed, acceleration, and neuromuscular coordination essential for soccer performance.",
        "expected_outcome": "Improved 30m sprint time by 0.1-0.3 seconds over 4-6 weeks. Enhanced explosive power and stride efficiency.",
        "duration": 25,
        "intensity": "maximum",
        "equipment_needed": ["cones", "stopwatch"],
        "progression": {
            "week_1_2": {"sets": 4, "rest": "90s", "intensity": "95%"},
            "week_3_4": {"sets": 5, "rest": "90s", "intensity": "100%"},
            "week_5_6": {"sets": 6, "rest": "120s", "intensity": "100%"}
        }
    },
    
    "ladder_agility_drill": {
        "name": "Speed Ladder Agility Complex",
        "category": "agility",
        "description": "Multi-directional footwork patterns using speed ladder to enhance coordination and quick feet.",
        "instructions": [
            "Lay out speed ladder on flat ground",
            "Start at one end in athletic stance",
            "Perform pattern: Two feet in each box (10 boxes)",
            "Immediately follow with: In-in-out-out pattern",
            "Finish with: Single leg hops (right leg, then left leg)",
            "Focus on staying on balls of feet throughout",
            "Maintain quick, light contact with ground"
        ],
        "purpose": "Improves foot speed, coordination, balance, and reactive agility needed for quick direction changes in soccer.",
        "expected_outcome": "20% improvement in agility test times, better first touch control under pressure, enhanced change of direction speed.",
        "duration": 15,
        "intensity": "high",
        "equipment_needed": ["speed_ladder"],
        "progression": {
            "week_1_2": {"rounds": 3, "patterns": 3, "rest": "60s"},
            "week_3_4": {"rounds": 4, "patterns": 4, "rest": "45s"},
            "week_5_6": {"rounds": 5, "patterns": 5, "rest": "30s"}
        }
    },

    # ========== TECHNICAL SKILL EXERCISES ==========
    "ball_mastery_cone_weaving": {
        "name": "Ball Mastery Cone Weaving",
        "category": "technical",
        "description": "Close ball control through cone patterns using various surfaces of feet.",
        "instructions": [
            "Set up 6 cones in a straight line, 2 yards apart",
            "Start with ball at first cone using inside of right foot",
            "Weave through cones: inside right, inside left, outside right, outside left",
            "Keep ball close (within 1 yard) throughout the pattern",
            "Accelerate through the last two cones",
            "Turn around and repeat pattern coming back",
            "Focus on keeping head up and scanning field"
        ],
        "purpose": "Develops close ball control, spatial awareness, and ability to manipulate ball in tight spaces during match situations.",
        "expected_outcome": "Improved ball control rating from current level, increased confidence in 1v1 situations, better first touch under pressure.",
        "duration": 20,
        "intensity": "medium",
        "equipment_needed": ["cones", "soccer_ball"],
        "progression": {
            "week_1_2": {"repetitions": 5, "speed": "70%", "touches": "unlimited"},
            "week_3_4": {"repetitions": 7, "speed": "80%", "touches": "2_per_cone"},
            "week_5_6": {"repetitions": 10, "speed": "90%", "touches": "1_per_cone"}
        }
    },

    "passing_accuracy_gates": {
        "name": "Passing Accuracy Through Gates",
        "category": "technical",
        "description": "Precision passing through small gates to improve accuracy and weight of pass.",
        "instructions": [
            "Set up 5 small gates (1 yard wide) at various distances: 10, 15, 20, 25, 30 yards",
            "Start with 15 balls at central position",
            "Pass through each gate in sequence using inside of foot",
            "Focus on proper body position: plant foot beside ball, strike through center",
            "Follow through towards target",
            "Retrieve balls and repeat from different angles",
            "Progress to using weak foot for 50% of passes"
        ],
        "purpose": "Improves passing accuracy, weight of pass, and ability to find teammates in tight spaces during match play.",
        "expected_outcome": "Increase passing accuracy by 10-15%, improved assist numbers, better distribution in final third.",
        "duration": 25,
        "intensity": "medium",
        "equipment_needed": ["cones", "soccer_balls"],
        "progression": {
            "week_1_2": {"accuracy_target": "60%", "strong_foot": "80%", "weak_foot": "20%"},
            "week_3_4": {"accuracy_target": "70%", "strong_foot": "70%", "weak_foot": "30%"},
            "week_5_6": {"accuracy_target": "80%", "strong_foot": "60%", "weak_foot": "40%"}
        }
    },

    # ========== TACTICAL EXERCISES ==========
    "small_sided_positioning": {
        "name": "4v4+2 Positional Play",
        "category": "tactical",
        "description": "Small-sided game focusing on maintaining possession through proper positioning and movement.",
        "instructions": [
            "Set up 30x20 yard area with small goals on each end",
            "Two teams of 4 players each, plus 2 neutral players who always play with team in possession",
            "Objective: Complete 8 passes before attempting to score",
            "Players must stay in their designated zones initially",
            "Progress to free movement while maintaining team shape",
            "Neutral players help create numerical advantage",
            "Focus on quick decision making and first touch"
        ],
        "purpose": "Develops game intelligence, positioning awareness, quick decision making, and ability to maintain possession under pressure.",
        "expected_outcome": "Improved game intelligence rating, better positioning in matches, increased pass completion rate in game situations.",
        "duration": 30,
        "intensity": "high",
        "equipment_needed": ["cones", "bibs", "small_goals", "soccer_balls"],
        "progression": {
            "week_1_2": {"games": 4, "duration": "6_min", "passes_required": 6},
            "week_3_4": {"games": 5, "duration": "7_min", "passes_required": 8},
            "week_5_6": {"games": 6, "duration": "8_min", "passes_required": 10}
        }
    },

    # ========== PHYSICAL CONDITIONING ==========
    "plyometric_jump_circuit": {
        "name": "Soccer-Specific Plyometric Circuit",
        "category": "physical",
        "description": "Explosive jumping exercises to develop power for headers, tackles, and general athleticism.",
        "instructions": [
            "Station 1: Box jumps (20 inches) - 8 reps",
            "Station 2: Single-leg bounds (each leg) - 6 reps per leg",
            "Station 3: Lateral bounds over cone - 10 reps each direction",
            "Station 4: Depth jumps from 12-inch box - 6 reps",
            "Station 5: Tuck jumps - 8 reps",
            "Rest 60 seconds between stations",
            "Complete 3 full circuits with 2 minutes rest between circuits",
            "Focus on landing softly and immediately preparing for next rep"
        ],
        "purpose": "Increases vertical jump height, explosive power, and reactive strength for improved aerial ability and overall athleticism.",
        "expected_outcome": "5-10cm improvement in vertical jump, better heading ability, increased power in tackles and explosive movements.",
        "duration": 25,
        "intensity": "high",
        "equipment_needed": ["plyo_boxes", "cones"],
        "progression": {
            "week_1_2": {"circuits": 2, "box_height": "16_inches", "rest": "90s"},
            "week_3_4": {"circuits": 3, "box_height": "18_inches", "rest": "75s"},
            "week_5_6": {"circuits": 3, "box_height": "20_inches", "rest": "60s"}
        }
    },

    "vo2_max_shuttle_runs": {
        "name": "VO2 Max Shuttle Run Intervals",
        "category": "physical",
        "description": "High-intensity shuttle runs designed to improve maximum oxygen uptake and cardiovascular endurance.",
        "instructions": [
            "Set up two lines 20 meters apart",
            "Run at 85-90% maximum effort from line to line",
            "Touch each line with your hand",
            "Continue for specified work period without stopping",
            "Focus on maintaining pace throughout interval",
            "Walk slowly during rest periods",
            "Monitor heart rate to ensure proper intensity zone",
            "Stay hydrated between intervals"
        ],
        "purpose": "Improves VO2 max, cardiovascular endurance, and ability to maintain high intensity throughout match duration.",
        "expected_outcome": "3-5 ml/kg/min improvement in VO2 max, better endurance in later stages of matches, faster recovery between high-intensity efforts.",
        "duration": 30,
        "intensity": "maximum",
        "equipment_needed": ["cones", "heart_rate_monitor"],
        "progression": {
            "week_1_2": {"intervals": 6, "work": "90s", "rest": "90s"},
            "week_3_4": {"intervals": 8, "work": "90s", "rest": "75s"},
            "week_5_6": {"intervals": 10, "work": "90s", "rest": "60s"}
        }
    },

    # ========== PSYCHOLOGICAL/MENTAL TRAINING ==========
    "pressure_decision_making": {
        "name": "Pressure Decision Making Drill",
        "category": "psychological",
        "description": "Decision making under time pressure with multiple options to simulate match pressure situations.",
        "instructions": [
            "Set up 4 colored gates around central circle (15 yards apart)",
            "Player starts in center with ball",
            "Coach calls out color and technique (e.g., 'Red - Pass', 'Blue - Dribble')",
            "Player has 3 seconds to execute correct action through correct gate",
            "Add defenders to increase pressure after mastering basic pattern",
            "Include unexpected calls and changes mid-execution",
            "Focus on staying calm and making quick, accurate decisions",
            "Debrief each decision for learning"
        ],
        "purpose": "Develops mental toughness, decision making under pressure, and ability to process information quickly during matches.",
        "expected_outcome": "Improved decision making rating, reduced errors under pressure, increased confidence in high-pressure situations.",
        "duration": 20,
        "intensity": "medium",
        "equipment_needed": ["colored_cones", "soccer_ball", "bibs"],
        "progression": {
            "week_1_2": {"scenarios": 20, "time_limit": "4s", "defenders": 0},
            "week_3_4": {"scenarios": 30, "time_limit": "3s", "defenders": 1},
            "week_5_6": {"scenarios": 40, "time_limit": "2s", "defenders": 2}
        }
    },

    "visualization_mental_rehearsal": {
        "name": "Match Situation Visualization",
        "category": "psychological",
        "description": "Mental rehearsal of key match situations to improve performance under pressure.",
        "instructions": [
            "Find quiet space and sit comfortably with eyes closed",
            "Begin with 5 deep breaths to relax",
            "Visualize yourself in specific match scenario (e.g., taking penalty, 1v1 with goalkeeper)",
            "See, hear, and feel the environment in detail",
            "Rehearse perfect execution of the skill 5 times mentally",
            "Feel the positive emotions of successful completion",
            "Include potential challenges and how you overcome them",
            "End with positive affirmation about your abilities",
            "Practice different scenarios each session"
        ],
        "purpose": "Enhances mental preparation, builds confidence, and improves performance in high-pressure match situations through mental rehearsal.",
        "expected_outcome": "Increased confidence in key situations, better composure under pressure, improved conversion rates in crucial moments.",
        "duration": 15,
        "intensity": "low",
        "equipment_needed": ["quiet_space"],
        "progression": {
            "week_1_2": {"scenarios": 2, "repetitions": 3, "complexity": "basic"},
            "week_3_4": {"scenarios": 3, "repetitions": 5, "complexity": "intermediate"},
            "week_5_6": {"scenarios": 4, "repetitions": 5, "complexity": "advanced"}
        }
    }
}

# Periodization Templates
PERIODIZATION_TEMPLATES = {
    "foundation_building": {
        "phase_name": "Foundation Building Phase",
        "duration_weeks": 4,
        "objectives": [
            "Establish proper movement patterns and technique",
            "Build aerobic base and general strength",
            "Develop ball familiarity and basic skills",
            "Learn tactical fundamentals"
        ],
        "weekly_distribution": {
            "physical": 30,
            "technical": 40,
            "tactical": 20,
            "psychological": 10
        },
        "intensity_progression": [60, 65, 70, 65]  # Percentage by week
    },
    
    "development_phase": {
        "phase_name": "Skill Development Phase", 
        "duration_weeks": 6,
        "objectives": [
            "Improve technical skills under pressure",
            "Develop tactical understanding",
            "Increase physical capacity",
            "Build mental resilience"
        ],
        "weekly_distribution": {
            "physical": 25,
            "technical": 35,
            "tactical": 30,
            "psychological": 10
        },
        "intensity_progression": [70, 75, 80, 85, 80, 75]
    },
    
    "peak_performance": {
        "phase_name": "Peak Performance Phase",
        "duration_weeks": 4,
        "objectives": [
            "Maximize match performance",
            "Perfect key skills and tactics",
            "Peak physical condition",
            "Optimal mental state"
        ],
        "weekly_distribution": {
            "physical": 20,
            "technical": 30,
            "tactical": 35,
            "psychological": 15
        },
        "intensity_progression": [85, 90, 95, 85]
    }
}

def generate_daily_routine(phase: str, week_number: int, day_number: int, player_weaknesses: List[str]) -> Dict[str, Any]:
    """Generate a daily routine based on phase, week, day, and player needs"""
    template = PERIODIZATION_TEMPLATES.get(phase, PERIODIZATION_TEMPLATES["foundation_building"])
    intensity = template["intensity_progression"][week_number - 1] if week_number <= len(template["intensity_progression"]) else 75
    
    # Select exercises based on player weaknesses and phase focus
    exercises = []
    
    # Always include some physical conditioning
    exercises.append(EXERCISE_DATABASE["sprint_intervals_30m"])
    
    # Add technical work based on weaknesses
    if "ball_control" in player_weaknesses:
        exercises.append(EXERCISE_DATABASE["ball_mastery_cone_weaving"])
    if "passing" in player_weaknesses:
        exercises.append(EXERCISE_DATABASE["passing_accuracy_gates"])
        
    # Add tactical work (increases in later phases)
    if phase in ["development_phase", "peak_performance"]:
        exercises.append(EXERCISE_DATABASE["small_sided_positioning"])
        
    # Add psychological training
    exercises.append(EXERCISE_DATABASE["visualization_mental_rehearsal"])
    
    return {
        "day_number": day_number,
        "phase": phase,
        "exercises": exercises,
        "total_duration": sum(ex["duration"] for ex in exercises),
        "intensity_rating": get_intensity_rating(intensity),
        "focus_areas": get_focus_areas(phase, player_weaknesses),
        "objectives": template["objectives"]
    }

def get_intensity_rating(intensity_percentage: float) -> str:
    """Convert intensity percentage to rating"""
    if intensity_percentage >= 90: 
        return "maximum"
    elif intensity_percentage >= 75: 
        return "high" 
    elif intensity_percentage >= 60: 
        return "medium"
    else: 
        return "low"

def get_focus_areas(phase: str, weaknesses: List[str]) -> List[str]:
    """Get focus areas based on phase and player weaknesses"""
    base_focus = {
        "foundation_building": ["technique", "fitness_base", "fundamentals"],
        "development_phase": ["skill_refinement", "tactical_awareness", "conditioning"],
        "peak_performance": ["match_simulation", "peak_fitness", "mental_preparation"]
    }
    
    focus = base_focus.get(phase, base_focus["foundation_building"])
    
    # Add weakness-specific focus
    if "speed" in weaknesses:
        focus.append("sprint_development")
    if "ball_control" in weaknesses:
        focus.append("technical_mastery")
        
    return focus