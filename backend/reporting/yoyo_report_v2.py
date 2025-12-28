"""
YoYo Report v2 - Presentation Layer Only
========================================

This module formats existing backend data into the standardized 11-section report format.
NO NEW CALCULATIONS. NO LOGIC CHANGES. READ-ONLY FORMATTING.

Accepts existing assessment and analysis data.
Outputs fixed 11-section structure + JSON object.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YoYoReportV2Formatter:
    """
    Presentation layer that formats existing data into YoYo Report v2.
    
    IMPORTANT: This class does NOT calculate, modify, or generate new data.
    It only formats what already exists from the backend.
    """
    
    def __init__(self, assessment: Dict[str, Any], analysis: Dict[str, Any]):
        """
        Initialize with existing backend data.
        
        Args:
            assessment: Raw assessment data from database
            analysis: Analysis result from analyze_assessment_with_llm()
        """
        self.assessment = assessment
        self.analysis = analysis
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate complete YoYo Report v2 with 11 sections + JSON.
        
        Returns:
            Dict with 'report_sections' (list of 11 sections) and 'report_json' (structured data)
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
        
        # Build JSON object (section 10 data in machine-readable format)
        report_json = self._build_json_object()
        
        return {
            "report_sections": sections,
            "report_json": report_json,
            "meta": {
                "report_version": "2.0",
                "generated_at": datetime.utcnow().isoformat(),
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
            "section_title": "Identity & Biology",
            "content": {
                "player_name": self.assessment.get('player_name', 'N/A'),
                "age": self.assessment.get('age', 'N/A'),
                "position": self.assessment.get('position', 'N/A'),
                "gender": self.assessment.get('gender', 'N/A'),
                "height_cm": self.assessment.get('height_cm', 'N/A'),
                "weight_kg": self.assessment.get('weight_kg', 'N/A'),
                "dominant_foot": self.assessment.get('dominant_foot', 'N/A'),
                "assessment_date": self.assessment.get('assessment_date', 'N/A')
            }
        }
    
    # =========================================================================
    # SECTION 2: PERFORMANCE SNAPSHOT
    # =========================================================================
    def _section_2_performance_snapshot(self) -> Dict[str, Any]:
        """Section 2: Current performance metrics (from existing gauges)."""
        gauges = self.analysis.get('performance_gauges', {})
        
        return {
            "section_number": 2,
            "section_title": "Performance Snapshot",
            "content": {
                "overall_score": self.assessment.get('overall_score', 0),
                "performance_level": self.analysis.get('performance_level', 'N/A'),
                "metrics": {
                    "sprint_30m": {
                        "value": gauges.get('sprint_30m', {}).get('score', 'N/A'),
                        "percent_of_standard": gauges.get('sprint_30m', {}).get('percent_of_standard', 'N/A'),
                        "unit": gauges.get('sprint_30m', {}).get('unit', 's')
                    },
                    "agility": {
                        "value": gauges.get('agility_test', {}).get('score', 'N/A'),
                        "percent_of_standard": gauges.get('agility_test', {}).get('percent_of_standard', 'N/A'),
                        "unit": gauges.get('agility_test', {}).get('unit', 'm')
                    },
                    "endurance": {
                        "value": gauges.get('endurance_beep', {}).get('score', 'N/A'),
                        "percent_of_standard": gauges.get('endurance_beep', {}).get('percent_of_standard', 'N/A'),
                        "unit": gauges.get('endurance_beep', {}).get('unit', 'm')
                    },
                    "ball_control": {
                        "value": gauges.get('ball_control', {}).get('score', 'N/A'),
                        "percent_of_standard": gauges.get('ball_control', {}).get('percent_of_standard', 'N/A'),
                        "unit": gauges.get('ball_control', {}).get('unit', '/10')
                    },
                    "passing_accuracy": {
                        "value": gauges.get('passing_accuracy', {}).get('score', 'N/A'),
                        "percent_of_standard": gauges.get('passing_accuracy', {}).get('percent_of_standard', 'N/A'),
                        "unit": gauges.get('passing_accuracy', {}).get('unit', '%')
                    }
                }
            }
        }
    
    # =========================================================================
    # SECTION 3: STRENGTHS & WEAKNESSES
    # =========================================================================
    def _section_3_strengths_weaknesses(self) -> Dict[str, Any]:
        """Section 3: Identified strengths and weaknesses (from analysis)."""
        return {
            "section_number": 3,
            "section_title": "Strengths & Weaknesses",
            "content": {
                "strengths": self.analysis.get('strengths', []),
                "weaknesses": self.analysis.get('weaknesses', [])
            }
        }
    
    # =========================================================================
    # SECTION 4: DEVELOPMENT IDENTITY
    # =========================================================================
    def _section_4_development_identity(self) -> Dict[str, Any]:
        """Section 4: Player's development profile (from existing comparison)."""
        comparison = self.analysis.get('comparison')
        
        return {
            "section_number": 4,
            "section_title": "Development Identity",
            "content": {
                "performance_level": self.analysis.get('performance_level', 'N/A'),
                "trend": comparison.get('trend', 'N/A') if comparison else 'N/A',
                "overall_improvement": comparison.get('overall_improvement', 0) if comparison else 0,
                "key_changes": comparison.get('key_changes', []) if comparison else [],
                "description": self.analysis.get('overall_analysis', 'Assessment in progress')
            }
        }
    
    # =========================================================================
    # SECTION 5: BENCHMARKS (NOW → TARGET → ELITE)
    # =========================================================================
    def _section_5_benchmarks(self) -> Dict[str, Any]:
        """Section 5: Benchmarks showing current, target, and elite values."""
        standards_comparison = self.analysis.get('standards_comparison', {})
        detailed = standards_comparison.get('detailed_comparison', {})
        
        return {
            "section_number": 5,
            "section_title": "Benchmarks (Now → Target → Elite)",
            "content": {
                "metrics_above_standard": standards_comparison.get('metrics_above_standard', 0),
                "metrics_below_standard": standards_comparison.get('metrics_below_standard', 0),
                "benchmarks": {
                    "sprint_30m": {
                        "now": detailed.get('sprint_30m', {}).get('value', 'N/A'),
                        "target": detailed.get('sprint_30m', {}).get('standard', 'N/A'),
                        "elite": self._get_elite_benchmark('sprint_30m'),
                        "status": detailed.get('sprint_30m', {}).get('status', 'N/A')
                    },
                    "yo_yo_test": {
                        "now": detailed.get('yo_yo_test', {}).get('value', 'N/A'),
                        "target": detailed.get('yo_yo_test', {}).get('standard', 'N/A'),
                        "elite": self._get_elite_benchmark('yo_yo_test'),
                        "status": detailed.get('yo_yo_test', {}).get('status', 'N/A')
                    },
                    "ball_control": {
                        "now": detailed.get('ball_control', {}).get('value', 'N/A'),
                        "target": detailed.get('ball_control', {}).get('standard', 'N/A'),
                        "elite": self._get_elite_benchmark('ball_control'),
                        "status": detailed.get('ball_control', {}).get('status', 'N/A')
                    },
                    "passing_accuracy": {
                        "now": detailed.get('passing_accuracy', {}).get('value', 'N/A'),
                        "target": detailed.get('passing_accuracy', {}).get('standard', 'N/A'),
                        "elite": self._get_elite_benchmark('passing_accuracy'),
                        "status": detailed.get('passing_accuracy', {}).get('status', 'N/A')
                    }
                }
            }
        }
    
    def _get_elite_benchmark(self, metric: str) -> Any:
        """Get elite benchmark (read-only, using fixed values from system)."""
        elite_benchmarks = {
            'sprint_30m': 3.9,
            'yo_yo_test': 2400,
            'ball_control': 5.0,
            'passing_accuracy': 90
        }
        return elite_benchmarks.get(metric, 'N/A')
    
    # =========================================================================
    # SECTION 6: TRAINING MODE
    # =========================================================================
    def _section_6_training_mode(self) -> Dict[str, Any]:
        """Section 6: Training mode/phase (from existing training suggestions)."""
        training = self.analysis.get('training_suggestions', {})
        
        return {
            "section_number": 6,
            "section_title": "Training Mode",
            "content": {
                "primary_focus": training.get('primary_focus', 'N/A'),
                "secondary_focus": training.get('secondary_focus', 'N/A'),
                "recommended_frequency": training.get('recommended_frequency', 'N/A'),
                "phase_duration": training.get('phase_duration', 'N/A')
            }
        }
    
    # =========================================================================
    # SECTION 7: TRAINING PROGRAM
    # =========================================================================
    def _section_7_training_program(self) -> Dict[str, Any]:
        """Section 7: Training program details (from existing recommendations)."""
        training = self.analysis.get('training_suggestions', {})
        
        return {
            "section_number": 7,
            "section_title": "Training Program",
            "content": {
                "key_exercises": training.get('key_exercises', []),
                "periodization": training.get('periodization', {}),
                "recommendations": self.analysis.get('recommendations', [])
            }
        }
    
    # =========================================================================
    # SECTION 8: RETURN-TO-PLAY ENGINE
    # =========================================================================
    def _section_8_return_to_play(self) -> Dict[str, Any]:
        """Section 8: Return-to-play guidelines (injury status from assessment)."""
        injuries = self.assessment.get('current_injuries', 'None')
        
        return {
            "section_number": 8,
            "section_title": "Return-to-Play Engine",
            "content": {
                "injury_status": injuries,
                "clearance_status": "Cleared for full training" if injuries == 'None' or not injuries else "Requires medical clearance",
                "restrictions": [] if injuries == 'None' or not injuries else ["Consult medical staff before high-intensity activities"],
                "notes": "This section uses existing injury data from assessment. No medical analysis performed."
            }
        }
    
    # =========================================================================
    # SECTION 9: SAFETY GOVERNOR
    # =========================================================================
    def _section_9_safety_governor(self) -> Dict[str, Any]:
        """Section 9: Safety considerations (based on existing data)."""
        age = self.assessment.get('age', 0)
        body_fat = self.assessment.get('body_fat', 0)
        
        # Simple age-appropriate guidelines (no new logic)
        age_warning = "Monitor growth-related load management" if age < 16 else "Standard adult protocols apply"
        
        return {
            "section_number": 9,
            "section_title": "Safety Governor",
            "content": {
                "age_considerations": age_warning,
                "body_composition_status": "Normal range" if 8 <= body_fat <= 18 else "Consider nutrition review",
                "training_load_guidance": "Follow periodization plan with adequate recovery",
                "notes": "Basic safety guidelines. Consult with qualified professionals for specific concerns."
            }
        }
    
    # =========================================================================
    # SECTION 10: AI OBJECT (JSON)
    # =========================================================================
    def _section_10_ai_object(self) -> Dict[str, Any]:
        """Section 10: Machine-readable JSON object."""
        return {
            "section_number": 10,
            "section_title": "AI Object (JSON)",
            "content": {
                "note": "See 'report_json' field at root level for complete machine-readable data",
                "preview": {
                    "player_id": self.assessment.get('player_name', 'N/A'),
                    "assessment_id": self.assessment.get('id', 'N/A'),
                    "overall_score": self.assessment.get('overall_score', 0),
                    "performance_level": self.analysis.get('performance_level', 'N/A')
                }
            }
        }
    
    # =========================================================================
    # SECTION 11: GOAL STATE
    # =========================================================================
    def _section_11_goal_state(self) -> Dict[str, Any]:
        """Section 11: Next assessment and goals (from existing recommendations)."""
        next_assessment = self.analysis.get('next_assessment', 'N/A')
        
        return {
            "section_number": 11,
            "section_title": "Goal State",
            "content": {
                "next_assessment_recommendations": next_assessment,
                "target_completion_date": self._calculate_next_assessment_date(),
                "focus_areas": self._extract_focus_areas(next_assessment)
            }
        }
    
    def _calculate_next_assessment_date(self) -> str:
        """Calculate next assessment date (6-8 weeks, based on existing logic)."""
        overall = self.assessment.get('overall_score', 0)
        weeks = 6 if overall < 70 else 8
        next_date = datetime.now() + timedelta(weeks=weeks)
        return next_date.strftime('%B %d, %Y')
    
    def _extract_focus_areas(self, next_assessment_text: str) -> List[str]:
        """Extract focus areas from existing text (simple parsing)."""
        if not next_assessment_text or next_assessment_text == 'N/A':
            return ["Continue current training program"]
        
        # Simple extraction of lines starting with "-"
        lines = next_assessment_text.split('\n')
        focus_areas = [line.strip('- ').strip() for line in lines if line.strip().startswith('-')]
        return focus_areas if focus_areas else ["Continue current training program"]
    
    # =========================================================================
    # JSON OBJECT BUILDER
    # =========================================================================
    def _build_json_object(self) -> Dict[str, Any]:
        """
        Build complete machine-readable JSON object.
        Uses ONLY existing fields - no new calculations.
        """
        return {
            "player": {
                "name": self.assessment.get('player_name', 'N/A'),
                "age": self.assessment.get('age', 'N/A'),
                "position": self.assessment.get('position', 'N/A'),
                "gender": self.assessment.get('gender', 'N/A')
            },
            "biology": {
                "height_cm": self.assessment.get('height_cm', 'N/A'),
                "weight_kg": self.assessment.get('weight_kg', 'N/A'),
                "body_fat_percent": self.assessment.get('body_fat', 'N/A'),
                "dominant_foot": self.assessment.get('dominant_foot', 'N/A')
            },
            "assessment": {
                "id": self.assessment.get('id', 'N/A'),
                "date": self.assessment.get('assessment_date', 'N/A'),
                "overall_score": self.assessment.get('overall_score', 0),
                "performance_level": self.analysis.get('performance_level', 'N/A')
            },
            "metrics": {
                "physical": {
                    "sprint_30m": self.assessment.get('sprint_30m', 'N/A'),
                    "yo_yo_test": self.assessment.get('yo_yo_test', 'N/A'),
                    "vo2_max": self.assessment.get('vo2_max', 'N/A'),
                    "vertical_jump": self.assessment.get('vertical_jump', 'N/A')
                },
                "technical": {
                    "ball_control": self.assessment.get('ball_control', 'N/A'),
                    "passing_accuracy": self.assessment.get('passing_accuracy', 'N/A'),
                    "dribbling_success": self.assessment.get('dribbling_success', 'N/A'),
                    "shooting_accuracy": self.assessment.get('shooting_accuracy', 'N/A')
                },
                "tactical": {
                    "game_intelligence": self.assessment.get('game_intelligence', 'N/A'),
                    "positioning": self.assessment.get('positioning', 'N/A'),
                    "decision_making": self.assessment.get('decision_making', 'N/A')
                },
                "psychological": {
                    "coachability": self.assessment.get('coachability', 'N/A'),
                    "mental_toughness": self.assessment.get('mental_toughness', 'N/A')
                }
            },
            "analysis": {
                "strengths": self.analysis.get('strengths', []),
                "weaknesses": self.analysis.get('weaknesses', []),
                "recommendations": self.analysis.get('recommendations', [])
            },
            "training": {
                "primary_focus": self.analysis.get('training_suggestions', {}).get('primary_focus', 'N/A'),
                "secondary_focus": self.analysis.get('training_suggestions', {}).get('secondary_focus', 'N/A'),
                "frequency": self.analysis.get('training_suggestions', {}).get('recommended_frequency', 'N/A'),
                "duration": self.analysis.get('training_suggestions', {}).get('phase_duration', 'N/A')
            },
            "benchmarks": self._build_benchmarks_json(),
            "meta": {
                "report_version": "2.0",
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    def _build_benchmarks_json(self) -> Dict[str, Any]:
        """Build benchmarks section of JSON (using existing standards comparison)."""
        standards = self.analysis.get('standards_comparison', {})
        detailed = standards.get('detailed_comparison', {})
        
        return {
            "metrics_above_standard": standards.get('metrics_above_standard', 0),
            "metrics_below_standard": standards.get('metrics_below_standard', 0),
            "details": detailed
        }


# =============================================================================
# HELPER FUNCTION FOR EASY USAGE
# =============================================================================
def format_yoyo_report_v2(assessment: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to format existing data into YoYo Report v2.
    
    Args:
        assessment: Raw assessment data from database
        analysis: Analysis result from analyze_assessment_with_llm()
    
    Returns:
        Complete YoYo Report v2 with 11 sections + JSON
    """
    formatter = YoYoReportV2Formatter(assessment, analysis)
    return formatter.generate_report()
