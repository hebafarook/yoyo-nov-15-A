from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import logging
import hashlib
import jwt
import os
import uuid
from datetime import datetime, timezone, timedelta
from models import User, UserCreate, UserLogin, SavedReport, SavedReportCreate, UserProfile, AssessmentBenchmark, AssessmentBenchmarkCreate
from utils.database import prepare_for_mongo, parse_from_mongo, db

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password

def create_access_token(user_id: str, username: str, role: str = "player") -> str:
    """Create JWT access token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user info"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def verify_token_async(token: str) -> dict:
    """Async version of verify_token for compatibility"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = await db.users.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = await db.users.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        
        # For player role, set player_id to username or generate unique ID
        player_id = None
        if user_data.role == "player":
            player_id = user_data.username  # Use username as player identifier
        
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            is_coach=user_data.is_coach or (user_data.role == "coach"),
            player_id=player_id,
            age=user_data.age,
            position=user_data.position,
            gender=user_data.gender,
            height=user_data.height,
            weight=user_data.weight,
            dominant_foot=user_data.dominant_foot,
            current_injuries=user_data.current_injuries,
            parent_email=user_data.parent_email,
            coach_email=user_data.coach_email
        )
        
        # Save user to database
        user_data_dict = prepare_for_mongo(user.dict())
        result = await db.users.insert_one(user_data_dict)
        
        # Create user profile
        profile = UserProfile(user_id=user.id)
        profile_data = prepare_for_mongo(profile.dict())
        await db.user_profiles.insert_one(profile_data)
        
        # Send invitation emails to parent and coach if provided
        if user_data.role == "player":
            if user_data.parent_email:
                # TODO: Send email invitation to parent
                logger.info(f"Parent invitation queued for: {user_data.parent_email}")
                # Create relationship link
                await create_parent_relationship(user.id, user_data.parent_email)
            
            if user_data.coach_email:
                # TODO: Send email invitation to coach
                logger.info(f"Coach invitation queued for: {user_data.coach_email}")
                # Create relationship link
                await create_coach_relationship(user.id, user_data.coach_email)
        
        # Create access token
        access_token = create_access_token(user.id, user.username, user.role)
        
        logger.info(f"User registered: {user.username} (role: {user.role})")
        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_coach": user.is_coach,
                "player_id": user.player_id,
                "age": user.age,
                "position": user.position
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@router.post("/login", response_model=dict)
async def login_user(login_data: UserLogin):
    """Login user and return access token"""
    try:
        # Find user by username
        user_doc = await db.users.find_one({"username": login_data.username})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user = User(**parse_from_mongo(user_doc))
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Update last login
        await db.users.update_one(
            {"id": user.id},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        # Create access token
        access_token = create_access_token(user.id, user.username, user.role)
        
        logger.info(f"User logged in: {user.username} (role: {user.role})")
        return {
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_coach": user.is_coach,
                "player_id": user.player_id,
                "age": user.age,
                "position": user.position
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )

@router.post("/forgot-password")
async def forgot_password(email: str):
    """Generate password reset token for user"""
    try:
        # Find user by email
        user_doc = await db.users.find_one({"email": email})
        if not user_doc:
            # Don't reveal if email exists for security
            return {
                "message": "If this email exists, a reset token has been generated",
                "success": True
            }
        
        # Generate reset token
        reset_token = str(uuid.uuid4())
        reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # Token valid for 1 hour
        
        # Update user with reset token
        await db.users.update_one(
            {"id": user_doc["id"]},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_expiry": reset_token_expiry.isoformat()
            }}
        )
        
        logger.info(f"Password reset token generated for user: {user_doc['username']}")
        
        # In production, send email here. For now, return token
        return {
            "message": "Password reset token generated",
            "success": True,
            "reset_token": reset_token,  # In production, this would be sent via email
            "username": user_doc["username"],
            "expires_in": "1 hour"
        }
        
    except Exception as e:
        logger.error(f"Error generating reset token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate reset token"
        )

