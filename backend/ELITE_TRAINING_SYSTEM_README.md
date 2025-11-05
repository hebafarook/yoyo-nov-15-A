# Elite Soccer Training & Assessment System
## FIFA & Manchester United Edition

### Overview
Dynamic elite soccer training generator that uses testing data, wellness, and match schedule to create daily and weekly plans based on FIFA's Four-Corner Model and Manchester United-style tactical periodisation.

### System Name
**"Elite Soccer Training & Assessment System — FIFA & Manchester United Edition"**

### Key Features

#### 1. **Comprehensive Input Parameters**
- **Player Profile**: Name, age, position, level, injury status
- **Testing Data**: Sprint (10m, 30m), Yo-Yo IR2, CMJ, 505 agility, squat 1RM, nordic strength
- **Wellness Monitoring**: Sleep hours, soreness (1-5), mood (1-5), stress (1-5), HRV score
- **Match Schedule**: Days to next match, matches this week, opponent, match importance
- **Tactical Focus**: Possession, transition, pressing, build-up, set pieces (1-5 scale each)
- **Load Monitoring**: ACWR, RPE average, total distance, sprint count, HSR meters
- **Existing Program Integration**: Session library IDs, club periodisation, banned exercises, mandatory drills

#### 2. **Dynamic Output Generation**
- Daily Training Plans
- Weekly Microcycles
- Recovery Prescriptions
- Testing Summaries
- Coach Checklists
- Integration Suggestions

#### 3. **Training Logic**

**Phase-Based Periodization:**
- **Foundation Phase (Weeks 1-4)**: Aerobic base, movement quality, tactical refresh, core stability
- **Development Phase (Weeks 5-12)**: Pressing triggers, positional play, explosive power, RSA
- **Competition Phase (Weeks 13-52)**: Game-specific conditioning, set-piece refinement, micro-peaks

**Tactical Day Assignment** (Based on match proximity):
- **MD-6**: High Intensity Transition (8v8 transition games, 6x40m sprints)
- **MD-5**: Strength Integration (9v6+3 positional play, gym work)
- **MD-4**: Tactical Positional (11v11 positional focus, set-pieces)
- **MD-3**: Speed Precision (6x(4x20m) speed endurance, 5v5 games)
- **MD-2**: Activation (Shape review, set-pieces, short possession)
- **MD-1/0**: Match or Recovery

**Load Status Assessment:**
- ACWR < 0.8 = UNDERLOAD
- ACWR 0.8-1.5 = OPTIMAL
- ACWR > 1.5 = OVERLOAD

#### 4. **Recovery Module**

**Intelligent Recovery Prescription:**
- Monitors: Load flag, wellness, HRV, soreness
- Modalities: Pool/hydro, mobility, breathing, soft tissue
- Nutrition: 3:1 carb:protein timing, hydration protocols
- Sleep: 8-9h targets, quality monitoring
- Field work: Intensity adjustments based on recovery state

**Return-to-Play (RTP) Protocols:**
- **Stage 1**: Pain-free ROM, isometrics, bike (2-3 days)
- **Stage 2**: Linear run progressions, submax COD (3-5 days)
- **Stage 3**: Position-specific drills at 70-80% HSR (4-7 days)
- **Stage 4**: Full team with constraints (3-5 days)
- **Stage 5**: Match return with load monitoring (ongoing)

#### 5. **Testing & Benchmarking**

**Elite Benchmarks:**
- 10m Sprint: Elite ≤1.65s, Excellent ≤1.75s, Good ≤1.85s, Average ≤1.95s
- 30m Sprint: Elite ≤3.90s, Excellent ≤4.10s, Good ≤4.30s, Average ≤4.50s
- Yo-Yo IR2: Elite ≥2400m, Excellent ≥2000m, Good ≥1700m, Average ≥1400m
- CMJ: Elite ≥65cm, Excellent ≥60cm, Good ≥55cm, Average ≥50cm
- 505 Agility: Elite ≤2.20s, Excellent ≤2.30s, Good ≤2.40s, Average ≤2.50s
- Squat 1RM: Elite ≥2.0x BW, Excellent ≥1.8x, Good ≥1.6x, Average ≥1.4x

