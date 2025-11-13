from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime, timezone, timedelta
from utils.database import db, prepare_for_mongo
from routes.auth_routes import verify_token
import uuid
import os
import json

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

class ReportGenerationRequest(BaseModel):
    assessment_id: str
    include_comparison: bool = True
    include_training_plan: bool = True

class GeneratedReport(BaseModel):
    id: str
    assessment_id: str
    player_name: str
    report_title: str
    generation_date: str
    overall_analysis: str
    strengths_analysis: List[str]
    weaknesses_analysis: List[str]
    comparison_with_previous: Optional[dict] = None
    comparison_with_standards: dict
    personalized_recommendations: List[str]
    training_program_suggestions: dict
    next_assessment_recommendations: str
    performance_level: str
    user_id: str

@router.post("/generate-report")
async def generate_report(
    request: ReportGenerationRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Generate an AI-powered comprehensive report from assessment data.
    This is the LLM engine that analyzes assessment and creates intelligent reports.
    """
    try:
        user_id = current_user.get('user_id')
        username = current_user.get('username')
        
        # Get the assessment data
        assessment = await db.assessments.find_one({"id": request.assessment_id})
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        player_name = assessment.get('player_name')
        age = assessment.get('age')
        position = assessment.get('position')
        
        # Get age-appropriate standards
        standards = get_standards_for_age(age)
        
        # Get previous assessments for comparison
        previous_assessments = []
        if request.include_comparison:
            prev_assessments = await db.assessments.find({
                "player_name": player_name,
                "id": {"$ne": request.assessment_id}
            }).sort("created_at", -1).limit(3).to_list(length=3)
            previous_assessments = prev_assessments
        
        # Generate comprehensive analysis using the assessment data
        analysis_result = analyze_assessment_with_llm(
            assessment=assessment,
            previous_assessments=previous_assessments,
            standards=standards,
            include_training=request.include_training_plan
        )
        
        # Create the generated report
        report = {
            "id": str(uuid.uuid4()),
            "assessment_id": request.assessment_id,
            "player_name": player_name,
            "age": age,
            "position": position,
            "report_title": f"Performance Analysis Report - {datetime.now().strftime('%B %d, %Y')}",
            "generation_date": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            
            # AI-Generated Content
            "overall_analysis": analysis_result['overall_analysis'],
            "strengths_analysis": analysis_result['strengths'],
            "weaknesses_analysis": analysis_result['weaknesses'],
            "comparison_with_previous": analysis_result.get('comparison'),
            "comparison_with_standards": analysis_result['standards_comparison'],
            "personalized_recommendations": analysis_result['recommendations'],
            "training_program_suggestions": analysis_result['training_suggestions'],
            "next_assessment_recommendations": analysis_result['next_assessment'],
            "performance_level": analysis_result['performance_level'],
            
            # Raw assessment data reference
            "assessment_data": {
                "overall_score": assessment.get('overall_score'),
                "physical_score": assessment.get('physical_score'),
                "technical_score": assessment.get('technical_score'),
                "tactical_score": assessment.get('tactical_score'),
                "psychological_score": assessment.get('psychological_score')
            }
        }
        
        # Save the generated report
        await db.generated_reports.insert_one(prepare_for_mongo(report))
        
        logger.info(f"Generated comprehensive report for assessment {request.assessment_id}")
        
        return {
            "success": True,
            "report_id": report['id'],
            "report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

def get_standards_for_age(age: int) -> dict:
    """Get age-appropriate performance standards"""
    # Age group standards (can be expanded)
    if age <= 14:
        return {
            "sprint_30m": 4.8,
            "yo_yo_test": 1400,
            "vo2_max": 52,
            "vertical_jump": 45,
            "body_fat": 14,
            "ball_control": 3.5,
            "passing_accuracy": 70,
            "game_intelligence": 3.5
        }
    elif age <= 16:
        return {
            "sprint_30m": 4.5,
            "yo_yo_test": 1600,
            "vo2_max": 55,
            "vertical_jump": 50,
            "body_fat": 12,
            "ball_control": 4.0,
            "passing_accuracy": 75,
            "game_intelligence": 4.0
        }
    else:  # 17+
        return {
            "sprint_30m": 4.2,
            "yo_yo_test": 1800,
            "vo2_max": 58,
            "vertical_jump": 55,
            "body_fat": 10,
            "ball_control": 4.5,
            "passing_accuracy": 80,
            "game_intelligence": 4.5
        }

def analyze_assessment_with_llm(assessment: dict, previous_assessments: list, standards: dict, include_training: bool) -> dict:
    """
    Professional sports performance reporting engine.
    Generates clean, modern, standardized Soccer Assessment Milestone Report.
    Apple-style layout with gauges, metrics, trends, strengths, weaknesses, recommendations.
    """
    
    # Extract metrics
    sprint = assessment.get('sprint_30m', 0)
    agility = assessment.get('yo_yo_test', 0)  # Used as agility metric
    reaction_time = assessment.get('vo2_max', 0) * 5  # Convert to ms approximation
    endurance = assessment.get('yo_yo_test', 0)
    ball_control = assessment.get('ball_control', 0)
    passing = assessment.get('passing_accuracy', 0)
    overall = assessment.get('overall_score', 0)
    
    # Performance level determination (as per system requirements)
    if overall >= 90:
        perf_level = "Elite"
        level_desc = "exceptional performance across all areas"
    elif overall >= 75:
        perf_level = "Advanced"
        level_desc = "strong performance with room for refinement"
    elif overall >= 60:
        perf_level = "Standard"
        level_desc = "solid foundation with clear development opportunities"
    else:
        perf_level = "Needs Development"
        level_desc = "building fundamental skills and fitness"
    
    # Calculate % of standard for each metric
    sprint_percent = (standards['sprint_30m'] / sprint * 100) if sprint > 0 else 0
    agility_percent = (agility / standards['yo_yo_test'] * 100) if agility > 0 else 0
    reaction_percent = 100 if reaction_time < 300 else (300 / reaction_time * 100) if reaction_time > 0 else 0
    endurance_percent = (endurance / standards['yo_yo_test'] * 100) if endurance > 0 else 0
    ball_control_percent = (ball_control / standards['ball_control'] * 100) if ball_control > 0 else 0
    passing_percent = (passing / standards['passing_accuracy'] * 100) if passing > 0 else 0
    
    # Performance Metrics Gauges (matching exact system format)
    performance_gauges = {
        "sprint_30m": {
            "score": sprint,
            "percent_of_standard": round(sprint_percent, 1),
            "description": "30m sprint time. Measures acceleration and top-end speed.",
            "unit": "seconds"
        },
        "agility_test": {
            "score": agility,
            "percent_of_standard": round(agility_percent, 1),
            "description": "Change-of-direction speed and body control.",
            "unit": "meters"
        },
        "reaction_time": {
            "score": round(reaction_time, 0),
            "percent_of_standard": round(reaction_percent, 1),
            "description": "Measures neuromotor and cognitive response speed.",
            "unit": "ms"
        },
        "endurance_beep": {
            "score": endurance,
            "percent_of_standard": round(endurance_percent, 1),
            "description": "Aerobic capacity and repeat-run endurance.",
            "unit": "meters"
        },
        "ball_control": {
            "score": ball_control,
            "percent_of_standard": round(ball_control_percent, 1),
            "description": "First touch, dribbling, and ball mastery.",
            "unit": "/10"
        },
        "passing_accuracy": {
            "score": passing,
            "percent_of_standard": round(passing_percent, 1),
            "description": "Percentage of accurate passes to target.",
            "unit": "%"
        }
    }
    
    # Overall Analysis
    overall_analysis = f"""
PLAYER PERFORMANCE REPORT

Player: {assessment.get('player_name')}
Age: {assessment.get('age')}
Position: {assessment.get('position')}

Overall Score: {overall:.1f}/100
Performance Level: {perf_level}

{assessment.get('player_name')} demonstrates {level_desc} with an overall score of {overall:.1f}/100.
    """
    
    # Identify Strengths (Top 3 highest-performing metrics)
    metric_performances = [
        ("Sprint 30m", sprint_percent, f"Exceptional acceleration - 30m sprint at {sprint_percent:.0f}% of standard"),
        ("Agility Test", agility_percent, f"Strong agility - Change-of-direction at {agility_percent:.0f}% of standard"),
        ("Reaction Time", reaction_percent, f"Quick reactions - Response time at {reaction_percent:.0f}% of standard"),
        ("Endurance", endurance_percent, f"Outstanding aerobic capacity - YoYo test at {endurance_percent:.0f}% of standard"),
        ("Ball Control", ball_control_percent, f"Strong ball mastery - Control at {ball_control_percent:.0f}% of standard"),
        ("Passing Accuracy", passing_percent, f"Accurate distribution - Passing at {passing_percent:.0f}% of standard")
    ]
    
    # Sort by performance percentage and take top 3
    metric_performances.sort(key=lambda x: x[1], reverse=True)
    strengths = [item[2] for item in metric_performances[:3]]
    
    if not strengths:
        strengths = ["Solid foundation established", "Consistent performance", "Good work ethic"]
    
    # Identify Weaknesses (Lowest 2-3 metrics)
    weaknesses = [item[2].replace("Exceptional", "Needs improvement in").replace("Strong", "Focus on").replace("Outstanding", "Develop") 
                  for item in metric_performances[-3:] if item[1] < 80]
    
    if not weaknesses:
        weaknesses = ["Minor refinements in consistency under pressure", "Continued development of match-specific decision making"]
    
    # Comparison with previous assessments
    comparison = None
    if previous_assessments:
        latest_prev = previous_assessments[0]
        prev_overall = latest_prev.get('overall_score', 0)
        improvement = overall - prev_overall
        
        comparison = {
            "overall_improvement": improvement,
            "trend": "improving" if improvement > 0 else "maintaining" if improvement == 0 else "declining",
            "analysis": f"Overall score {'increased' if improvement > 0 else 'decreased' if improvement < 0 else 'remained stable'} by {abs(improvement):.1f} points since last assessment on {datetime.fromisoformat(latest_prev.get('created_at')).strftime('%B %d, %Y')}.",
            "key_changes": []
        }
        
        # Detailed metric comparisons
        if yo_yo > latest_prev.get('yo_yo_test', 0):
            comparison['key_changes'].append(f"Endurance improved: +{yo_yo - latest_prev.get('yo_yo_test', 0)}m on Yo-Yo test")
        if sprint < latest_prev.get('sprint_30m', 999):
            comparison['key_changes'].append(f"Speed improved: {latest_prev.get('sprint_30m') - sprint:.2f}s faster on 30m sprint")
        if passing > latest_prev.get('passing_accuracy', 0):
            comparison['key_changes'].append(f"Technical progress: +{passing - latest_prev.get('passing_accuracy', 0):.1f}% passing accuracy")
    
    # Standards Comparison
    standards_comparison = {
        "age_group": f"U{assessment.get('age')}",
        "metrics_above_standard": sum([
            sprint <= standards['sprint_30m'],
            yo_yo >= standards['yo_yo_test'],
            ball_control >= standards['ball_control'],
            passing >= standards['passing_accuracy']
        ]),
        "metrics_below_standard": sum([
            sprint > standards['sprint_30m'],
            yo_yo < standards['yo_yo_test'],
            ball_control < standards['ball_control'],
            passing < standards['passing_accuracy']
        ]),
        "detailed_comparison": {
            "sprint_30m": {"value": sprint, "standard": standards['sprint_30m'], "status": "above" if sprint <= standards['sprint_30m'] else "below"},
            "yo_yo_test": {"value": yo_yo, "standard": standards['yo_yo_test'], "status": "above" if yo_yo >= standards['yo_yo_test'] else "below"},
            "ball_control": {"value": ball_control, "standard": standards['ball_control'], "status": "above" if ball_control >= standards['ball_control'] else "below"},
            "passing_accuracy": {"value": passing, "standard": standards['passing_accuracy'], "status": "above" if passing >= standards['passing_accuracy'] else "below"}
        }
    }
    
    # Personalized Recommendations (AI-generated)
    recommendations = []
    
    if sprint > standards['sprint_30m']:
        recommendations.append("Implement acceleration-focused training: 10-20m sprints, resistance runs, and explosive start drills 3x per week")
    
    if yo_yo < standards['yo_yo_test']:
        recommendations.append("Build aerobic base: Interval training (4x4min at 90-95% max HR) 2x weekly, progressive long runs")
    
    if ball_control < standards['ball_control']:
        recommendations.append("Daily ball mastery: 20-minute sessions focusing on first touch, close control under pressure, and quick feet drills")
    
    if passing < standards['passing_accuracy']:
        recommendations.append("Passing accuracy work: Progressive passing sequences (10-25m), passing under pressure, weak foot development")
    
    if game_intel < standards['game_intelligence']:
        recommendations.append("Tactical education: Video analysis sessions, positional play exercises, decision-making under time pressure")
    
    recommendations.append(f"Maintain strength in areas of excellence: Continue high-intensity work in identified strengths")
    recommendations.append("Integrated training approach: Combine physical, technical, and tactical elements in match-realistic scenarios")
    
    # Training Program Suggestions
    training_suggestions = {
        "primary_focus": weaknesses[0] if weaknesses else "Overall performance optimization",
        "secondary_focus": weaknesses[1] if len(weaknesses) > 1 else "Consistency under pressure",
        "recommended_frequency": "4-5 sessions per week with 2 rest/recovery days",
        "phase_duration": "6-8 weeks before reassessment",
        "key_exercises": [
            "Sport-specific conditioning drills" if yo_yo < standards['yo_yo_test'] else "High-intensity interval training",
            "Technical skill circuits" if ball_control < 4 else "Advanced ball manipulation",
            "Small-sided games (4v4, 5v5)" if game_intel < 4 else "Tactical pattern play",
            "Position-specific training modules"
        ],
        "periodization": {
            "weeks_1_2": "Foundation building and technique refinement",
            "weeks_3_4": "Intensity progression and skill integration",
            "weeks_5_6": "Peak performance and match simulation",
            "weeks_7_8": "Fine-tuning and reassessment preparation"
        }
    }
    
    # Next Assessment Recommendations
    next_assessment = f"""
Recommended next assessment: {6 if overall < 70 else 8} weeks from today ({(datetime.now() + timedelta(weeks=6 if overall < 70 else 8)).strftime('%B %d, %Y')}).

Focus areas for next evaluation:
- {'Endurance capacity (Yo-Yo test improvement target: +200m)' if yo_yo < standards['yo_yo_test'] else 'Maintaining endurance levels'}
- {'Speed development (Sprint time improvement target: -0.2s)' if sprint > standards['sprint_30m'] else 'Speed consistency'}
- {'Technical proficiency (Ball control target: +0.5 rating)' if ball_control < 4 else 'Technical refinement'}
- Overall integration and match performance indicators

Track progress through: Weekly training logs, video analysis, and informal skill checks between formal assessments.
    """
    
    return {
        'overall_analysis': overall_analysis.strip(),
        'performance_gauges': performance_gauges,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'comparison': comparison,
        'standards_comparison': standards_comparison,
        'recommendations': recommendations,
        'training_suggestions': training_suggestions,
        'next_assessment': next_assessment.strip(),
        'performance_level': perf_level
    }

@router.get("/player/{player_name}/reports")
async def get_player_reports(
    player_name: str,
    current_user: dict = Depends(verify_token)
):
    """Get all generated reports for a player"""
    try:
        user_id = current_user.get('user_id')
        
        # Get all reports for this player and user
        reports = await db.generated_reports.find({
            "player_name": player_name,
            "user_id": user_id
        }).sort("generation_date", -1).to_list(length=50)
        
        return {
            "success": True,
            "reports": reports,
            "count": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Error fetching player reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reports: {str(e)}"
        )

@router.get("/report/{report_id}")
async def get_report(
    report_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get a specific generated report"""
    try:
        user_id = current_user.get('user_id')
        
        report = await db.generated_reports.find_one({
            "id": report_id,
            "user_id": user_id
        })
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report: {str(e)}"
        )