@router.post("/reset-password")
async def reset_password(reset_token: str, new_password: str):
    """Reset user password using reset token"""
    try:
        # Find user by reset token
        user_doc = await db.users.find_one({"reset_token": reset_token})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Check if token is expired
        reset_token_expiry = user_doc.get("reset_token_expiry")
        if not reset_token_expiry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Parse expiry time
        if isinstance(reset_token_expiry, str):
            expiry_datetime = datetime.fromisoformat(reset_token_expiry.replace('Z', '+00:00'))
        else:
            expiry_datetime = reset_token_expiry
        
        # Make expiry datetime timezone-aware if it isn't
        if expiry_datetime.tzinfo is None:
            expiry_datetime = expiry_datetime.replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) > expiry_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Hash new password
        hashed_password = hash_password(new_password)
        
        # Update user password and clear reset token
        await db.users.update_one(
            {"id": user_doc["id"]},
            {"$set": {
                "hashed_password": hashed_password,
                "reset_token": None,
                "reset_token_expiry": None
            }}
        )
        
        logger.info(f"Password reset successful for user: {user_doc['username']}")
        
        return {
            "message": "Password reset successful",
            "success": True,
            "username": user_doc["username"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.get("/profile", response_model=dict)
async def get_user_profile(current_user: dict = Depends(verify_token)):
    """Get user profile information"""
    try:
        user_doc = await db.users.find_one({"id": current_user["user_id"]})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**parse_from_mongo(user_doc))
        
        # Get user profile
        profile_doc = await db.user_profiles.find_one({"user_id": user.id})
        if profile_doc:
            profile = UserProfile(**parse_from_mongo(profile_doc))
        else:
            # Create profile if it doesn't exist
            profile = UserProfile(user_id=user.id)
            profile_data = prepare_for_mongo(profile.dict())
            await db.user_profiles.insert_one(profile_data)
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_coach": user.is_coach,
                "player_id": user.player_id,
                "age": user.age,
                "position": user.position,
                "profile_picture": user.profile_picture,
                "created_at": user.created_at,
                "last_login": user.last_login
            },
            "profile": {
                "players_managed": profile.players_managed,
                "saved_reports_count": len(profile.saved_reports),
                "benchmarks_count": len(profile.benchmarks) if hasattr(profile, 'benchmarks') else 0,
                "coaching_level": profile.coaching_level,
                "organization": profile.organization,
                "preferences": profile.preferences
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )

@router.post("/save-report", response_model=SavedReport)
async def save_assessment_report(
    report_data: SavedReportCreate, 
    current_user: dict = Depends(verify_token)
):
    """Save assessment report to user profile"""
    try:
        # Verify user owns this report or is a coach
        user_doc = await db.users.find_one({"id": current_user["user_id"]})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create saved report
        saved_report = SavedReport(
            user_id=current_user["user_id"],
            player_name=report_data.player_name,
            assessment_id=report_data.assessment_id,
            report_data=report_data.report_data,
            report_type=report_data.report_type,
            title=report_data.title or f"Assessment Report - {report_data.player_name}",
            notes=report_data.notes
        )
        
        # Save to database
        report_dict = prepare_for_mongo(saved_report.dict())
        await db.saved_reports.insert_one(report_dict)
        
        # Update user profile
        await db.user_profiles.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$addToSet": {
                    "saved_reports": saved_report.id,
                    "players_managed": report_data.player_name
                },
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        
        logger.info(f"Report saved for user {current_user['username']}: {saved_report.id}")
        return saved_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save report"
        )

@router.get("/saved-reports", response_model=List[SavedReport])
async def get_saved_reports(current_user: dict = Depends(verify_token)):
    """Get all saved reports for the current user"""
    try:
        reports = await db.saved_reports.find(
            {"user_id": current_user["user_id"]}
        ).sort("saved_at", -1).to_list(1000)
        
        return [SavedReport(**parse_from_mongo(report)) for report in reports]
        
    except Exception as e:
        logger.error(f"Error fetching saved reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch saved reports"
        )

@router.get("/saved-reports/{report_id}", response_model=SavedReport)
async def get_saved_report(report_id: str, current_user: dict = Depends(verify_token)):
    """Get a specific saved report"""
    try:
        report = await db.saved_reports.find_one({
            "id": report_id,
            "user_id": current_user["user_id"]
        })
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        return SavedReport(**parse_from_mongo(report))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching saved report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch saved report"
        )

