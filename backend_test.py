import requests
import sys
import json
from datetime import datetime

class SoccerTrainingAPITester:
    def __init__(self, base_url="https://soccer-ai-coach-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.player_id = None
        self.assessment_data = None
        self.benchmark_id = None
        self.program_id = None
        # Assessment Benchmark System variables
        self.access_token = None
        self.user_id = None
        self.first_benchmark_id = None
        self.second_benchmark_id = None
        self.third_benchmark_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    else:
                        print(f"   Response: Large data object received")
                except:
                    print(f"   Response: Non-JSON response")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")

            return success, response.json() if response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_create_assessment(self):
        """Test creating a player assessment with Youth Handbook fields"""
        assessment_data = {
            "player_name": "Cristiano Silva",
            "age": 20,
            "position": "forward",
            # Physical metrics (20%)
            "sprint_30m": 4.2,
            "yo_yo_test": 1800,
            "vo2_max": 58.5,
            "vertical_jump": 55,
            "body_fat": 10.0,
            # Technical metrics (40%)
            "ball_control": 4,
            "passing_accuracy": 85.0,
            "dribbling_success": 70.0,
            "shooting_accuracy": 75.0,
            "defensive_duels": 80.0,
            # Tactical metrics (30%)
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            # Psychological metrics (10%)
            "coachability": 5,
            "mental_toughness": 4
        }
        
        success, response = self.run_test(
            "Create Player Assessment",
            "POST",
            "assessments",
            200,
            data=assessment_data
        )
        
        if success and 'id' in response:
            self.player_id = response['id']
            self.assessment_data = response
            print(f"   Player ID: {self.player_id}")
        
        return success

    def test_get_assessments(self):
        """Test getting all assessments"""
        return self.run_test("Get All Assessments", "GET", "assessments", 200)

    def test_get_specific_assessment(self):
        """Test getting a specific assessment"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        return self.run_test(
            "Get Specific Assessment",
            "GET",
            f"assessments/{self.player_id}",
            200
        )

    def test_generate_ai_training_program(self):
        """Test generating AI training program"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        program_data = {
            "player_id": self.player_id,
            "program_type": "AI_Generated"
        }
        
        print("   ⚠️  This test may take 10-30 seconds due to AI processing...")
        success, response = self.run_test(
            "Generate AI Training Program",
            "POST",
            "training-programs",
            200,
            data=program_data
        )
        
        if success:
            print(f"   Program Type: {response.get('program_type', 'N/A')}")
            content_preview = response.get('program_content', '')[:200] + "..." if len(response.get('program_content', '')) > 200 else response.get('program_content', '')
            print(f"   Content Preview: {content_preview}")
            
        return success

    def test_generate_ronaldo_template(self):
        """Test generating Ronaldo template program"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        program_data = {
            "player_id": self.player_id,
            "program_type": "Ronaldo_Template"
        }
        
        success, response = self.run_test(
            "Generate Ronaldo Template Program",
            "POST",
            "training-programs",
            200,
            data=program_data
        )
        
        if success:
            print(f"   Program Type: {response.get('program_type', 'N/A')}")
            milestones = response.get('milestones', [])
            print(f"   Milestones: {len(milestones)} defined")
            
        return success

    def test_get_training_programs(self):
        """Test getting training programs for a player"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        return self.run_test(
            "Get Training Programs",
            "GET",
            f"training-programs/{self.player_id}",
            200
        )

    def test_add_progress_entry(self):
        """Test adding a progress entry"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        progress_data = {
            "player_id": self.player_id,
            "metric_type": "speed",
            "metric_name": "40m Sprint",
            "value": 4.7
        }
        
        return self.run_test(
            "Add Progress Entry",
            "POST",
            "progress",
            200,
            data=progress_data
        )

    def test_get_progress(self):
        """Test getting progress entries"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        return self.run_test(
            "Get Progress Entries",
            "GET",
            f"progress/{self.player_id}",
            200
        )

    def test_add_voice_note(self):
        """Test adding a voice note"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        note_data = {
            "player_id": self.player_id,
            "note_text": "Player showed excellent improvement in sprint times today. Focus on agility drills next session.",
            "audio_duration": 5.2
        }
        
        return self.run_test(
            "Add Voice Note",
            "POST",
            "voice-notes",
            200,
            data=note_data
        )

    def test_get_voice_notes(self):
        """Test getting voice notes"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        return self.run_test(
            "Get Voice Notes",
            "GET",
            f"voice-notes/{self.player_id}",
            200
        )

    def test_save_vo2_benchmark(self):
        """Test saving a VO2 Max benchmark"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        benchmark_data = {
            "player_id": self.player_id,
            "vo2_max": 58.5,
            "calculation_inputs": {
                "age": 20,
                "gender": "male",
                "restingHeartRate": 60,
                "maxHeartRate": 190
            },
            "calculation_method": "ACSM",
            "notes": "Calculated using ACSM formula during fitness assessment",
            "fitness_level": "Good"
        }
        
        success, response = self.run_test(
            "Save VO2 Max Benchmark",
            "POST",
            "vo2-benchmarks",
            200,
            data=benchmark_data
        )
        
        if success and 'id' in response:
            self.benchmark_id = response['id']
            print(f"   Benchmark ID: {self.benchmark_id}")
        
        return success

    def test_get_vo2_benchmarks(self):
        """Test getting all VO2 Max benchmarks for a player"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        return self.run_test(
            "Get VO2 Max Benchmarks",
            "GET",
            f"vo2-benchmarks/{self.player_id}",
            200
        )

    def test_get_latest_vo2_benchmark(self):
        """Test getting the latest VO2 Max benchmark for a player"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        return self.run_test(
            "Get Latest VO2 Max Benchmark",
            "GET",
            f"vo2-benchmarks/latest/{self.player_id}",
            200
        )

    def test_save_multiple_vo2_benchmarks(self):
        """Test saving multiple VO2 Max benchmarks to verify sorting"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        # Save a second benchmark with different values
        benchmark_data_2 = {
            "player_id": self.player_id,
            "vo2_max": 60.2,
            "calculation_inputs": {
                "age": 20,
                "gender": "male",
                "restingHeartRate": 58,
                "maxHeartRate": 192
            },
            "calculation_method": "ACSM",
            "notes": "Follow-up test showing improvement",
            "fitness_level": "Very Good"
        }
        
        return self.run_test(
            "Save Second VO2 Max Benchmark",
            "POST",
            "vo2-benchmarks",
            200,
            data=benchmark_data_2
        )

    def test_delete_vo2_benchmark(self):
        """Test deleting a VO2 Max benchmark"""
        if not hasattr(self, 'benchmark_id') or not self.benchmark_id:
            print("❌ Skipping - No benchmark ID available")
            return False
            
        return self.run_test(
            "Delete VO2 Max Benchmark",
            "DELETE",
            f"vo2-benchmarks/{self.benchmark_id}",
            200
        )

    def test_weekly_progress_tracking(self):
        """Test weekly progress tracking endpoints"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        # Create a weekly progress entry
        progress_data = {
            "player_id": self.player_id,
            "week_number": 1,
            "program_id": "test_program_123",
            "completed_exercises": ["Sprint training", "Ball control drills"],
            "performance_notes": "Excellent progress in speed work",
            "intensity_rating": 4,
            "fatigue_level": 2,
            "improvement_areas": ["Shooting accuracy", "Tactical awareness"],
            "week_completed": True
        }
        
        return self.run_test(
            "Create Weekly Progress",
            "POST",
            "weekly-progress",
            200,
            data=progress_data
        )

    def test_get_weekly_progress(self):
        """Test getting weekly progress for a player"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        return self.run_test(
            "Get Weekly Progress",
            "GET",
            f"weekly-progress/{self.player_id}",
            200
        )

    # ========== NEW PERIODIZED TRAINING PROGRAM TESTS ==========
    
    def test_create_periodized_program(self):
        """Test creating a comprehensive periodized training program"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        program_data = {
            "player_id": self.player_id,
            "program_name": "Elite Development Program - Test Player",
            "total_duration_weeks": 14,
            "program_objectives": [
                "Develop technical skills under pressure",
                "Improve physical conditioning and speed",
                "Enhance tactical awareness and decision making"
            ],
            "assessment_interval_weeks": 4
        }
        
        print("   ⚠️  This test may take 10-20 seconds due to complex program generation...")
        success, response = self.run_test(
            "Create Periodized Training Program",
            "POST",
            "periodized-programs",
            200,
            data=program_data
        )
        
        if success:
            print(f"   Program Name: {response.get('program_name', 'N/A')}")
            print(f"   Total Weeks: {response.get('total_duration_weeks', 'N/A')}")
            print(f"   Macro Cycles: {len(response.get('macro_cycles', []))}")
            self.program_id = response.get('id')
            
        return success

    def test_get_player_program(self):
        """Test getting player's periodized program"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        success, response = self.run_test(
            "Get Player's Periodized Program",
            "GET",
            f"periodized-programs/{self.player_id}",
            200
        )
        
        if success and response:
            print(f"   Program Found: {response.get('program_name', 'N/A')}")
            print(f"   Current Phase: {response.get('current_phase', 'N/A')}")
            print(f"   Current Week: {response.get('current_week', 'N/A')}")
            
        return success

    def test_get_current_routine(self):
        """Test getting today's training routine"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        success, response = self.run_test(
            "Get Current Training Routine",
            "GET",
            f"current-routine/{self.player_id}",
            200
        )
        
        if success:
            routine = response.get('routine')
            if routine:
                print(f"   Today's Phase: {routine.get('phase', 'N/A')}")
                print(f"   Exercises: {len(routine.get('exercises', []))}")
                print(f"   Duration: {routine.get('total_duration', 'N/A')} minutes")
            else:
                print("   Today is a rest day or program completed")
                
        return success

    def test_log_daily_progress(self):
        """Test logging daily training progress"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        progress_data = {
            "player_id": self.player_id,
            "routine_id": "routine_123",
            "completed_exercises": [
                {
                    "player_id": self.player_id,
                    "exercise_id": "sprint_intervals_30m",
                    "routine_id": "routine_123",
                    "completed": True,
                    "feedback": "Great intensity, felt strong",
                    "difficulty_rating": 4,
                    "performance_rating": 5,
                    "time_taken": 25
                },
                {
                    "player_id": self.player_id,
                    "exercise_id": "ball_mastery_cone_weaving",
                    "routine_id": "routine_123",
                    "completed": True,
                    "feedback": "Improved ball control",
                    "difficulty_rating": 3,
                    "performance_rating": 4,
                    "time_taken": 20
                }
            ],
            "overall_rating": 4,
            "energy_level": 4,
            "motivation_level": 5,
            "daily_notes": "Excellent training session, felt very motivated",
            "total_time_spent": 60
        }
        
        success, response = self.run_test(
            "Log Daily Training Progress",
            "POST",
            "daily-progress",
            200,
            data=progress_data
        )
        
        if success:
            print(f"   Exercises Completed: {len(response.get('completed_exercises', []))}")
            print(f"   Overall Rating: {response.get('overall_rating', 'N/A')}/5")
            print(f"   Total Time: {response.get('total_time_spent', 'N/A')} minutes")
            
        return success

    def test_get_daily_progress(self):
        """Test getting daily progress history"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        success, response = self.run_test(
            "Get Daily Progress History",
            "GET",
            f"daily-progress/{self.player_id}",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Progress Entries: {len(response)}")
                if response:
                    latest = response[0]
                    print(f"   Latest Entry: {latest.get('overall_rating', 'N/A')}/5 rating")
            else:
                print("   Response format unexpected")
                
        return success

    def test_get_performance_metrics(self):
        """Test getting performance metrics and trends"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        success, response = self.run_test(
            "Get Performance Metrics",
            "GET",
            f"performance-metrics/{self.player_id}",
            200
        )
        
        if success:
            metrics = response.get('metrics', [])
            trends = response.get('improvement_trends', {})
            print(f"   Performance Metrics: {len(metrics)}")
            print(f"   Improvement Trends: {len(trends)} categories")
            if trends:
                for trend_name, trend_data in trends.items():
                    improvement = trend_data.get('improvement_percentage', 0)
                    print(f"     {trend_name}: {improvement}% improvement")
                    
        return success

    def test_periodized_program_edge_cases(self):
        """Test edge cases for periodized program system"""
        print("\n🔍 Testing Edge Cases...")
        
        # Test with non-existent player
        success1, _ = self.run_test(
            "Get Program for Non-existent Player",
            "GET",
            "periodized-programs/non_existent_player",
            200  # Should return None/null, not error
        )
        
        # Test current routine for non-existent player
        success2, _ = self.run_test(
            "Get Routine for Non-existent Player",
            "GET",
            "current-routine/non_existent_player",
            404  # Should return 404
        )
        
        # Test daily progress with invalid data
        invalid_progress = {
            "player_id": "invalid_player",
            "routine_id": "",
            "completed_exercises": [],
            "overall_rating": 6,  # Invalid rating (should be 1-5)
            "energy_level": 0,    # Invalid level
            "motivation_level": -1  # Invalid level
        }
        
        success3, _ = self.run_test(
            "Log Progress with Invalid Data",
            "POST",
            "daily-progress",
            422  # Should return validation error
        )
        
        return success1 and success2 and success3

    # ========== NEW ASSESSMENT BENCHMARK SYSTEM TESTS ==========
    
    def test_user_registration(self):
        """Test user registration for authentication"""
        import time
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"testcoach_benchmark_{timestamp}",
            "email": f"testcoach_{timestamp}@benchmark.com",
            "full_name": "Test Coach Benchmark",
            "password": "securepassword123",
            "is_coach": True
        }
        
        success, response = self.run_test(
            "Register Test User for Benchmarks",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response['user']['id']
            self.test_username = user_data['username']
            print(f"   Access Token: {self.access_token[:20]}...")
            print(f"   User ID: {self.user_id}")
        
        return success

    def test_user_login(self):
        """Test user login"""
        if not hasattr(self, 'test_username'):
            print("❌ Skipping - No test username available")
            return False
            
        login_data = {
            "username": self.test_username,
            "password": "securepassword123"
        }
        
        success, response = self.run_test(
            "Login Test User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Access Token: {self.access_token[:20]}...")
        
        return success

    def test_save_first_benchmark_baseline(self):
        """Test saving first assessment benchmark (should auto-detect as baseline)"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        benchmark_data = {
            "user_id": self.user_id,
            "player_name": "Lionel Martinez",
            "assessment_id": "test-assessment-001",
            "age": 16,
            "position": "Midfielder",
            "sprint_30m": 4.2,
            "yo_yo_test": 2400,
            "vo2_max": 55.0,
            "vertical_jump": 50,
            "body_fat": 12.0,
            "ball_control": 4,
            "passing_accuracy": 85.0,
            "dribbling_success": 75.0,
            "shooting_accuracy": 70.0,
            "defensive_duels": 65.0,
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4,
            "overall_score": 78.5,
            "performance_level": "Advanced",
            "benchmark_type": "regular",
            "notes": "First benchmark test"
        }
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Save First Benchmark (Baseline Auto-Detection)",
            "POST",
            "auth/save-benchmark",
            200,
            data=benchmark_data,
            headers=headers
        )
        
        if success:
            self.first_benchmark_id = response.get('id')
            print(f"   Benchmark ID: {self.first_benchmark_id}")
            print(f"   Is Baseline: {response.get('is_baseline')}")
            print(f"   Benchmark Type: {response.get('benchmark_type')}")
            
            # Verify it's marked as baseline
            if response.get('is_baseline') != True:
                print("❌ ERROR: First benchmark should be auto-detected as baseline")
                return False
            if response.get('benchmark_type') != "baseline":
                print("❌ ERROR: First benchmark type should be 'baseline'")
                return False
        
        return success

    def test_save_second_benchmark_regular(self):
        """Test saving second assessment benchmark (should be regular with improvement calculation)"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        benchmark_data = {
            "user_id": self.user_id,
            "player_name": "Lionel Martinez",
            "assessment_id": "test-assessment-002",
            "age": 16,
            "position": "Midfielder",
            "sprint_30m": 4.0,  # Improved
            "yo_yo_test": 2500,  # Improved
            "vo2_max": 57.0,  # Improved
            "vertical_jump": 52,  # Improved
            "body_fat": 11.5,  # Improved
            "ball_control": 4,
            "passing_accuracy": 87.0,  # Improved
            "dribbling_success": 78.0,  # Improved
            "shooting_accuracy": 72.0,  # Improved
            "defensive_duels": 68.0,  # Improved
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4,
            "overall_score": 81.2,  # Improved
            "performance_level": "Advanced",
            "benchmark_type": "regular",
            "notes": "Second benchmark showing improvement"
        }
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Save Second Benchmark (Regular with Improvement)",
            "POST",
            "auth/save-benchmark",
            200,
            data=benchmark_data,
            headers=headers
        )
        
        if success:
            self.second_benchmark_id = response.get('id')
            print(f"   Benchmark ID: {self.second_benchmark_id}")
            print(f"   Is Baseline: {response.get('is_baseline')}")
            print(f"   Has Improvement Data: {response.get('improvement_from_baseline') is not None}")
            
            # Verify it's NOT baseline and has improvement data
            if response.get('is_baseline') != False:
                print("❌ ERROR: Second benchmark should NOT be baseline")
                return False
            if response.get('improvement_from_baseline') is None:
                print("❌ ERROR: Second benchmark should have improvement_from_baseline data")
                return False
        
        return success

    def test_save_third_benchmark_progression(self):
        """Test saving third assessment benchmark to verify progression tracking"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        benchmark_data = {
            "user_id": self.user_id,
            "player_name": "Lionel Martinez",
            "assessment_id": "test-assessment-003",
            "age": 16,
            "position": "Midfielder",
            "sprint_30m": 3.9,  # Further improved
            "yo_yo_test": 2600,  # Further improved
            "vo2_max": 58.5,  # Further improved
            "vertical_jump": 54,  # Further improved
            "body_fat": 11.0,  # Further improved
            "ball_control": 5,  # Improved
            "passing_accuracy": 89.0,  # Further improved
            "dribbling_success": 80.0,  # Further improved
            "shooting_accuracy": 75.0,  # Further improved
            "defensive_duels": 70.0,  # Further improved
            "game_intelligence": 5,  # Improved
            "positioning": 5,  # Improved
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 5,  # Improved
            "overall_score": 84.8,  # Further improved
            "performance_level": "Elite",
            "benchmark_type": "milestone",
            "notes": "Third benchmark showing continued progression"
        }
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Save Third Benchmark (Progression Tracking)",
            "POST",
            "auth/save-benchmark",
            200,
            data=benchmark_data,
            headers=headers
        )
        
        if success:
            self.third_benchmark_id = response.get('id')
            print(f"   Benchmark ID: {self.third_benchmark_id}")
            print(f"   Benchmark Type: {response.get('benchmark_type')}")
            print(f"   Overall Score: {response.get('overall_score')}")
        
        return success

    def test_get_all_benchmarks(self):
        """Test retrieving all benchmarks for user (should be sorted by date, newest first)"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get All User Benchmarks",
            "GET",
            "auth/benchmarks",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Total Benchmarks: {len(response)}")
            if len(response) >= 3:
                print(f"   First (newest): {response[0].get('benchmark_type')} - {response[0].get('overall_score')}")
                print(f"   Last (oldest): {response[-1].get('benchmark_type')} - {response[-1].get('overall_score')}")
                
                # Verify sorting (newest first)
                dates = [b.get('benchmark_date') for b in response]
                if dates != sorted(dates, reverse=True):
                    print("⚠️  WARNING: Benchmarks may not be sorted by date (newest first)")
        
        return success

    def test_get_benchmarks_filtered_by_player(self):
        """Test retrieving benchmarks filtered by player name"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get Benchmarks Filtered by Player",
            "GET",
            "auth/benchmarks?player_name=Lionel Martinez",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Filtered Benchmarks: {len(response)}")
            # Verify all returned benchmarks are for the correct player
            for benchmark in response:
                if benchmark.get('player_name') != 'Lionel Martinez':
                    print(f"❌ ERROR: Found benchmark for wrong player: {benchmark.get('player_name')}")
                    return False
        
        return success

    def test_get_baseline_benchmark(self):
        """Test retrieving baseline benchmark for specific player"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get Baseline Benchmark for Player",
            "GET",
            "auth/benchmarks/baseline?player_name=Lionel Martinez",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Baseline ID: {response.get('id')}")
            print(f"   Is Baseline: {response.get('is_baseline')}")
            print(f"   Benchmark Type: {response.get('benchmark_type')}")
            
            # Verify it's actually the baseline
            if response.get('is_baseline') != True:
                print("❌ ERROR: Retrieved benchmark is not marked as baseline")
                return False
        
        return success

    def test_get_specific_benchmark(self):
        """Test retrieving specific benchmark by ID"""
        if not hasattr(self, 'access_token') or not self.access_token or not hasattr(self, 'second_benchmark_id'):
            print("❌ Skipping - No access token or benchmark ID available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get Specific Benchmark by ID",
            "GET",
            f"auth/benchmarks/{self.second_benchmark_id}",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Retrieved Benchmark ID: {response.get('id')}")
            print(f"   Player Name: {response.get('player_name')}")
            print(f"   Overall Score: {response.get('overall_score')}")
        
        return success

    def test_get_player_progress_analysis(self):
        """Test getting comprehensive progress analysis for player"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get Player Progress Analysis",
            "GET",
            "auth/benchmarks/progress/Lionel Martinez",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Player: {response.get('player_name')}")
            print(f"   Total Benchmarks: {response.get('total_benchmarks')}")
            print(f"   Baseline Score: {response.get('baseline_score')}")
            print(f"   Latest Score: {response.get('latest_score')}")
            print(f"   Overall Improvement: {response.get('overall_improvement')}%")
            print(f"   Timeline Entries: {len(response.get('improvement_timeline', []))}")
        
        return success

    def test_try_delete_baseline_benchmark(self):
        """Test trying to delete baseline benchmark (should fail with 400 error)"""
        if not hasattr(self, 'access_token') or not self.access_token or not hasattr(self, 'first_benchmark_id'):
            print("❌ Skipping - No access token or baseline benchmark ID available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Try to Delete Baseline Benchmark (Should Fail)",
            "DELETE",
            f"auth/benchmarks/{self.first_benchmark_id}",
            400,  # Should return 400 Bad Request
            headers=headers
        )
        
        if success:
            print(f"   Correctly prevented baseline deletion: {response.get('detail', 'No error message')}")
        
        return success

    def test_delete_regular_benchmark(self):
        """Test deleting regular benchmark (should succeed)"""
        if not hasattr(self, 'access_token') or not self.access_token or not hasattr(self, 'third_benchmark_id'):
            print("❌ Skipping - No access token or regular benchmark ID available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Delete Regular Benchmark (Should Succeed)",
            "DELETE",
            f"auth/benchmarks/{self.third_benchmark_id}",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Successfully deleted benchmark: {response.get('message', 'No message')}")
        
        return success

    def test_benchmark_error_handling(self):
        """Test error handling for benchmark endpoints"""
        if not hasattr(self, 'access_token') or not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Test with invalid benchmark ID
        success1, _ = self.run_test_with_auth(
            "Get Non-existent Benchmark",
            "GET",
            "auth/benchmarks/invalid-benchmark-id",
            404,
            headers=headers
        )
        
        # Test baseline for non-existent player
        success2, _ = self.run_test_with_auth(
            "Get Baseline for Non-existent Player",
            "GET",
            "auth/benchmarks/baseline?player_name=NonExistentPlayer",
            404,
            headers=headers
        )
        
        # Test progress for non-existent player
        success3, _ = self.run_test_with_auth(
            "Get Progress for Non-existent Player",
            "GET",
            "auth/benchmarks/progress/NonExistentPlayer",
            404,
            headers=headers
        )
        
        return success1 and success2 and success3

    def test_unauthorized_access(self):
        """Test accessing benchmark endpoints without authentication"""
        # Test without authorization header
        success1, _ = self.run_test(
            "Access Benchmarks Without Auth (Should Fail)",
            "GET",
            "auth/benchmarks",
            401  # Should return 401 Unauthorized
        )
        
        # Test with invalid token
        invalid_headers = {'Authorization': 'Bearer invalid-token-here'}
        success2, _ = self.run_test_with_auth(
            "Access Benchmarks with Invalid Token (Should Fail)",
            "GET",
            "auth/benchmarks",
            401,
            headers=invalid_headers
        )
        
        return success1 and success2

    def run_test_with_auth(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test with authentication headers"""
        url = f"{self.api_url}/{endpoint}"
        if not headers:
            headers = {}
        headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    else:
                        print(f"   Response: Large data object received")
                except:
                    print(f"   Response: Non-JSON response")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")

            return success, response.json() if response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

def main():
    print("🚀 Starting Soccer Pro Training Tracker API Tests")
    print("=" * 60)
    
    tester = SoccerTrainingAPITester()
    
    # Test sequence
    test_results = []
    
    # Basic API tests
    test_results.append(tester.test_root_endpoint())
    
    # Assessment tests
    test_results.append(tester.test_create_assessment())
    test_results.append(tester.test_get_assessments())
    test_results.append(tester.test_get_specific_assessment())
    
    # Training program tests (most critical)
    test_results.append(tester.test_generate_ai_training_program())
    test_results.append(tester.test_generate_ronaldo_template())
    test_results.append(tester.test_get_training_programs())
    
    # Progress tracking tests
    test_results.append(tester.test_add_progress_entry())
    test_results.append(tester.test_get_progress())
    
    # Voice notes tests
    test_results.append(tester.test_add_voice_note())
    test_results.append(tester.test_get_voice_notes())
    
    # VO2 Max Benchmark tests (NEW - HIGH PRIORITY)
    print("\n🔥 Testing NEW VO2 Max Benchmark Endpoints...")
    test_results.append(tester.test_save_vo2_benchmark())
    test_results.append(tester.test_get_vo2_benchmarks())
    test_results.append(tester.test_get_latest_vo2_benchmark())
    test_results.append(tester.test_save_multiple_vo2_benchmarks())
    test_results.append(tester.test_get_latest_vo2_benchmark())  # Test again to verify latest
    test_results.append(tester.test_delete_vo2_benchmark())
    
    # Weekly Progress Tracking tests
    print("\n📊 Testing Weekly Progress Tracking...")
    test_results.append(tester.test_weekly_progress_tracking())
    test_results.append(tester.test_get_weekly_progress())
    
    # NEW PERIODIZED TRAINING PROGRAM TESTS (HIGH PRIORITY)
    print("\n🔥 Testing NEW Enhanced Training Program System...")
    test_results.append(tester.test_create_periodized_program())
    test_results.append(tester.test_get_player_program())
    test_results.append(tester.test_get_current_routine())
    test_results.append(tester.test_log_daily_progress())
    test_results.append(tester.test_get_daily_progress())
    test_results.append(tester.test_get_performance_metrics())
    
    # Edge case testing
    print("\n⚠️  Testing Edge Cases and Error Handling...")
    test_results.append(tester.test_periodized_program_edge_cases())
    
    # NEW ASSESSMENT BENCHMARK SYSTEM TESTS (HIGH PRIORITY)
    print("\n🔥 Testing NEW Assessment Benchmark System...")
    print("   This system allows saving assessment data as benchmarks for progress tracking")
    
    # Authentication setup
    test_results.append(tester.test_user_registration())
    
    # Core benchmark functionality
    test_results.append(tester.test_save_first_benchmark_baseline())
    test_results.append(tester.test_save_second_benchmark_regular())
    test_results.append(tester.test_save_third_benchmark_progression())
    
    # Retrieval and filtering
    test_results.append(tester.test_get_all_benchmarks())
    test_results.append(tester.test_get_benchmarks_filtered_by_player())
    test_results.append(tester.test_get_baseline_benchmark())
    test_results.append(tester.test_get_specific_benchmark())
    
    # Progress analysis
    test_results.append(tester.test_get_player_progress_analysis())
    
    # Deletion and protection
    test_results.append(tester.test_try_delete_baseline_benchmark())
    test_results.append(tester.test_delete_regular_benchmark())
    
    # Error handling and security
    test_results.append(tester.test_benchmark_error_handling())
    test_results.append(tester.test_unauthorized_access())
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())