"""
API Routes for AI Coach & Computer Vision
Predictive Models + MediaPipe Analysis + AI Feedback
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, Dict, Any, List
import logging
import os
from datetime import datetime, timezone
import base64
import cv2
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ai_predictive_models import PredictiveModelEngine
from mediapipe_vision import MediaPipePoseAnalyzer, VideoAnalyzer, RepCounter
from emergentintegrations.llm.chat import LlmChat, UserMessage
from utils.database import get_database
from pydantic import BaseModel

router = APIRouter(prefix="/ai-coach", tags=["AI Coach & Vision"])
logger = logging.getLogger(__name__)

# Initialize engines
predictive_engine = PredictiveModelEngine()
pose_analyzer = MediaPipePoseAnalyzer()
video_analyzer = VideoAnalyzer()

# Emergent LLM configuration
EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')

class PredictiveAnalysisRequest(BaseModel):
    player_name: str
    days_to_match: Optional[int] = 7
    goals: Optional[List[str]] = []

class FormAnalysisFrame(BaseModel):
    frame_base64: str
    exercise_type: str  # squat, lunge, sprint

@router.post("/predictive-analysis")
async def generate_predictive_analysis(request: PredictiveAnalysisRequest):
    """
    Generate comprehensive predictive analysis:
    - Injury risk prediction
    - Performance forecasting  
    - Match readiness score
    - Optimal training load
    """
    try:
        db = get_database()
        player_name = request.player_name
        
        logger.info(f"Generating predictive analysis for {player_name}")
        
        # Gather all player data
        assessments = await db.assessments.find(
            {"player_name": player_name}
        ).sort("created_at", -1).to_list(length=50)
        
        # Get wellness logs (if available)
        wellness_logs = await db.wellness_logs.find(
            {"player_name": player_name}
        ).sort("date", -1).to_list(length=30)
        
        # Get training load data
        training_loads = await db.load_monitoring.find(
            {"player_name": player_name}
        ).sort("date", -1).to_list(length=28)
        
        if not assessments:
            raise HTTPException(status_code=404, detail="No assessment data found for this player")
        
        # Prepare data for predictive engine
        player_data = {
            "assessments": assessments,
            "training_loads": training_loads,
            "wellness_logs": wellness_logs,
            "upcoming_match": {"days_to_match": request.days_to_match},
            "goals": request.goals
        }
        
        # Generate analysis
        analysis = predictive_engine.generate_comprehensive_analysis(player_data)
        
        # Save to database
        analysis_data = analysis.dict()
        analysis_data["player_name"] = player_name
        analysis_data["timestamp"] = analysis_data["timestamp"].isoformat()
        
        await db.predictive_analyses.insert_one(analysis_data)
        
        logger.info(f"✅ Predictive analysis complete for {player_name}")
        
        return {
            "success": True,
            "player_name": player_name,
            "analysis": analysis.dict(),
            "message": "Comprehensive AI analysis generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predictive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-form-frame")
async def analyze_form_frame(
    frame_base64: str = Form(...),
    exercise_type: str = Form(...)
):
    """
    Analyze a single frame for form/pose detection
    Used for real-time mobile camera analysis
    """
    try:
        logger.info(f"Analyzing {exercise_type} form from mobile frame")
        
        # Decode base64 image
        img_data = base64.b64decode(frame_base64.split(',')[1] if ',' in frame_base64 else frame_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Analyze pose
        analysis = pose_analyzer.analyze_frame(frame, exercise_type)
        
        if not analysis:
            return {
                "pose_detected": False,
                "message": "No pose detected in frame"
            }
        
        # Draw landmarks on frame
        annotated_frame = pose_analyzer.draw_landmarks(
            frame, 
            analysis['landmarks']
        )
        
        # Encode annotated frame back to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "pose_detected": True,
            "exercise_type": exercise_type,
            "form_score": analysis['analysis']['form_score'],
            "verdict": analysis['analysis']['verdict'],
            "issues": analysis['analysis']['issues'],
            "corrections": analysis['analysis']['corrections'],
            "angles": {k: round(v, 1) for k, v in analysis['angles'].items()},
            "annotated_frame": f"data:image/jpeg;base64,{annotated_base64}"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing frame: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-video")
async def analyze_video(
    video: UploadFile = File(...),
    exercise_type: str = Form(...)
):
    """
    Analyze an uploaded video file
    Returns: Rep count, average form score, common issues
    """
    try:
        logger.info(f"Analyzing uploaded video for {exercise_type}")
        
        # Save uploaded video temporarily
        temp_path = f"/tmp/video_{datetime.now().timestamp()}.mp4"
        
        with open(temp_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        # Analyze video
        results = video_analyzer.analyze_video(temp_path, exercise_type)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if "error" in results:
            return {
                "success": False,
                "error": results["error"]
            }
        
        return {
            "success": True,
            "exercise_type": exercise_type,
            "rep_count": results["rep_count"],
            "average_form_score": results["average_form_score"],
            "common_issues": results["common_issues"],
            "total_frames": results["total_frames"],
            "analyzed_frames": results["analyzed_frames"]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-coaching-feedback")
async def get_ai_coaching_feedback(
    player_name: str = Form(...),
    form_issues: str = Form(...),
    exercise_type: str = Form(...),
    form_score: float = Form(...)
):
    """
    Generate natural language AI coaching feedback
    Uses Emergent LLM (GPT-4o by default)
    """
    try:
        logger.info(f"Generating AI feedback for {player_name}")
        
        if not EMERGENT_KEY or EMERGENT_KEY == "your_emergent_llm_key_here":
            # Mock response for testing when API key is not configured
            mock_feedback = f"""Great work on your {exercise_type} training, {player_name}! 

