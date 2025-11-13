from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone, timedelta, date
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from models_club import (
    Club, ClubCreate, Team, TeamCreate, ClubStaff, ClubStaffCreate,
    ClubPlayer, SafetyAlert, Match, InjuryRecord, ClubAIInsight,
    TrainingSession, ClubDrill
)
from utils.database import prepare_for_mongo, parse_from_mongo

router = APIRouter(prefix="/club", tags=["club"])
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['soccer_coach_db']

# ============ AUTHENTICATION & PERMISSIONS ============
async def verify_club_access(club_id: str, user_id: str) -> bool:
    """Verify user has access to club"""
    # Check if user is club staff
    staff = await db.club_staff.find_one({"user_id": user_id, "club_id": club_id, "active": True})
    return staff is not None

async def get_user_club_id(user_id: str) -> Optional[str]:
    """Get club_id for user"""
    staff = await db.club_staff.find_one({"user_id": user_id, "active": True})
    return staff.get("club_id") if staff else None

# ============ CLUB MANAGEMENT ============

@router.post("/create-club", response_model=Club)
async def create_club(club: ClubCreate):
    """Create new club"""
    try:
        new_club = Club(**club.dict())
        club_data = prepare_for_mongo(new_club.dict())
        await db.clubs.insert_one(club_data)
        
        logger.info(f"✅ Club created: {new_club.name} ({new_club.club_code})")
        return new_club
    except Exception as e:
        logger.error(f"Error creating club: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clubs", response_model=List[Club])
async def get_all_clubs():
    """Get all clubs"""
    try:
        clubs = await db.clubs.find({"active": True}).to_list(100)
        return [Club(**parse_from_mongo(club)) for club in clubs]
    except Exception as e:
        logger.error(f"Error fetching clubs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}", response_model=Club)
async def get_club(club_id: str):
    """Get club by ID"""
    try:
        club = await db.clubs.find_one({"id": club_id})
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        return Club(**parse_from_mongo(club))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching club: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ CLUB DASHBOARD DATA ============

@router.get("/{club_id}/dashboard")
async def get_club_dashboard(club_id: str):
    """Get comprehensive club dashboard data"""
    try:
        # Get club info
        club = await db.clubs.find_one({"id": club_id})
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get teams count
        teams_count = await db.teams.count_documents({"club_id": club_id, "active": True})
        
        # Get players count
        players_count = await db.club_players.count_documents({"club_id": club_id, "active": True})
        
        # Get coaches/staff count
        staff_count = await db.club_staff.count_documents({"club_id": club_id, "active": True})
        
        # Get active alerts
        alerts = await db.safety_alerts.find({
            "club_id": club_id,
            "status": "active"
        }).sort("severity", -1).limit(10).to_list(10)
        
        # Get recent injuries
        injuries = await db.injury_records.find({
            "club_id": club_id,
            "status": {"$in": ["active", "recovering"]}
        }).limit(5).to_list(5)
        
        # Get upcoming matches (next 7 days)
        today = datetime.now(timezone.utc)
        next_week = today + timedelta(days=7)
        upcoming_matches = await db.matches.find({
            "club_id": club_id,
            "match_date": {"$gte": today, "$lte": next_week},
            "played": False
        }).sort("match_date", 1).limit(10).to_list(10)
        
        # Get AI insights
        ai_insights = await db.club_ai_insights.find({
            "club_id": club_id,
            "status": "active"
        }).sort("priority", -1).limit(5).to_list(5)
        
        # Get weekly training load summary
        players = await db.club_players.find({"club_id": club_id, "active": True}).to_list(500)
        total_load = sum(p.get("weekly_training_load", 0) for p in players)
        avg_load = total_load / players_count if players_count > 0 else 0
        
        # Safety summary
        red_flag_count = await db.club_players.count_documents({
            "club_id": club_id,
            "safety_status": "red_flag"
        })
        caution_count = await db.club_players.count_documents({
            "club_id": club_id,
            "safety_status": "caution"
        })
        
        # Assessment pipeline
        pending_assessments = await db.assessments.count_documents({
            "user_id": {"$in": [p.get("user_id") for p in players]},
            "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=30)}
        })
        
        return {
            "success": True,
            "club": Club(**parse_from_mongo(club)),
            "summary": {
                "total_teams": teams_count,
                "total_players": players_count,
                "total_staff": staff_count,
                "active_alerts": len(alerts),
                "active_injuries": len(injuries),
                "upcoming_matches": len(upcoming_matches),
                "red_flag_players": red_flag_count,
                "caution_players": caution_count,
                "avg_weekly_load": round(avg_load, 2)
            },
            "alerts": [SafetyAlert(**parse_from_mongo(a)) for a in alerts],
            "injuries": [InjuryRecord(**parse_from_mongo(i)) for i in injuries],
            "upcoming_matches": [Match(**parse_from_mongo(m)) for m in upcoming_matches],
            "ai_insights": [ClubAIInsight(**parse_from_mongo(ai)) for ai in ai_insights],
            "recent_assessments_count": pending_assessments
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ TEAMS MANAGEMENT ============

@router.post("/teams/create", response_model=Team)
async def create_team(team: TeamCreate):
    """Create new team"""
    try:
        new_team = Team(**team.dict())
        team_data = prepare_for_mongo(new_team.dict())
        await db.teams.insert_one(team_data)
        
        logger.info(f"✅ Team created: {new_team.name} ({new_team.team_code})")
        return new_team
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}/teams", response_model=List[Team])
async def get_club_teams(club_id: str):
    """Get all teams in club"""
    try:
        teams = await db.teams.find({"club_id": club_id, "active": True}).to_list(100)
        return [Team(**parse_from_mongo(team)) for team in teams]
    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/{team_id}")
