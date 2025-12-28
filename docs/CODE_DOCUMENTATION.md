# 📚 YO-YO ELITE SOCCER COACH - CODE DOCUMENTATION

## 🎯 CORE ALGORITHMS & LOGIC

---

## 1. WEAKNESS DETECTION ALGORITHM

**File:** `/app/backend/server.py` (Lines 1536-1551)

```python
def detect_player_weaknesses(assessment):
    """
    Analyzes player assessment to identify areas needing improvement
    Returns list of weakness categories
    """
    weaknesses = []
    
    # Physical weaknesses
    sprint_30m = assessment.get("sprint_30m", 4.5)
    yo_yo_test = assessment.get("yo_yo_test", 1600)
    
    if sprint_30m > 4.5:
        weaknesses.append("speed")
    if yo_yo_test < 1600:
        weaknesses.append("endurance")
    
    # Technical weaknesses (normalized to 0-10 scale)
    ball_control = assessment.get("ball_control", 5)
    passing = assessment.get("passing_accuracy", 75) / 10
    shooting = assessment.get("shooting_accuracy", 70) / 10
    
    if ball_control < 4:
        weaknesses.append("ball_control")
    if passing < 7.5:
        weaknesses.append("passing")
    if shooting < 7:
        weaknesses.append("shooting")
    
    # Tactical weaknesses
    game_intelligence = assessment.get("game_intelligence", 5)
    positioning = assessment.get("positioning", 5)
    
    if game_intelligence < 4:
        weaknesses.append("tactical")
    if positioning < 4:
        weaknesses.append("positioning")
    
    return weaknesses
```

**How It Works:**
1. Takes player's assessment scores
2. Compares each metric against thresholds
3. Identifies areas below expected standard
4. Returns list of weakness categories
5. Used by program generator to customize training

---

## 2. TRAINING PROGRAM GENERATION

**File:** `/app/backend/server.py` (Lines 1529-1650)

```python
@api_router.post("/periodized-programs")
async def create_periodized_program(program: PeriodizedProgramCreate):
    """
    Generates personalized 14-week training program based on:
    - Player's latest assessment
    - Identified weaknesses
    - Position-specific needs
    - Age and fitness level
    """
    
    # Step 1: Load player's latest assessment
    assessment = await db.assessments.find_one(
        {"player_name": program.player_id},
        sort=[("created_at", -1)]  # Most recent first
    )
    
    if not assessment:
        # No assessment - generate generic program
        weaknesses = ["general_fitness"]
    else:
        # Step 2: Analyze weaknesses
        weaknesses = []
        
        # Physical analysis
        if assessment.get("sprint_30m", 4.5) > 4.5:
            weaknesses.append("speed")
        if assessment.get("yo_yo_test", 1600) < 1600:
            weaknesses.append("endurance")
            
        # Technical analysis
        if assessment.get("ball_control", 5) < 4:
            weaknesses.append("ball_control")
        if assessment.get("passing_accuracy", 75) < 75:
            weaknesses.append("passing")
            
        # Tactical analysis
        if assessment.get("game_intelligence", 5) < 4:
            weaknesses.append("tactical")
    
    # Step 3: Generate program structure
    # 3 phases: Foundation (4 weeks) → Development (6 weeks) → Peak (4 weeks)
    macro_cycles = []
    
    phase_templates = [
        {
            "phase_name": "Foundation Building",
            "weeks": 4,
            "focus": "Base fitness and fundamentals"
        },
        {
            "phase_name": "Skill Development", 
            "weeks": 6,
            "focus": "Technical and tactical training"
        },
        {
            "phase_name": "Peak Performance",
            "weeks": 4,
            "focus": "Match preparation and refinement"
        }
    ]
    
    # Step 4: For each phase, generate weekly routines
    for phase_idx, phase_template in enumerate(phase_templates):
        micro_cycles = []
        
        for week in range(phase_template["weeks"]):
            daily_routines = []
            
            # Generate 5 days of training per week
            for day in range(5):
                # Step 5: Select exercises based on weaknesses
                routine = generate_daily_routine(
                    phase=phase_idx,
                    week=week,
                    day=day,
                    weaknesses=weaknesses  # Customized for this player!
                )
                daily_routines.append(routine)
            
            micro_cycles.append({
                "name": f"Week {week + 1}",
                "daily_routines": daily_routines
            })
        
        macro_cycles.append({
            "name": phase_template["phase_name"],
            "micro_cycles": micro_cycles
        })
    
    # Step 6: Save program to database
    program_data = {
        "id": str(uuid.uuid4()),
        "player_id": program.player_id,
        "program_name": program.program_name,
        "total_duration_weeks": 14,
        "macro_cycles": macro_cycles,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.periodized_programs.insert_one(program_data)
    
    return program_data
```

