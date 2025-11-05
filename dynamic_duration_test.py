#!/usr/bin/env python3
"""
Dynamic Program Duration AND Days Per Week Testing
Testing that BOTH the number of days per week AND the total program duration change based on training frequency selection.
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

class DynamicDurationTest:
    def __init__(self):
        self.session = None
        self.user_data = None
        self.jwt_token = None
        self.assessment_id = None
        self.player_name = "Duration Test Player"
        self.test_results = []
        self.programs_created = []
        
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
            
    async def test_user_registration_and_login(self):
        """Test 1: Register and login test user"""
        try:
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                "username": f"durationtest{unique_id}",
                "email": f"durationtest{unique_id}@test.com", 
                "password": "test123",
                "full_name": "Duration Test User",
                "role": "player",
                "age": 18,
                "position": "Midfielder"
            }
            
            # Register
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_data = data.get("user", {})
                    self.jwt_token = data.get("access_token")
                    
                    if self.jwt_token and self.user_data:
                        self.log_result(
                            "User Registration & Login", 
                            True, 
                            f"Successfully registered and authenticated user: {self.user_data.get('username')}",
                            {"user_id": self.user_data.get("id"), "role": self.user_data.get("role")}
                        )
                        return True
                    else:
                        self.log_result("User Registration & Login", False, "Missing JWT token or user data in response")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("User Registration & Login", False, f"Registration failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("User Registration & Login", False, f"Registration error: {str(e)}")
            return False
            
    async def test_create_assessment_with_gaps(self):
        """Test 2: Create assessment with specific gaps for Duration Test Player"""
        try:
            assessment_data = {
                "player_name": self.player_name,
                "age": 18,
                "position": "Midfielder",
                # Physical metrics (20%) - Mixed performance
                "sprint_30m": 4.4,  # Average for age group
                "yo_yo_test": 1600,  # Good
                "vo2_max": 57.0,  # Good
                "vertical_jump": 52,  # Good
                "body_fat": 11.0,  # Good
                # Technical metrics (40%) - Some weaknesses
                "ball_control": 3,  # Average - WEAKNESS
                "passing_accuracy": 75.0,  # Average - WEAKNESS
                "dribbling_success": 55.0,  # Average - WEAKNESS
                "shooting_accuracy": 60.0,  # Average
                "defensive_duels": 65.0,  # Average
                # Tactical metrics (30%) - Mixed
                "game_intelligence": 4,  # Good
                "positioning": 2,  # Poor - MAJOR WEAKNESS
                "decision_making": 3,  # Average
                # Psychological metrics (10%) - Strong
                "coachability": 5,  # Excellent
                "mental_toughness": 4  # Good
            }
            
            async with self.session.post(f"{API_BASE}/assessments", json=assessment_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.assessment_id = data.get("id")
                    
                    if self.assessment_id:
                        self.log_result(
                            "Assessment Creation with Gaps", 
                            True, 
                            f"Successfully created assessment for {self.player_name} with 3 weaknesses",
                            {
                                "assessment_id": self.assessment_id,
                                "overall_score": data.get("overall_score"),
                                "weaknesses": ["ball_control (3/5)", "passing_accuracy (75%)", "positioning (2/5)"]
                            }
                        )
                        return True
                    else:
                        self.log_result("Assessment Creation with Gaps", False, "No assessment ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Assessment Creation with Gaps", False, f"Assessment creation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Assessment Creation with Gaps", False, f"Assessment creation error: {str(e)}")
            return False
            
    async def test_assessment_analysis_duration_options(self):
        """Test 3: Check if assessment analysis returns different duration options for each frequency"""
        try:
            async with self.session.get(f"{API_BASE}/analyze-assessment/{self.player_name}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if program_duration_options exists
                    duration_options = data.get("program_duration_options", {})
                    
                    if duration_options:
                        three_day = duration_options.get("3_days", {})
                        four_day = duration_options.get("4_days", {})
                        five_day = duration_options.get("5_days", {})
                        
                        # Verify all frequencies have duration data
                        if three_day and four_day and five_day:
                            three_weeks = three_day.get("weeks", 0)
                            four_weeks = four_day.get("weeks", 0)
                            five_weeks = five_day.get("weeks", 0)
                            
                            # Verify duration progression (3-day should be longest, 5-day shortest)
                            if three_weeks > four_weeks > five_weeks:
                                self.log_result(
                                    "Assessment Analysis Duration Options", 
                                    True, 
                                    "Assessment analysis correctly returns different duration options for each frequency",
                                    {
                                        "3_days": f"{three_weeks} weeks",
                                        "4_days": f"{four_weeks} weeks", 
                                        "5_days": f"{five_weeks} weeks",
                                        "duration_progression": "3-day > 4-day > 5-day ✓"
                                    }
                                )
                                return True
                            else:
                                self.log_result("Assessment Analysis Duration Options", False, f"Duration progression incorrect: 3-day={three_weeks}, 4-day={four_weeks}, 5-day={five_weeks}")
                                return False
                        else:
                            self.log_result("Assessment Analysis Duration Options", False, "Missing duration data for some frequencies", {"available": list(duration_options.keys())})
                            return False
                    else:
                        self.log_result("Assessment Analysis Duration Options", False, "No program_duration_options found in assessment analysis")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Assessment Analysis Duration Options", False, f"Assessment analysis failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Assessment Analysis Duration Options", False, f"Assessment analysis error: {str(e)}")
            return False
            
    async def test_generate_5_day_baseline_program(self):
        """Test 4A: Generate 5-Day Program (Baseline) - 10 weeks, 5 days/week = 50 total days"""
        try:
            program_data = {
                "player_id": self.player_name,
                "program_name": "5-Day Baseline Program",
                "total_duration_weeks": 10,
                "program_objectives": ["Test"],
                "training_frequency": 5
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
                if response.status == 200:
                    data = await response.json()
                    program_id = data.get("id")
                    
                    if program_id:
                        # Analyze program structure
                        macro_cycles = data.get("macro_cycles", [])
                        total_weeks = sum(cycle.get("duration_weeks", 0) for cycle in macro_cycles)
                        
                        # Count daily routines
                        total_training_days = 0
                        days_per_week_check = []
                        
                        for cycle in macro_cycles:
                            for micro_cycle in cycle.get("micro_cycles", []):
                                week_days = len(micro_cycle.get("daily_routines", []))
                                days_per_week_check.append(week_days)
                                total_training_days += week_days
                        
                        # Verify 5 days per week
                        correct_days_per_week = all(days == 5 for days in days_per_week_check)
                        expected_total_days = total_weeks * 5
                        
                        if correct_days_per_week and total_training_days == expected_total_days:
                            self.programs_created.append({
                                "frequency": 5,
                                "weeks": total_weeks,
                                "total_days": total_training_days,
                                "program_id": program_id
                            })
                            
                            self.log_result(
                                "5-Day Baseline Program Generation", 
                                True, 
                                f"Successfully generated 5-day program with correct structure",
                                {
                                    "program_id": program_id,
                                    "total_weeks": total_weeks,
                                    "days_per_week": 5,
                                    "total_training_days": total_training_days,
                                    "expected_days": expected_total_days
                                }
                            )
                            return True
                        else:
                            self.log_result("5-Day Baseline Program Generation", False, f"Incorrect program structure: days_per_week_correct={correct_days_per_week}, total_days={total_training_days}, expected={expected_total_days}")
                            return False
                    else:
                        self.log_result("5-Day Baseline Program Generation", False, "No program ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("5-Day Baseline Program Generation", False, f"Program generation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("5-Day Baseline Program Generation", False, f"Program generation error: {str(e)}")
            return False
            
    async def test_generate_4_day_program(self):
        """Test 4B: Generate 4-Day Program - Should be +25% longer (13 weeks), 4 days/week = 52 total days"""
        try:
            program_data = {
                "player_id": self.player_name,
                "program_name": "4-Day Extended Program",
                "total_duration_weeks": 13,  # 10 × 1.25
                "program_objectives": ["Test"],
                "training_frequency": 4
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
                if response.status == 200:
                    data = await response.json()
                    program_id = data.get("id")
                    
                    if program_id:
                        # Analyze program structure
                        macro_cycles = data.get("macro_cycles", [])
                        total_weeks = sum(cycle.get("duration_weeks", 0) for cycle in macro_cycles)
                        
                        # Count daily routines
                        total_training_days = 0
                        days_per_week_check = []
                        
                        for cycle in macro_cycles:
                            for micro_cycle in cycle.get("micro_cycles", []):
                                week_days = len(micro_cycle.get("daily_routines", []))
                                days_per_week_check.append(week_days)
                                total_training_days += week_days
                        
                        # Verify 4 days per week
                        correct_days_per_week = all(days == 4 for days in days_per_week_check)
                        expected_total_days = total_weeks * 4
                        
                        if correct_days_per_week and total_training_days == expected_total_days:
                            self.programs_created.append({
                                "frequency": 4,
                                "weeks": total_weeks,
                                "total_days": total_training_days,
                                "program_id": program_id
                            })
                            
                            self.log_result(
                                "4-Day Extended Program Generation", 
                                True, 
                                f"Successfully generated 4-day program with correct structure",
                                {
                                    "program_id": program_id,
                                    "total_weeks": total_weeks,
                                    "days_per_week": 4,
                                    "total_training_days": total_training_days,
                                    "expected_days": expected_total_days
                                }
                            )
                            return True
                        else:
                            self.log_result("4-Day Extended Program Generation", False, f"Incorrect program structure: days_per_week_correct={correct_days_per_week}, total_days={total_training_days}, expected={expected_total_days}")
                            return False
                    else:
                        self.log_result("4-Day Extended Program Generation", False, "No program ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("4-Day Extended Program Generation", False, f"Program generation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("4-Day Extended Program Generation", False, f"Program generation error: {str(e)}")
            return False
            
    async def test_generate_3_day_program(self):
        """Test 4C: Generate 3-Day Program - Should be +67% longer (17 weeks), 3 days/week = 51 total days"""
        try:
            program_data = {
                "player_id": self.player_name,
                "program_name": "3-Day Extended Program",
                "total_duration_weeks": 17,  # 10 × 1.67
                "program_objectives": ["Test"],
                "training_frequency": 3
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
                if response.status == 200:
                    data = await response.json()
                    program_id = data.get("id")
                    
                    if program_id:
                        # Analyze program structure
                        macro_cycles = data.get("macro_cycles", [])
                        total_weeks = sum(cycle.get("duration_weeks", 0) for cycle in macro_cycles)
                        
                        # Count daily routines
                        total_training_days = 0
                        days_per_week_check = []
                        
                        for cycle in macro_cycles:
                            for micro_cycle in cycle.get("micro_cycles", []):
                                week_days = len(micro_cycle.get("daily_routines", []))
                                days_per_week_check.append(week_days)
                                total_training_days += week_days
                        
                        # Verify 3 days per week
                        correct_days_per_week = all(days == 3 for days in days_per_week_check)
                        expected_total_days = total_weeks * 3
                        
                        if correct_days_per_week and total_training_days == expected_total_days:
                            self.programs_created.append({
                                "frequency": 3,
                                "weeks": total_weeks,
                                "total_days": total_training_days,
                                "program_id": program_id
                            })
                            
                            self.log_result(
                                "3-Day Extended Program Generation", 
                                True, 
                                f"Successfully generated 3-day program with correct structure",
                                {
                                    "program_id": program_id,
                                    "total_weeks": total_weeks,
                                    "days_per_week": 3,
                                    "total_training_days": total_training_days,
                                    "expected_days": expected_total_days
                                }
                            )
                            return True
                        else:
                            self.log_result("3-Day Extended Program Generation", False, f"Incorrect program structure: days_per_week_correct={correct_days_per_week}, total_days={total_training_days}, expected={expected_total_days}")
                            return False
                    else:
                        self.log_result("3-Day Extended Program Generation", False, "No program ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("3-Day Extended Program Generation", False, f"Program generation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("3-Day Extended Program Generation", False, f"Program generation error: {str(e)}")
            return False
            
    async def test_verify_dynamic_duration_math(self):
        """Test 5: Verify the math - duration should change to maintain training volume"""
        try:
            if len(self.programs_created) < 3:
                self.log_result("Dynamic Duration Math Verification", False, "Not enough programs created to verify math")
                return False
                
            # Sort programs by frequency
            programs = sorted(self.programs_created, key=lambda x: x["frequency"])
            
            three_day = next((p for p in programs if p["frequency"] == 3), None)
            four_day = next((p for p in programs if p["frequency"] == 4), None)
            five_day = next((p for p in programs if p["frequency"] == 5), None)
            
            if not (three_day and four_day and five_day):
                self.log_result("Dynamic Duration Math Verification", False, "Missing programs for math verification")
                return False
                
            # Check duration progression (3-day should be longest, 5-day shortest)
            duration_correct = three_day["weeks"] > four_day["weeks"] > five_day["weeks"]
            
            # Check total training days are similar (within reasonable range)
            min_days = min(three_day["total_days"], four_day["total_days"], five_day["total_days"])
            max_days = max(three_day["total_days"], four_day["total_days"], five_day["total_days"])
            days_variance = max_days - min_days
            
            # Allow up to 10% variance in total training days
            acceptable_variance = days_variance <= (min_days * 0.1)
            
            if duration_correct and acceptable_variance:
                self.log_result(
                    "Dynamic Duration Math Verification", 
                    True, 
                    "Math verification PASSED: Duration changes correctly to maintain training volume",
                    {
                        "3_day_program": f"{three_day['weeks']} weeks, {three_day['total_days']} total days",
                        "4_day_program": f"{four_day['weeks']} weeks, {four_day['total_days']} total days",
                        "5_day_program": f"{five_day['weeks']} weeks, {five_day['total_days']} total days",
                        "duration_progression": "3-day > 4-day > 5-day ✓",
                        "days_variance": f"{days_variance} days (acceptable: ≤{min_days * 0.1:.1f})"
                    }
                )
                return True
            else:
                self.log_result(
                    "Dynamic Duration Math Verification", 
                    False, 
                    f"Math verification FAILED: duration_correct={duration_correct}, acceptable_variance={acceptable_variance}",
                    {
                        "3_day": f"{three_day['weeks']}w, {three_day['total_days']}d",
                        "4_day": f"{four_day['weeks']}w, {four_day['total_days']}d", 
                        "5_day": f"{five_day['weeks']}w, {five_day['total_days']}d",
                        "days_variance": days_variance
                    }
                )
                return False
                
        except Exception as e:
            self.log_result("Dynamic Duration Math Verification", False, f"Math verification error: {str(e)}")
            return False
            
    async def test_frontend_integration_check(self):
        """Test 6: Check if frontend components exist and are properly structured"""
        try:
            # Check if TrainingDashboard.js exists and has generateProgram function
            training_dashboard_exists = os.path.exists("/app/frontend/src/components/TrainingDashboard.js")
            assessment_report_exists = os.path.exists("/app/frontend/src/components/AssessmentReport.js")
            
            integration_details = {
                "TrainingDashboard.js": "exists" if training_dashboard_exists else "missing",
                "AssessmentReport.js": "exists" if assessment_report_exists else "missing"
            }
            
            if training_dashboard_exists or assessment_report_exists:
                # Check for generateProgram function in files
                generate_program_found = False
                
                if training_dashboard_exists:
                    with open("/app/frontend/src/components/TrainingDashboard.js", 'r') as f:
                        content = f.read()
                        if "generateProgram" in content and "training_frequency" in content:
                            generate_program_found = True
                            integration_details["generateProgram_function"] = "found in TrainingDashboard.js"
                
                if assessment_report_exists and not generate_program_found:
                    with open("/app/frontend/src/components/AssessmentReport.js", 'r') as f:
                        content = f.read()
                        if "generateProgram" in content:
                            generate_program_found = True
                            integration_details["generateProgram_function"] = "found in AssessmentReport.js"
                
                if generate_program_found:
                    self.log_result(
                        "Frontend Integration Check", 
                        True, 
                        "Frontend components exist and contain generateProgram functionality",
                        integration_details
                    )
                    return True
                else:
                    self.log_result("Frontend Integration Check", False, "Frontend components exist but generateProgram function not found", integration_details)
                    return False
            else:
                self.log_result("Frontend Integration Check", False, "Frontend components not found", integration_details)
                return False
                
        except Exception as e:
            self.log_result("Frontend Integration Check", False, f"Frontend integration check error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all dynamic duration tests"""
        print("🔥 DYNAMIC PROGRAM DURATION AND DAYS PER WEEK TESTING 🔥")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print(f"Test Player: {self.player_name}")
        print("=" * 70)
        
        await self.setup_session()
        
        try:
            # Test sequence
            tests = [
                ("User Registration & Login", self.test_user_registration_and_login),
                ("Assessment Creation with Gaps", self.test_create_assessment_with_gaps),
                ("Assessment Analysis Duration Options", self.test_assessment_analysis_duration_options),
                ("5-Day Baseline Program Generation", self.test_generate_5_day_baseline_program),
                ("4-Day Extended Program Generation", self.test_generate_4_day_program),
                ("3-Day Extended Program Generation", self.test_generate_3_day_program),
                ("Dynamic Duration Math Verification", self.test_verify_dynamic_duration_math),
                ("Frontend Integration Check", self.test_frontend_integration_check)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                print(f"\n🧪 Running: {test_name}")
                success = await test_func()
                if success:
                    passed += 1
                    
            # Summary
            print("\n" + "=" * 70)
            print("📊 DYNAMIC DURATION TEST SUMMARY")
            print("=" * 70)
            
            success_rate = (passed / total) * 100
            print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
            
            if success_rate >= 85:
                print("🎉 EXCELLENT: Dynamic duration functionality is working perfectly!")
            elif success_rate >= 70:
                print("✅ GOOD: Most functionality working, minor issues to address")
            else:
                print("⚠️  NEEDS ATTENTION: Significant issues found in dynamic duration system")
                
            # Key findings
            print("\n🔍 KEY FINDINGS:")
            if self.programs_created:
                print("   Programs Created:")
                for program in sorted(self.programs_created, key=lambda x: x["frequency"]):
                    print(f"   • {program['frequency']}-day: {program['weeks']} weeks, {program['total_days']} total training days")
            
            # Detailed results
            print("\n📋 DETAILED RESULTS:")
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
    tester = DynamicDurationTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())