@router.delete("/saved-reports/{report_id}")
async def delete_saved_report(report_id: str, current_user: dict = Depends(verify_token)):
    """Delete a saved report"""
    try:
        result = await db.saved_reports.delete_one({
            "id": report_id,
            "user_id": current_user["user_id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Update user profile
        await db.user_profiles.update_one(
            {"user_id": current_user["user_id"]},
            {"$pull": {"saved_reports": report_id}}
        )
        
        return {"message": "Report deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting saved report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )


# ============ ASSESSMENT BENCHMARK ENDPOINTS ============

@router.post("/save-benchmark", response_model=AssessmentBenchmark)
async def save_assessment_benchmark(
    benchmark_data: AssessmentBenchmarkCreate,
    current_user: dict = Depends(verify_token)
):
    """Save assessment as benchmark in player profile"""
    try:
        # Verify user owns this benchmark
        if benchmark_data.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to save benchmark for this user"
            )
        
        # Check if this is the first benchmark (baseline)
        existing_benchmarks = await db.assessment_benchmarks.count_documents(
            {"user_id": current_user["user_id"], "player_name": benchmark_data.player_name}
        )
        
        is_baseline = existing_benchmarks == 0
        
        # Get previous benchmark for comparison
        previous_benchmark = None
        if not is_baseline:
            prev_doc = await db.assessment_benchmarks.find(
                {"user_id": current_user["user_id"], "player_name": benchmark_data.player_name}
            ).sort("benchmark_date", -1).limit(1).to_list(1)
            if prev_doc:
                previous_benchmark = AssessmentBenchmark(**parse_from_mongo(prev_doc[0]))
        
        # Calculate improvement from baseline if not the first benchmark
        improvement_from_baseline = None
        if not is_baseline and previous_benchmark and previous_benchmark.is_baseline:
            improvement_from_baseline = {
                "sprint_30m": round(((previous_benchmark.sprint_30m - benchmark_data.sprint_30m) / previous_benchmark.sprint_30m) * 100, 2) if previous_benchmark.sprint_30m > 0 else 0,
                "yo_yo_test": round(((benchmark_data.yo_yo_test - previous_benchmark.yo_yo_test) / previous_benchmark.yo_yo_test) * 100, 2) if previous_benchmark.yo_yo_test > 0 else 0,
                "vo2_max": round(((benchmark_data.vo2_max - previous_benchmark.vo2_max) / previous_benchmark.vo2_max) * 100, 2) if previous_benchmark.vo2_max > 0 else 0,
                "vertical_jump": round(((benchmark_data.vertical_jump - previous_benchmark.vertical_jump) / previous_benchmark.vertical_jump) * 100, 2) if previous_benchmark.vertical_jump > 0 else 0,
                "body_fat": round(((previous_benchmark.body_fat - benchmark_data.body_fat) / previous_benchmark.body_fat) * 100, 2) if previous_benchmark.body_fat > 0 else 0,
                "ball_control": round(((benchmark_data.ball_control - previous_benchmark.ball_control) / previous_benchmark.ball_control) * 100, 2) if previous_benchmark.ball_control > 0 else 0,
                "passing_accuracy": round(((benchmark_data.passing_accuracy - previous_benchmark.passing_accuracy) / previous_benchmark.passing_accuracy) * 100, 2) if previous_benchmark.passing_accuracy > 0 else 0,
                "dribbling_success": round(((benchmark_data.dribbling_success - previous_benchmark.dribbling_success) / previous_benchmark.dribbling_success) * 100, 2) if previous_benchmark.dribbling_success > 0 else 0,
                "shooting_accuracy": round(((benchmark_data.shooting_accuracy - previous_benchmark.shooting_accuracy) / previous_benchmark.shooting_accuracy) * 100, 2) if previous_benchmark.shooting_accuracy > 0 else 0,
                "defensive_duels": round(((benchmark_data.defensive_duels - previous_benchmark.defensive_duels) / previous_benchmark.defensive_duels) * 100, 2) if previous_benchmark.defensive_duels > 0 else 0,
                "game_intelligence": round(((benchmark_data.game_intelligence - previous_benchmark.game_intelligence) / previous_benchmark.game_intelligence) * 100, 2) if previous_benchmark.game_intelligence > 0 else 0,
                "positioning": round(((benchmark_data.positioning - previous_benchmark.positioning) / previous_benchmark.positioning) * 100, 2) if previous_benchmark.positioning > 0 else 0,
                "decision_making": round(((benchmark_data.decision_making - previous_benchmark.decision_making) / previous_benchmark.decision_making) * 100, 2) if previous_benchmark.decision_making > 0 else 0,
                "coachability": round(((benchmark_data.coachability - previous_benchmark.coachability) / previous_benchmark.coachability) * 100, 2) if previous_benchmark.coachability > 0 else 0,
                "mental_toughness": round(((benchmark_data.mental_toughness - previous_benchmark.mental_toughness) / previous_benchmark.mental_toughness) * 100, 2) if previous_benchmark.mental_toughness > 0 else 0,
                "overall_score": round(((benchmark_data.overall_score - previous_benchmark.overall_score) / previous_benchmark.overall_score) * 100, 2) if previous_benchmark.overall_score > 0 else 0
            }
        
        # Create benchmark
        benchmark = AssessmentBenchmark(
            user_id=current_user["user_id"],
            player_name=benchmark_data.player_name,
            assessment_id=benchmark_data.assessment_id,
            age=benchmark_data.age,
            position=benchmark_data.position,
            sprint_30m=benchmark_data.sprint_30m,
            yo_yo_test=benchmark_data.yo_yo_test,
            vo2_max=benchmark_data.vo2_max,
            vertical_jump=benchmark_data.vertical_jump,
            body_fat=benchmark_data.body_fat,
            ball_control=benchmark_data.ball_control,
            passing_accuracy=benchmark_data.passing_accuracy,
            dribbling_success=benchmark_data.dribbling_success,
            shooting_accuracy=benchmark_data.shooting_accuracy,
            defensive_duels=benchmark_data.defensive_duels,
            game_intelligence=benchmark_data.game_intelligence,
            positioning=benchmark_data.positioning,
            decision_making=benchmark_data.decision_making,
            coachability=benchmark_data.coachability,
            mental_toughness=benchmark_data.mental_toughness,
            overall_score=benchmark_data.overall_score,
            performance_level=benchmark_data.performance_level,
            benchmark_type="baseline" if is_baseline else benchmark_data.benchmark_type,
            is_baseline=is_baseline,
            notes=benchmark_data.notes,
            improvement_from_baseline=improvement_from_baseline,
            previous_benchmark_id=previous_benchmark.id if previous_benchmark else None
        )
        
        # Save to database
        benchmark_dict = prepare_for_mongo(benchmark.dict())
        await db.assessment_benchmarks.insert_one(benchmark_dict)
        
        # Update user profile
        update_data = {
            "$addToSet": {
                "benchmarks": benchmark.id,
                "players_managed": benchmark_data.player_name
            },
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
        
        # Set baseline benchmark ID if this is the first benchmark
        if is_baseline:
            update_data["$set"]["baseline_benchmark_id"] = benchmark.id
        
        await db.user_profiles.update_one(
            {"user_id": current_user["user_id"]},
            update_data,
            upsert=True
        )
        
        logger.info(f"Benchmark saved for user {current_user['username']}: {benchmark.id} (baseline: {is_baseline})")
        return benchmark
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save benchmark: {str(e)}"
        )

@router.get("/benchmarks", response_model=List[AssessmentBenchmark])
async def get_user_benchmarks(
    player_name: Optional[str] = None,
    current_user: dict = Depends(verify_token)
):
    """Get all benchmarks for the current user, optionally filtered by player name"""
    try:
        query = {"user_id": current_user["user_id"]}
        if player_name:
            query["player_name"] = player_name
        
        benchmarks = await db.assessment_benchmarks.find(query).sort("benchmark_date", -1).to_list(1000)
        
        return [AssessmentBenchmark(**parse_from_mongo(benchmark)) for benchmark in benchmarks]
        
    except Exception as e:
        logger.error(f"Error fetching benchmarks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch benchmarks"
        )

@router.get("/benchmarks/baseline", response_model=AssessmentBenchmark)
async def get_baseline_benchmark(
    player_name: str,
    current_user: dict = Depends(verify_token)
):
    """Get the baseline benchmark for a specific player"""
    try:
        benchmark = await db.assessment_benchmarks.find_one({
            "user_id": current_user["user_id"],
            "player_name": player_name,
            "is_baseline": True
        })
        
        if not benchmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Baseline benchmark not found for this player"
            )
        
        return AssessmentBenchmark(**parse_from_mongo(benchmark))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching baseline benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch baseline benchmark"
        )

@router.get("/benchmarks/{benchmark_id}", response_model=AssessmentBenchmark)
async def get_benchmark(benchmark_id: str, current_user: dict = Depends(verify_token)):
    """Get a specific benchmark"""
    try:
        benchmark = await db.assessment_benchmarks.find_one({
            "id": benchmark_id,
            "user_id": current_user["user_id"]
        })
        
        if not benchmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benchmark not found"
            )
        
        return AssessmentBenchmark(**parse_from_mongo(benchmark))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch benchmark"
        )

