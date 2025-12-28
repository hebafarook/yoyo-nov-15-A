#!/usr/bin/env python3
"""
Get Started Button Smart Routing Backend Testing
Testing the smart routing logic for the "Get Started" button as requested in the review.

Test Scenarios:
1. User with no assessment - should return empty array from /api/auth/benchmarks
2. User with assessment but no program - should return benchmark data and 404/null for program
3. User with assessment and program - should return both benchmark and program data
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://drill-uploader.preview.emergentagent.com/api"

class GetStartedRoutingTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user = None
        self.jwt_token = None
        
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
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
    async def register_test_user(self):
        """Register a new test user for routing tests"""
        test_name = "User Registration for Routing Test"
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        self.test_user = {
            "username": "routetest001",
            "email": "routetest001@test.com",
            "full_name": "Route Test User",
            "password": "testpass123",
            "role": "player",
            "age": 16,
            "position": "Forward"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=self.test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Store user data and token
                    self.jwt_token = response_data["access_token"]
                    self.test_user["user_id"] = response_data["user"]["id"]
                    self.test_user["player_id"] = response_data["user"]["player_id"]
                    
                    self.log_result(test_name, True, f"User registered successfully with ID: {self.test_user['user_id']}")
                    return True
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
            
    async def login_test_user(self):
        """Login with the test user to get JWT token"""
        test_name = "User Login for Routing Test"
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.jwt_token = response_data["access_token"]
                    self.log_result(test_name, True, "Login successful, JWT token obtained")
                    return True
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
            
    async def test_scenario_1_no_assessment(self):
        """Test Scenario 1: User with no assessment"""
        print("🔥 TESTING SCENARIO 1: User with no assessment")
        print("=" * 50)
        
        test_name = "Scenario 1: GET /api/auth/benchmarks (should return empty array)"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{BACKEND_URL}/auth/benchmarks",
                headers=headers
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    if isinstance(response_data, list) and len(response_data) == 0:
                        self.log_result(test_name, True, "Correctly returned empty array - user should be routed to assessment page")
                        return True
                    else:
                        self.log_result(test_name, False, f"Expected empty array, got: {response_data}")
                        return False
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
            
    async def test_scenario_2_assessment_no_program(self):
        """Test Scenario 2: User with assessment but no program"""
        print("🔥 TESTING SCENARIO 2: User with assessment but no program")
        print("=" * 50)
        
        # Step 1: Create an assessment
        assessment_test = "Scenario 2: Create Assessment"
        assessment_data = {
            "user_id": self.test_user["user_id"],
            "player_name": "Route Test Player",
            "age": 16,
            "position": "Forward",
            # Physical metrics
            "sprint_30m": 4.5,
            "yo_yo_test": 1600,
            "vo2_max": 55.0,
            "vertical_jump": 45,
            "body_fat": 12.0,
            # Technical metrics
            "ball_control": 4,
            "passing_accuracy": 75.0,
            "dribbling_success": 65.0,
            "shooting_accuracy": 60.0,
            "defensive_duels": 70.0,
            # Tactical metrics
            "game_intelligence": 4,
            "positioning": 3,
            "decision_making": 4,
            # Psychological metrics
            "coachability": 5,
            "mental_toughness": 4
        }
        
        assessment_id = None
        try:
            async with self.session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    assessment_id = response_data["id"]
                    self.log_result(assessment_test, True, f"Assessment created with ID: {assessment_id}")
                else:
                    self.log_result(assessment_test, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(assessment_test, False, f"Exception: {str(e)}")
            return False
            
        # Step 2: Save assessment as benchmark
        benchmark_test = "Scenario 2: Save Assessment as Benchmark"
        benchmark_data = {
            "user_id": self.test_user["user_id"],
            "player_name": "Route Test Player",
            "assessment_id": assessment_id,
            "age": 16,
            "position": "Forward",
            "sprint_30m": 4.5,
            "yo_yo_test": 1600,
            "vo2_max": 55.0,
            "vertical_jump": 45,
            "body_fat": 12.0,
            "ball_control": 4,
            "passing_accuracy": 75.0,
            "dribbling_success": 65.0,
            "shooting_accuracy": 60.0,
            "defensive_duels": 70.0,
            "game_intelligence": 4,
            "positioning": 3,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4,
            "overall_score": 3.8,
            "performance_level": "Good"
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/save-benchmark",
                json=benchmark_data,
                headers=headers
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.log_result(benchmark_test, True, f"Benchmark saved successfully")
                else:
                    self.log_result(benchmark_test, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(benchmark_test, False, f"Exception: {str(e)}")
            return False
            
        # Step 3: Check benchmarks endpoint returns data
        benchmarks_test = "Scenario 2: GET /api/auth/benchmarks (should return 1 benchmark)"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{BACKEND_URL}/auth/benchmarks",
                headers=headers
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    if isinstance(response_data, list) and len(response_data) == 1:
                        benchmark = response_data[0]
                        if "player_name" in benchmark and benchmark["player_name"] == "Route Test Player":
                            self.log_result(benchmarks_test, True, f"Correctly returned 1 benchmark with player_name: {benchmark['player_name']}")
                        else:
                            self.log_result(benchmarks_test, False, f"Benchmark missing player_name or incorrect: {benchmark}")
                            return False
                    else:
                        self.log_result(benchmarks_test, False, f"Expected 1 benchmark, got: {len(response_data) if isinstance(response_data, list) else 'not a list'}")
                        return False
                else:
                    self.log_result(benchmarks_test, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(benchmarks_test, False, f"Exception: {str(e)}")
            return False
            
        # Step 4: Check program endpoint returns 404/null
        program_test = "Scenario 2: GET /api/periodized-programs/Route Test Player (should return 404 or null)"
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/periodized-programs/Route Test Player",
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 404:
                    self.log_result(program_test, True, "Correctly returned 404 - no program exists, user should be routed to training page to generate program")
                    return True
                elif response.status == 200:
                    response_data = await response.json()
                    if response_data is None or (isinstance(response_data, list) and len(response_data) == 0):
                        self.log_result(program_test, True, "Correctly returned null/empty - no program exists, user should be routed to training page to generate program")
                        return True
                    else:
                        self.log_result(program_test, False, f"Expected 404 or null, got data: {response_data}")
                        return False
                else:
                    response_data = await response.json()
                    self.log_result(program_test, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(program_test, False, f"Exception: {str(e)}")
            return False
            
    async def test_scenario_3_assessment_and_program(self):
        """Test Scenario 3: User with assessment and program"""
        print("🔥 TESTING SCENARIO 3: User with assessment and program")
        print("=" * 50)
        
        # Step 1: Create a periodized program for the player
        program_test = "Scenario 3: Create Periodized Program"
        program_data = {
            "player_id": "Route Test Player",  # Using player_name as player_id
            "program_name": "Elite Training Program for Route Test Player",
            "total_duration_weeks": 14,
            "program_objectives": [
                "Improve shooting accuracy from 60% to 75%",
                "Enhance positioning skills from 3/5 to 4/5",
                "Build overall fitness and endurance"
            ]
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    program_id = response_data["id"]
                    self.log_result(program_test, True, f"Periodized program created with ID: {program_id}")
                else:
                    self.log_result(program_test, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(program_test, False, f"Exception: {str(e)}")
            return False
            
        # Step 2: Verify benchmarks still return data
        benchmarks_test = "Scenario 3: GET /api/auth/benchmarks (should still return benchmark)"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{BACKEND_URL}/auth/benchmarks",
                headers=headers
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    if isinstance(response_data, list) and len(response_data) >= 1:
                        self.log_result(benchmarks_test, True, f"Correctly returned {len(response_data)} benchmark(s)")
                    else:
                        self.log_result(benchmarks_test, False, f"Expected at least 1 benchmark, got: {len(response_data) if isinstance(response_data, list) else 'not a list'}")
                        return False
                else:
                    self.log_result(benchmarks_test, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(benchmarks_test, False, f"Exception: {str(e)}")
            return False
            
        # Step 3: Verify program endpoint returns the program
        program_get_test = "Scenario 3: GET /api/periodized-programs/Route Test Player (should return program)"
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/periodized-programs/Route Test Player",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    if isinstance(response_data, list) and len(response_data) > 0:
                        program = response_data[0]
                        if "player_id" in program and program["player_id"] == "Route Test Player":
                            self.log_result(program_get_test, True, f"Correctly returned program for player: {program['player_id']} - user should be routed to training page to continue program")
                            return True
                        else:
                            self.log_result(program_get_test, False, f"Program player_id mismatch: {program}")
                            return False
                    elif isinstance(response_data, dict) and "player_id" in response_data:
                        if response_data["player_id"] == "Route Test Player":
                            self.log_result(program_get_test, True, f"Correctly returned program for player: {response_data['player_id']} - user should be routed to training page to continue program")
                            return True
                        else:
                            self.log_result(program_get_test, False, f"Program player_id mismatch: {response_data}")
                            return False
                    else:
                        self.log_result(program_get_test, False, f"Unexpected response format: {response_data}")
                        return False
                else:
                    self.log_result(program_get_test, False, f"HTTP {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(program_get_test, False, f"Exception: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all Get Started routing tests"""
        print("🔥 STARTING GET STARTED BUTTON SMART ROUTING TESTING 🔥")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 70)
        print()
        
        await self.setup()
        
        try:
            # Setup: Register and login test user
            if not await self.register_test_user():
                print("❌ Failed to register test user. Aborting tests.")
                return 0, 1
                
            if not await self.login_test_user():
                print("❌ Failed to login test user. Aborting tests.")
                return 0, 1
                
            # Test Scenario 1: No assessment
            scenario1_success = await self.test_scenario_1_no_assessment()
            
            # Test Scenario 2: Assessment but no program
            scenario2_success = await self.test_scenario_2_assessment_no_program()
            
            # Test Scenario 3: Assessment and program
            scenario3_success = await self.test_scenario_3_assessment_and_program()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("=" * 70)
        print("🏆 GET STARTED ROUTING TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Scenario Results
        print("📊 SCENARIO RESULTS:")
        print(f"Scenario 1 (No Assessment): {'✅ PASS' if scenario1_success else '❌ FAIL'}")
        print(f"Scenario 2 (Assessment, No Program): {'✅ PASS' if scenario2_success else '❌ FAIL'}")
        print(f"Scenario 3 (Assessment + Program): {'✅ PASS' if scenario3_success else '❌ FAIL'}")
        print()
        
        # Smart Routing Logic Summary
        print("🧠 SMART ROUTING LOGIC VERIFICATION:")
        if scenario1_success:
            print("✅ Empty benchmarks → Route to Assessment Page")
        if scenario2_success:
            print("✅ Has benchmarks, No program → Route to Training Page (Generate)")
        if scenario3_success:
            print("✅ Has benchmarks + program → Route to Training Page (Continue)")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
            
        print("=" * 70)
        print(f"Test completed at: {datetime.now()}")
        print("=" * 70)
        
        return passed_tests, failed_tests

async def main():
    """Main test execution"""
    tester = GetStartedRoutingTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())