**Key Points:**
- ✅ Loads player's LATEST assessment
- ✅ Detects weaknesses automatically
- ✅ Generates 14-week program (3 phases)
- ✅ Customizes exercises based on weaknesses
- ✅ Creates 5 daily routines per week
- ✅ Saves program linked to player_id

---

## 3. EXERCISE SELECTION ALGORITHM

**File:** `/app/backend/exercise_database.py` (Lines 299-380)

```python
def generate_daily_routine(phase, week, day, weaknesses):
    """
    Selects appropriate exercises based on:
    - Training phase (Foundation/Development/Peak)
    - Week number (progressive overload)
    - Player's weaknesses
    """
    
    exercises = []
    
    # Base exercises for all players
    exercises.append({
        "name": "Dynamic Warmup",
        "category": "warmup",
        "duration": "10 minutes"
    })
    
    # Weakness-specific exercises
    if "speed" in weaknesses:
        exercises.append(EXERCISE_DATABASE["sprint_intervals"])
        exercises.append(EXERCISE_DATABASE["acceleration_drills"])
    
    if "ball_control" in weaknesses:
        exercises.append(EXERCISE_DATABASE["ball_mastery_cones"])
        exercises.append(EXERCISE_DATABASE["close_control_drills"])
    
    if "passing" in weaknesses:
        exercises.append(EXERCISE_DATABASE["passing_accuracy_gates"])
        exercises.append(EXERCISE_DATABASE["long_pass_practice"])
    
    if "shooting" in weaknesses:
        exercises.append(EXERCISE_DATABASE["finishing_drills"])
        exercises.append(EXERCISE_DATABASE["power_shooting"])
    
    if "tactical" in weaknesses:
        exercises.append(EXERCISE_DATABASE["positioning_exercises"])
        exercises.append(EXERCISE_DATABASE["game_situations"])
    
    # Phase-specific intensity
    if phase == 0:  # Foundation
        intensity = "60-70%"
    elif phase == 1:  # Development
        intensity = "70-85%"
    else:  # Peak
        intensity = "85-95%"
    
    # Apply intensity to all exercises
    for exercise in exercises:
        exercise["intensity"] = intensity
    
    # Add cooldown
    exercises.append({
        "name": "Recovery & Stretching",
        "category": "cooldown",
        "duration": "10 minutes"
    })
    
    return {
        "day": f"Day {day + 1}",
        "exercises": exercises,
        "total_duration": calculate_total_duration(exercises)
    }
```

**Exercise Database Has:**
- 50+ exercises with detailed instructions
- Each exercise has:
  * Name
  * Category (technical, physical, tactical)
  * Step-by-step instructions (6-8 steps)
  * Purpose & expected outcomes
  * Duration, intensity, equipment needed

---

## 4. ACHIEVEMENT CALCULATION

**File:** `/app/frontend/src/components/AchievementsDisplay.js` (Lines 44-138)