@router.delete("/benchmarks/{benchmark_id}")
async def delete_benchmark(benchmark_id: str, current_user: dict = Depends(verify_token)):
    """Delete a benchmark (cannot delete baseline)"""
    try:
        # Check if this is a baseline benchmark
        benchmark = await db.assessment_benchmarks.find_one({
            "id": benchmark_id,
            "user_id": current_user["user_id"]
        })
        
        if not benchmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benchmark not found"
            )
        
        if benchmark.get("is_baseline", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete baseline benchmark"
            )
        
        result = await db.assessment_benchmarks.delete_one({
            "id": benchmark_id,
            "user_id": current_user["user_id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Benchmark not found"
            )
        
        # Update user profile
        await db.user_profiles.update_one(
            {"user_id": current_user["user_id"]},
            {"$pull": {"benchmarks": benchmark_id}}
        )
        
        return {"message": "Benchmark deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete benchmark"
        )

@router.get("/benchmarks/progress/{player_name}", response_model=dict)
async def get_player_progress(
    player_name: str,
    current_user: dict = Depends(verify_token)
):
    """Get comprehensive progress analysis for a player"""
    try:
        # Get all benchmarks for this player
        benchmarks = await db.assessment_benchmarks.find({
            "user_id": current_user["user_id"],
            "player_name": player_name
        }).sort("benchmark_date", 1).to_list(1000)
        
        if not benchmarks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No benchmarks found for this player"
            )
        
        benchmark_list = [AssessmentBenchmark(**parse_from_mongo(b)) for b in benchmarks]
        
        # Get baseline and latest
        baseline = benchmark_list[0]
        latest = benchmark_list[-1]
        
        # Calculate overall progress
        progress = {
            "player_name": player_name,
            "total_benchmarks": len(benchmark_list),
            "baseline_date": baseline.benchmark_date,
            "latest_date": latest.benchmark_date,
            "baseline_score": baseline.overall_score,
            "latest_score": latest.overall_score,
            "overall_improvement": round(((latest.overall_score - baseline.overall_score) / baseline.overall_score) * 100, 2) if baseline.overall_score > 0 else 0,
            "benchmarks": benchmark_list,
            "improvement_timeline": [
                {
                    "date": b.benchmark_date,
                    "overall_score": b.overall_score,
                    "benchmark_type": b.benchmark_type
                }
                for b in benchmark_list
            ]
        }
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating player progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate player progress"
        )


