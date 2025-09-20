import requests
import sys
import json
from datetime import datetime

class SoccerTrainingAPITester:
    def __init__(self, base_url="https://soccer-skill-track.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.player_id = None
        self.assessment_data = None

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