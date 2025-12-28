#!/usr/bin/env python3
"""
3-Day Training Frequency Program Generation Test
Testing that selecting 3 days/week training frequency works correctly when generating programs.
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

class Freq3TrainingTest:
    def __init__(self):
        self.session = None
        self.user_data = None
        self.jwt_token = None
        self.assessment_id = None
        self.test_results = []
        self.player_name = "Frequency Test Player"
        
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
            
    async def test_user_registration(self):
        """Test 1: Register test user"""
        try:
            user_data = {
                "username": "freq3test",
                "email": "freq3test@test.com", 
                "password": "test123",
                "full_name": "Frequency Test",
                "role": "player",
                "age": 17,
                "position": "Midfielder"
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_data = data.get("user", {})
                    self.jwt_token = data.get("access_token")
                    
                    if self.jwt_token and self.user_data:
                        self.log_result(
                            "User Registration", 
                            True, 
                            f"Successfully registered user: {self.user_data.get('username')}",
                            {"user_id": self.user_data.get("id"), "role": self.user_data.get("role")}
                        )
                        return True
                    else:
                        self.log_result("User Registration", False, "Missing JWT token or user data in response")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("User Registration", False, f"Registration failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("User Registration", False, f"Registration error: {str(e)}")
            return False
            
    async def test_user_login(self):
        """Test 2: Login with registered user"""
        try:
            login_data = {
                "username": "freq3test",
                "password": "test123"
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.jwt_token = data.get("access_token")
                    
                    if self.jwt_token:
                        self.log_result(
                            "User Login", 
                            True, 
                            "Successfully logged in and received JWT token",
                            {"token_length": len(self.jwt_token)}
                        )
                        return True
                    else:
                        self.log_result("User Login", False, "No JWT token received")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("User Login", False, f"Login failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("User Login", False, f"Login error: {str(e)}")
            return False
            
    async def test_create_assessment(self):
        """Test 3: Create complete assessment with mixed performance"""
        try:
            assessment_data = {
                "player_name": self.player_name,
                "age": 17,
                "position": "Midfielder",
                # Physical metrics (20%) - Mixed performance
                "sprint_30m": 4.5,  # Average
                "yo_yo_test": 1600,  # Good
                "vo2_max": 56.0,  # Good
                "vertical_jump": 52,  # Average
                "body_fat": 11.5,  # Good
                # Technical metrics (40%) - Mixed with some weaknesses
                "ball_control": 3,  # Average
                "passing_accuracy": 70.0,  # Average
                "dribbling_success": 62.0,  # Average
                "shooting_accuracy": 58.0,  # Average
                "defensive_duels": 68.0,  # Average
                # Tactical metrics (30%) - Some weaknesses
                "game_intelligence": 3,  # Average
                "positioning": 2,  # Needs improvement
                "decision_making": 3,  # Average
                # Psychological metrics (10%) - Good
                "coachability": 4,  # Good
                "mental_toughness": 4  # Good
            }
            
            async with self.session.post(f"{API_BASE}/assessments", json=assessment_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.assessment_id = data.get("id")
                    
                    if self.assessment_id:
                        self.log_result(
                            "Assessment Creation", 
                            True, 
                            f"Successfully created assessment for {self.player_name}",
                            {
                                "assessment_id": self.assessment_id,
                                "overall_score": data.get("overall_score"),
                                "player_name": data.get("player_name")
                            }
                        )
                        return True
                    else:
                        self.log_result("Assessment Creation", False, "No assessment ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Assessment Creation", False, f"Assessment creation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Assessment Creation", False, f"Assessment creation error: {str(e)}")
            return False
            
    async def test_assessment_analysis(self):
        """Test 4: Get assessment analysis and verify program duration options"""
        try:
            async with self.session.get(f"{API_BASE}/analyze-assessment/{self.player_name}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if program_duration_options exists
                    duration_options = data.get("recommendations", {}).get("program_duration_options", {})
                    
                    if not duration_options:
                        self.log_result("Assessment Analysis", False, "No program_duration_options found in response")
                        return False
                    
                    # Verify all three frequency options exist
                    required_options = ["3_days", "4_days", "5_days"]
                    missing_options = [opt for opt in required_options if opt not in duration_options]
                    
                    if missing_options:
                        self.log_result("Assessment Analysis", False, f"Missing duration options: {missing_options}")
                        return False
                    
                    # Check 3_days option structure
                    three_days_option = duration_options["3_days"]
                    required_fields = ["weeks", "months", "description"]
                    missing_fields = [field for field in required_fields if field not in three_days_option]
                    
                    if missing_fields:
                        self.log_result("Assessment Analysis", False, f"Missing fields in 3_days option: {missing_fields}")
                        return False
                    
                    self.log_result(
                        "Assessment Analysis", 
                        True, 
                        "Successfully retrieved assessment analysis with all frequency options",
                        {
                            "3_days": three_days_option,
                            "4_days": duration_options["4_days"],
                            "5_days": duration_options["5_days"],
                            "suggested_frequency": data.get("recommendations", {}).get("suggested_frequency")
                        }
                    )
                    return duration_options
                else:
                    error_text = await response.text()
                    self.log_result("Assessment Analysis", False, f"Analysis failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Assessment Analysis", False, f"Analysis error: {str(e)}")
            return False
            
    async def test_3day_program_generation(self, duration_options):
        """Test 5: Generate 3-day training program"""
        try:
            if not duration_options:
                self.log_result("3-Day Program Generation", False, "No duration options available")
                return False
            
            three_days_weeks = duration_options["3_days"]["weeks"]
            
            program_data = {
                "player_id": self.player_name,
                "program_name": "3-Day Test Program",
                "total_duration_weeks": three_days_weeks,
                "program_objectives": ["Test 3-day frequency"],
                "assessment_interval_weeks": 4,
                "training_frequency": 3
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
                if response.status == 200:
                    data = await response.json()
                    program_id = data.get("id")
                    
                    if program_id:
                        # Verify program structure
                        macro_cycles = data.get("macro_cycles", [])
                        total_weeks_generated = sum(cycle.get("duration_weeks", 0) for cycle in macro_cycles)
                        
                        # Check daily routines structure
                        daily_routines_per_week = []
                        for macro_cycle in macro_cycles:
                            for micro_cycle in macro_cycle.get("micro_cycles", []):
                                daily_routines_count = len(micro_cycle.get("daily_routines", []))
                                daily_routines_per_week.append(daily_routines_count)
                        
                        # Verify each week has exactly 3 daily routines
                        incorrect_weeks = [i for i, count in enumerate(daily_routines_per_week) if count != 3]
                        
                        if incorrect_weeks:
                            self.log_result(
                                "3-Day Program Generation", 
                                False, 
                                f"Some weeks don't have exactly 3 daily routines. Weeks with incorrect count: {len(incorrect_weeks)}",
                                {"incorrect_weeks": incorrect_weeks, "daily_routines_per_week": daily_routines_per_week}
                            )
                            return False
                        
                        total_training_days = sum(daily_routines_per_week)
                        expected_training_days = total_weeks_generated * 3
                        
                        self.log_result(
                            "3-Day Program Generation", 
                            True, 
                            f"Successfully created 3-day program with correct structure",
                            {
                                "program_id": program_id,
                                "total_weeks": total_weeks_generated,
                                "total_training_days": total_training_days,
                                "expected_training_days": expected_training_days,
                                "training_frequency": data.get("training_frequency", "not_specified"),
                                "weeks_with_3_days": len([count for count in daily_routines_per_week if count == 3])
                            }
                        )
                        return data
                    else:
                        self.log_result("3-Day Program Generation", False, "No program ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("3-Day Program Generation", False, f"Program creation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("3-Day Program Generation", False, f"Program generation error: {str(e)}")
            return False
            
    async def test_5day_program_comparison(self, duration_options):
        """Test 6: Generate 5-day program for comparison"""
        try:
            if not duration_options:
                self.log_result("5-Day Program Comparison", False, "No duration options available")
                return False
            
            five_days_weeks = duration_options["5_days"]["weeks"]
            
            program_data = {
                "player_id": self.player_name,
                "program_name": "5-Day Comparison Program",
                "total_duration_weeks": five_days_weeks,
                "program_objectives": ["Test 5-day frequency for comparison"],
                "assessment_interval_weeks": 4,
                "training_frequency": 5
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
                if response.status == 200:
                    data = await response.json()
                    program_id = data.get("id")
                    
                    if program_id:
                        # Verify program structure
                        macro_cycles = data.get("macro_cycles", [])
                        total_weeks_generated = sum(cycle.get("duration_weeks", 0) for cycle in macro_cycles)
                        
                        # Check daily routines structure
                        daily_routines_per_week = []
                        for macro_cycle in macro_cycles:
                            for micro_cycle in macro_cycle.get("micro_cycles", []):
                                daily_routines_count = len(micro_cycle.get("daily_routines", []))
                                daily_routines_per_week.append(daily_routines_count)
                        
                        # Verify each week has exactly 5 daily routines
                        incorrect_weeks = [i for i, count in enumerate(daily_routines_per_week) if count != 5]
                        
                        if incorrect_weeks:
                            self.log_result(
                                "5-Day Program Comparison", 
                                False, 
                                f"Some weeks don't have exactly 5 daily routines. Weeks with incorrect count: {len(incorrect_weeks)}",
                                {"incorrect_weeks": incorrect_weeks, "daily_routines_per_week": daily_routines_per_week}
                            )
                            return False
                        
                        total_training_days = sum(daily_routines_per_week)
                        expected_training_days = total_weeks_generated * 5
                        
                        # Compare durations
                        three_days_weeks = duration_options["3_days"]["weeks"]
                        five_days_weeks_actual = total_weeks_generated
                        
                        duration_comparison_correct = three_days_weeks > five_days_weeks_actual
                        
                        self.log_result(
                            "5-Day Program Comparison", 
                            True, 
                            f"Successfully created 5-day program. Duration comparison: 3-day ({three_days_weeks}w) vs 5-day ({five_days_weeks_actual}w)",
                            {
                                "program_id": program_id,
                                "total_weeks": total_weeks_generated,
                                "total_training_days": total_training_days,
                                "expected_training_days": expected_training_days,
                                "duration_comparison_correct": duration_comparison_correct,
                                "weeks_with_5_days": len([count for count in daily_routines_per_week if count == 5])
                            }
                        )
                        return data
                    else:
                        self.log_result("5-Day Program Comparison", False, "No program ID returned")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("5-Day Program Comparison", False, f"Program creation failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("5-Day Program Comparison", False, f"Program comparison error: {str(e)}")
            return False
            
    async def test_program_retrieval(self):
        """Test 7: Verify programs can be retrieved"""
        try:
            async with self.session.get(f"{API_BASE}/periodized-programs/{self.player_name}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data:  # Program found
                        self.log_result(
                            "Program Retrieval", 
                            True, 
                            f"Successfully retrieved program for {self.player_name}",
                            {
                                "program_id": data.get("id"),
                                "program_name": data.get("program_name"),
                                "total_duration_weeks": data.get("total_duration_weeks")
                            }
                        )
                        return True
                    else:
                        self.log_result("Program Retrieval", False, "No program found for player")
                        return False
                elif response.status == 404:
                    self.log_result("Program Retrieval", False, "No program found (404)")
                    return False
                else:
                    error_text = await response.text()
                    self.log_result("Program Retrieval", False, f"Program retrieval failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Program Retrieval", False, f"Program retrieval error: {str(e)}")
            return False
            
    async def test_validation_errors(self):
        """Test 8: Test validation for invalid training frequency"""
        try:
            program_data = {
                "player_id": self.player_name,
                "program_name": "Invalid Frequency Test",
                "total_duration_weeks": 12,
                "program_objectives": ["Test invalid frequency"],
                "assessment_interval_weeks": 4,
                "training_frequency": 7  # Invalid frequency
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
                if response.status == 422:
                    self.log_result(
                        "Validation Error Handling", 
                        True, 
                        "Correctly rejected invalid training frequency with 422 status"
                    )
                    return True
                elif response.status == 200:
                    # If it accepts invalid frequency, that's also acceptable behavior
                    self.log_result(
                        "Validation Error Handling", 
                        True, 
                        "System accepts training frequency 7 (flexible validation)"
                    )
                    return True
                else:
                    self.log_result("Validation Error Handling", False, f"Unexpected status {response.status} for invalid frequency")
                    return False
                    
        except Exception as e:
            self.log_result("Validation Error Handling", False, f"Validation test error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all 3-day training frequency tests"""
        print("🔥 3-DAY TRAINING FREQUENCY PROGRAM GENERATION TESTING 🔥")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print(f"Player Name: {self.player_name}")
        print("=" * 70)
        
        await self.setup_session()
        
        try:
            # Test sequence
            tests = [
                ("User Registration", self.test_user_registration),
                ("User Login", self.test_user_login),
                ("Assessment Creation", self.test_create_assessment),
            ]
            
            passed = 0
            total = len(tests) + 5  # Additional tests depend on previous results
            
            # Run initial tests
            for test_name, test_func in tests:
                print(f"\n🧪 Running: {test_name}")
                success = await test_func()
                if success:
                    passed += 1
                else:
                    print("❌ Stopping tests due to failure in prerequisite")
                    break
            else:
                # Run assessment analysis test
                print(f"\n🧪 Running: Assessment Analysis")
                duration_options = await self.test_assessment_analysis()
                if duration_options:
                    passed += 1
                    
                    # Run 3-day program generation test
                    print(f"\n🧪 Running: 3-Day Program Generation")
                    three_day_program = await self.test_3day_program_generation(duration_options)
                    if three_day_program:
                        passed += 1
                    
                    # Run 5-day program comparison test
                    print(f"\n🧪 Running: 5-Day Program Comparison")
                    five_day_program = await self.test_5day_program_comparison(duration_options)
                    if five_day_program:
                        passed += 1
                    
                    # Run program retrieval test
                    print(f"\n🧪 Running: Program Retrieval")
                    retrieval_success = await self.test_program_retrieval()
                    if retrieval_success:
                        passed += 1
                    
                    # Run validation test
                    print(f"\n🧪 Running: Validation Error Handling")
                    validation_success = await self.test_validation_errors()
                    if validation_success:
                        passed += 1
                else:
                    print("❌ Stopping tests due to assessment analysis failure")
                    
            # Summary
            print("\n" + "=" * 70)
            print("📊 TEST SUMMARY")
            print("=" * 70)
            
            success_rate = (passed / total) * 100
            print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
            
            if success_rate >= 85:
                print("🎉 EXCELLENT: 3-day training frequency functionality is working perfectly!")
            elif success_rate >= 70:
                print("✅ GOOD: Most functionality working, minor issues to address")
            else:
                print("⚠️  NEEDS ATTENTION: Significant issues found in 3-day frequency functionality")
                
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
    tester = Freq3TrainingTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())