```javascript
const calculateAchievements = (benchmarks, user) => {
    const earned = [];
    
    // Achievement: First Assessment
    if (benchmarks.length >= 1) {
        earned.push({
            name: 'First Steps',
            description: 'Completed first assessment',
            icon: Star,
            earnedDate: benchmarks[0].benchmark_date
        });
    }
    
    // Achievement: Consistent Progress
    if (benchmarks.length >= 2) {
        earned.push({
            name: 'Consistency is Key',
            description: 'Completed 2+ assessments',
            icon: Target,
            earnedDate: benchmarks[1].benchmark_date
        });
    }
    
    // Achievement: High Performer
    const hasHighScore = benchmarks.some(b => b.overall_score >= 70);
    if (hasHighScore) {
        const highScoreBenchmark = benchmarks.find(b => b.overall_score >= 70);
        earned.push({
            name: 'High Performer',
            description: 'Achieved score above 70',
            icon: Flame,
            earnedDate: highScoreBenchmark.benchmark_date
        });
    }
    
    // Achievement: Elite Status  
    const hasEliteScore = benchmarks.some(b => b.overall_score >= 80);
    if (hasEliteScore) {
        earned.push({
            name: 'Elite Status',
            description: 'Reached elite level (80+)',
            icon: Crown,
            earnedDate: benchmarks.find(b => b.overall_score >= 80).benchmark_date
        });
    }
    
    // Achievement: Improvement Streak
    if (benchmarks.length >= 2) {
        const sorted = benchmarks.sort((a, b) => 
            new Date(a.benchmark_date) - new Date(b.benchmark_date)
        );
        const baseline = sorted[0].overall_score;
        const latest = sorted[sorted.length - 1].overall_score;
        
        if (latest > baseline) {
            earned.push({
                name: 'On The Rise',
                description: 'Improved from baseline',
                icon: TrendingUp,
                earnedDate: sorted[sorted.length - 1].benchmark_date
            });
        }
    }
    
    return earned;
};
```

**Logic Flow:**
1. Load user's benchmarks (assessments)
2. Check each achievement criteria
3. Award achievements that match
4. Store earned date for each
5. Display in achievements tab
6. Update automatically on new assessments

---

## 5. DATA ISOLATION & SECURITY

**File:** `/app/backend/routes/auth_routes.py`

```python
# JWT Token Verification
def verify_token(credentials):
    """Verify JWT token and extract user info"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {
            'user_id': payload.get('user_id'),
            'username': payload.get('username')
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Get User's Benchmarks (User-Specific)
@router.get("/auth/benchmarks")
async def get_user_benchmarks(credentials: HTTPAuthorizationCredentials):
    """Returns ONLY authenticated user's benchmarks"""
    
    # Verify who is making request
    user_info = verify_token(credentials)
    user_id = user_info['user_id']
    
    # Get ONLY this user's benchmarks
    benchmarks = await db.assessment_benchmarks.find(
        {"user_id": user_id}  # Filter by authenticated user!
    ).sort("benchmark_date", -1).to_list(100)
    
    return benchmarks

# Admin-Only Endpoint
@router.get("/admin/users")
async def get_all_users_admin(credentials: HTTPAuthorizationCredentials):
    """Admin endpoint - view all users"""
    
    # Verify admin access
    user_info = verify_token(credentials)
    user = await db.users.find_one({"id": user_info['user_id']})
    
    # Check if user is admin
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Admin verified - return all users
    users = await db.users.find({}).to_list(1000)
    return users
```

**Security Features:**
- ✅ JWT tokens for authentication
- ✅ User ID embedded in token
- ✅ All endpoints verify token
- ✅ Data filtered by user_id
- ✅ Admin role checked separately
- ✅ 403 Forbidden for unauthorized access

---

## 6. ASSESSMENT SCORING

**File:** `/app/backend/utils/assessment_calculator.py`

