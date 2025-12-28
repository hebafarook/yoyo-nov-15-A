"""
YoYo Report v2 - Presentation Layer Only
========================================

This module formats existing backend data into the standardized 11-section report format.
NO NEW CALCULATIONS. NO LOGIC CHANGES. READ-ONLY FORMATTING.

Accepts existing assessment and analysis data.
Outputs fixed 11-section structure + JSON object.

Sections (FIXED ORDER - DO NOT REORDER):
1. Identity & Biology
2. Performance Snapshot
3. Strengths & Weaknesses
4. Development Identity
5. Benchmarks (Now → Target → Elite)
6. Training Mode
7. Training Program (with 9 sub-sections)
8. Return-to-Play Engine
9. Safety Governor
10. AI Object (JSON)
11. Goal State
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# Section titles - FIXED ORDER, DO NOT REORDER
SECTION_TITLES = [
    "Identity & Biology",
    "Performance Snapshot",
    "Strengths & Weaknesses",
    "Development Identity",
    "Benchmarks (Now → Target → Elite)",
    "Training Mode",
    "Training Program",
    "Return-to-Play Engine",
    "Safety Governor",
    "AI Object (JSON)",
    "Goal State"
]


def _safe_get(data: Optional[Dict], *keys, default: Any = "") -> Any:
    """Safely get nested dictionary values, returning default if not found."""
    if data is None:
        return default
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default


class YoYoReportV2Formatter:
    """
    Presentation layer that formats existing data into YoYo Report v2.
    
    IMPORTANT: This class does NOT calculate, modify, or generate new data.
    It only formats what already exists from the backend.
    """
    
    def __init__(
        self,
        user: Optional[Dict[str, Any]] = None,
        assessment: Optional[Dict[str, Any]] = None,
        benchmark: Optional[Dict[str, Any]] = None,
        training_program: Optional[Dict[str, Any]] = None,
        injury_data: Optional[Dict[str, Any]] = None,
        match_history: Optional[List[Dict[str, Any]]] = None,
        generated_report: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with existing backend data.
        
        Args:
            user: User profile data from database
            assessment: Raw assessment data from database
            benchmark: Benchmark data from database
            training_program: Training program data
            injury_data: Injury/medical data if exists
            match_history: Match history list
            generated_report: Previously generated AI report (comprehensive_reports)
        """
        self.user = user or {}
        self.assessment = assessment or {}
        self.benchmark = benchmark or {}
        self.training_program = training_program or {}
        self.injury_data = injury_data or {}
        self.match_history = match_history or []
        self.generated_report = generated_report or {}
        
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate complete YoYo Report v2 with 11 sections + JSON.
        
        Returns:
            Dict with:
                - report_sections: List of 11 sections in fixed order
                - report_json: Machine-readable JSON object
                - meta: Report metadata
        """
        sections = [
            self._section_1_identity_biology(),
            self._section_2_performance_snapshot(),
            self._section_3_strengths_weaknesses(),
            self._section_4_development_identity(),
            self._section_5_benchmarks(),
            self._section_6_training_mode(),
            self._section_7_training_program(),
            self._section_8_return_to_play(),
            self._section_9_safety_governor(),
            self._section_10_ai_object(),
            self._section_11_goal_state()
        ]
        
        # Build JSON object
        report_json = self._build_json_object()
        
        return {
            "report_sections": sections,
            "report_json": report_json,
            "meta": {
                "report_version": "2.0",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "section_count": len(sections)
            }
        }
    
    # =========================================================================
    # SECTION 1: IDENTITY & BIOLOGY
    # =========================================================================
    def _section_1_identity_biology(self) -> Dict[str, Any]:
        """Section 1: Player identity and biological data."""
        return {
            "section_number": 1,
            "section_title": SECTION_TITLES[0],
            "content": {
                "player_name": (
                    self.assessment.get('player_name') or 
                    self.user.get('full_name') or 
                    self.user.get('username') or 
                    "N/A"
                ),
                "age": self.assessment.get('age') or self.user.get('age') or "N/A",
                "gender": (
                    self.assessment.get('gender') or 
                    self.user.get('gender') or 
                    "N/A"
                ),
                "position": (
                    self.assessment.get('position') or 
                    self.user.get('position') or 
                    "N/A"
                ),
                "dominant_leg": (
                    self.assessment.get('dominant_foot') or
                    self.user.get('dominant_foot') or
                    "N/A"
                ),
                "height_cm": self.assessment.get('height_cm') or self.user.get('height_cm') or "N/A",
                "weight_kg": self.assessment.get('weight_kg') or self.user.get('weight_kg') or "N/A",
                "assessment_date": self.assessment.get('assessment_date') or "N/A"
            }
        }
    
    # =========================================================================
    # SECTION 2: PERFORMANCE SNAPSHOT
    # =========================================================================
    def _section_2_performance_snapshot(self) -> Dict[str, Any]:
        """Section 2: Current performance metrics with existing classifications."""
        # Use benchmark or assessment data
        overall_score = (
            self.benchmark.get('overall_score') or 
            self.assessment.get('overall_score') or 
            "N/A"
        )
        performance_level = (
            self.benchmark.get('performance_level') or 
            _safe_get(self.generated_report, 'scores', 'performance_level') or
            "N/A"
        )
        
        return {
            "section_number": 2,
            "section_title": SECTION_TITLES[1],
            "content": {
                "overall_score": overall_score,
                "performance_level": performance_level,
                "physical_metrics": {
                    "sprint_30m": {
                        "value": self.assessment.get('sprint_30m') or "N/A",
                        "label": "30m Sprint Time (seconds)"
                    },
                    "yo_yo_test": {
                        "value": self.assessment.get('yo_yo_test') or "N/A",
                        "label": "Yo-Yo IR Test (meters)"
                    },
                    "vo2_max": {
                        "value": self.assessment.get('vo2_max') or "N/A",
                        "label": "VO2 Max (ml/kg/min)"
                    },
                    "vertical_jump": {
                        "value": self.assessment.get('vertical_jump') or "N/A",
                        "label": "Vertical Jump (cm)"
                    },
                    "body_fat": {
                        "value": self.assessment.get('body_fat') or "N/A",
                        "label": "Body Fat (%)"
                    }
                },
                "technical_metrics": {
                    "ball_control": {
                        "value": self.assessment.get('ball_control') or "N/A",
                        "label": "Ball Control (1-5)"
                    },
                    "passing_accuracy": {
                        "value": self.assessment.get('passing_accuracy') or "N/A",
                        "label": "Passing Accuracy (%)"
                    },
                    "dribbling_success": {
                        "value": self.assessment.get('dribbling_success') or "N/A",
                        "label": "Dribbling Success (%)"
                    },
                    "shooting_accuracy": {
                        "value": self.assessment.get('shooting_accuracy') or "N/A",
                        "label": "Shooting Accuracy (%)"
                    },
                    "defensive_duels": {
                        "value": self.assessment.get('defensive_duels') or "N/A",
                        "label": "Defensive Duels Won (%)"
                    }
                },
                "tactical_metrics": {
                    "game_intelligence": {
                        "value": self.assessment.get('game_intelligence') or "N/A",
                        "label": "Game Intelligence (1-5)"
                    },
                    "positioning": {
                        "value": self.assessment.get('positioning') or "N/A",
                        "label": "Positioning (1-5)"
                    },
                    "decision_making": {
                        "value": self.assessment.get('decision_making') or "N/A",
                        "label": "Decision Making (1-5)"
                    }
                },
                "psychological_metrics": {
                    "coachability": {
                        "value": self.assessment.get('coachability') or "N/A",
                        "label": "Coachability (1-5)"
                    },
                    "mental_toughness": {
                        "value": self.assessment.get('mental_toughness') or "N/A",
                        "label": "Mental Toughness (1-5)"
                    }
                }
            }
        }
    
    # =========================================================================
    # SECTION 3: STRENGTHS & WEAKNESSES
    # =========================================================================
    def _section_3_strengths_weaknesses(self) -> Dict[str, Any]:
        """Section 3: Identified strengths and weaknesses from existing outputs."""
        # Try to get from generated report first, then from benchmark
        strengths = (
            _safe_get(self.generated_report, 'strengths') or
            self.benchmark.get('strengths') or
            []
        )
        weaknesses = (
            _safe_get(self.generated_report, 'weaknesses') or
            self.benchmark.get('weaknesses') or
            []
        )
        
        return {
            "section_number": 3,
            "section_title": SECTION_TITLES[2],
            "content": {
                "strengths": strengths if strengths else ["N/A"],
                "weaknesses": weaknesses if weaknesses else ["N/A"]
            }
        }
    
    # =========================================================================
    # SECTION 4: DEVELOPMENT IDENTITY
    # =========================================================================
    def _section_4_development_identity(self) -> Dict[str, Any]:
        """Section 4: Player's development profile from existing labels."""
        # Use existing labels/profile if present
        performance_level = (
            self.benchmark.get('performance_level') or
            _safe_get(self.generated_report, 'scores', 'performance_level') or
            "N/A"
        )
        
        # Get AI analysis if available
        ai_analysis = _safe_get(self.generated_report, 'ai_analysis') or ""
        
        # Get strengths/weaknesses for summary derivation
        strengths = _safe_get(self.generated_report, 'strengths') or []
        weaknesses = _safe_get(self.generated_report, 'weaknesses') or []
        
        # Derive short summary if no existing profile label
        profile_summary = "N/A"
        if ai_analysis:
            profile_summary = ai_analysis[:500] + "..." if len(ai_analysis) > 500 else ai_analysis
        elif strengths or weaknesses:
            profile_summary = f"Strengths: {', '.join(strengths[:2]) if strengths else 'N/A'}. Areas to develop: {', '.join(weaknesses[:2]) if weaknesses else 'N/A'}."
        
        return {
            "section_number": 4,
            "section_title": SECTION_TITLES[3],
            "content": {
                "performance_level": performance_level,
                "profile_label": self.benchmark.get('profile_label') or performance_level,
                "development_summary": profile_summary
            }
        }
    
    # =========================================================================
    # SECTION 5: BENCHMARKS (NOW → TARGET → ELITE)
    # =========================================================================
    def _section_5_benchmarks(self) -> Dict[str, Any]:
        """Section 5: Benchmarks using ONLY existing computed/stored data."""
        # Use benchmarks that are already stored in the system
        # Do NOT create new norms
        
        # Check for standards comparison in generated report
        standards_comparison = _safe_get(self.generated_report, 'standards_comparison') or {}
        
        return {
            "section_number": 5,
            "section_title": SECTION_TITLES[4],
            "content": {
                "note": "Only displays benchmarks already computed/stored by backend",
                "existing_benchmarks": {
                    "overall_score": {
                        "now": self.assessment.get('overall_score') or "N/A",
                        "target": self.benchmark.get('target_score') or "N/A",
                        "elite": self.benchmark.get('elite_score') or "N/A"
                    }
                },
                "standards_comparison": standards_comparison if standards_comparison else "N/A"
            }
        }
    
    # =========================================================================
    # SECTION 6: TRAINING MODE
    # =========================================================================
    def _section_6_training_mode(self) -> Dict[str, Any]:
        """Section 6: Training mode (FIELD or GK) based on position or mode flag."""
        position = (
            self.assessment.get('position') or 
            self.user.get('position') or 
            ""
        ).lower()
        
        # Determine mode from position or existing flag
        mode = self.training_program.get('mode') or self.user.get('training_mode')
        if not mode:
            # Check for goalkeeper position variants
            gk_keywords = ["goalkeeper", "gk", "keeper", "goalie", "portero", "gardien"]
            if any(kw in position for kw in gk_keywords):
                mode = "GK"
            else:
                mode = "FIELD"
        
        return {
            "section_number": 6,
            "section_title": SECTION_TITLES[5],
            "content": {
                "mode": mode,
                "position": self.assessment.get('position') or "N/A"
            }
        }
    
    # =========================================================================
    # SECTION 7: TRAINING PROGRAM (WITH 9 SUB-SECTIONS)
    # =========================================================================
    def _section_7_training_program(self) -> Dict[str, Any]:
        """Section 7: Training program with required sub-sections."""
        # Get existing recommendations if available
        coach_recommendations = _safe_get(self.generated_report, 'coach_recommendations') or []
        development_roadmap = _safe_get(self.generated_report, 'development_roadmap') or {}
        
        # Extract from training program if exists
        program_content = self.training_program.get('program_content') or ""
        weekly_schedule = self.training_program.get('weekly_schedule') or {}
        
        return {
            "section_number": 7,
            "section_title": SECTION_TITLES[6],
            "content": {
                "7.1_technical": coach_recommendations[:2] if len(coach_recommendations) >= 2 else ["N/A"],
                "7.2_tactical": [r for r in coach_recommendations if 'tactical' in r.lower() or 'position' in r.lower()] or ["N/A"],
                "7.3_possession": [r for r in coach_recommendations if 'pass' in r.lower() or 'possess' in r.lower()] or ["N/A"],
                "7.4_athletic_speed_agility": [r for r in coach_recommendations if 'speed' in r.lower() or 'agil' in r.lower() or 'sprint' in r.lower()] or ["N/A"],
                "7.5_cardio": [r for r in coach_recommendations if 'cardio' in r.lower() or 'endurance' in r.lower() or 'aerobic' in r.lower()] or ["N/A"],
                "7.6_gym_strength": [r for r in coach_recommendations if 'strength' in r.lower() or 'gym' in r.lower() or 'weight' in r.lower()] or ["N/A"],
                "7.7_mobility_flexibility": [r for r in coach_recommendations if 'flex' in r.lower() or 'mobil' in r.lower() or 'stretch' in r.lower()] or ["N/A"],
                "7.8_recovery_regeneration": [r for r in coach_recommendations if 'recovery' in r.lower() or 'rest' in r.lower()] or ["N/A"],
                "7.9_injury_prevention_prehab": [r for r in coach_recommendations if 'injury' in r.lower() or 'prevent' in r.lower() or 'prehab' in r.lower()] or ["N/A"],
                "weekly_schedule": weekly_schedule if weekly_schedule else "N/A",
                "development_phases": development_roadmap if development_roadmap else "N/A"
            }
        }
    
    # =========================================================================
    # SECTION 8: RETURN-TO-PLAY ENGINE
    # =========================================================================
    def _section_8_return_to_play(self) -> Dict[str, Any]:
        """Section 8: Return-to-play guidelines (only if injury exists)."""
        # Check for existing injury data
        current_injuries = (
            self.injury_data.get('current_injuries') or
            self.assessment.get('current_injuries') or
            self.user.get('current_injuries')
        )
        
        if not current_injuries:
            return {
                "section_number": 8,
                "section_title": SECTION_TITLES[7],
                "content": "N/A"
            }
        
        # Only display existing injury-related data
        return {
            "section_number": 8,
            "section_title": SECTION_TITLES[7],
            "content": {
                "injury_status": current_injuries,
                "rtp_stage": self.injury_data.get('rtp_stage') or "N/A",
                "clearance_status": self.injury_data.get('clearance_status') or "Requires medical clearance",
                "restrictions": self.injury_data.get('restrictions') or ["Consult medical staff"],
                "note": "Data from existing injury records only"
            }
        }
    
    # =========================================================================
    # SECTION 9: SAFETY GOVERNOR
    # =========================================================================
    def _section_9_safety_governor(self) -> Dict[str, Any]:
        """Section 9: Existing safety rules only - no new rules created."""
        # Only use safety rules already stored in the system
        existing_safety_rules = (
            self.training_program.get('safety_rules') or
            self.user.get('safety_rules') or
            []
        )
        
        if not existing_safety_rules:
            return {
                "section_number": 9,
                "section_title": SECTION_TITLES[8],
                "content": "N/A"
            }
        
        return {
            "section_number": 9,
            "section_title": SECTION_TITLES[8],
            "content": {
                "safety_rules": existing_safety_rules,
                "note": "Existing safety rules only - no new rules generated"
            }
        }
    
    # =========================================================================
    # SECTION 10: AI OBJECT (JSON)
    # =========================================================================
    def _section_10_ai_object(self) -> Dict[str, Any]:
        """Section 10: Machine-readable JSON object (see report_json)."""
        return {
            "section_number": 10,
            "section_title": SECTION_TITLES[9],
            "content": {
                "note": "Complete JSON object available in 'report_json' field at root level",
                "preview": {
                    "player_id": self.user.get('id') or self.assessment.get('user_id') or "",
                    "name": self.assessment.get('player_name') or self.user.get('full_name') or ""
                }
            }
        }
    
    # =========================================================================
    # SECTION 11: GOAL STATE
    # =========================================================================
    def _section_11_goal_state(self) -> Dict[str, Any]:
        """Section 11: Goals derived from existing plan targets."""
        # Get existing goals/targets
        goals = (
            self.training_program.get('goals') or
            self.training_program.get('milestones') or
            _safe_get(self.generated_report, 'development_roadmap') or
            {}
        )
        
        # Get end of cycle summary if exists
        next_assessment = self.benchmark.get('next_assessment_date') or "N/A"
        
        content = "N/A"
        if goals or next_assessment != "N/A":
            content = {
                "goals": goals if goals else "N/A",
                "next_assessment": next_assessment,
                "end_of_cycle_summary": self.training_program.get('end_of_cycle_summary') or "Complete current training phase and reassess"
            }
        
        return {
            "section_number": 11,
            "section_title": SECTION_TITLES[10],
            "content": content
        }
    
    # =========================================================================
    # JSON OBJECT BUILDER
    # =========================================================================
    def _build_json_object(self) -> Dict[str, Any]:
        """
        Build complete machine-readable JSON object.
        All keys MUST exist as per schema. Fill from existing data; if missing, use empty values.
        """
        # Determine mode
        position = (self.assessment.get('position') or self.user.get('position') or "").lower()
        mode = self.training_program.get('mode') or self.user.get('training_mode')
        if not mode:
            mode = "GK" if ("goalkeeper" in position or "gk" in position) else "FIELD"
        
        # Build sub_program from existing training data
        existing_phases = _safe_get(self.generated_report, 'development_roadmap') or {}
        weekly_schedule = self.training_program.get('weekly_schedule') or {}
        coach_recs = _safe_get(self.generated_report, 'coach_recommendations') or []
        
        return {
            "player_id": self.user.get('id') or self.assessment.get('user_id') or "",
            "name": self.assessment.get('player_name') or self.user.get('full_name') or "",
            "age": str(self.assessment.get('age') or self.user.get('age') or ""),
            "gender": self.assessment.get('gender') or self.user.get('gender') or "",
            "position": self.assessment.get('position') or self.user.get('position') or "",
            "dominant_leg": self.assessment.get('dominant_foot') or self.user.get('dominant_foot') or "",
            "mode": mode,
            "profile_label": self.benchmark.get('performance_level') or "",
            "weekly_sessions": str(self.training_program.get('weekly_sessions') or ""),
            "total_weeks": str(self.training_program.get('total_weeks') or ""),
            "benchmarks": {
                "overall_score": {
                    "now": self.assessment.get('overall_score') or "",
                    "target": self.benchmark.get('target_score') or "",
                    "elite": self.benchmark.get('elite_score') or ""
                }
            },
            "safety_rules": self.training_program.get('safety_rules') or self.user.get('safety_rules') or [],
            "sub_program": {
                "phases": existing_phases if existing_phases else {},
                "weekly_microcycle": weekly_schedule if weekly_schedule else {},
                "expanded_sections": {
                    "technical": [r for r in coach_recs if 'tech' in r.lower() or 'skill' in r.lower()] or [],
                    "tactical": [r for r in coach_recs if 'tactical' in r.lower() or 'position' in r.lower()] or [],
                    "possession": [r for r in coach_recs if 'pass' in r.lower() or 'possess' in r.lower()] or [],
                    "cardio": {"recommendations": [r for r in coach_recs if 'cardio' in r.lower() or 'endurance' in r.lower()]} or {},
                    "gym": {"recommendations": [r for r in coach_recs if 'strength' in r.lower() or 'gym' in r.lower()]} or {},
                    "speed_agility": [r for r in coach_recs if 'speed' in r.lower() or 'agil' in r.lower()] or [],
                    "mobility": [r for r in coach_recs if 'flex' in r.lower() or 'mobil' in r.lower()] or [],
                    "recovery": [r for r in coach_recs if 'recovery' in r.lower() or 'rest' in r.lower()] or [],
                    "prehab": [r for r in coach_recs if 'injury' in r.lower() or 'prehab' in r.lower()] or []
                }
            },
            "matches": [
                {
                    "date": m.get('date', ''),
                    "opponent": m.get('opponent', ''),
                    "result": m.get('result', '')
                } for m in self.match_history
            ] if self.match_history else []
        }