**Automated Testing Validation:**
- Flags outdated testing (> 8 weeks)
- Identifies missing tests
- Calculates Speed Index, Endurance Index, Power Index
- Provides specific test recommendations

#### 6. **Integration Hooks**

**"Room to Integrate" with Existing Programs:**
- Inherits club periodisation ID when available
- Maps suggested drills to existing session library
- Respects banned exercises list
- Prioritizes mandatory club drills
- Allows attachment of:
  - Opposition scouting drills
  - Set-piece routines
  - Academy-specific technical blocks

**Merge Strategy:**
```
Priority Order: club_mandatory > logic_suggested > optional_extras
```

### API Endpoints

#### Core Generation
- `POST /api/elite-training/generate-plan` - Generate comprehensive elite training plan

#### Data Logging
- `POST /api/elite-training/wellness` - Log daily wellness data
- `GET /api/elite-training/wellness/{player_name}` - Get wellness history
- `POST /api/elite-training/testing-data` - Log physical testing data
- `GET /api/elite-training/testing-data/{player_name}` - Get latest testing data
- `POST /api/elite-training/load-monitoring` - Log training load data
- `GET /api/elite-training/load-monitoring/{player_name}` - Get load history
- `POST /api/elite-training/match-schedule` - Update match schedule
- `GET /api/elite-training/match-schedule/{player_name}` - Get match schedule

#### Protocols & Plans
- `GET /api/elite-training/rtp-protocol/{stage}` - Get RTP protocol for specific stage
- `GET /api/elite-training/rtp-protocols` - Get all RTP protocols
- `GET /api/elite-training/training-plans/{player_name}` - Get training plan history

### Example Usage

```python
# Generate Elite Training Plan
import requests

plan_request = {
    "player_profile": {
        "name": "Marcus Rashford",
        "age": 26,
        "position": "Forward",
        "level": "first_team",
        "injury_status": "fit"
    },
    "testing_data": {
        "sprint_10m": 1.72,
        "sprint_30m": 4.05,
        "yoyo_ir2": 2100,
        "cmj": 62.0,
        "test_505": 2.25,
        "squat_1rm": 180.0,
        "nordic_strength": 320.0
    },
    "wellness": {
        "sleep_hours": 8.5,
        "soreness_1_5": 4,
        "mood_1_5": 4,
        "stress_1_5": 3,
        "hrv_score": 68.0
    },
    "match_schedule": {
        "days_to_next_match": 4,
        "matches_this_week": 1,
        "opponent": "Liverpool",
        "match_importance": 5
    },
    "tactical_focus": {
        "possession": 4,
        "transition": 5,
        "pressing": 5,
        "buildup": 4,
        "set_pieces": 3
    },
    "previous_load": {
        "acwr": 1.12,
        "rpe_avg": 6.5,
        "total_distance_m": 9500.0,
        "sprint_count": 28,
        "hsr_m": 1200.0
    }
}

response = requests.post(
    "http://localhost:8001/api/elite-training/generate-plan",
    json=plan_request
)

training_plan = response.json()
print(training_plan["daily_training_plan"])
```

### Coach Checklist (Standard Items)
- First touch direction
- Press timing (<3s)
- Communication
- Decel & hip control
- Decision speed under fatigue

### Report Logic
- Weekly player reports with testing deltas, load trends, wellness trends
- Automated alerts when:
  - ACWR > 1.5
  - HRV ↓ 10%
  - Wellness avg < 3
- Exportable reports
- Can append external club PDFs/session plans

### Database Collections
- `elite_training_plans` - Generated training plans
- `wellness_logs` - Daily wellness monitoring
- `testing_data` - Physical testing results
- `load_monitoring` - Training load tracking
- `match_schedules` - Match schedule data

### System Status
✅ **FULLY OPERATIONAL**
- Backend routes integrated
- All models defined
- Core logic implemented
- Database ready
- API endpoints active
- RTP protocols loaded

### Integration Notes
This system is designed to **complement** the existing Yo-Yo Elite Soccer Player AI Coach system, not replace it. It adds:
- More sophisticated load monitoring
- Match schedule integration
- Elite-level benchmarking
- Return-to-play protocols
- Club program integration hooks
- Manchester United-style tactical periodisation

The two systems can work together, with the Elite System focusing on professional/elite athletes and the original system serving youth development and general assessment.
