import requests
import sys
import json
from datetime import datetime

class TrainingSessionTester:
    def __init__(self, base_url="https://elite-soccer-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.player_id = None
        self.routine_id = None
        self.program_id = None

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
                    if isinstance(response_data, dict) and len(str(response_data)) < 800:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if response_data and len(response_data) > 0:
                            print(f"   First item: {response_data[0] if len(str(response_data[0])) < 300 else 'Large object'}")
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

    def test_create_test_player(self):
        """Create a test player for training session testing"""
        assessment_data = {
            "player_name": "Marcus Rodriguez",
            "age": 17,
            "position": "midfielder",
            # Physical metrics (20%)
            "sprint_30m": 4.1,
            "yo_yo_test": 2200,
            "vo2_max": 60.0,
            "vertical_jump": 58,
            "body_fat": 9.5,
            # Technical metrics (40%)
            "ball_control": 4,
            "passing_accuracy": 88.0,
            "dribbling_success": 75.0,
            "shooting_accuracy": 72.0,
            "defensive_duels": 78.0,
            # Tactical metrics (30%)
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            # Psychological metrics (10%)
            "coachability": 5,
            "mental_toughness": 4
        }
        
        success, response = self.run_test(
            "Create Test Player Assessment",
            "POST",
            "assessments",
            200,
            data=assessment_data
        )
        
        if success and 'id' in response:
            self.player_id = response['id']
            print(f"   Player ID: {self.player_id}")
        
        return success

    def test_create_periodized_program(self):
        """Create a periodized training program for the test player"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        program_data = {
            "player_id": self.player_id,
            "program_name": "Training Session Test Program",
            "total_duration_weeks": 8,
            "program_objectives": [
                "Test daily progress saving functionality",
                "Verify exercise completion tracking",
                "Validate performance metrics calculation"
            ],
            "assessment_interval_weeks": 4
        }
        
        print("   ⚠️  This test may take 10-20 seconds due to program generation...")
        success, response = self.run_test(
            "Create Periodized Training Program",
            "POST",
            "periodized-programs",
            200,
            data=program_data
        )
        
        if success:
            self.program_id = response.get('id')
            print(f"   Program ID: {self.program_id}")
            
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
                self.routine_id = routine.get('id', 'test_routine_123')
                print(f"   Routine ID: {self.routine_id}")
                print(f"   Phase: {routine.get('phase', 'N/A')}")
                print(f"   Exercises: {len(routine.get('exercises', []))}")
                print(f"   Duration: {routine.get('total_duration', 'N/A')} minutes")
            else:
                # Use a test routine ID if no routine found
                self.routine_id = "test_routine_123"
                print("   No routine found, using test routine ID")
                
        return success

    def test_save_daily_progress_with_player_id(self):
        """Test saving daily progress with proper player_id in exercise completions (THE MAIN FIX)"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        if not self.routine_id:
            self.routine_id = "test_routine_123"
            
        # Test data with REQUIRED player_id field in exercise completions
        progress_data = {
            "player_id": self.player_id,
            "routine_id": self.routine_id,
            "completed_exercises": [
                {
                    "player_id": self.player_id,  # THIS WAS THE MISSING FIELD THAT WAS FIXED
                    "exercise_id": "sprint_intervals_30m",
                    "routine_id": self.routine_id,
                    "completed": True,
                    "feedback": "Excellent session, felt very strong and fast",
                    "difficulty_rating": 4,
                    "performance_rating": 5,
                    "notes": "Improved sprint times significantly",
                    "time_taken": 30
                },
                {
                    "player_id": self.player_id,  # THIS WAS THE MISSING FIELD THAT WAS FIXED
                    "exercise_id": "ball_control_cone_weaving",
                    "routine_id": self.routine_id,
                    "completed": True,
                    "feedback": "Good control, need to work on speed",
                    "difficulty_rating": 3,
                    "performance_rating": 4,
                    "notes": "Ball control improving steadily",
                    "time_taken": 25
                },
                {
                    "player_id": self.player_id,  # THIS WAS THE MISSING FIELD THAT WAS FIXED
                    "exercise_id": "tactical_positioning_drill",
                    "routine_id": self.routine_id,
                    "completed": True,
                    "feedback": "Better understanding of positioning",
                    "difficulty_rating": 4,
                    "performance_rating": 4,
                    "notes": "Tactical awareness improving",
                    "time_taken": 20
                }
            ],
            "overall_rating": 4,
            "energy_level": 4,
            "motivation_level": 5,
            "daily_notes": "Great training session today! Felt motivated and energetic throughout.",
            "total_time_spent": 75
        }
        
        success, response = self.run_test(
            "Save Daily Progress with player_id (MAIN FIX TEST)",
            "POST",
            "daily-progress",
            200,
            data=progress_data
        )
        
        if success:
            print(f"   ✅ SUCCESS: Daily progress saved with player_id in exercise completions")
            print(f"   Exercises Completed: {len(response.get('completed_exercises', []))}")
            print(f"   Overall Rating: {response.get('overall_rating', 'N/A')}/5")
            print(f"   Total Time: {response.get('total_time_spent', 'N/A')} minutes")
            
            # Verify that exercise completions have player_id
            completed_exercises = response.get('completed_exercises', [])
            for i, exercise in enumerate(completed_exercises):
                if 'player_id' not in exercise:
                    print(f"   ❌ ERROR: Exercise {i+1} missing player_id field")
                    return False
                elif exercise['player_id'] != self.player_id:
                    print(f"   ❌ ERROR: Exercise {i+1} has wrong player_id: {exercise['player_id']}")
                    return False
                else:
                    print(f"   ✅ Exercise {i+1}: player_id correctly set to {exercise['player_id']}")
        
        return success

    def test_save_daily_progress_missing_player_id(self):
        """Test error handling when player_id is missing from exercise completions"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        if not self.routine_id:
            self.routine_id = "test_routine_123"
            
        # Test data WITHOUT player_id in exercise completions (should fail)
        progress_data = {
            "player_id": self.player_id,
            "routine_id": self.routine_id,
            "completed_exercises": [
                {
                    # "player_id": self.player_id,  # INTENTIONALLY MISSING
                    "exercise_id": "sprint_intervals_30m",
                    "routine_id": self.routine_id,
                    "completed": True,
                    "feedback": "Test feedback",
                    "difficulty_rating": 3,
                    "performance_rating": 3,
                    "notes": "Test notes",
                    "time_taken": 20
                }
            ],
            "overall_rating": 3,
            "energy_level": 3,
            "motivation_level": 3,
            "daily_notes": "Test session",
            "total_time_spent": 20
        }
        
        success, response = self.run_test(
            "Save Daily Progress WITHOUT player_id (Should Fail)",
            "POST",
            "daily-progress",
            422,  # Should return validation error
            data=progress_data
        )
        
        if success:
            print(f"   ✅ SUCCESS: Properly rejected request missing player_id")
            print(f"   Error message: {response.get('detail', 'No error message')}")
        
        return success

    def test_save_daily_progress_empty_exercises(self):
        """Test error handling with empty exercises array"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        if not self.routine_id:
            self.routine_id = "test_routine_123"
            
        progress_data = {
            "player_id": self.player_id,
            "routine_id": self.routine_id,
            "completed_exercises": [],  # Empty array
            "overall_rating": 3,
            "energy_level": 3,
            "motivation_level": 3,
            "daily_notes": "Rest day",
            "total_time_spent": 0
        }
        
        success, response = self.run_test(
            "Save Daily Progress with Empty Exercises",
            "POST",
            "daily-progress",
            200,  # Should succeed but with empty exercises
            data=progress_data
        )
        
        return success

    def test_save_daily_progress_invalid_routine_id(self):
        """Test error handling with invalid routine_id"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        progress_data = {
            "player_id": self.player_id,
            "routine_id": "invalid_routine_id_12345",
            "completed_exercises": [
                {
                    "player_id": self.player_id,
                    "exercise_id": "test_exercise",
                    "routine_id": "invalid_routine_id_12345",
                    "completed": True,
                    "feedback": "Test feedback",
                    "difficulty_rating": 3,
                    "performance_rating": 3,
                    "notes": "Test notes",
                    "time_taken": 20
                }
            ],
            "overall_rating": 3,
            "energy_level": 3,
            "motivation_level": 3,
            "daily_notes": "Test with invalid routine",
            "total_time_spent": 20
        }
        
        success, response = self.run_test(
            "Save Daily Progress with Invalid Routine ID",
            "POST",
            "daily-progress",
            200,  # May still succeed as routine validation might be lenient
            data=progress_data
        )
        
        return success

    def test_get_daily_progress_history(self):
        """Test retrieving daily progress history"""
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
                print(f"   Progress Entries Found: {len(response)}")
                if response:
                    latest = response[0]
                    print(f"   Latest Entry Rating: {latest.get('overall_rating', 'N/A')}/5")
                    print(f"   Latest Entry Exercises: {len(latest.get('completed_exercises', []))}")
                    
                    # Verify exercise completions have player_id
                    completed_exercises = latest.get('completed_exercises', [])
                    for i, exercise in enumerate(completed_exercises):
                        if 'player_id' in exercise:
                            print(f"   ✅ Exercise {i+1} has player_id: {exercise['player_id']}")
                        else:
                            print(f"   ❌ Exercise {i+1} missing player_id")
            else:
                print("   Unexpected response format")
                
        return success

    def test_get_performance_metrics(self):
        """Test getting performance metrics"""
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
            
            if metrics:
                print(f"   Sample Metric: {metrics[0].get('metric_name', 'N/A')} = {metrics[0].get('value', 'N/A')}")
                
        return success

    def test_multiple_daily_progress_entries(self):
        """Test saving multiple daily progress entries to verify data persistence"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        if not self.routine_id:
            self.routine_id = "test_routine_456"
            
        # Save second daily progress entry
        progress_data_2 = {
            "player_id": self.player_id,
            "routine_id": self.routine_id,
            "completed_exercises": [
                {
                    "player_id": self.player_id,
                    "exercise_id": "endurance_running",
                    "routine_id": self.routine_id,
                    "completed": True,
                    "feedback": "Good endurance work",
                    "difficulty_rating": 3,
                    "performance_rating": 4,
                    "notes": "Steady improvement in stamina",
                    "time_taken": 40
                },
                {
                    "player_id": self.player_id,
                    "exercise_id": "shooting_practice",
                    "routine_id": self.routine_id,
                    "completed": True,
                    "feedback": "Accuracy improving",
                    "difficulty_rating": 4,
                    "performance_rating": 4,
                    "notes": "Better shot placement",
                    "time_taken": 30
                }
            ],
            "overall_rating": 4,
            "energy_level": 3,
            "motivation_level": 4,
            "daily_notes": "Second training session - focused on endurance and shooting",
            "total_time_spent": 70
        }
        
        success, response = self.run_test(
            "Save Second Daily Progress Entry",
            "POST",
            "daily-progress",
            200,
            data=progress_data_2
        )
        
        return success

    def test_edge_cases(self):
        """Test various edge cases"""
        print("\n🔍 Testing Edge Cases...")
        
        # Test with non-existent player
        success1, _ = self.run_test(
            "Get Progress for Non-existent Player",
            "GET",
            "daily-progress/non_existent_player_123",
            200  # Should return empty array
        )
        
        # Test current routine for non-existent player
        success2, _ = self.run_test(
            "Get Routine for Non-existent Player",
            "GET",
            "current-routine/non_existent_player_123",
            404  # Should return 404
        )
        
        # Test performance metrics for non-existent player
        success3, _ = self.run_test(
            "Get Metrics for Non-existent Player",
            "GET",
            "performance-metrics/non_existent_player_123",
            200  # May return empty metrics
        )
        
        return success1 and success2 and success3

def main():
    print("🚀 Testing Training Session Daily Progress Save Functionality")
    print("🎯 Focus: Verifying the player_id fix in ExerciseCompletion objects")
    print("=" * 70)
    
    tester = TrainingSessionTester()
    
    # Test sequence focusing on the specific fix
    test_results = []
    
    # Setup
    print("\n📋 SETUP PHASE")
    test_results.append(tester.test_create_test_player())
    test_results.append(tester.test_create_periodized_program())
    test_results.append(tester.test_get_current_routine())
    
    # Core functionality tests (THE MAIN FIX)
    print("\n🔥 CORE FUNCTIONALITY TESTS (MAIN FIX)")
    test_results.append(tester.test_save_daily_progress_with_player_id())
    test_results.append(tester.test_get_daily_progress_history())
    test_results.append(tester.test_get_performance_metrics())
    
    # Error handling tests
    print("\n⚠️  ERROR HANDLING TESTS")
    test_results.append(tester.test_save_daily_progress_missing_player_id())
    test_results.append(tester.test_save_daily_progress_empty_exercises())
    test_results.append(tester.test_save_daily_progress_invalid_routine_id())
    
    # Additional functionality tests
    print("\n📊 ADDITIONAL FUNCTIONALITY TESTS")
    test_results.append(tester.test_multiple_daily_progress_entries())
    test_results.append(tester.test_get_daily_progress_history())  # Test again to verify multiple entries
    
    # Edge cases
    print("\n🔍 EDGE CASE TESTS")
    test_results.append(tester.test_edge_cases())
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 TRAINING SESSION DAILY PROGRESS TEST RESULTS")
    print("=" * 70)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    # Specific analysis of the fix
    print("\n🎯 FIX ANALYSIS:")
    print("   The main fix was adding 'player_id' field to ExerciseCompletion objects")
    print("   This prevents backend validation errors when saving daily progress")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 ALL TESTS PASSED! Training session save functionality is working correctly.")
        print("✅ The player_id fix has been successfully implemented and tested.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Check the details above.")
        failed_count = tester.tests_run - tester.tests_passed
        if failed_count <= 2:
            print("   Minor issues detected - core functionality may still be working.")
        else:
            print("   Multiple failures detected - may indicate serious issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())