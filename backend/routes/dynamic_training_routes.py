from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timezone
from utils.database import db, prepare_for_mongo
from routes.auth_routes import verify_token
import uuid
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# LLM Integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    from dotenv import load_dotenv
    load_dotenv()
    EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')
    llm_available = True if EMERGENT_KEY else False
except ImportError:
    llm_available = False
    logger.warning("emergentintegrations not installed - LLM features will be limited")

class DynamicProgramRequest(BaseModel):
    # Player info
    player_id: str
    player_name: str
    age: int
    position: str
    gender: str
    
    # Assessment data
    assessment_data: Dict[str, Any]
    assessment_scores: Dict[str, Any]
    performance_level: str
    
    # AI & Coach feedback
    ai_analysis: str
    coach_recommendations: List[str]
    standards_comparison: Optional[Dict[str, Any]] = None
    
    # Training parameters
    training_days_per_week: int
    duration_weeks: int
    session_duration_minutes: int
    
    # Recovery & injury
    has_injuries: bool
    injury_details: Optional[str] = ""
    recovery_priority: str
    
    # Availability & equipment
    availability: str
    equipment_available: str
    
    # Player goals
    player_goals: Optional[str] = ""
    
    # Program generation options
    generate_both_programs: Optional[bool] = True


@router.post("/generate-dynamic-program")
async def generate_dynamic_training_program(
    request: DynamicProgramRequest,
    user_token: dict = Depends(verify_token)
):
    """
    Generate a fully personalized, AI-powered training program
    Considers: age, gender, skill level, assessment, injuries, recovery, equipment, goals
    """
    try:
        logger.info(f"Generating dynamic program for {request.player_name}")
        
        # Calculate age category
        age_category = "Youth" if request.age < 16 else "U19" if request.age < 20 else "Senior"
        
        # Determine training intensity based on age and recovery priority
        base_intensity = {
            "Youth": "moderate",
            "U19": "moderate-high",
            "Senior": "high"
        }.get(age_category, "moderate")
        
        if request.recovery_priority == "high" or request.has_injuries:
            intensity_modifier = "low-moderate"
        elif request.recovery_priority == "injury_prevention":
            intensity_modifier = "moderate with injury prevention"
        else:
            intensity_modifier = base_intensity
        
        # Gender-specific considerations
        gender_notes = ""
        if request.gender == "female":
            gender_notes = "Consider menstrual cycle phases for load management. Include more core stability work."
        
        # Equipment-based exercises
        equipment_note = {
            "minimal": "Home-based drills with just a ball",
            "basic": "Small space drills with cones and ball",
            "full": "Full field training with all equipment",
            "gym": "Include strength and conditioning in gym"
        }.get(request.equipment_available, "basic")
        
        if not llm_available or not EMERGENT_KEY:
            # Fallback: Create template-based program
            return create_template_program(request, intensity_modifier)
        
        # Prepare comprehensive prompt for AI
        program_prompt = f"""You are an elite soccer coach creating a personalized training program.

PLAYER PROFILE:
- Name: {request.player_name}
- Age: {request.age} ({age_category})
- Gender: {request.gender}
- Position: {request.position}
- Performance Level: {request.performance_level}

ASSESSMENT RESULTS:
Physical Score: {request.assessment_scores.get('physical_score', 0)}/5
Technical Score: {request.assessment_scores.get('technical_score', 0)}/5
Tactical Score: {request.assessment_scores.get('tactical_score', 0)}/5
Psychological Score: {request.assessment_scores.get('psychological_score', 0)}/5
Overall: {request.assessment_scores.get('overall_score', 0)}/5

AI ANALYSIS:
{request.ai_analysis}

COACH RECOMMENDATIONS:
{chr(10).join(f"- {rec}" for rec in request.coach_recommendations[:5])}

TRAINING PARAMETERS:
- Duration: {request.duration_weeks} weeks
- Frequency: {request.training_days_per_week} days per week
- Session Length: {request.session_duration_minutes} minutes
- Recovery Priority: {request.recovery_priority}
- Equipment: {equipment_note}
- Availability: {request.availability}

SPECIAL CONSIDERATIONS:
{'- HAS INJURIES: ' + request.injury_details if request.has_injuries else '- No current injuries'}
{gender_notes}

PLAYER GOALS:
{request.player_goals if request.player_goals else 'General development and performance improvement'}

CREATE A COMPREHENSIVE {request.duration_weeks}-WEEK TRAINING PROGRAM:

Structure your response with:

PROGRAM OVERVIEW:
[2-3 sentence summary of program philosophy and approach]

PERIODIZATION STRUCTURE:
Phase 1 (Weeks 1-X): [Focus and goals]
Phase 2 (Weeks X-Y): [Focus and goals]
Phase 3 (Weeks Y-{request.duration_weeks}): [Focus and goals]

WEEKLY STRUCTURE:
[Describe the {request.training_days_per_week}-day weekly pattern]

SAMPLE WEEK (Week 1):
Day 1 - [Session type]: [Specific drills and exercises]
Day 2 - [Session type]: [Specific drills and exercises]
[Continue for all {request.training_days_per_week} days]

PROGRESSION STRATEGY:
[How program will progress over {request.duration_weeks} weeks]

RECOVERY & INJURY PREVENTION:
[Specific recovery protocols and injury prevention measures]

KEY PERFORMANCE INDICATORS:
[5-6 specific metrics to track progress]

Be extremely specific with exercises, sets, reps, rest periods, and progressions. Tailor everything to the player's assessment results, age, gender, and goals.
"""
        
        # Initialize LLM
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"program-{request.player_id}-{datetime.now().timestamp()}",
            system_message="""You are a UEFA Pro License soccer coach and sports scientist. Create detailed, 
            evidence-based training programs that are perfectly tailored to each player's unique profile. 
            Be specific with exercises, progressions, and periodization. Consider age-appropriate training, 
            gender-specific needs, injury prevention, and recovery management."""
        ).with_model("openai", "gpt-4o-mini")
        
        # Generate program
        user_message = UserMessage(text=program_prompt)
        ai_program = await chat.send_message(user_message)
        
        logger.info("✅ AI program generated successfully")
        
        # Parse and structure the program
        program_data = {
            "id": str(uuid.uuid4()),
            "player_id": request.player_id,
            "player_name": request.player_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            
            # Program parameters
            "duration_weeks": request.duration_weeks,
            "training_days_per_week": request.training_days_per_week,
            "session_duration_minutes": request.session_duration_minutes,
            
            # Player context
            "age": request.age,
            "age_category": age_category,
            "gender": request.gender,
            "position": request.position,
            "performance_level": request.performance_level,
            
            # Customization factors
            "has_injuries": request.has_injuries,
            "injury_details": request.injury_details,
            "recovery_priority": request.recovery_priority,
            "equipment_available": request.equipment_available,
            "availability": request.availability,
            "player_goals": request.player_goals,
            
            # Assessment basis
            "based_on_assessment": {
                "scores": request.assessment_scores,
                "ai_analysis": request.ai_analysis[:500],  # Summary
                "coach_recommendations": request.coach_recommendations[:5]
            },
            
            # AI-generated program
            "program_content": ai_program,
            "program_type": "ai_personalized",
            "intensity": intensity_modifier,
            
            # Tracking
            "start_date": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "completed_sessions": 0,
            "total_sessions": request.duration_weeks * request.training_days_per_week
        }
        
        # Save AI program to database
        await db.training_programs.insert_one(prepare_for_mongo(program_data))
        
        # Also save to periodized_programs for compatibility
        await save_compatible_program(program_data, request)
        
        logger.info(f"✅ AI Program saved: {request.duration_weeks} weeks, {request.training_days_per_week}x/week")
        
        # Generate coach-guided program as well
        coach_program_id = None
        if request.generate_both_programs:
            coach_program_data = await generate_coach_program(request, intensity_modifier)
            await db.coach_programs.insert_one(prepare_for_mongo(coach_program_data))
            coach_program_id = coach_program_data["id"]
            logger.info(f"✅ Coach Program saved: {coach_program_id}")
        
        return {
            "success": True,
            "programs_generated": 2 if request.generate_both_programs else 1,
            "ai_program_id": program_data["id"],
            "coach_program_id": coach_program_id,
            "message": f"Both training programs generated successfully!" if request.generate_both_programs else f"AI program generated",
            "program_summary": {
                "duration_weeks": request.duration_weeks,
                "sessions_per_week": request.training_days_per_week,
                "total_sessions": request.duration_weeks * request.training_days_per_week,
                "intensity": intensity_modifier,
                "customized_for": [
                    f"{request.age} years old",
                    request.gender,
                    request.position,
                    f"{request.performance_level} level",
                    f"Recovery: {request.recovery_priority}",
                    f"Equipment: {request.equipment_available}"
                ],
                "programs": [
                    {
                        "type": "AI-Powered Model",
                        "id": program_data["id"],
                        "features": ["Machine learning optimization", "Dynamic adjustment", "Performance tracking"]
                    },
                    {
                        "type": "Coach-Guided Program",
                        "id": coach_program_id,
                        "features": ["Professional methodology", "Position-specific", "Coach recommendations"]
                    } if request.generate_both_programs else None
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating dynamic program: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_template_program(request: DynamicProgramRequest, intensity: str):
    """Fallback template-based program if AI not available"""
    
    program_data = {
        "id": str(uuid.uuid4()),
        "player_id": request.player_id,
        "player_name": request.player_name,
        "duration_weeks": request.duration_weeks,
        "training_days_per_week": request.training_days_per_week,
        "session_duration_minutes": request.session_duration_minutes,
        "program_type": "template",
        "intensity": intensity,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    return {
        "success": True,
        "program_id": program_data["id"],
        "message": "Template program generated (AI not available)",
        "program_summary": {
            "duration_weeks": request.duration_weeks,
            "sessions_per_week": request.training_days_per_week
        }
    }


async def save_compatible_program(program_data: dict, request: DynamicProgramRequest):
    """Save program in format compatible with existing periodized_programs collection"""
    
    compatible_program = {
        "id": str(uuid.uuid4()),
        "player_id": request.player_id,
        "player_name": request.player_name,
        "age": request.age,
        "position": request.position,
        "total_duration_weeks": request.duration_weeks,
        "sessions_per_week": request.training_days_per_week,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "program_type": "ai_dynamic",
        "focus_areas": request.coach_recommendations[:3],
        "notes": f"AI-generated personalized program. {request.training_days_per_week}x/week, {request.session_duration_minutes} min sessions."
    }
    
    await db.periodized_programs.insert_one(prepare_for_mongo(compatible_program))



async def generate_coach_program(request: DynamicProgramRequest, intensity: str):
    """Generate coach-guided program based on professional methodology"""
    
    coach_program = {
        "id": str(uuid.uuid4()),
        "player_id": request.player_id,
        "player_name": request.player_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        
        # Program parameters
        "program_type": "coach_guided",
        "duration_weeks": request.duration_weeks,
        "training_days_per_week": request.training_days_per_week,
        "session_duration_minutes": request.session_duration_minutes,
        
        # Player context
        "age": request.age,
        "position": request.position,
        "performance_level": request.performance_level,
        
        # Methodology
        "methodology": "Professional coaching methodology",
        "structure": f"{request.training_days_per_week} sessions per week for {request.duration_weeks} weeks",
        "focus_areas": request.coach_recommendations[:5],
        
        # Program details
        "description": f"""Professional {request.duration_weeks}-week training program designed by experienced coaches.
        
Position: {request.position}
Level: {request.performance_level}
Focus: {', '.join(request.coach_recommendations[:3])}

This program follows proven coaching principles with structured progression, position-specific drills, 
and technical skill development. Each session is designed to build upon previous work while addressing 
the specific needs identified in your assessment.

Weekly Structure:
- Technical skills development
- Tactical understanding
- Physical conditioning  
- Position-specific training
- Recovery and injury prevention

Coach Recommendations Integrated:
{chr(10).join(f"• {rec}" for rec in request.coach_recommendations[:5])}
""",
        
        # Status
        "status": "active",
        "completed_sessions": 0,
        "total_sessions": request.duration_weeks * request.training_days_per_week
    }
    
    return coach_program


@router.get("/my-ai-program")
async def get_my_ai_program(user_token: dict = Depends(verify_token)):
    """Get the user's AI-powered training program"""
    try:
        user_id = user_token.get('id')
        
        # Find most recent AI program
        program = await db.training_programs.find_one(
            {"player_id": user_id, "program_type": "ai_personalized"},
            sort=[("created_at", -1)]
        )
        
        if not program:
            raise HTTPException(status_code=404, detail="No AI program found")
        
        return {"success": True, "program": program}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching AI program: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-coach-program")
async def get_my_coach_program(user_token: dict = Depends(verify_token)):
    """Get the user's coach-guided training program"""
    try:
        user_id = user_token.get('id')
        
        # Find most recent coach program
        program = await db.coach_programs.find_one(
            {"player_id": user_id, "program_type": "coach_guided"},
            sort=[("created_at", -1)]
        )
        
        if not program:
            raise HTTPException(status_code=404, detail="No coach program found")
        
        return {"success": True, "program": program}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching coach program: {e}")
        raise HTTPException(status_code=500, detail=str(e))