# =============================================================================
# HELPER FUNCTION FOR EASY USAGE
# =============================================================================
def format_yoyo_report_v2(
    user: Optional[Dict[str, Any]] = None,
    assessment: Optional[Dict[str, Any]] = None,
    benchmark: Optional[Dict[str, Any]] = None,
    training_program: Optional[Dict[str, Any]] = None,
    injury_data: Optional[Dict[str, Any]] = None,
    match_history: Optional[List[Dict[str, Any]]] = None,
    generated_report: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to format existing data into YoYo Report v2.
    
    Args:
        user: User profile from database
        assessment: Raw assessment data from database
        benchmark: Benchmark data from database
        training_program: Training program data
        injury_data: Injury/medical data if exists
        match_history: Match history list
        generated_report: Previously generated AI report
    
    Returns:
        Complete YoYo Report v2 with 11 sections + JSON
    """
    formatter = YoYoReportV2Formatter(
        user=user,
        assessment=assessment,
        benchmark=benchmark,
        training_program=training_program,
        injury_data=injury_data,
        match_history=match_history,
        generated_report=generated_report
    )
    return formatter.generate_report()


def validate_report_structure(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that report has correct structure.
    
    Returns:
        Dict with 'valid' boolean and 'errors' list
    """
    errors = []
    
    # Check for required top-level keys
    if 'report_sections' not in report:
        errors.append("Missing 'report_sections' key")
    if 'report_json' not in report:
        errors.append("Missing 'report_json' key")
    if 'meta' not in report:
        errors.append("Missing 'meta' key")
    
    # Check sections count and order
    if 'report_sections' in report:
        sections = report['report_sections']
        if len(sections) != 11:
            errors.append(f"Expected 11 sections, got {len(sections)}")
        
        # Check section order
        for i, section in enumerate(sections):
            if section.get('section_number') != i + 1:
                errors.append(f"Section {i+1} has wrong section_number: {section.get('section_number')}")
            expected_title = SECTION_TITLES[i]
            if section.get('section_title') != expected_title:
                errors.append(f"Section {i+1} has wrong title. Expected '{expected_title}', got '{section.get('section_title')}'")
    
    # Check JSON object keys
    if 'report_json' in report:
        json_obj = report['report_json']
        required_keys = [
            'player_id', 'name', 'age', 'gender', 'position', 'dominant_leg',
            'mode', 'profile_label', 'weekly_sessions', 'total_weeks',
            'benchmarks', 'safety_rules', 'sub_program', 'matches'
        ]
        for key in required_keys:
            if key not in json_obj:
                errors.append(f"Missing required JSON key: {key}")
        
        # Check sub_program structure
        if 'sub_program' in json_obj:
            sub_program = json_obj['sub_program']
            required_sub_keys = ['phases', 'weekly_microcycle', 'expanded_sections']
            for key in required_sub_keys:
                if key not in sub_program:
                    errors.append(f"Missing sub_program key: {key}")
            
            if 'expanded_sections' in sub_program:
                expanded = sub_program['expanded_sections']
                required_expanded = [
                    'technical', 'tactical', 'possession', 'cardio', 'gym',
                    'speed_agility', 'mobility', 'recovery', 'prehab'
                ]
                for key in required_expanded:
                    if key not in expanded:
                        errors.append(f"Missing expanded_sections key: {key}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