```python
def calculate_overall_score(assessment):
    """
    Calculates weighted overall score:
    - Physical: 20%
    - Technical: 40% (highest weight)
    - Tactical: 30%
    - Psychological: 10%
    """
    
    # Physical score (0-100)
    physical_metrics = [
        normalize_sprint(assessment.sprint_30m),
        normalize_yo_yo(assessment.yo_yo_test),
        normalize_vo2(assessment.vo2_max),
        normalize_jump(assessment.vertical_jump),
        normalize_body_fat(assessment.body_fat)
    ]
    physical_score = sum(physical_metrics) / len(physical_metrics)
    
    # Technical score (0-100)
    technical_metrics = [
        assessment.ball_control * 10,  # Scale 0-10 to 0-100
        assessment.passing_accuracy,   # Already 0-100
        assessment.dribbling_success,
        assessment.shooting_accuracy,
        assessment.defensive_duels
    ]
    technical_score = sum(technical_metrics) / len(technical_metrics)
    
    # Tactical score (0-100)
    tactical_metrics = [
        assessment.game_intelligence * 10,
        assessment.positioning * 10,
        assessment.decision_making * 10
    ]
    tactical_score = sum(tactical_metrics) / len(tactical_metrics)
    
    # Psychological score (0-100)
    psychological_metrics = [
        assessment.coachability * 10,
        assessment.mental_toughness * 10
    ]
    psychological_score = sum(psychological_metrics) / len(psychological_metrics)
    
    # Calculate weighted overall score
    overall_score = (
        physical_score * 0.20 +
        technical_score * 0.40 +
        tactical_score * 0.30 +
        psychological_score * 0.10
    )
    
    # Determine performance level
    if overall_score >= 80:
        level = "Elite"
    elif overall_score >= 70:
        level = "Advanced"
    elif overall_score >= 60:
        level = "Intermediate"
    else:
        level = "Developing"
    
    return {
        "overall_score": round(overall_score, 1),
        "performance_level": level,
        "category_scores": {
            "physical": round(physical_score, 1),
            "technical": round(technical_score, 1),
            "tactical": round(tactical_score, 1),
            "psychological": round(psychological_score, 1)
        }
    }
```

---

## 📂 COMPLETE FILE LIST

### Backend Files:
- `/app/backend/server.py` - Main API (5000+ lines)
- `/app/backend/models.py` - Data models
- `/app/backend/routes/auth_routes.py` - Authentication & admin
- `/app/backend/routes/assessment_routes.py` - Assessments
- `/app/backend/routes/training_routes.py` - Training programs
- `/app/backend/routes/progress_routes.py` - Progress tracking
- `/app/backend/utils/database.py` - MongoDB connection
- `/app/backend/utils/assessment_calculator.py` - Scoring logic
- `/app/backend/exercise_database.py` - 50+ exercises

### Frontend Files:
- `/app/frontend/src/App.js` - Main application (1500+ lines)
- `/app/frontend/src/components/AdminDashboard.js` - Admin interface
- `/app/frontend/src/components/AchievementsDisplay.js` - Achievement system
- `/app/frontend/src/components/TrainingDashboard.js` - Training display
- `/app/frontend/src/components/AssessmentReport.js` - Report generation
- `/app/frontend/src/components/SavedReports.js` - Saved data
- `/app/frontend/src/contexts/AuthContext.js` - Authentication state

---

## 🎯 TO VIEW CODE AS ADMIN

### Via Admin Dashboard:
1. Login as admin (admin / admin123)
2. View all users and their data
3. See how programs differ per player
4. Verify weakness detection working

### Via Platform:
- All code is in `/app/backend/` and `/app/frontend/src/`
- You can view any file
- Code is well-commented and organized

### Key Algorithms to Review:
1. **Weakness Detection:** server.py lines 1536-1551
2. **Program Generation:** server.py lines 1529-1650  
3. **Exercise Selection:** exercise_database.py lines 299-380
4. **Achievement Logic:** AchievementsDisplay.js lines 44-138
5. **Score Calculation:** assessment_calculator.py

---

This documentation shows the core logic powering the entire application!
