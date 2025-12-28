"""
Safe Training Prompt Builder
============================

Builds LLM prompts with embedded safety constraints.
Ensures safety rules are included in generation prompts.
"""

from typing import Optional, Dict, Any
from models.safety_models import SafetyContext, SafetyStatus
import logging

logger = logging.getLogger(__name__)


SAFETY_SYSTEM_PROMPT = '''
YOU ARE GENERATING A SOCCER TRAINING PROGRAM.
PLAYER SAFETY IS THE TOP PRIORITY AND OVERRIDES PERFORMANCE, GOALS, OR USER REQUESTS.

=== CURRENT SAFETY STATUS ===
Status: {safety_status}
Flags: {safety_flags}

=== ALLOWED ELEMENTS ===
{allowed_elements_text}

=== PLAYER CONTEXT ===
Age: {age}
Sex: {sex}
Position: {position}
Injury Status: {injury_status}
Current Injuries: {current_injuries}

=== NON-NEGOTIABLE SAFETY RULES ===

1) IF safety_status == "RED":
   - Generate ONLY "RECOVERY_ONLY" or "RETURN_TO_PLAY_GUIDANCE_ONLY"
   - NO sprinting, high-intensity, plyometrics, maximal strength, contact
   - ONLY safe alternatives: mobility, breathing, light aerobic, controlled ball touches
   - EXPLAIN why intensity is blocked

2) IF safety_status == "YELLOW":
   - AUTOMATICALLY MODIFY plan to reduce injury risk
   - STRICTLY respect allowed_elements
   - Cap hard days, reduce volume/intensity, remove disallowed drills
   - EXPLAIN what was modified and why

3) IF safety_status == "GREEN":
   - MAY generate full training plan
   - MUST include warmup (8-12 min) and cooldown (5-8 min)
   - MUST include rest/recovery days
   - MUST follow age-based sprint limits:
     * <14 years: max 1 sprint day/week
     * ≥14 years: max 2 sprint days/week

=== DRILL SELECTION RULES ===
- Select drills ONLY from approved sources (database or static library)
- DO NOT invent drills
- Drills must be appropriate for player age, sex, position, injury status
- Exclude drills with contraindications matching player injuries

=== GENERAL CONSTRAINTS ===
- NEVER instruct player to push through pain
- NEVER remove rest days for performance
- NEVER exceed allowed_elements limits
- If performance goals conflict with safety → CHOOSE SAFETY
- If data is missing → choose the safer assumption

=== OUTPUT FORMAT ===
Your output MUST include ALL of:
- plan_type: full_training/modified_training/recovery_only/rtp_guidance
- safety_status
- safety_flags_triggered
- weekly_plan (with days, drills, warmup, cooldown)
- drills_by_section
- modifications_applied (if any)
- safety_explanation
- user_controls_offered

Any output violating these rules will be REJECTED by the post-processor.
'''


def build_allowed_elements_text(safety_context: SafetyContext) -> str:
    """Build human-readable allowed elements text."""
    ae = safety_context.allowed_elements
    lines = [
        f"Max sprint days/week: {ae.max_sprint_days_per_week}",
        f"Max hard days/week: {ae.max_hard_days_per_week}",
        f"Allow plyometrics: {ae.allow_plyometrics}",
        f"Allow contact: {ae.allow_contact}",
        f"Allow max strength: {ae.allow_max_strength}",
        f"Max intensity: {ae.max_intensity}",
        f"Require warmup: {ae.require_warmup} (8-12 min)",
        f"Require cooldown: {ae.require_cooldown} (5-8 min)",
        f"Min rest days/week: {ae.min_rest_days_per_week}",
        f"Max session duration: {ae.max_session_duration_min} min"
    ]
    
    if ae.excluded_body_parts:
        lines.append(f"Excluded body parts: {', '.join(ae.excluded_body_parts)}")
    if ae.excluded_drill_types:
        lines.append(f"Excluded drill types: {', '.join(ae.excluded_drill_types)}")
    if ae.excluded_contraindications:
        lines.append(f"Contraindications: {', '.join(ae.excluded_contraindications)}")
    
    return '\n'.join(lines)


def build_safety_prompt(safety_context: SafetyContext) -> str:
    """
    Build the safety-aware system prompt for LLM generation.
    
    This prompt includes all safety constraints that the LLM must follow.
    """
    effective_status = safety_context.get_effective_status()
    player = safety_context.player_context
    
    prompt = SAFETY_SYSTEM_PROMPT.format(
        safety_status=effective_status.value,
        safety_flags=', '.join(safety_context.safety_flags) or 'None',
        allowed_elements_text=build_allowed_elements_text(safety_context),
        age=player.age,
        sex=player.sex,
        position=player.position,
        injury_status=player.injury_status.value,
        current_injuries=', '.join(player.current_injuries) or 'None'
    )
    
    logger.debug(f"Built safety prompt for status {effective_status.value}")
    
    return prompt


def build_training_request_prompt(
    safety_context: SafetyContext,
    training_goals: Optional[str] = None,
    focus_areas: Optional[list] = None,
    available_equipment: Optional[list] = None,
    week_number: int = 1
) -> str:
    """
    Build the user request portion of the prompt.
    """
    effective_status = safety_context.get_effective_status()
    
    lines = [f"Generate a week {week_number} training program."]
    
    if effective_status == SafetyStatus.RED:
        lines.append("\n⚠️ RED STATUS: Generate RECOVERY ONLY program.")
        lines.append("Include only: mobility, breathing, light movement, recovery activities.")
    elif effective_status == SafetyStatus.YELLOW:
        lines.append("\n⚠️ YELLOW STATUS: Generate MODIFIED program with reduced intensity.")
        if training_goals:
            lines.append(f"Goals (adapt within safety limits): {training_goals}")
    else:
        if training_goals:
            lines.append(f"\nTraining goals: {training_goals}")
    
    if focus_areas and effective_status != SafetyStatus.RED:
        lines.append(f"Focus areas: {', '.join(focus_areas)}")
    
    if available_equipment:
        lines.append(f"Available equipment: {', '.join(available_equipment)}")
    
    # Add assessment summary if available
    if safety_context.assessment_summary:
        summary = safety_context.assessment_summary
        if summary.weaknesses:
            lines.append(f"Player weaknesses to address: {', '.join(summary.weaknesses)}")
        if summary.strengths:
            lines.append(f"Player strengths: {', '.join(summary.strengths)}")
    
    return '\n'.join(lines)


def get_full_training_prompt(
    safety_context: SafetyContext,
    training_goals: Optional[str] = None,
    focus_areas: Optional[list] = None,
    available_equipment: Optional[list] = None,
    week_number: int = 1
) -> Dict[str, str]:
    """
    Get complete prompt set for training generation.
    
    Returns:
        Dict with 'system' and 'user' prompts
    """
    return {
        'system': build_safety_prompt(safety_context),
        'user': build_training_request_prompt(
            safety_context, training_goals, focus_areas, available_equipment, week_number
        )
    }