async def get_team_detail(team_id: str):
    """Get team details with players and coaches"""
    try:
        team = await db.teams.find_one({"id": team_id})
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        team_obj = Team(**parse_from_mongo(team))
        
        # Get players
        players = await db.club_players.find({
            "id": {"$in": team_obj.player_ids},
            "active": True
        }).to_list(50)
        
        # Get coaches
        coaches = await db.club_staff.find({
            "id": {"$in": team_obj.coach_ids},
            "active": True
        }).to_list(10)
        
        # Get recent matches
        matches = await db.matches.find({
            "team_id": team_id
        }).sort("match_date", -1).limit(5).to_list(5)
        
        # Get training sessions
        sessions = await db.training_sessions.find({
            "team_id": team_id
        }).sort("session_date", -1).limit(10).to_list(10)
        
        return {
            "success": True,
            "team": team_obj,
            "players": [ClubPlayer(**parse_from_mongo(p)) for p in players],
            "coaches": [ClubStaff(**parse_from_mongo(c)) for c in coaches],
            "recent_matches": [Match(**parse_from_mongo(m)) for m in matches],
            "recent_sessions": [TrainingSession(**parse_from_mongo(s)) for s in sessions]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/teams/{team_id}/add-player")
async def add_player_to_team(team_id: str, player_id: str):
    """Add player to team"""
    try:
        # Update team
        await db.teams.update_one(
            {"id": team_id},
            {"$addToSet": {"player_ids": player_id}, "$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        
        # Update player
        await db.club_players.update_one(
            {"id": player_id},
            {"$set": {"team_id": team_id, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {"success": True, "message": "Player added to team"}
    except Exception as e:
        logger.error(f"Error adding player to team: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ PLAYERS DIRECTORY ============

@router.get("/{club_id}/players")
async def get_club_players(
    club_id: str,
    team_id: Optional[str] = None,
    position: Optional[str] = None,
    safety_status: Optional[str] = None,
    has_alerts: Optional[bool] = None
):
    """Get all players with filters"""
    try:
        query = {"club_id": club_id, "active": True}
        
        if team_id:
            query["team_id"] = team_id
        if position:
            query["position"] = position
        if safety_status:
            query["safety_status"] = safety_status
        if has_alerts is not None:
            query["has_active_alerts"] = has_alerts
        
        players = await db.club_players.find(query).to_list(500)
        return {
            "success": True,
            "count": len(players),
            "players": [ClubPlayer(**parse_from_mongo(p)) for p in players]
        }
    except Exception as e:
        logger.error(f"Error fetching players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/players/{player_id}/profile")
async def get_player_club_profile(player_id: str):
    """Get detailed player profile with club data"""
    try:
        player = await db.club_players.find_one({"id": player_id})
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        player_obj = ClubPlayer(**parse_from_mongo(player))
        
        # Get assessment history
        assessments = await db.assessment_benchmarks.find({
            "user_id": player_obj.user_id
        }).sort("saved_at", -1).limit(5).to_list(5)
        
        # Get training sessions
        sessions = await db.training_sessions.find({
            "attendance": player_id
        }).sort("session_date", -1).limit(10).to_list(10)
        
        # Get alerts
        alerts = await db.safety_alerts.find({
            "player_id": player_id,
            "status": "active"
        }).to_list(10)
        
        # Get injury history
        injuries = await db.injury_records.find({
            "player_id": player_id
        }).sort("injury_date", -1).to_list(5)
        
        return {
            "success": True,
            "player": player_obj,
            "assessments": assessments,
            "recent_sessions": [TrainingSession(**parse_from_mongo(s)) for s in sessions],
            "alerts": [SafetyAlert(**parse_from_mongo(a)) for a in alerts],
            "injury_history": [InjuryRecord(**parse_from_mongo(i)) for i in injuries]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ COACHES/STAFF MANAGEMENT ============

@router.post("/staff/create", response_model=ClubStaff)
async def create_club_staff(staff: ClubStaffCreate):
    """Create new staff member"""
    try:
        new_staff = ClubStaff(**staff.dict())
        staff_data = prepare_for_mongo(new_staff.dict())
        await db.club_staff.insert_one(staff_data)
        
        logger.info(f"✅ Staff created: {new_staff.full_name} ({new_staff.role})")
        return new_staff
    except Exception as e:
        logger.error(f"Error creating staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_id}/staff", response_model=List[ClubStaff])
async def get_club_staff(club_id: str, role: Optional[str] = None):
    """Get all club staff"""
    try:
        query = {"club_id": club_id, "active": True}
        if role:
            query["role"] = role
        
        staff = await db.club_staff.find(query).to_list(100)
        return [ClubStaff(**parse_from_mongo(s)) for s in staff]
    except Exception as e:
        logger.error(f"Error fetching staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ ASSESSMENTS OVERVIEW ============

@router.get("/{club_id}/assessments/overview")
async def get_assessments_overview(club_id: str):
    """Get club-wide assessment overview"""
    try:
        # Get all club players
        players = await db.club_players.find({"club_id": club_id, "active": True}).to_list(500)
        player_user_ids = [p.get("user_id") for p in players]
        
        # Get all assessments for club players
        assessments = await db.assessment_benchmarks.find({
            "user_id": {"$in": player_user_ids}
        }).to_list(1000)
        
        # Get recent assessments (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_assessments = [a for a in assessments if a.get("saved_at", datetime.min.replace(tzinfo=timezone.utc)) >= thirty_days_ago]
        
        # Group by team
        teams = await db.teams.find({"club_id": club_id, "active": True}).to_list(100)
        team_assessments = {}
        for team in teams:
            team_players = [p for p in players if p.get("team_id") == team.get("id")]
            team_user_ids = [p.get("user_id") for p in team_players]
            team_assessments[team.get("name")] = [a for a in assessments if a.get("user_id") in team_user_ids]
        
        return {
            "success": True,
            "total_assessments": len(assessments),
            "recent_assessments": len(recent_assessments),
            "assessments_by_team": {name: len(alist) for name, alist in team_assessments.items()},
            "recent_assessments_data": recent_assessments[:20]  # Last 20
        }
    except Exception as e:
        logger.error(f"Error fetching assessments overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ SAFETY & TRAINING LOAD CENTER ============

@router.get("/{club_id}/safety/overview")
async def get_safety_overview(club_id: str):
    """Get club-wide safety overview"""
    try:
        # Get all players
        players = await db.club_players.find({"club_id": club_id, "active": True}).to_list(500)
        
        # Safety status breakdown
        safe_count = sum(1 for p in players if p.get("safety_status") == "safe")
        caution_count = sum(1 for p in players if p.get("safety_status") == "caution")
        red_flag_count = sum(1 for p in players if p.get("safety_status") == "red_flag")
        
        # Get active alerts
        alerts = await db.safety_alerts.find({
            "club_id": club_id,
            "status": "active"
        }).to_list(100)
        
        # Alert breakdown
        critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
        high_alerts = [a for a in alerts if a.get("severity") == "high"]
        medium_alerts = [a for a in alerts if a.get("severity") == "medium"]
        
        # Training load summary
        total_load = sum(p.get("weekly_training_load", 0) for p in players)
        avg_load = total_load / len(players) if players else 0
        high_load_players = [p for p in players if p.get("weekly_training_load", 0) > 15]
        
        return {
            "success": True,
            "safety_summary": {
                "safe": safe_count,
                "caution": caution_count,
                "red_flag": red_flag_count,
                "total_players": len(players),
                "safety_score": round((safe_count / len(players) * 100) if players else 100, 1)
            },
            "alerts_summary": {
                "total": len(alerts),
                "critical": len(critical_alerts),
                "high": len(high_alerts),
                "medium": len(medium_alerts)
            },
            "load_summary": {
                "average_load": round(avg_load, 2),
                "total_load": round(total_load, 2),
                "high_load_count": len(high_load_players)
            },
            "active_alerts": [SafetyAlert(**parse_from_mongo(a)) for a in alerts[:20]],
            "high_load_players": [ClubPlayer(**parse_from_mongo(p)) for p in high_load_players]
        }
    except Exception as e:
        logger.error(f"Error fetching safety overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Continue in next file due to length...