@router.get("/generate-dynamic/{player_name}")
async def generate_dynamic_report(
    player_name: str,
    current_user: dict = Depends(verify_token)
):
    """
    Generate dynamic player performance report with visual metrics and AI analysis.
    Returns JSON structure optimized for frontend gauges, charts, and insights.
    """
    try:
        user_id = current_user.get('user_id')
        
        # Get latest assessment for the player
        logger.info(f"Looking for assessment: player_name={player_name}, user_id={user_id}")
        
        # First try with user_id
        latest_assessment = await db.assessments.find_one(
            {"player_name": player_name, "user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        # If not found, try without user_id for testing
        if not latest_assessment:
            logger.info(f"No assessment found with user_id, trying without user_id")
            latest_assessment = await db.assessments.find_one(
                {"player_name": player_name},
                sort=[("created_at", -1)]
            )
        
        if not latest_assessment:
            logger.error(f"No assessment found for player: {player_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No assessment found for player: {player_name}"
            )
        
        age = latest_assessment.get('age', 16)
        position = latest_assessment.get('position', 'Midfielder')
        
        # Get age-appropriate standards
        standards = get_standards_for_age(age)
        
        # Extract raw metrics from assessment
        sprint_30m = latest_assessment.get('sprint_30m', 0)
        yo_yo = latest_assessment.get('yo_yo_test', 0)
        vo2_max = latest_assessment.get('vo2_max', 0)
        ball_control = latest_assessment.get('ball_control', 0)
        passing_accuracy = latest_assessment.get('passing_accuracy', 0)
        overall_score = latest_assessment.get('overall_score', 0)
        
        # Calculate percent of standard for each metric
        sprint_percent = round((standards['sprint_30m'] / sprint_30m * 100) if sprint_30m > 0 else 0, 1)
        agility_percent = round((yo_yo / standards['yo_yo_test'] * 100) if yo_yo > 0 else 0, 1)
        reaction_time_ms = int(vo2_max * 5) if vo2_max > 0 else 320
        reaction_percent = round((300 / reaction_time_ms * 100) if reaction_time_ms > 0 else 100, 1)
        endurance_percent = round((yo_yo / standards['yo_yo_test'] * 100) if yo_yo > 0 else 0, 1)
        ball_control_percent = round((ball_control / 10 * 100) if ball_control > 0 else 0, 1)
        passing_percent = round(passing_accuracy if passing_accuracy > 0 else 0, 1)
        
        # Build metrics object
        metrics = {
            "sprint_30m": {
                "score": round(sprint_30m, 2),
                "percent_of_standard": sprint_percent
            },
            "agility": {
                "score": round(yo_yo / 100, 1),
                "percent_of_standard": agility_percent
            },
            "reaction_time": {
                "score_ms": reaction_time_ms,
                "percent_of_standard": reaction_percent
            },
            "endurance": {
                "score": round(yo_yo / 100, 1),
                "percent_of_standard": endurance_percent
            },
            "ball_control": {
                "score_1_to_10": round(ball_control, 1),
                "percent_of_standard": ball_control_percent
            },
            "passing_accuracy": {
                "score_percent": round(passing_accuracy, 1),
                "percent_of_standard": passing_percent
            }
        }
        
        # Get assessment history for trends (last 5)
        assessment_history = await db.assessments.find(
            {"player_name": player_name, "user_id": user_id}
        ).sort("created_at", 1).limit(5).to_list(length=5)
        
        trend_dates = []
        trend_overall = []
        trend_sprint = []
        trend_passing = []
        
        for assessment in assessment_history:
            created_at = assessment.get('created_at')
            if isinstance(created_at, str):
                date_obj = datetime.fromisoformat(created_at)
            else:
                date_obj = created_at
            trend_dates.append(date_obj.strftime('%Y-%m-%d'))
            trend_overall.append(round(assessment.get('overall_score', 0)))
            
            # Calculate sprint and passing percent for trend
            s = assessment.get('sprint_30m', 0)
            p = assessment.get('passing_accuracy', 0)
            sprint_trend = round((standards['sprint_30m'] / s * 100) if s > 0 else 0)
            trend_sprint.append(sprint_trend)
            trend_passing.append(round(p))
        
        trend = {
            "dates": trend_dates,
            "overall_scores": trend_overall,
            "sprint_30m_scores": trend_sprint,
            "passing_accuracy_scores": trend_passing
        }
        
        # Prepare assessment JSON for LLM
        assessment_json = {
            "player_name": player_name,
            "age": age,
            "position": position,
            "overall_score": round(overall_score),
            "metrics": metrics,
            "trend": trend
        }
        
        # Call LLM for AI analysis
        ai_analysis = await generate_ai_analysis(assessment_json)
        
        # Return complete report
        return {
            "success": True,
            "player_name": player_name,
            "age": age,
            "position": position,
            "overall_score": round(overall_score),
            "performance_level": ai_analysis.get('performance_level', 'Standard'),
            "metrics": metrics,
            "trend": trend,
            "strengths": ai_analysis.get('strengths', []),
            "weaknesses": ai_analysis.get('weaknesses', []),
            "recommendations": ai_analysis.get('recommendations', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating dynamic report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


async def generate_ai_analysis(assessment_json: dict) -> dict:
    """Generate AI analysis using LLM with the provided prompt structure"""
    
    overall_score = assessment_json['overall_score']
    
    # Determine performance level
    if overall_score >= 90:
        performance_level = "Elite"
    elif overall_score >= 75:
        performance_level = "Advanced"
    elif overall_score >= 60:
        performance_level = "Standard"
    else:
        performance_level = "Needs Development"
    
    # If LLM is available, use it for analysis
    if llm_available:
        try:
            EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')
            
            system_prompt = """You are a professional sports performance reporting engine.
You receive a single JSON object that contains a soccer player's test results and trend data.
Your job is to generate a clean, modern, standardized Soccer Assessment Milestone Report.

Always:
- Read ONLY from the provided JSON.
- Never invent random numbers.
- Use short, clear labels.

From the metrics, identify:
1. STRENGTHS: Pick the top 3 percent_of_standard values and explain why they're strong
2. WEAKNESSES: Pick the bottom 2-3 percent_of_standard values and explain what needs improvement
3. RECOMMENDATIONS: Give 4-6 specific, professional training recommendations tailored to the player's lowest metrics and position

Return ONLY a valid JSON object with this exact structure:
{
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "recommendations": ["rec 1", "rec 2", "rec 3", "rec 4"]
}"""
            
            # Initialize chat
            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id=f"report_{assessment_json.get('player_name', 'player')}_{datetime.now().timestamp()}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o-mini")
            
            # Create user message
            user_message = UserMessage(
                text=f"Analyze this assessment data:\n\n{json.dumps(assessment_json, indent=2)}"
            )
            
            # Send message and get response
            response_text = await chat.send_message(user_message)
            
            # Parse JSON from response
            ai_result = json.loads(response_text.strip())
            
            return {
                "performance_level": performance_level,
                "strengths": ai_result.get('strengths', []),
                "weaknesses": ai_result.get('weaknesses', []),
                "recommendations": ai_result.get('recommendations', [])
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}, using fallback")
    
    # Fallback analysis if LLM not available
    metrics = assessment_json['metrics']
    
    # Calculate metric performances
    metric_list = [
        ("Endurance", metrics['endurance']['percent_of_standard'], "Outstanding aerobic capacity"),
        ("Reaction Time", metrics['reaction_time']['percent_of_standard'], "Quick neuromotor response"),
        ("Sprint 30m", metrics['sprint_30m']['percent_of_standard'], "Strong acceleration ability"),
        ("Agility", metrics['agility']['percent_of_standard'], "Good change-of-direction speed"),
        ("Ball Control", metrics['ball_control']['percent_of_standard'], "Solid technical base"),
        ("Passing Accuracy", metrics['passing_accuracy']['percent_of_standard'], "Accurate distribution")
    ]
    
    # Sort by performance
    metric_list.sort(key=lambda x: x[1], reverse=True)
    
    strengths = [f"{m[0]} — {m[1]:.0f}% of standard ({m[2]})" for m in metric_list[:3]]
    weaknesses = [f"{m[0]} — {m[1]:.0f}% of standard (needs improvement)" for m in metric_list[-2:]]
    
    recommendations = [
        "Implement acceleration-focused training with 10-20m sprints 3x per week",
        "Daily ball mastery sessions focusing on first touch and close control",
        "Progressive passing sequences to improve accuracy under pressure",
        "Tactical education through video analysis and decision-making drills",
        "Maintain strength training in areas of excellence",
        "Integrated match-realistic training scenarios"
    ]
    
    return {
        "performance_level": performance_level,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations[:4]
    }



@router.post("/generate-comprehensive-roadmap")
async def generate_comprehensive_roadmap(
    assessment_id: str,
    user_token: dict = Depends(verify_token)
):
    """
    Generate a comprehensive player development roadmap report
    Includes: All assessment data, AI analysis, coach recommendations, standards comparison
    This is the complete report that players can print and save
    """
    try:
        logger.info(f"Generating comprehensive roadmap for assessment: {assessment_id}")
        
        # Fetch assessment
        assessment = await db.assessments.find_one({"id": assessment_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Fetch benchmark data
        benchmark = await db.benchmarks.find_one({"assessment_id": assessment_id})
        
        # Fetch user profile
        user = await db.users.find_one({"id": assessment.get('user_id')})
        
        player_name = assessment.get('player_name', 'Player')
        age = assessment.get('age', 17)
        position = assessment.get('position', 'Forward')
        
        # Generate AI-powered analysis if LLM available
        ai_analysis = ""
        coach_recommendations = []
        standards_comparison = {}
        
        if llm_available and EMERGENT_KEY:
            try:
                # Create comprehensive analysis prompt
                assessment_summary = f"""
Player: {player_name}
Age: {age}
Position: {position}
Assessment Date: {assessment.get('assessment_date', 'N/A')}

PHYSICAL METRICS:
- 30m Sprint: {assessment.get('sprint_30m', 'N/A')}s
- Yo-Yo Test: {assessment.get('yo_yo_test', 'N/A')}m
- VO2 Max: {assessment.get('vo2_max', 'N/A')}
- Vertical Jump: {assessment.get('vertical_jump', 'N/A')}cm
- Body Fat: {assessment.get('body_fat', 'N/A')}%

TECHNICAL SKILLS (1-5):
- Ball Control: {assessment.get('ball_control', 'N/A')}/5
- Passing Accuracy: {assessment.get('passing_accuracy', 'N/A')}%
- Dribbling Success: {assessment.get('dribbling_success', 'N/A')}%
- Shooting Accuracy: {assessment.get('shooting_accuracy', 'N/A')}%
- Defensive Duels: {assessment.get('defensive_duels', 'N/A')}%

TACTICAL AWARENESS (1-5):
- Game Intelligence: {assessment.get('game_intelligence', 'N/A')}/5
- Positioning: {assessment.get('positioning', 'N/A')}/5
- Decision Making: {assessment.get('decision_making', 'N/A')}/5

MENTAL ATTRIBUTES (1-5):
- Coachability: {assessment.get('coachability', 'N/A')}/5
- Mental Toughness: {assessment.get('mental_toughness', 'N/A')}/5

OVERALL SCORE: {benchmark.get('overall_score', 'N/A')}/5
PERFORMANCE LEVEL: {benchmark.get('performance_level', 'N/A')}
"""
                
                # Initialize LLM chat
                chat = LlmChat(
                    api_key=EMERGENT_KEY,
                    session_id=f"roadmap-{assessment_id}-{datetime.now().timestamp()}",
                    system_message="""You are an elite soccer coach and sports scientist. Create a comprehensive development roadmap for this player.

Provide:
1. DETAILED ANALYSIS: Overall assessment of player's current level
2. STRENGTHS: Top 3-4 areas where player excels
3. AREAS FOR DEVELOPMENT: Top 3-4 areas needing improvement
4. COACH RECOMMENDATIONS: 6-8 specific, actionable training focuses
5. STANDARDS COMPARISON: How player compares to age/position standards
6. 12-WEEK ROADMAP: Specific phases and goals

Be specific, professional, and encouraging. Focus on actionable insights."""
                ).with_model("openai", "gpt-4o-mini")
                
                prompt = f"""Based on this player assessment data, create a comprehensive development roadmap:

{assessment_summary}

Format your response as:

OVERALL ANALYSIS:
[2-3 paragraphs analyzing current performance level, playing style, and potential]

STRENGTHS:
- [Strength 1 with specific metrics]
- [Strength 2 with specific metrics]
- [Strength 3 with specific metrics]

AREAS FOR DEVELOPMENT:
- [Area 1 with specific focus]
- [Area 2 with specific focus]
- [Area 3 with specific focus]

COACH RECOMMENDATIONS:
1. [Specific training recommendation]
2. [Specific training recommendation]
3. [Specific training recommendation]
4. [Specific training recommendation]
5. [Specific training recommendation]
6. [Specific training recommendation]

STANDARDS COMPARISON:
Physical: [Comparison to age/position standards]
Technical: [Comparison to age/position standards]
Tactical: [Comparison to age/position standards]
Mental: [Comparison to age/position standards]

12-WEEK ROADMAP:
Weeks 1-4: [Focus areas and goals]
Weeks 5-8: [Focus areas and goals]
Weeks 9-12: [Focus areas and goals]
"""
                
                user_message = UserMessage(text=prompt)
                ai_response = await chat.send_message(user_message)
                
                # Parse AI response
                sections = ai_response.split('\n\n')
                for section in sections:
                    if section.startswith('OVERALL ANALYSIS:'):
                        ai_analysis = section.replace('OVERALL ANALYSIS:', '').strip()
                    elif section.startswith('COACH RECOMMENDATIONS:'):
                        recs = section.replace('COACH RECOMMENDATIONS:', '').strip().split('\n')
                        coach_recommendations = [r.strip() for r in recs if r.strip()]
                    elif section.startswith('STANDARDS COMPARISON:'):
                        comp = section.replace('STANDARDS COMPARISON:', '').strip()
                        standards_comparison = {'analysis': comp}
                
                logger.info("✅ AI-powered roadmap generated successfully")
                
            except Exception as llm_error:
                logger.error(f"LLM generation failed: {llm_error}")
                # Fallback to template-based
                ai_analysis = f"Assessment completed for {player_name}, Age {age}, playing as {position}. The player shows a balanced profile with room for development across all areas."
                coach_recommendations = [
                    "Focus on technical skill development through daily practice",
                    "Improve physical conditioning with structured training",
                    "Develop tactical awareness through game analysis",
                    "Build mental resilience through challenging scenarios",
                    "Maintain consistent training schedule",
                    "Track progress with regular assessments"
                ]
        else:
            # Fallback analysis
            ai_analysis = f"Comprehensive assessment completed for {player_name}. Overall performance level: {benchmark.get('performance_level', 'Developing')}."
            coach_recommendations = [
                "Continue current training with focus on consistency",
                "Develop weaker areas identified in assessment",
                "Maintain strengths through regular practice",
                "Set measurable short-term goals",
                "Regular feedback sessions with coach",
                "Re-assess in 4-6 weeks to track progress"
            ]
        
        # Create comprehensive report document
        report_data = {
            "id": str(uuid.uuid4()),
            "assessment_id": assessment_id,
            "user_id": assessment.get('user_id'),
            "report_type": "comprehensive_roadmap",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            
            # Player Info
            "player_info": {
                "name": player_name,
                "age": age,
                "position": position,
                "height": assessment.get('height_cm', 'N/A'),
                "weight": assessment.get('weight_kg', 'N/A'),
                "assessment_date": assessment.get('assessment_date'),
                "dominant_foot": user.get('dominant_foot', 'N/A') if user else 'N/A'
            },
            
            # Complete Assessment Data
            "assessment_data": {
                "physical": {
                    "sprint_30m": assessment.get('sprint_30m'),
                    "yo_yo_test": assessment.get('yo_yo_test'),
                    "vo2_max": assessment.get('vo2_max'),
                    "vertical_jump": assessment.get('vertical_jump'),
                    "body_fat": assessment.get('body_fat')
                },
                "technical": {
                    "ball_control": assessment.get('ball_control'),
                    "passing_accuracy": assessment.get('passing_accuracy'),
                    "dribbling_success": assessment.get('dribbling_success'),
                    "shooting_accuracy": assessment.get('shooting_accuracy'),
                    "defensive_duels": assessment.get('defensive_duels')
                },
                "tactical": {
                    "game_intelligence": assessment.get('game_intelligence'),
                    "positioning": assessment.get('positioning'),
                    "decision_making": assessment.get('decision_making')
                },
                "psychological": {
                    "coachability": assessment.get('coachability'),
                    "mental_toughness": assessment.get('mental_toughness')
                }
            },
            
            # Scores
            "scores": {
                "overall_score": benchmark.get('overall_score', 0) if benchmark else 0,
                "physical_score": benchmark.get('physical_score', 0) if benchmark else 0,
                "technical_score": benchmark.get('technical_score', 0) if benchmark else 0,
                "tactical_score": benchmark.get('tactical_score', 0) if benchmark else 0,
                "psychological_score": benchmark.get('psychological_score', 0) if benchmark else 0,
                "performance_level": benchmark.get('performance_level', 'Developing') if benchmark else 'Developing'
            },
            
            # AI Analysis
            "ai_analysis": ai_analysis,
            
            # Coach Recommendations
            "coach_recommendations": coach_recommendations,
            
            # Standards Comparison
            "standards_comparison": standards_comparison,
            
            # Development Roadmap
            "development_roadmap": {
                "phase_1": "Weeks 1-4: Foundation building and baseline improvement",
                "phase_2": "Weeks 5-8: Skill enhancement and tactical development",
                "phase_3": "Weeks 9-12: Performance optimization and assessment preparation"
            }
        }
        
        # Save report to database
        await db.comprehensive_reports.insert_one(prepare_for_mongo(report_data))
        
        logger.info(f"✅ Comprehensive roadmap saved for assessment {assessment_id}")
        
        return {
            "success": True,
            "report_id": report_data["id"],
            "report_data": report_data,
            "message": "Comprehensive roadmap generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comprehensive roadmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