# ============ ADMIN ENDPOINTS ============

@router.get("/admin/users", response_model=List[User])
async def get_all_users_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Admin endpoint to get all users"""
    try:
        # Verify admin token
        user_info = verify_token(credentials)
        user_id = user_info['user_id']
        
        # Get requesting user
        requesting_user = await db.users.find_one({"id": user_id})
        if not requesting_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is admin
        if requesting_user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get all users
        users = await db.users.find({}).to_list(1000)
        parsed_users = []
        
        for user_doc in users:
            try:
                parsed_user = parse_from_mongo(user_doc)
                # Remove sensitive data
                if 'hashed_password' in parsed_user:
                    del parsed_user['hashed_password']
                parsed_users.append(User(**parsed_user))
            except Exception as e:
                logger.error(f"Error parsing user: {e}")
                continue
        
        return parsed_users
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/admin/user/{user_id}/assessments")
async def get_user_assessments_admin(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Admin endpoint to get any user's assessments"""
    try:
        # Verify admin token
        user_info = verify_token(credentials)
        admin_id = user_info['user_id']
        
        # Get requesting user
        requesting_user = await db.users.find_one({"id": admin_id})
        if not requesting_user or requesting_user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get target user's assessments
        assessments = await db.assessments.find({"user_id": user_id}).to_list(100)
        return assessments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user assessments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/user/{user_id}/programs")
async def get_user_programs_admin(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Admin endpoint to get any user's training programs"""
    try:
        # Verify admin token
        user_info = verify_token(credentials)
        admin_id = user_info['user_id']
        
        # Get requesting user
        requesting_user = await db.users.find_one({"id": admin_id})
        if not requesting_user or requesting_user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get target user
        target_user = await db.users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get their programs (by player_name)
        player_name = target_user.get('username') or target_user.get('player_id')
        if player_name:
            programs = await db.periodized_programs.find({"player_id": player_name}).to_list(100)
            return programs
        
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user programs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
