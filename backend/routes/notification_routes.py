# Notification Routes for Email Reminders, Push Notifications, and Check-ins
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timezone
import logging

from models import NotificationPreferences, CheckInOut
from routes.auth_routes import verify_token
from utils.database import db, prepare_for_mongo, parse_from_mongo
from utils.email_service import email_service
from utils.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

# ==================== NOTIFICATION PREFERENCES ====================

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(current_user: dict = Depends(verify_token)):
    """Get user's notification preferences"""
    try:
        prefs = await db.notification_preferences.find_one({"user_id": current_user["user_id"]})
        
        if not prefs:
            # Create default preferences
            default_prefs = NotificationPreferences(user_id=current_user["user_id"])
            await db.notification_preferences.insert_one(prepare_for_mongo(default_prefs.dict()))
            return default_prefs
            
        return NotificationPreferences(**parse_from_mongo(prefs))
        
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(verify_token)
):
    """Update user's notification preferences"""
    try:
        preferences.user_id = current_user["user_id"]
        prefs_dict = prepare_for_mongo(preferences.dict())
        
        await db.notification_preferences.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": prefs_dict},
            upsert=True
        )
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register-fcm-token")
async def register_fcm_token(
    token: str,
    current_user: dict = Depends(verify_token)
):
    """Register FCM token for push notifications"""
    try:
        await db.notification_preferences.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": {"fcm_token": token}},
            upsert=True
        )
        
        return {"message": "FCM token registered successfully"}
        
    except Exception as e:
        logger.error(f"Error registering FCM token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CHECK-IN / CHECK-OUT ====================

@router.post("/check-in", response_model=CheckInOut)
async def check_in(
    player_name: str,
    session_type: str = "training",
    current_user: dict = Depends(verify_token)
):
    """Check in before training session"""
    try:
        check_in_record = CheckInOut(
            user_id=current_user["user_id"],
            player_name=player_name,
            check_in_time=datetime.now(timezone.utc),
            session_type=session_type
        )
        
        check_in_dict = prepare_for_mongo(check_in_record.dict())
        await db.check_ins.insert_one(check_in_dict)
        
        logger.info(f"User {current_user['user_id']} checked in for {player_name}")
        return check_in_record
        
    except Exception as e:
        logger.error(f"Error during check-in: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-out/{check_in_id}")
async def check_out(
    check_in_id: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(verify_token)
):
    """Check out after completing training session"""
    try:
        check_in_record = await db.check_ins.find_one({
            "id": check_in_id,
            "user_id": current_user["user_id"]
        })
        
        if not check_in_record:
            raise HTTPException(status_code=404, detail="Check-in record not found")
        
        if check_in_record.get("completed"):
            raise HTTPException(status_code=400, detail="Already checked out")
        
        check_out_time = datetime.now(timezone.utc)
        
        await db.check_ins.update_one(
            {"id": check_in_id},
            {"$set": {
                "check_out_time": check_out_time.isoformat(),
                "notes": notes,
                "completed": True
            }}
        )
        
        logger.info(f"User {current_user['user_id']} checked out: {check_in_id}")
        
        return {
            "message": "Checked out successfully",
            "duration_minutes": (check_out_time - datetime.fromisoformat(check_in_record["check_in_time"].replace('Z', '+00:00'))).total_seconds() / 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during check-out: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check-ins", response_model=List[CheckInOut])
async def get_check_ins(
    player_name: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(verify_token)
):
    """Get user's check-in history"""
    try:
        query = {"user_id": current_user["user_id"]}
        if player_name:
            query["player_name"] = player_name
        
        check_ins = await db.check_ins.find(query).sort("check_in_time", -1).limit(limit).to_list(length=limit)
        
        return [CheckInOut(**parse_from_mongo(c)) for c in check_ins]
        
    except Exception as e:
        logger.error(f"Error fetching check-ins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SEND NOTIFICATIONS ====================

@router.post("/send-test-email")
async def send_test_email(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(verify_token)
):
    """Send test email notification"""
    try:
        user_doc = await db.users.find_one({"id": current_user["user_id"]})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Send test email in background
        background_tasks.add_task(
            email_service.send_daily_training_reminder,
            user_doc["email"],
            user_doc["full_name"],
            "Test Player",
            [
                {"name": "Sprint Intervals", "duration": 20, "category": "Speed"},
                {"name": "Ball Control Drills", "duration": 25, "category": "Technical"},
                {"name": "Positioning Practice", "duration": 30, "category": "Tactical"}
            ]
        )
        
        return {"message": "Test email queued for delivery"}
        
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-daily-reminder/{player_name}")
async def send_daily_reminder(
    player_name: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(verify_token)
):
    """Manually trigger daily training reminder"""
    try:
        # Get user info
        user_doc = await db.users.find_one({"id": current_user["user_id"]})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get notification preferences
        prefs = await db.notification_preferences.find_one({"user_id": current_user["user_id"]})
        
        # Get today's exercises from program
        program = await db.periodized_programs.find_one(
            {"player_id": player_name},
            sort=[("created_at", -1)]
        )
        
        exercises = []
        if program and program.get("macro_cycles"):
            # Extract exercises from current phase/week/day
            # Simplified - would need actual date-based lookup
            first_cycle = program["macro_cycles"][0]
            if first_cycle.get("micro_cycles"):
                first_week = first_cycle["micro_cycles"][0]
                if first_week.get("daily_routines"):
                    first_day = first_week["daily_routines"][0]
                    exercises = first_day.get("exercises", [])[:5]
        
        # Send email if enabled
        if prefs and prefs.get("email_notifications", True) and prefs.get("daily_reminders", True):
            background_tasks.add_task(
                email_service.send_daily_training_reminder,
                user_doc["email"],
                user_doc["full_name"],
                player_name,
                exercises
            )
        
        # Send push if enabled and token exists
        if prefs and prefs.get("push_notifications", True) and prefs.get("fcm_token"):
            background_tasks.add_task(
                notification_service.send_daily_training_push,
                prefs["fcm_token"],
                player_name,
                len(exercises)
            )
        
        return {"message": "Daily reminder sent"}
        
    except Exception as e:
        logger.error(f"Error sending daily reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CALENDAR / SIRI INTEGRATION ====================

@router.get("/calendar-export/{player_name}")
async def export_to_calendar(
    player_name: str,
    current_user: dict = Depends(verify_token)
):
    """Generate iCalendar (.ics) file for Apple Calendar/Siri integration"""
    try:
        # Get user's program
        program = await db.periodized_programs.find_one(
            {"player_id": player_name},
            sort=[("created_at", -1)]
        )
        
        if not program:
            raise HTTPException(status_code=404, detail="No program found for this player")
        
        # Generate iCalendar events
        # Simplified version - full implementation would use icalendar library
        ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Yo-Yo Elite Soccer//Training Program//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Soccer Training - {player_name}
X-WR-TIMEZONE:UTC
BEGIN:VEVENT
UID:{program['player_id']}-training-daily@yoyo-elite.com
DTSTART:20250105T080000Z
DTEND:20250105T090000Z
RRULE:FREQ=DAILY;COUNT=90
SUMMARY:⚽ Soccer Training - {player_name}
DESCRIPTION:Daily training session from your personalized program
LOCATION:Training Ground
STATUS:CONFIRMED
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Time for your training session!
TRIGGER:-PT30M
END:VALARM
END:VEVENT
END:VCALENDAR"""
        
        return {
            "message": "Calendar export generated",
            "ical_url": f"/api/notifications/download-calendar/{player_name}",
            "instructions": "Add this to Apple Calendar, then use Siri: 'Hey Siri, remind me about Soccer Training'"
        }
        
    except Exception as e:
        logger.error(f"Error generating calendar export: {e}")
        raise HTTPException(status_code=500, detail=str(e))
