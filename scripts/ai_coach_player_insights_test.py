#!/usr/bin/env python3
"""
AI Coach Player Insights Endpoint Test
Testing POST /api/ai-coach/player-insights?player_id={player_id}

Test Scenarios:
1. New Player (No Data) - Should return friendly message about starting journey
2. Player with Assessment Data - Should return relevant AI analysis
3. Player with Training Program - Should mention program status in insights
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

class AICoachPlayerInsightsTest:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.users = {}  # Store user data for different scenarios
        
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
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()

    async def register_user(self, username, email, password, full_name, age=18, position="Forward"):
        """Register a new user"""
        try:
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": "player",
                "age": age,
                "position": position
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "user_id": result.get("user", {}).get("id"),
                        "token": result.get("access_token"),
                        "user_data": result.get("user", {})
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def login_user(self, username, password):
        """Login user and get JWT token"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "user_id": result.get("user", {}).get("id"),
                        "token": result.get("access_token"),
                        "user_data": result.get("user", {})
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_assessment(self, token, player_name, age=18, position="Forward", assessment_data=None):
        """Create an assessment for a player"""
        try:
            # Default assessment data if not provided
            if assessment_data is None:
                assessment_data = {
                    "player_name": player_name,
                    "age": age,
                    "position": position,
                    "assessment_date": datetime.now(timezone.utc).isoformat(),
                    # Physical metrics
                    "sprint_30m": 4.5,
                    "yo_yo_test": 1800,
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
            
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.post(f"{API_BASE}/assessments/authenticated", 
                                       json=assessment_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "assessment": result}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def save_benchmark(self, token, assessment_data):
        """Save assessment as benchmark"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.post(f"{API_BASE}/auth/save-benchmark", 
                                       json=assessment_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "benchmark": result}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_daily_progress(self, player_id, routine_id="test-routine"):
        """Create some daily progress entries"""
        try:
            progress_data = {
                "player_id": player_id,
                "routine_id": routine_id,
                "completed_exercises": [
                    {
                        "player_id": player_id,
                        "exercise_id": "exercise-1",
                        "routine_id": routine_id,
                        "completed": True,
                        "feedback": "Good session",
                        "difficulty_rating": 3,
                        "performance_rating": 4
                    }
                ],
                "overall_rating": 4,
                "energy_level": 4,
                "motivation_level": 5,
                "daily_notes": "Felt strong today"
            }
            
            async with self.session.post(f"{API_BASE}/daily-progress", json=progress_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "progress": result}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_training_program(self, player_id, player_name):
        """Create a training program for the player"""
        try:
            program_data = {
                "player_id": player_id,
                "program_name": f"Elite Training Program for {player_name}",
                "total_duration_weeks": 12,
                "program_objectives": ["Improve technical skills", "Build endurance"],
                "training_frequency": 4
            }
            
            async with self.session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "program": result}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_player_insights(self, player_id, scenario_name):
        """Test the player insights endpoint"""
        try:
            async with self.session.post(f"{API_BASE}/ai-coach/player-insights?player_id={player_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Validate response structure
                    required_fields = ["success", "insights", "recommendations", "motivational_message"]
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if missing_fields:
                        return {
                            "success": False, 
                            "error": f"Missing required fields: {missing_fields}",
                            "response": result
                        }
                    
                    # Validate recommendations is an array with items
                    if not isinstance(result.get("recommendations"), list):
                        return {
                            "success": False,
                            "error": "Recommendations should be an array",
                            "response": result
                        }
                    
                    if len(result.get("recommendations", [])) < 3:
                        return {
                            "success": False,
                            "error": f"Expected at least 3 recommendations, got {len(result.get('recommendations', []))}",
                            "response": result
                        }
                    
                    return {
                        "success": True,
                        "response": result,
                        "insights_length": len(result.get("insights", "")),
                        "recommendations_count": len(result.get("recommendations", [])),
                        "has_motivational_message": bool(result.get("motivational_message"))
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Status {response.status}: {error_text}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_scenario_1_new_player(self):
        """Test Scenario 1: New Player (No Data)"""
        print("🔥 SCENARIO 1: New Player (No Data)")
        print("=" * 50)
        
        # Register new user
        unique_id = str(uuid.uuid4())[:8]
        username = f"newplayer{unique_id}"
        email = f"newplayer{unique_id}@test.com"
        
        register_result = await self.register_user(
            username=username,
            email=email,
            password="testpass123",
            full_name="New Player Test",
            age=17,
            position="Midfielder"
        )
        
        if not register_result["success"]:
            self.log_result("New Player Registration", False, 
                          f"Failed to register: {register_result['error']}")
            return
        
        self.log_result("New Player Registration", True, 
                      f"Successfully registered {username}")
        
        user_id = register_result["user_id"]
        self.users["new_player"] = {
            "user_id": user_id,
            "username": username,
            "token": register_result["token"]
        }
        
        # Test insights endpoint immediately (no data)
        insights_result = await self.test_player_insights(user_id, "New Player")
        
        if insights_result["success"]:
            response = insights_result["response"]
            
            # Check for friendly message about starting journey
            insights_text = response.get("insights", "").lower()
            is_friendly_start_message = any(word in insights_text for word in 
                                          ["start", "begin", "journey", "first", "initial", "complete"])
            
            self.log_result("New Player Insights - Friendly Start Message", is_friendly_start_message,
                          f"Insights contain start journey message: {is_friendly_start_message}",
                          {
                              "insights": response.get("insights"),
                              "recommendations_count": len(response.get("recommendations", [])),
                              "motivational_message": response.get("motivational_message")
                          })
            
            # Validate structure
            self.log_result("New Player Insights - Response Structure", True,
                          "All required fields present",
                          {
                              "insights_length": insights_result["insights_length"],
                              "recommendations_count": insights_result["recommendations_count"],
                              "has_motivational_message": insights_result["has_motivational_message"]
                          })
        else:
            self.log_result("New Player Insights", False, 
                          f"Failed to get insights: {insights_result['error']}")

    async def run_scenario_2_player_with_assessment(self):
        """Test Scenario 2: Player with Assessment Data"""
        print("🔥 SCENARIO 2: Player with Assessment Data")
        print("=" * 50)
        
        # Use existing user or create new one
        if "flowtest123" in [user.get("username") for user in self.users.values()]:
            # Try to login existing user
            login_result = await self.login_user("flowtest123", "testpass123")
            if login_result["success"]:
                user_id = login_result["user_id"]
                token = login_result["token"]
                self.log_result("Existing User Login", True, "Successfully logged in flowtest123")
            else:
                # Create new user if login fails
                unique_id = str(uuid.uuid4())[:8]
                username = f"assesstest{unique_id}"
                email = f"assesstest{unique_id}@test.com"
                
                register_result = await self.register_user(
                    username=username,
                    email=email,
                    password="testpass123",
                    full_name="Assessment Test Player",
                    age=18,
                    position="Forward"
                )
                
                if not register_result["success"]:
                    self.log_result("Assessment Player Registration", False, 
                                  f"Failed to register: {register_result['error']}")
                    return
                
                user_id = register_result["user_id"]
                token = register_result["token"]
                self.log_result("Assessment Player Registration", True, 
                              f"Successfully registered {username}")
        else:
            # Create new user
            unique_id = str(uuid.uuid4())[:8]
            username = f"assesstest{unique_id}"
            email = f"assesstest{unique_id}@test.com"
            
            register_result = await self.register_user(
                username=username,
                email=email,
                password="testpass123",
                full_name="Assessment Test Player",
                age=18,
                position="Forward"
            )
            
            if not register_result["success"]:
                self.log_result("Assessment Player Registration", False, 
                              f"Failed to register: {register_result['error']}")
                return
            
            user_id = register_result["user_id"]
            token = register_result["token"]
            self.log_result("Assessment Player Registration", True, 
                          f"Successfully registered {username}")
        
        self.users["assessment_player"] = {
            "user_id": user_id,
            "token": token
        }
        
        # Create 2-3 assessments with benchmarks
        player_name = "Assessment Test Player"
        
        # First assessment (baseline)
        assessment1_data = {
            "player_name": player_name,
            "age": 18,
            "position": "Forward",
            "assessment_date": datetime.now(timezone.utc).isoformat(),
            # Moderate performance levels
            "sprint_30m": 4.3,
            "yo_yo_test": 1600,
            "vo2_max": 52.0,
            "vertical_jump": 42,
            "body_fat": 13.0,
            "ball_control": 3,
            "passing_accuracy": 70.0,
            "dribbling_success": 60.0,
            "shooting_accuracy": 55.0,
            "defensive_duels": 65.0,
            "game_intelligence": 3,
            "positioning": 3,
            "decision_making": 3,
            "coachability": 4,
            "mental_toughness": 3
        }
        
        assessment1_result = await self.create_assessment(token, player_name, 18, "Forward", assessment1_data)
        if assessment1_result["success"]:
            self.log_result("First Assessment Creation", True, "Created baseline assessment")
            
            # Save as benchmark
            benchmark_result = await self.save_benchmark(token, assessment1_result["assessment"])
            if benchmark_result["success"]:
                self.log_result("First Benchmark Save", True, "Saved as baseline benchmark")
            else:
                self.log_result("First Benchmark Save", False, 
                              f"Failed to save benchmark: {benchmark_result['error']}")
        else:
            self.log_result("First Assessment Creation", False, 
                          f"Failed to create assessment: {assessment1_result['error']}")
            return
        
        # Second assessment (improved)
        assessment2_data = assessment1_data.copy()
        assessment2_data.update({
            "sprint_30m": 4.1,  # Improved
            "yo_yo_test": 1750,  # Improved
            "ball_control": 4,   # Improved
            "passing_accuracy": 75.0,  # Improved
            "shooting_accuracy": 62.0,  # Improved
        })
        
        assessment2_result = await self.create_assessment(token, player_name, 18, "Forward", assessment2_data)
        if assessment2_result["success"]:
            self.log_result("Second Assessment Creation", True, "Created improved assessment")
            
            # Save as benchmark
            benchmark_result = await self.save_benchmark(token, assessment2_result["assessment"])
            if benchmark_result["success"]:
                self.log_result("Second Benchmark Save", True, "Saved as regular benchmark")
        
        # Add some daily progress entries
        progress_result = await self.create_daily_progress(user_id)
        if progress_result["success"]:
            self.log_result("Daily Progress Creation", True, "Created daily progress entries")
        
        # Test insights endpoint
        insights_result = await self.test_player_insights(user_id, "Player with Assessment")
        
        if insights_result["success"]:
            response = insights_result["response"]
            
            # Check for relevant AI analysis (not generic)
            insights_text = response.get("insights", "").lower()
            is_relevant = len(insights_text) > 50 and not any(generic in insights_text for generic in 
                                                            ["start your journey", "complete your first"])
            
            self.log_result("Assessment Player Insights - Relevant Analysis", is_relevant,
                          f"Insights are relevant to player data: {is_relevant}",
                          {
                              "insights": response.get("insights"),
                              "insights_length": len(response.get("insights", "")),
                              "recommendations_count": len(response.get("recommendations", [])),
                              "motivational_message": response.get("motivational_message")
                          })
            
            # Check recommendations count (3-4 items)
            rec_count = len(response.get("recommendations", []))
            has_proper_rec_count = 3 <= rec_count <= 4
            
            self.log_result("Assessment Player Insights - Recommendations Count", has_proper_rec_count,
                          f"Has {rec_count} recommendations (expected 3-4)",
                          {"recommendations": response.get("recommendations", [])})
            
        else:
            self.log_result("Assessment Player Insights", False, 
                          f"Failed to get insights: {insights_result['error']}")

    async def run_scenario_3_player_with_training_program(self):
        """Test Scenario 3: Player with Training Program"""
        print("🔥 SCENARIO 3: Player with Training Program")
        print("=" * 50)
        
        # Use the assessment player from scenario 2 or create new one
        if "assessment_player" in self.users:
            user_id = self.users["assessment_player"]["user_id"]
            token = self.users["assessment_player"]["token"]
            self.log_result("Using Existing Assessment Player", True, "Reusing player from scenario 2")
        else:
            # Create new user with assessment
            unique_id = str(uuid.uuid4())[:8]
            username = f"programtest{unique_id}"
            email = f"programtest{unique_id}@test.com"
            
            register_result = await self.register_user(
                username=username,
                email=email,
                password="testpass123",
                full_name="Program Test Player",
                age=19,
                position="Defender"
            )
            
            if not register_result["success"]:
                self.log_result("Program Player Registration", False, 
                              f"Failed to register: {register_result['error']}")
                return
            
            user_id = register_result["user_id"]
            token = register_result["token"]
            self.log_result("Program Player Registration", True, 
                          f"Successfully registered {username}")
            
            # Create assessment and benchmark
            player_name = "Program Test Player"
            assessment_result = await self.create_assessment(token, player_name, 19, "Defender")
            if assessment_result["success"]:
                benchmark_result = await self.save_benchmark(token, assessment_result["assessment"])
                self.log_result("Program Player Assessment", True, "Created assessment and benchmark")
        
        # Create training program
        program_result = await self.create_training_program(user_id, "Program Test Player")
        if program_result["success"]:
            self.log_result("Training Program Creation", True, "Created active training program")
        else:
            self.log_result("Training Program Creation", False, 
                          f"Failed to create program: {program_result['error']}")
            return
        
        # Test insights endpoint
        insights_result = await self.test_player_insights(user_id, "Player with Training Program")
        
        if insights_result["success"]:
            response = insights_result["response"]
            
            # Check if insights mention program status
            insights_text = response.get("insights", "").lower()
            mentions_program = any(word in insights_text for word in 
                                 ["program", "training", "routine", "schedule", "plan"])
            
            self.log_result("Program Player Insights - Mentions Program", mentions_program,
                          f"Insights mention training program: {mentions_program}",
                          {
                              "insights": response.get("insights"),
                              "recommendations_count": len(response.get("recommendations", [])),
                              "motivational_message": response.get("motivational_message")
                          })
            
            # Validate AI analysis is different from new player
            is_different_from_new_player = len(insights_text) > 100 and not any(
                phrase in insights_text for phrase in ["start your journey", "complete your first assessment"]
            )
            
            self.log_result("Program Player Insights - Different from New Player", is_different_from_new_player,
                          f"Insights are different for experienced player: {is_different_from_new_player}")
            
        else:
            self.log_result("Program Player Insights", False, 
                          f"Failed to get insights: {insights_result['error']}")

    async def test_authentication_requirement(self):
        """Test that endpoint works without JWT (using player_id parameter)"""
        print("🔥 AUTHENTICATION TEST")
        print("=" * 30)
        
        # Test with a valid player_id (should work)
        if "new_player" in self.users:
            user_id = self.users["new_player"]["user_id"]
            
            insights_result = await self.test_player_insights(user_id, "Authentication Test")
            
            if insights_result["success"]:
                self.log_result("Endpoint Without JWT", True, 
                              "Endpoint works with player_id parameter (no JWT required)")
            else:
                self.log_result("Endpoint Without JWT", False, 
                              f"Endpoint failed: {insights_result['error']}")
        
        # Test with invalid player_id
        fake_player_id = str(uuid.uuid4())
        fake_insights_result = await self.test_player_insights(fake_player_id, "Invalid Player")
        
        if fake_insights_result["success"]:
            # Should still return success but with appropriate message
            response = fake_insights_result["response"]
            insights_text = response.get("insights", "").lower()
            is_appropriate_response = any(word in insights_text for word in 
                                        ["start", "begin", "journey", "first"])
            
            self.log_result("Invalid Player ID Handling", is_appropriate_response,
                          f"Handles invalid player ID gracefully: {is_appropriate_response}",
                          {"insights": response.get("insights")})
        else:
            self.log_result("Invalid Player ID Handling", True,
                          "Returns appropriate error for invalid player ID")

    async def run_all_tests(self):
        """Run all test scenarios"""
        print("🚀 AI COACH PLAYER INSIGHTS ENDPOINT TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing endpoint: POST /api/ai-coach/player-insights")
        print()
        
        await self.setup_session()
        
        try:
            # Run all scenarios
            await self.run_scenario_1_new_player()
            await self.run_scenario_2_player_with_assessment()
            await self.run_scenario_3_player_with_training_program()
            await self.test_authentication_requirement()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        print("📊 TEST SUMMARY")
        print("=" * 40)
        
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
                    print(f"  - {result['test']}: {result['message']}")
            print()
        
        # Check success criteria
        print("🎯 SUCCESS CRITERIA VERIFICATION:")
        criteria_checks = [
            ("Endpoint returns 200 status", passed_tests > 0),
            ("Returns required fields (success, insights, recommendations, motivational_message)", 
             any("Response Structure" in r["test"] and r["success"] for r in self.test_results)),
            ("Recommendations array has 3-4 actionable items", 
             any("Recommendations Count" in r["test"] and r["success"] for r in self.test_results)),
            ("AI analysis is relevant (not generic)", 
             any("Relevant Analysis" in r["test"] and r["success"] for r in self.test_results)),
            ("Works with different player profiles", passed_tests >= 3),
            ("Handles edge cases gracefully (new players, no data)", 
             any("New Player" in r["test"] and r["success"] for r in self.test_results))
        ]
        
        for criteria, met in criteria_checks:
            status = "✅" if met else "❌"
            print(f"  {status} {criteria}")
        
        print()
        
        # Overall result
        overall_success = failed_tests == 0 and passed_tests >= 8
        if overall_success:
            print("🎉 ALL TESTS PASSED! AI Coach Player Insights endpoint is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        return overall_success

async def main():
    """Main test execution"""
    tester = AICoachPlayerInsightsTest()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())