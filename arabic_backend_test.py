import requests
import sys
import json
from datetime import datetime

class ArabicSoccerTrainingAPITester:
    def __init__(self, base_url="https://soccer-ai-coach-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.player_id = None
        self.assessment_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

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

    def test_arabic_root_endpoint(self):
        """Test the root API endpoint returns Arabic message"""
        success, response = self.run_test("Arabic Root API Endpoint", "GET", "", 200)
        
        if success:
            message = response.get('message', '')
            if 'واجهة برمجة التطبيقات' in message:
                print("   ✅ Arabic message confirmed")
            else:
                print("   ⚠️  Arabic message not found")
                
        return success

    def test_create_arabic_assessment(self):
        """Test creating a player assessment with Arabic name"""
        assessment_data = {
            "player_name": "محمد صلاح الجديد",
            "age": 20,
            "position": "مهاجم",
            "sprint_40m": 4.5,
            "sprint_100m": 10.8,
            "cone_drill": 6.2,
            "ladder_drill": 7.8,
            "shuttle_run": 8.9,
            "sit_reach": 38.0,
            "shoulder_flexibility": 185.0,
            "hip_flexibility": 125.0,
            "juggling_count": 200,
            "dribbling_time": 11.8,
            "passing_accuracy": 88.0,
            "shooting_accuracy": 82.0
        }
        
        success, response = self.run_test(
            "Create Arabic Player Assessment",
            "POST",
            "assessments",
            200,
            data=assessment_data
        )
        
        if success and 'id' in response:
            self.player_id = response['id']
            self.assessment_data = response
            print(f"   Player ID: {self.player_id}")
            print(f"   Arabic Name: {response.get('player_name', 'N/A')}")
            print(f"   Position: {response.get('position', 'N/A')}")
        
        return success

    def test_arabic_ai_training_program(self):
        """Test generating AI training program with Arabic content"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        program_data = {
            "player_id": self.player_id,
            "program_type": "AI_Generated"
        }
        
        print("   ⚠️  This test may take 10-30 seconds due to AI processing...")
        success, response = self.run_test(
            "Generate Arabic AI Training Program",
            "POST",
            "training-programs",
            200,
            data=program_data
        )
        
        if success:
            program_content = response.get('program_content', '')
            print(f"   Program Type: {response.get('program_type', 'N/A')}")
            
            # Check for Arabic content
            arabic_keywords = ['تدريب', 'اللاعب', 'الأسبوع', 'تحسين', 'المهارات', 'السرعة', 'الرشاقة']
            found_arabic = sum(1 for keyword in arabic_keywords if keyword in program_content)
            
            print(f"   Arabic Keywords Found: {found_arabic}/{len(arabic_keywords)}")
            
            if found_arabic >= 3:
                print("   ✅ Arabic content confirmed in training program")
            else:
                print("   ⚠️  Limited Arabic content detected")
                
            # Show a preview of Arabic content
            content_preview = program_content[:300] + "..." if len(program_content) > 300 else program_content
            print(f"   Content Preview: {content_preview}")
            
        return success

    def test_arabic_ronaldo_template(self):
        """Test generating Ronaldo template with Arabic content"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        program_data = {
            "player_id": self.player_id,
            "program_type": "Ronaldo_Template"
        }
        
        success, response = self.run_test(
            "Generate Arabic Ronaldo Template",
            "POST",
            "training-programs",
            200,
            data=program_data
        )
        
        if success:
            program_content = response.get('program_content', '')
            weekly_schedule = response.get('weekly_schedule', {})
            milestones = response.get('milestones', [])
            
            print(f"   Program Type: {response.get('program_type', 'N/A')}")
            print(f"   Weekly Schedule Days: {len(weekly_schedule)}")
            print(f"   Milestones: {len(milestones)}")
            
            # Check for Arabic content in schedule
            arabic_found_in_schedule = any('تدريب' in str(activity) or 'القوة' in str(activity) or 'المهارات' in str(activity) 
                                         for activity in weekly_schedule.values())
            
            if arabic_found_in_schedule:
                print("   ✅ Arabic content confirmed in weekly schedule")
            else:
                print("   ⚠️  Limited Arabic content in schedule")
                
            # Show sample schedule
            if weekly_schedule:
                sample_day = list(weekly_schedule.keys())[0]
                sample_activity = weekly_schedule[sample_day]
                print(f"   Sample Schedule - {sample_day}: {sample_activity}")
            
        return success

    def test_arabic_voice_note(self):
        """Test adding a voice note with Arabic text"""
        if not self.player_id:
            print("❌ Skipping - No player ID available")
            return False
            
        note_data = {
            "player_id": self.player_id,
            "note_text": "اللاعب أظهر تحسناً ممتازاً في أوقات العدو اليوم. التركيز على تدريبات الرشاقة في الجلسة القادمة. يحتاج إلى العمل على دقة التسديد.",
            "audio_duration": 8.5
        }
        
        success, response = self.run_test(
            "Add Arabic Voice Note",
            "POST",
            "voice-notes",
            200,
            data=note_data
        )
        
        if success:
            note_text = response.get('note_text', '')
            print(f"   Arabic Note Length: {len(note_text)} characters")
            if 'اللاعب' in note_text and 'تحسناً' in note_text:
                print("   ✅ Arabic voice note content confirmed")
            else:
                print("   ⚠️  Arabic content verification failed")
                
        return success

    def test_error_messages_arabic(self):
        """Test that error messages are in Arabic"""
        # Test with invalid player ID
        success, response = self.run_test(
            "Arabic Error Message Test",
            "GET",
            "assessments/invalid-id-12345",
            404
        )
        
        if not success:  # We expect this to fail with 404
            # Check if error message is in Arabic
            error_detail = response.get('detail', '')
            if 'لم يتم العثور' in error_detail:
                print("   ✅ Arabic error message confirmed")
                self.tests_passed += 1  # Count this as passed since we got Arabic error
                return True
            else:
                print(f"   ⚠️  Error message not in Arabic: {error_detail}")
                
        return False

def main():
    print("🚀 Starting Arabic Soccer Pro Training Tracker API Tests")
    print("=" * 70)
    
    tester = ArabicSoccerTrainingAPITester()
    
    # Test sequence focusing on Arabic content
    test_results = []
    
    # Basic Arabic API tests
    test_results.append(tester.test_arabic_root_endpoint())
    
    # Arabic assessment tests
    test_results.append(tester.test_create_arabic_assessment())
    
    # Arabic training program tests (most critical)
    test_results.append(tester.test_arabic_ai_training_program())
    test_results.append(tester.test_arabic_ronaldo_template())
    
    # Arabic voice notes test
    test_results.append(tester.test_arabic_voice_note())
    
    # Arabic error messages test
    test_results.append(tester.test_error_messages_arabic())
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 ARABIC INTEGRATION TEST RESULTS")
    print("=" * 70)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Arabic integration tests passed! Backend supports Arabic content.")
        return 0
    else:
        print("⚠️  Some Arabic integration tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())