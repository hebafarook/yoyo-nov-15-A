#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING FOR 3 CRITICAL FIXES

Testing the exact scenarios from the review request:
1. Dynamic Training Program Duration (HIGH PRIORITY)
2. Assessment Report Save Endpoints  
3. Dynamic Assessment Analysis

Focus: Verify all fixes are working correctly through comprehensive backend testing.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend .env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.split('=', 1)[1].strip()
            break
    else:
        BACKEND_URL = "http://localhost:8001"

API_BASE = f"{BACKEND_URL}/api"

class CriticalFixesTest:
    def __init__(self):
        self.session = None
        self.user_data = None
        self.jwt_token = None
        self.test_results = []
        self.assessment_data = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")

    async def setup_test_user(self):
        """Setup test user for all scenarios"""
        try:
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                "username": f"dyntest{unique_id}",
                "email": f"dyntest{unique_id}@test.com", 
                "password": "testpass123",
                "full_name": "Dynamic Test User",
                "role": "player",
                "age": 17,
                "position": "Forward"
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_data = data.get("user", {})
                    self.jwt_token = data.get("access_token")
                    
                    if self.jwt_token and self.user_data:
                        self.log_result(
                            "Test User Setup", 
                            True, 
                            f"Successfully registered user: {self.user_data.get('username')}",
                            {"user_id": self.user_data.get("id"), "role": self.user_data.get("role")}
                        )
                        return True
                    else:
                        self.log_result("Test User Setup", False, "Missing JWT token or user data in response")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Test User Setup", False, f"Registration failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Test User Setup", False, f"Registration error: {str(e)}")
            return False

    async def create_test_assessment(self, player_name="Dynamic Duration Test Player", weakness_level="mixed"):
        """Create assessment with specified weakness level"""
        try:
            if weakness_level == "high_weaknesses":
                # Many weaknesses to trigger longer duration
                assessment_data = {
                    "player_name": player_name,
                    "age": 17,
                    "position": "Forward",
                    # Physical metrics (weak)
                    "sprint_30m": 5.2,  # Poor
                    "yo_yo_test": 1400,  # Below average
                    "vo2_max": 54.0,     # Below average
                    "vertical_jump": 45,  # Below average
                    "body_fat": 14.0,    # Above average
                    # Technical metrics (weak)
                    "ball_control": 2,   # Poor
                    "passing_accuracy": 55.0,  # Poor
                    "dribbling_success": 45.0,  # Poor
                    "shooting_accuracy": 45.0,  # Poor
                    "defensive_duels": 60.0,    # Below average
                    # Tactical metrics (weak)
                    "game_intelligence": 2,  # Poor
                    "positioning": 2,        # Poor
                    "decision_making": 2,    # Poor
                    # Psychological metrics (average)
                    "coachability": 3,
                    "mental_toughness": 3
                }
            elif weakness_level == "low_weaknesses":
                # Few weaknesses to trigger shorter duration
                assessment_data = {
                    "player_name": player_name,
                    "age": 17,
                    "position": "Forward",
                    # Physical metrics (good)
                    "sprint_30m": 4.1,   # Good
                    "yo_yo_test": 1900,  # Good
                    "vo2_max": 59.0,     # Good
                    "vertical_jump": 58,  # Good
                    "body_fat": 9.0,     # Good
                    # Technical metrics (good)
                    "ball_control": 4,   # Good
                    "passing_accuracy": 85.0,  # Good
                    "dribbling_success": 70.0,  # Good
                    "shooting_accuracy": 70.0,  # Good
                    "defensive_duels": 78.0,    # Good
                    # Tactical metrics (good)
                    "game_intelligence": 4,  # Good
                    "positioning": 4,        # Good
                    "decision_making": 4,    # Good
                    # Psychological metrics (good)
                    "coachability": 4,
                    "mental_toughness": 4
                }
            else:  # mixed weaknesses (default)
                assessment_data = {
                    "player_name": player_name,
                    "age": 17,
                    "position": "Forward",
                    # Physical metrics (mixed)
                    "sprint_30m": 4.3,   # Average
                    "yo_yo_test": 1700,  # Average
                    "vo2_max": 57.0,     # Average
                    "vertical_jump": 52,  # Average
                    "body_fat": 11.0,    # Average
                    # Technical metrics (some weaknesses)
                    "ball_control": 2,   # Poor - weakness
                    "passing_accuracy": 55.0,  # Poor - weakness
                    "dribbling_success": 65.0,  # Average
                    "shooting_accuracy": 65.0,  # Average
                    "defensive_duels": 70.0,    # Average
                    # Tactical metrics (mixed)
                    "game_intelligence": 3,  # Average
                    "positioning": 2,        # Poor - weakness
                    "decision_making": 4,    # Good
                    # Psychological metrics (good)
                    "coachability": 4,
                    "mental_toughness": 4
                }
            
            async with self.session.post(f"{API_BASE}/assessments", json=assessment_data) as response:
                if response.status == 200:
                    data = await response.json()
                    assessment_id = data.get("id")
                    
                    if assessment_id:
                        self.assessment_data = data
                        self.log_result(
                            f"Assessment Creation ({weakness_level})", 
                            True, 
                            f"Successfully created assessment for {assessment_data['player_name']}",
                            {
                                "assessment_id": assessment_id,
                                "overall_score": data.get("overall_score"),
                                "weakness_level": weakness_level
                            }
                        )
                        return data
                    else:
                        self.log_result(f"Assessment Creation ({weakness_level})", False, "No assessment ID returned")
                        return None
                else:
                    error_text = await response.text()
                    self.log_result(f"Assessment Creation ({weakness_level})", False, f"Assessment creation failed with status {response.status}", {"error": error_text})
                    return None
                    
        except Exception as e:
            self.log_result(f"Assessment Creation ({weakness_level})", False, f"Assessment creation error: {str(e)}")
            return None

    # ==================== SCENARIO 1: DYNAMIC PROGRAM DURATION ====================
    
    async def test_scenario_1_dynamic_duration(self):
        """CRITICAL TEST SCENARIO 1: Dynamic Program Duration Based on Training Frequency"""
        print("\n🔥 SCENARIO 1: DYNAMIC PROGRAM DURATION TESTING 🔥")
        print("=" * 70)
        
        # Step 1: Create assessment with mixed metrics
        assessment = await self.create_test_assessment("Dynamic Duration Test Player", "mixed")
        if not assessment:
            return False
            
        player_name = "Dynamic Duration Test Player"
        
        # Step 2: Test assessment analysis endpoint
        try:
            async with self.session.get(f"{API_BASE}/analyze-assessment/{player_name}") as response:
                if response.status == 200:
                    analysis_data = await response.json()
                    
                    # Verify response contains program_duration_options under recommendations
                    recommendations = analysis_data.get("recommendations", {})
                    duration_options = recommendations.get("program_duration_options", {})
                    if not duration_options:
                        self.log_result("Assessment Analysis", False, "No program_duration_options in recommendations")
                        return False
                        
                    # Extract durations for each frequency
                    three_day_weeks = duration_options.get("3_days", {}).get("weeks")
                    four_day_weeks = duration_options.get("4_days", {}).get("weeks")
                    five_day_weeks = duration_options.get("5_days", {}).get("weeks")
                    
                    if not all([three_day_weeks, four_day_weeks, five_day_weeks]):
                        self.log_result("Assessment Analysis", False, "Missing duration options for all frequencies")
                        return False
                        
                    # Verify 3_days > 4_days > 5_days (due to frequency multipliers)
                    duration_correct = three_day_weeks > four_day_weeks > five_day_weeks
                    
                    self.log_result(
                        "Assessment Analysis - Duration Options", 
                        duration_correct, 
                        f"Duration progression: 3-day={three_day_weeks}w, 4-day={four_day_weeks}w, 5-day={five_day_weeks}w",
                        {
                            "3_days_weeks": three_day_weeks,
                            "4_days_weeks": four_day_weeks, 
                            "5_days_weeks": five_day_weeks,
                            "correct_progression": duration_correct
                        }
                    )
                    
                    if not duration_correct:
                        return False
                        
                else:
                    error_text = await response.text()
                    self.log_result("Assessment Analysis", False, f"Analysis failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Assessment Analysis", False, f"Analysis error: {str(e)}")
            return False
            
        # Step 3: Test 5-day program generation
        try:
            program_data_5day = {
                "player_id": player_name,
                "program_name": "5-Day Program",
                "total_duration_weeks": five_day_weeks,
                "program_objectives": ["Improve technical skills"],
                "assessment_interval_weeks": 4,
                "training_frequency": 5
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data_5day) as response:
                if response.status == 200:
                    program_5day = await response.json()
                    
                    # Verify total_duration_weeks matches requested (NOT fixed 14)
                    actual_duration = program_5day.get("total_duration_weeks")
                    requested_duration = five_day_weeks
                    
                    duration_matches = actual_duration == requested_duration
                    
                    # Count daily routines in first week to verify 5 days
                    macro_cycles = program_5day.get("macro_cycles", [])
                    daily_routines_count = 0
                    if macro_cycles and len(macro_cycles) > 0:
                        micro_cycles = macro_cycles[0].get("micro_cycles", [])
                        if micro_cycles and len(micro_cycles) > 0:
                            daily_routines = micro_cycles[0].get("daily_routines", [])
                            daily_routines_count = len(daily_routines)
                    
                    routines_correct = daily_routines_count == 5
                    
                    self.log_result(
                        "5-Day Program Generation", 
                        duration_matches and routines_correct, 
                        f"Duration: {actual_duration}w (requested {requested_duration}w), Daily routines: {daily_routines_count}",
                        {
                            "actual_duration": actual_duration,
                            "requested_duration": requested_duration,
                            "duration_matches": duration_matches,
                            "daily_routines_count": daily_routines_count,
                            "routines_correct": routines_correct
                        }
                    )
                    
                    if not (duration_matches and routines_correct):
                        return False
                        
                else:
                    error_text = await response.text()
                    self.log_result("5-Day Program Generation", False, f"Program creation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("5-Day Program Generation", False, f"Program creation error: {str(e)}")
            return False
            
        # Step 4: Test 3-day program generation
        try:
            program_data_3day = {
                "player_id": player_name,
                "program_name": "3-Day Program",
                "total_duration_weeks": three_day_weeks,
                "program_objectives": ["Improve technical skills"],
                "assessment_interval_weeks": 4,
                "training_frequency": 3
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data_3day) as response:
                if response.status == 200:
                    program_3day = await response.json()
                    
                    # Verify total_duration_weeks matches requested
                    actual_duration_3day = program_3day.get("total_duration_weeks")
                    requested_duration_3day = three_day_weeks
                    
                    duration_matches_3day = actual_duration_3day == requested_duration_3day
                    
                    # Count daily routines in first week to verify 3 days
                    macro_cycles_3day = program_3day.get("macro_cycles", [])
                    daily_routines_count_3day = 0
                    if macro_cycles_3day and len(macro_cycles_3day) > 0:
                        micro_cycles_3day = macro_cycles_3day[0].get("micro_cycles", [])
                        if micro_cycles_3day and len(micro_cycles_3day) > 0:
                            daily_routines_3day = micro_cycles_3day[0].get("daily_routines", [])
                            daily_routines_count_3day = len(daily_routines_3day)
                    
                    routines_correct_3day = daily_routines_count_3day == 3
                    
                    # Verify 3-day program is LONGER than 5-day program
                    duration_comparison_correct = actual_duration_3day > actual_duration
                    
                    self.log_result(
                        "3-Day Program Generation", 
                        duration_matches_3day and routines_correct_3day and duration_comparison_correct, 
                        f"Duration: {actual_duration_3day}w (requested {requested_duration_3day}w), Daily routines: {daily_routines_count_3day}, Longer than 5-day: {duration_comparison_correct}",
                        {
                            "actual_duration_3day": actual_duration_3day,
                            "requested_duration_3day": requested_duration_3day,
                            "duration_matches": duration_matches_3day,
                            "daily_routines_count": daily_routines_count_3day,
                            "routines_correct": routines_correct_3day,
                            "longer_than_5day": duration_comparison_correct
                        }
                    )
                    
                    if not (duration_matches_3day and routines_correct_3day and duration_comparison_correct):
                        return False
                        
                else:
                    error_text = await response.text()
                    self.log_result("3-Day Program Generation", False, f"Program creation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("3-Day Program Generation", False, f"Program creation error: {str(e)}")
            return False
            
        # Step 5: Test 4-day program generation
        try:
            program_data_4day = {
                "player_id": player_name,
                "program_name": "4-Day Program",
                "total_duration_weeks": four_day_weeks,
                "program_objectives": ["Improve technical skills"],
                "assessment_interval_weeks": 4,
                "training_frequency": 4
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data_4day) as response:
                if response.status == 200:
                    program_4day = await response.json()
                    
                    # Verify total_duration_weeks matches requested
                    actual_duration_4day = program_4day.get("total_duration_weeks")
                    requested_duration_4day = four_day_weeks
                    
                    duration_matches_4day = actual_duration_4day == requested_duration_4day
                    
                    # Count daily routines in first week to verify 4 days
                    macro_cycles_4day = program_4day.get("macro_cycles", [])
                    daily_routines_count_4day = 0
                    if macro_cycles_4day and len(macro_cycles_4day) > 0:
                        micro_cycles_4day = macro_cycles_4day[0].get("micro_cycles", [])
                        if micro_cycles_4day and len(micro_cycles_4day) > 0:
                            daily_routines_4day = micro_cycles_4day[0].get("daily_routines", [])
                            daily_routines_count_4day = len(daily_routines_4day)
                    
                    routines_correct_4day = daily_routines_count_4day == 4
                    
                    # Verify duration is between 3-day and 5-day programs
                    duration_between = actual_duration_3day > actual_duration_4day > actual_duration
                    
                    self.log_result(
                        "4-Day Program Generation", 
                        duration_matches_4day and routines_correct_4day and duration_between, 
                        f"Duration: {actual_duration_4day}w (requested {requested_duration_4day}w), Daily routines: {daily_routines_count_4day}, Between 3&5-day: {duration_between}",
                        {
                            "actual_duration_4day": actual_duration_4day,
                            "requested_duration_4day": requested_duration_4day,
                            "duration_matches": duration_matches_4day,
                            "daily_routines_count": daily_routines_count_4day,
                            "routines_correct": routines_correct_4day,
                            "duration_between_3_and_5": duration_between
                        }
                    )
                    
                    return duration_matches_4day and routines_correct_4day and duration_between
                        
                else:
                    error_text = await response.text()
                    self.log_result("4-Day Program Generation", False, f"Program creation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("4-Day Program Generation", False, f"Program creation error: {str(e)}")
            return False

    # ==================== SCENARIO 2: ASSESSMENT REPORT SAVE ====================
    
    async def test_scenario_2_report_save(self):
        """CRITICAL TEST SCENARIO 2: Assessment Report Save Functionality"""
        print("\n🔥 SCENARIO 2: ASSESSMENT REPORT SAVE FUNCTIONALITY 🔥")
        print("=" * 70)
        
        if not self.jwt_token:
            self.log_result("Report Save Setup", False, "No JWT token available for authentication")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Test save-report endpoint
        try:
            report_data = {
                "player_name": "Dynamic Duration Test Player",
                "assessment_id": "test-assessment-123",
                "report_data": {
                    "playerData": self.assessment_data if self.assessment_data else {},
                    "reportData": {
                        "overall_score": 3.2,
                        "physical_score": 3.0,
                        "technical_score": 2.8,
                        "tactical_score": 3.0,
                        "psychological_score": 4.0
                    }
                },
                "report_type": "milestone",
                "title": "Test Assessment Report",
                "notes": "Testing save functionality"
            }
            
            async with self.session.post(f"{API_BASE}/auth/save-report", json=report_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    report_id = data.get("id")
                    
                    if report_id:
                        self.log_result(
                            "Save Report Endpoint", 
                            True, 
                            "Successfully saved assessment report with JWT auth",
                            {
                                "report_id": report_id,
                                "report_type": data.get("report_type"),
                                "title": data.get("title")
                            }
                        )
                    else:
                        self.log_result("Save Report Endpoint", False, "No report ID returned")
                        return False
                elif response.status == 401:
                    self.log_result("Save Report Endpoint", False, "Authentication failed (401) - JWT token invalid")
                    return False
                else:
                    error_text = await response.text()
                    self.log_result("Save Report Endpoint", False, f"Save report failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Save Report Endpoint", False, f"Save report error: {str(e)}")
            return False
            
        # Step 2: Test GET saved-reports
        try:
            async with self.session.get(f"{API_BASE}/auth/saved-reports", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        self.log_result(
                            "Get Saved Reports", 
                            True, 
                            f"Successfully retrieved {len(data)} saved report(s)",
                            {"report_count": len(data)}
                        )
                    else:
                        self.log_result("Get Saved Reports", False, "No saved reports found")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Get Saved Reports", False, f"Failed to retrieve reports with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Get Saved Reports", False, f"Get reports error: {str(e)}")
            return False
            
        # Step 3: Test save-benchmark endpoint
        try:
            benchmark_data = {
                "user_id": self.user_data.get("id"),  # Add required user_id
                "player_name": "Dynamic Duration Test Player",
                "assessment_id": "test-assessment-123",
                "age": 17,
                "position": "Forward",
                "sprint_30m": 4.5,
                "yo_yo_test": 1500,
                "vo2_max": 57.0,
                "vertical_jump": 52,
                "body_fat": 11.0,
                "ball_control": 2,
                "passing_accuracy": 55.0,
                "dribbling_success": 65.0,
                "shooting_accuracy": 65.0,
                "defensive_duels": 70.0,
                "game_intelligence": 3,
                "positioning": 2,
                "decision_making": 4,
                "coachability": 4,
                "mental_toughness": 4,
                "overall_score": 65,
                "performance_level": "Average"
            }
            
            async with self.session.post(f"{API_BASE}/auth/save-benchmark", json=benchmark_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    benchmark_id = data.get("id")
                    is_baseline = data.get("is_baseline")
                    
                    if benchmark_id:
                        self.log_result(
                            "Save Benchmark Endpoint", 
                            True, 
                            f"Successfully saved benchmark (baseline: {is_baseline})",
                            {
                                "benchmark_id": benchmark_id,
                                "is_baseline": is_baseline
                            }
                        )
                    else:
                        self.log_result("Save Benchmark Endpoint", False, "No benchmark ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Save Benchmark Endpoint", False, f"Save benchmark failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Save Benchmark Endpoint", False, f"Save benchmark error: {str(e)}")
            return False
            
        # Step 4: Test GET benchmarks
        try:
            async with self.session.get(f"{API_BASE}/auth/benchmarks", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        self.log_result(
                            "Get Benchmarks", 
                            True, 
                            f"Successfully retrieved {len(data)} benchmark(s)",
                            {"benchmark_count": len(data)}
                        )
                        return True
                    else:
                        self.log_result("Get Benchmarks", False, "No benchmarks found")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Get Benchmarks", False, f"Failed to retrieve benchmarks with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Get Benchmarks", False, f"Get benchmarks error: {str(e)}")
            return False

    # ==================== SCENARIO 3: DYNAMIC ASSESSMENT ANALYSIS ====================
    
    async def test_scenario_3_dynamic_analysis(self):
        """CRITICAL TEST SCENARIO 3: Dynamic Assessment Analysis"""
        print("\n🔥 SCENARIO 3: DYNAMIC ASSESSMENT ANALYSIS 🔥")
        print("=" * 70)
        
        # Step 1: Create assessment with LOW scores (many weaknesses)
        low_assessment = await self.create_test_assessment("Low Score Player", "high_weaknesses")
        if not low_assessment:
            return False
            
        # Step 2: Analyze low score assessment
        try:
            async with self.session.get(f"{API_BASE}/analyze-assessment/Low Score Player") as response:
                if response.status == 200:
                    low_analysis = await response.json()
                    
                    low_weaknesses = low_analysis.get("weaknesses", [])
                    low_duration_options = low_analysis.get("program_duration_options", {})
                    low_suggested_frequency = low_analysis.get("suggested_frequency")
                    
                    # Extract duration for comparison
                    low_recommendations = low_analysis.get("recommendations", {})
                    low_duration_options = low_recommendations.get("program_duration_options", {})
                    low_duration_weeks = low_duration_options.get("5_days", {}).get("weeks", 0)
                    low_suggested_frequency = low_recommendations.get("suggested_frequency")
                    
                    self.log_result(
                        "Low Score Analysis", 
                        len(low_weaknesses) > 0 and low_duration_weeks > 0, 
                        f"Identified {len(low_weaknesses)} weaknesses, duration: {low_duration_weeks}w, frequency: {low_suggested_frequency}",
                        {
                            "weaknesses_count": len(low_weaknesses),
                            "duration_weeks": low_duration_weeks,
                            "suggested_frequency": low_suggested_frequency
                        }
                    )
                    
                else:
                    error_text = await response.text()
                    self.log_result("Low Score Analysis", False, f"Analysis failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Low Score Analysis", False, f"Analysis error: {str(e)}")
            return False
            
        # Step 3: Create assessment with HIGH scores (few weaknesses)
        high_assessment = await self.create_test_assessment("High Score Player", "low_weaknesses")
        if not high_assessment:
            return False
            
        # Step 4: Analyze high score assessment
        try:
            async with self.session.get(f"{API_BASE}/analyze-assessment/High Score Player") as response:
                if response.status == 200:
                    high_analysis = await response.json()
                    
                    high_weaknesses = high_analysis.get("weaknesses", [])
                    high_duration_options = high_analysis.get("program_duration_options", {})
                    high_suggested_frequency = high_analysis.get("suggested_frequency")
                    
                    # Extract duration for comparison
                    high_duration_weeks = high_duration_options.get("5_days", {}).get("weeks", 0)
                    
                    # Verify fewer weaknesses and shorter duration
                    fewer_weaknesses = len(high_weaknesses) < len(low_weaknesses)
                    shorter_duration = high_duration_weeks < low_duration_weeks
                    
                    self.log_result(
                        "High Score Analysis", 
                        fewer_weaknesses and shorter_duration, 
                        f"Identified {len(high_weaknesses)} weaknesses, duration: {high_duration_weeks}w, frequency: {high_suggested_frequency}",
                        {
                            "weaknesses_count": len(high_weaknesses),
                            "duration_weeks": high_duration_weeks,
                            "suggested_frequency": high_suggested_frequency,
                            "fewer_weaknesses": fewer_weaknesses,
                            "shorter_duration": shorter_duration
                        }
                    )
                    
                    # Step 5: Verify dynamic recommendations
                    dynamic_working = fewer_weaknesses and shorter_duration
                    
                    self.log_result(
                        "Dynamic Analysis Verification", 
                        dynamic_working, 
                        f"More weaknesses = longer duration: {len(low_weaknesses)} weaknesses → {low_duration_weeks}w vs {len(high_weaknesses)} weaknesses → {high_duration_weeks}w",
                        {
                            "low_weaknesses": len(low_weaknesses),
                            "low_duration": low_duration_weeks,
                            "high_weaknesses": len(high_weaknesses),
                            "high_duration": high_duration_weeks,
                            "dynamic_working": dynamic_working
                        }
                    )
                    
                    return dynamic_working
                    
                else:
                    error_text = await response.text()
                    self.log_result("High Score Analysis", False, f"Analysis failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("High Score Analysis", False, f"Analysis error: {str(e)}")
            return False

    async def run_all_critical_tests(self):
        """Run all 3 critical fix scenarios"""
        print("🔥 COMPREHENSIVE BACKEND TESTING FOR 3 CRITICAL FIXES 🔥")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Setup test user
            if not await self.setup_test_user():
                print("❌ Failed to setup test user - aborting tests")
                return
                
            # Run the 3 critical scenarios
            scenario_results = []
            
            print("\n" + "="*80)
            scenario_1_result = await self.test_scenario_1_dynamic_duration()
            scenario_results.append(("Dynamic Program Duration", scenario_1_result))
            
            print("\n" + "="*80)
            scenario_2_result = await self.test_scenario_2_report_save()
            scenario_results.append(("Assessment Report Save", scenario_2_result))
            
            print("\n" + "="*80)
            scenario_3_result = await self.test_scenario_3_dynamic_analysis()
            scenario_results.append(("Dynamic Assessment Analysis", scenario_3_result))
            
            # Calculate overall results
            passed_tests = sum(1 for result in self.test_results if "✅ PASS" in result['status'])
            total_tests = len(self.test_results)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # Summary
            print("\n" + "=" * 80)
            print("📊 CRITICAL FIXES TEST SUMMARY")
            print("=" * 80)
            
            print(f"Overall Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
            print("\n🎯 SCENARIO RESULTS:")
            
            for scenario_name, result in scenario_results:
                status = "✅ WORKING" if result else "❌ FAILING"
                print(f"   {status}: {scenario_name}")
                
            # Success criteria verification
            print("\n🔍 SUCCESS CRITERIA VERIFICATION:")
            all_scenarios_pass = all(result for _, result in scenario_results)
            
            if all_scenarios_pass:
                print("🎉 ALL 3 CRITICAL FIXES ARE WORKING CORRECTLY!")
            else:
                print("⚠️  SOME CRITICAL FIXES STILL HAVE ISSUES")
                
            # Detailed results
            print("\n📋 DETAILED TEST RESULTS:")
            for result in self.test_results:
                print(f"{result['status']}: {result['test']} - {result['message']}")
                
            # Critical issues
            failed_tests = [r for r in self.test_results if "❌ FAIL" in r['status']]
            if failed_tests:
                print("\n🚨 CRITICAL ISSUES FOUND:")
                for failed in failed_tests:
                    print(f"   • {failed['test']}: {failed['message']}")
                    if failed.get('details'):
                        print(f"     Details: {failed['details']}")
                        
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = CriticalFixesTest()
    await tester.run_all_critical_tests()

if __name__ == "__main__":
    asyncio.run(main())