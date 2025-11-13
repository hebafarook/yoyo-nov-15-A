from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timezone, timedelta, date
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from models_club import ClubAIInsight, Match, InjuryRecord, TrainingSession
from utils.database import prepare_for_mongo, parse_from_mongo
import asyncio

router = APIRouter(prefix="/club", tags=["club-ai"])
logger = logging.getLogger(__name__)

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['soccer_coach_db']

# Import LLM for AI insights
try:
    from emergentintegrations import LLM
    EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')
    llm_client = LLM(api_key=EMERGENT_KEY) if EMERGENT_KEY else None
except ImportError:
    llm_client = None
    logger.warning("Emergent Integrations not available")

# ============ AI INSIGHTS GENERATION ============

@router.post("/{club_id}/ai/generate-insights")
async def generate_club_ai_insights(club_id: str):
    """Generate AI insights for entire club"""
    try:
        if not llm_client:
            return {
                "success": False,
                "message": "LLM not configured"
            }
        
        # Get club data
        club = await db.clubs.find_one({"id": club_id})
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get players with safety concerns
        red_flag_players = await db.club_players.find({
            "club_id": club_id,
            "safety_status": "red_flag",
            "active": True
        }).to_list(50)
        
        # Get teams with issues
        teams = await db.teams.find({"club_id": club_id, "active": True}).to_list(100)
        low_performing_teams = [t for t in teams if t.get("team_overall_score", 0) < 60]
        
        # Get injury trends
        recent_injuries = await db.injury_records.find({
            "club_id": club_id,
            "injury_date": {"$gte": datetime.now(timezone.utc) - timedelta(days=90)}
        }).to_list(100)
        
        # Create prompt for LLM
        prompt = f"""Analyze the following club data and provide 5 key insights:

Club: {club.get('name')}
Total Teams: {len(teams)}
Red Flag Players: {len(red_flag_players)}
Low Performing Teams: {len(low_performing_teams)}
Recent Injuries (90 days): {len(recent_injuries)}

Provide insights on:
1. Player safety and injury prevention
2. Team performance gaps
3. Training load management
4. Development priorities
5. Tactical recommendations

Format as JSON array with: title, description, priority (low/medium/high), recommendations (list)"""

        # Generate insights with LLM
        response = llm_client.generate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        insights_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Parse insights (simplified)
        insights = []
        if "title" in insights_text.lower():
            # Store as club insight
            insight = ClubAIInsight(
                club_id=club_id,
                insight_type="club_analysis",
                scope="club_wide",
                title="Club Performance Analysis",
                description=insights_text,
                priority="high",
                category="performance",
                recommendations=["Review player safety protocols", "Address training load distribution"],
                confidence_score=0.85,
                impact_score=0.90
            )
            
            insight_data = prepare_for_mongo(insight.dict())
            await db.club_ai_insights.insert_one(insight_data)
            insights.append(insight)
        
        return {
            "success": True,
            "insights_generated": len(insights),
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}/ai/insights")
async def get_club_ai_insights(club_id: str, status: str = "active"):
    """Get AI insights for club"""
    try:
        insights = await db.club_ai_insights.find({
            "club_id": club_id,
            "status": status
        }).sort("created_at", -1).limit(50).to_list(50)
        
        return {
            "success": True,
            "count": len(insights),
            "insights": [ClubAIInsight(**parse_from_mongo(i)) for i in insights]
        }
    except Exception as e:
        logger.error(f"Error fetching AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}/ai/alerts-feed")