With a form score of {form_score}/100, you're making solid progress. Here's what I noticed:

**Issues to address:**
{form_issues}

**Key corrections:**
1. Focus on proper depth - aim for thighs parallel to ground
2. Keep your torso more upright - engage your core
3. Control the movement - slow down on the descent

**Why this matters:**
Proper form prevents injury and maximizes strength gains. These adjustments will help you build better movement patterns.

Keep pushing yourself - consistency is key! 💪"""
            
            return {
                "success": True,
                "player_name": player_name,
                "exercise_type": exercise_type,
                "form_score": form_score,
                "ai_feedback": mock_feedback,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": "Mock response - Emergent LLM key not configured"
            }
        
        # Initialize LLM chat
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"coach-{player_name}-{datetime.now().timestamp()}",
            system_message="""You are an elite soccer coach and biomechanics expert. 
            Provide encouraging, specific, and actionable coaching feedback on exercise form.
            Be supportive but direct. Use emojis sparingly. Keep responses under 150 words."""
        ).with_model("openai", "gpt-4o-mini")
        
        # Create coaching prompt
        prompt = f"""Player: {player_name}
Exercise: {exercise_type.upper()}
Form Score: {form_score}/100

Detected Issues:
{form_issues}

Provide coaching feedback that:
1. Acknowledges what they're doing well (if form_score > 70)
2. Explains WHY the issues matter (injury risk, performance impact)
3. Gives 2-3 specific corrections with cues
4. Encourages proper progression

Be motivational and professional."""
        
        # Get AI response
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        logger.info(f"✅ AI feedback generated for {player_name}")
        
        return {
            "success": True,
            "player_name": player_name,
            "exercise_type": exercise_type,
            "form_score": form_score,
            "ai_feedback": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating AI feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance-insights")
async def get_performance_insights(player_name: str = Form(...)):
    """
    Generate AI insights about player's performance trajectory
    """
    try:
        db = get_database()
        
        # Get assessment history
        assessments = await db.assessments.find(
            {"player_name": player_name}
        ).sort("created_at", -1).to_list(length=10)
        
        if len(assessments) < 2:
            return {
                "success": False,
                "message": "Need at least 2 assessments for insights"
            }
        
        # Prepare data summary
        latest = assessments[0]
        previous = assessments[1]
        
        score_change = latest.get('overall_score', 0) - previous.get('overall_score', 0)
        
        # Physical changes
        sprint_change = previous.get('sprint_30m', 0) - latest.get('sprint_30m', 0)  # Lower is better
        endurance_change = latest.get('yo_yo_test', 0) - previous.get('yo_yo_test', 0)
        
        prompt = f"""Analyze this soccer player's progress:

Player: {player_name}

Latest Assessment:
- Overall Score: {latest.get('overall_score', 0)}/100
- Sprint 30m: {latest.get('sprint_30m', 0)}s
- Yo-Yo Test: {latest.get('yo_yo_test', 0)}m

Previous Assessment:
- Overall Score: {previous.get('overall_score', 0)}/100  
- Sprint 30m: {previous.get('sprint_30m', 0)}s
- Yo-Yo Test: {previous.get('yo_yo_test', 0)}m

Changes:
- Overall: {'+' if score_change > 0 else ''}{score_change} points
- Sprint: {'+' if sprint_change < 0 else ''}{abs(sprint_change):.2f}s {'(faster)' if sprint_change > 0 else '(slower)'}
- Endurance: {'+' if endurance_change > 0 else ''}{endurance_change}m

Provide:
1. Key observations (2-3 points)
2. What's working well
3. Areas needing focus
4. One specific training recommendation

Keep under 200 words. Be professional and motivating."""
        
        # Get AI insights
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"insights-{player_name}-{datetime.now().timestamp()}",
            system_message="You are an elite soccer performance analyst and coach."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=prompt)
        insights = await chat.send_message(user_message)
        
        return {
            "success": True,
            "player_name": player_name,
            "score_change": round(score_change, 1),
            "assessments_analyzed": len(assessments),
            "ai_insights": insights,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis-history/{player_name}")
async def get_analysis_history(player_name: str, limit: int = 10):
    """Get historical predictive analyses for a player"""
    try:
        db = get_database()
        
        analyses = await db.predictive_analyses.find(
            {"player_name": player_name}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        return {
            "player_name": player_name,
            "analyses": analyses,
            "count": len(analyses)
        }
        
    except Exception as e:
        logger.error(f"Error fetching analysis history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
