#!/usr/bin/env python3
"""
Training Program Generation Issue Testing
Testing the specific scenario described in the review request.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://soccerpro-api.preview.emergentagent.com/api"

class TrainingProgramTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user = None
        self.assessment_data = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
    async def test_step_1_register_user(self):
        """Step 1: Register user as specified in review request"""
        test_name = "Step 1: Register Test User"
        
        test_user = {
            "username": "progtest001",
            "email": "progtest001@test.com",
            "password": "test123",
            "full_name": "Program Test",
            "role": "player",
            "age": 17,
            "position": "Forward"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.test_user = {
                        "username": test_user["username"],
                        "password": test_user["password"],
                        "user_data": response_data["user"],
                        "token": response_data["access_token"]
                    }
                    self.log_result(test_name, True, f"User registered successfully with ID: {response_data['user']['id']}")
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_step_2_create_assessment(self):
        """Step 2: Create assessment for player 'Program Test Player'"""
        test_name = "Step 2: Create Assessment"
        
        if not self.test_user:
            self.log_result(test_name, False, "No test user available")
            return
            
        # Assessment data with complete Youth Handbook fields
        assessment_data = {
            "player_name": "Program Test Player",
            "age": 17,
            "position": "Forward",
            # Physical metrics (20%)
            "sprint_30m": 4.5,
            "yo_yo_test": 1600,
            "vo2_max": 55.0,
            "vertical_jump": 52,
            "body_fat": 12.0,
            # Technical metrics (40%)
            "ball_control": 3,
            "passing_accuracy": 70.0,
            "dribbling_success": 65.0,
            "shooting_accuracy": 60.0,
            "defensive_duels": 55.0,
            # Tactical metrics (30%)
            "game_intelligence": 3,
            "positioning": 3,
            "decision_making": 4,
            # Psychological metrics (10%)
            "coachability": 4,
            "mental_toughness": 3
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.assessment_data = response_data
                    # Verify player_name field is saved correctly
                    if response_data.get("player_name") == "Program Test Player":
                        self.log_result(test_name, True, f"Assessment created successfully with player_name: {response_data['player_name']}")
                    else:
                        self.log_result(test_name, False, f"player_name mismatch: expected 'Program Test Player', got '{response_data.get('player_name')}'", response_data)
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_step_3_get_assessment_analysis(self):
        """Step 3: Get assessment analysis for 'Program Test Player'"""
        test_name = "Step 3: Get Assessment Analysis"
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/analyze-assessment/Program Test Player",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify analysis contains expected fields
                    required_fields = ["player_name", "strengths", "weaknesses", "recommendations"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing fields in analysis: {missing_fields}", response_data)
                    else:
                        # Check if recommendations include duration options
                        recommendations = response_data.get("recommendations", {})
                        if "program_duration" in recommendations:
                            self.log_result(test_name, True, f"Analysis successful with duration: {recommendations['program_duration']} weeks")
                        else:
                            self.log_result(test_name, False, "No program_duration in recommendations", response_data)
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_step_4_attempt_create_program(self):
        """Step 4: Attempt to create training program"""
        test_name = "Step 4: Create Training Program"
        
        program_data = {
            "player_id": "Program Test Player",
            "program_name": "Test Program",
            "total_duration_weeks": 12,
            "program_objectives": ["Test objective"],
            "assessment_interval_weeks": 4,
            "training_frequency": 5
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.log_result(test_name, True, f"Program created successfully with ID: {response_data.get('id')}")
                else:
                    # This is where we expect to capture the error
                    self.log_result(test_name, False, f"HTTP {response.status} - CAPTURED ERROR", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_step_5_check_database(self):
        """Step 5: Check what's in the database"""
        test_name = "Step 5: Database Verification"
        
        try:
            # Check assessments collection for player_name "Program Test Player"
            async with self.session.get(
                f"{BACKEND_URL}/assessments/player/Program Test Player",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    if isinstance(response_data, list) and len(response_data) > 0:
                        assessment = response_data[0]
                        player_name = assessment.get("player_name")
                        self.log_result(test_name, True, f"Found assessment in database with player_name: '{player_name}'")
                        
                        # Print all relevant fields for debugging
                        print("   DATABASE ASSESSMENT FIELDS:")
                        for key, value in assessment.items():
                            if key in ["id", "player_name", "age", "position", "created_at", "assessment_date"]:
                                print(f"     {key}: {value}")
                        print()
                    else:
                        self.log_result(test_name, False, "No assessments found in database", response_data)
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_debug_field_mismatch(self):
        """Debug: Test different player_id variations"""
        test_name = "Debug: Test Field Mismatch Scenarios"
        
        # Test various player_id formats that might work
        test_scenarios = [
            {"player_id": "Program Test Player", "description": "Original format"},
            {"player_id": self.assessment_data.get("id") if self.assessment_data else "unknown", "description": "Assessment ID"},
            {"player_id": self.test_user["user_data"]["id"] if self.test_user else "unknown", "description": "User ID"},
        ]
        
        for scenario in test_scenarios:
            if scenario["player_id"] == "unknown":
                continue
                
            program_data = {
                "player_id": scenario["player_id"],
                "program_name": f"Test Program - {scenario['description']}",
                "total_duration_weeks": 12,
                "program_objectives": ["Test objective"],
                "assessment_interval_weeks": 4,
                "training_frequency": 5
            }
            
            try:
                async with self.session.post(
                    f"{BACKEND_URL}/periodized-programs",
                    json=program_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
                    scenario_name = f"{test_name} - {scenario['description']}"
                    if response.status == 200:
                        self.log_result(scenario_name, True, f"SUCCESS with player_id: {scenario['player_id']}")
                    else:
                        self.log_result(scenario_name, False, f"HTTP {response.status} with player_id: {scenario['player_id']}", response_data)
                        
            except Exception as e:
                self.log_result(f"{test_name} - {scenario['description']}", False, f"Exception: {str(e)}")
                
    async def run_all_tests(self):
        """Run all training program generation tests"""
        print("🔥 TRAINING PROGRAM GENERATION ISSUE TESTING 🔥")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 60)
        print()
        
        await self.setup()
        
        try:
            # Follow the exact steps from the review request
            await self.test_step_1_register_user()
            await self.test_step_2_create_assessment()
            await self.test_step_3_get_assessment_analysis()
            await self.test_step_4_attempt_create_program()
            await self.test_step_5_check_database()
            
            # Additional debugging
            await self.test_debug_field_mismatch()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("=" * 60)
        print("🏆 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
            
        print("=" * 60)
        print("🔍 DEBUGGING INFORMATION")
        print("=" * 60)
        
        if self.assessment_data:
            print("ASSESSMENT DATA CREATED:")
            print(f"  - ID: {self.assessment_data.get('id')}")
            print(f"  - Player Name: {self.assessment_data.get('player_name')}")
            print(f"  - Age: {self.assessment_data.get('age')}")
            print(f"  - Position: {self.assessment_data.get('position')}")
            print()
            
        if self.test_user:
            print("USER DATA CREATED:")
            print(f"  - User ID: {self.test_user['user_data'].get('id')}")
            print(f"  - Username: {self.test_user['user_data'].get('username')}")
            print(f"  - Role: {self.test_user['user_data'].get('role')}")
            print()
            
        print("=" * 60)
        print(f"Test completed at: {datetime.now()}")
        print("=" * 60)
        
        return passed_tests, failed_tests

async def main():
    """Main test execution"""
    tester = TrainingProgramTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())