async def get_ai_alerts_feed(club_id: str):
    """Get prioritized AI alerts feed"""
    try:
        # Get safety alerts
        safety_alerts = await db.safety_alerts.find({
            "club_id": club_id,
            "status": "active"
        }).sort("severity", -1).limit(10).to_list(10)
        
        # Get AI insights
        ai_insights = await db.club_ai_insights.find({
            "club_id": club_id,
            "status": "active",
            "priority": {"$in": ["high", "critical"]}
        }).sort("created_at", -1).limit(10).to_list(10)
        
        # Get injury warnings
        injury_risks = await db.club_players.find({
            "club_id": club_id,
            "safety_status": "red_flag",
            "active": True
        }).limit(10).to_list(10)
        
        return {
            "success": True,
            "safety_alerts": safety_alerts,
            "ai_insights": [ClubAIInsight(**parse_from_mongo(i)) for i in ai_insights],
            "injury_risk_players": injury_risks,
            "total_alerts": len(safety_alerts) + len(ai_insights) + len(injury_risks)
        }
    except Exception as e:
        logger.error(f"Error fetching alerts feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ MATCH & EVENT MANAGEMENT ============

@router.post("/{club_id}/matches/create", response_model=Match)
async def create_match(match: Match):
    """Create new match"""
    try:
        match_data = prepare_for_mongo(match.dict())
        await db.matches.insert_one(match_data)
        logger.info(f"✅ Match created: {match.opponent} on {match.match_date}")
        return match
    except Exception as e:
        logger.error(f"Error creating match: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}/matches")
async def get_club_matches(
    club_id: str,
    team_id: Optional[str] = None,
    upcoming: bool = True
):
    """Get matches for club"""
    try:
        query = {"club_id": club_id}
        if team_id:
            query["team_id"] = team_id
        
        if upcoming:
            query["match_date"] = {"$gte": datetime.now(timezone.utc)}
            query["played"] = False
            matches = await db.matches.find(query).sort("match_date", 1).to_list(50)
        else:
            matches = await db.matches.find(query).sort("match_date", -1).to_list(100)
        
        return {
            "success": True,
            "count": len(matches),
            "matches": [Match(**parse_from_mongo(m)) for m in matches]
        }
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ MEDICAL & INJURY CENTER ============

@router.post("/{club_id}/injuries/create", response_model=InjuryRecord)
async def create_injury_record(injury: InjuryRecord):
    """Create injury record"""
    try:
        injury_data = prepare_for_mongo(injury.dict())
        await db.injury_records.insert_one(injury_data)
        
        # Update player status
        await db.club_players.update_one(
            {"id": injury.player_id},
            {"$set": {
                "injury_status": "injured",
                "safety_status": "red_flag",
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        logger.info(f"✅ Injury recorded for player {injury.player_id}")
        return injury
    except Exception as e:
        logger.error(f"Error creating injury record: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}/injuries")
async def get_club_injuries(club_id: str, status: Optional[str] = None):
    """Get injury records"""
    try:
        query = {"club_id": club_id}
        if status:
            query["status"] = status
        
        injuries = await db.injury_records.find(query).sort("injury_date", -1).to_list(100)
        
        return {
            "success": True,
            "count": len(injuries),
            "injuries": [InjuryRecord(**parse_from_mongo(i)) for i in injuries]
        }
    except Exception as e:
        logger.error(f"Error fetching injuries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ PERFORMANCE ANALYTICS ============

@router.get("/{club_id}/analytics/overview")
async def get_club_analytics(club_id: str):
    """Get club-wide performance analytics"""
    try:
        # Get all players
        players = await db.club_players.find({"club_id": club_id, "active": True}).to_list(500)
        
        # Calculate averages
        avg_physical = sum(p.get("physical_score", 0) for p in players) / len(players) if players else 0
        avg_technical = sum(p.get("technical_score", 0) for p in players) / len(players) if players else 0
        avg_tactical = sum(p.get("tactical_score", 0) for p in players) / len(players) if players else 0
        avg_mental = sum(p.get("mental_score", 0) for p in players) / len(players) if players else 0
        
        # Get teams analytics
        teams = await db.teams.find({"club_id": club_id, "active": True}).to_list(100)
        team_analytics = []
        for team in teams:
            team_players = [p for p in players if p.get("team_id") == team.get("id")]
            if team_players:
                team_analytics.append({
                    "team_name": team.get("name"),
                    "team_id": team.get("id"),
                    "player_count": len(team_players),
                    "avg_overall": sum(p.get("overall_score", 0) for p in team_players) / len(team_players),
                    "avg_attendance": sum(p.get("attendance_rate", 0) for p in team_players) / len(team_players)
                })
        
        return {
            "success": True,
            "club_averages": {
                "physical": round(avg_physical, 2),
                "technical": round(avg_technical, 2),
                "tactical": round(avg_tactical, 2),
                "mental": round(avg_mental, 2)
            },
            "team_analytics": team_analytics,
            "total_players": len(players),
            "total_teams": len(teams)
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ TRAINING SESSIONS ============

@router.post("/{club_id}/sessions/create", response_model=TrainingSession)
async def create_training_session(session: TrainingSession):
    """Create training session"""
    try:
        session_data = prepare_for_mongo(session.dict())
        await db.training_sessions.insert_one(session_data)
        logger.info(f"✅ Training session created for team {session.team_id}")
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}/sessions")
async def get_club_sessions(
    club_id: str,
    team_id: Optional[str] = None,
    upcoming: bool = False
):
    """Get training sessions"""
    try:
        query = {"club_id": club_id}
        if team_id:
            query["team_id"] = team_id
        
        if upcoming:
            query["session_date"] = {"$gte": date.today()}
            query["completed"] = False
        
        sessions = await db.training_sessions.find(query).sort("session_date", -1).to_list(100)
        
        return {
            "success": True,
            "count": len(sessions),
            "sessions": [TrainingSession(**parse_from_mongo(s)) for s in sessions]
        }
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
