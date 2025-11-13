#!/usr/bin/env python3
"""
Comprehensive Backend API Test for Yoyo the Fire Boy Soccer Training App
Tests all gamification features, group training, notifications, and achievements
"""

import requests
import sys
import json
from datetime import datetime
import random
import time

class YoyoFireBoyAPITester:
    def __init__(self, base_url="https://soccer-ai-coach-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_player_id = None
        self.test_group_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return response"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            return success, response
            
        except Exception as e:
            return False, str(e)

    def test_root_endpoint(self):
        """Test the root API endpoint with Arabic message"""
        success, response = self.make_request('GET', '')
        if success:
            try:
                data = response.json()
                arabic_message = "مرحباً بك في عالم يويو الفتى الناري! 🔥⚽"
                if arabic_message in data.get('message', ''):
                    self.log_test("Root Endpoint with Arabic Fire Boy Message", True)
                else:
                    self.log_test("Root Endpoint with Arabic Fire Boy Message", False, f"Expected Arabic message not found: {data}")
            except:
                self.log_test("Root Endpoint with Arabic Fire Boy Message", False, "Invalid JSON response")
        else:
            self.log_test("Root Endpoint with Arabic Fire Boy Message", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_create_assessment(self):
        """Test creating a player assessment with gamification features"""
        test_data = {
            "player_name": "يويو الفتى الناري",
            "age": 16,
            "position": "striker",
            "sprint_40m": 5.2,
            "sprint_100m": 12.8,
            "cone_drill": 8.5,
            "ladder_drill": 6.2,
            "shuttle_run": 9.1,
            "sit_reach": 25.5,
            "shoulder_flexibility": 180,
            "hip_flexibility": 90,
            "juggling_count": 50,
            "dribbling_time": 15.3,
            "passing_accuracy": 85.5,
            "shooting_accuracy": 78.2
        }
        
        success, response = self.make_request('POST', 'assessments', test_data, 200)
        if success:
            try:
                data = response.json()
                self.test_player_id = data.get('id')
                # Check if gamification fields are present
                has_coins = 'total_coins' in data and data['total_coins'] == 0
                has_level = 'level' in data and data['level'] == 1
                
                if has_coins and has_level:
                    self.log_test("Create Assessment with Gamification", True)
                    print(f"   Player ID: {self.test_player_id}")
                else:
                    self.log_test("Create Assessment with Gamification", False, f"Missing gamification fields: {data}")
            except:
                self.log_test("Create Assessment with Gamification", False, "Invalid JSON response")
        else:
            self.log_test("Create Assessment with Gamification", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_ai_training_program(self):
        """Test AI training program generation with Yoyo Fire Boy persona"""
        if not self.test_player_id:
            self.log_test("AI Training Program with Fire Boy Persona", False, "No test player ID")
            return
            
        test_data = {
            "player_id": self.test_player_id,
            "program_type": "AI_Generated",
            "is_group": False,
            "spotify_playlist": "https://open.spotify.com/playlist/test123"
        }
        
        print("   ⚠️  This test may take 10-30 seconds due to AI processing...")
        success, response = self.make_request('POST', 'training-programs', test_data, 200)
        if success:
            try:
                data = response.json()
                content = data.get('program_content', '')
                # Check for Arabic Fire Boy content
                fire_boy_indicators = ['يويو', 'الناري', '🔥', 'محفز', 'طاقة']
                has_fire_boy_content = any(indicator in content for indicator in fire_boy_indicators)
                
                if has_fire_boy_content and data.get('spotify_playlist'):
                    self.log_test("AI Training Program with Fire Boy Persona", True)
                    print(f"   Content length: {len(content)} characters")
                else:
                    self.log_test("AI Training Program with Fire Boy Persona", False, f"Missing Fire Boy content or Spotify: {len(content)} chars")
            except:
                self.log_test("AI Training Program with Fire Boy Persona", False, "Invalid JSON response")
        else:
            self.log_test("AI Training Program with Fire Boy Persona", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_ronaldo_template(self):
        """Test Ronaldo template with Fire Boy branding"""
        if not self.test_player_id:
            self.log_test("Ronaldo Template with Fire Boy Branding", False, "No test player ID")
            return
            
        test_data = {
            "player_id": self.test_player_id,
            "program_type": "Ronaldo_Template"
        }
        
        success, response = self.make_request('POST', 'training-programs', test_data, 200)
        if success:
            try:
                data = response.json()
                content = data.get('program_content', '')
                # Check for Fire Boy branding in Ronaldo template
                fire_indicators = ['يويو', 'الناري', '🔥', 'محارب', 'أسطورة']
                has_fire_branding = any(indicator in content for indicator in fire_indicators)
                
                if has_fire_branding:
                    self.log_test("Ronaldo Template with Fire Boy Branding", True)
                else:
                    self.log_test("Ronaldo Template with Fire Boy Branding", False, "Missing Fire Boy branding in template")
            except:
                self.log_test("Ronaldo Template with Fire Boy Branding", False, "Invalid JSON response")
        else:
            self.log_test("Ronaldo Template with Fire Boy Branding", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_progress_with_achievements(self):
        """Test progress entry with automatic achievement detection"""
        if not self.test_player_id:
            self.log_test("Progress Entry with Achievement System", False, "No test player ID")
            return
            
        # Test speed achievement (under 4 seconds for Speed Master)
        test_data = {
            "player_id": self.test_player_id,
            "metric_type": "speed",
            "metric_name": "عدو 40 متر",
            "value": 3.8  # Under 4 seconds should trigger Speed Master achievement
        }
        
        success, response = self.make_request('POST', 'progress', test_data, 200)
        if success:
            try:
                data = response.json()
                coins_earned = data.get('coins_earned', 0)
                trophies = data.get('trophies_unlocked', [])
                message = data.get('message', '')
                
                # Check for Arabic success message and coins
                has_arabic_message = 'يويو' in message and 'عملة' in message
                has_coins = coins_earned > 0
                
                if has_arabic_message and has_coins:
                    self.log_test("Progress Entry with Achievement System", True)
                    print(f"   Coins earned: {coins_earned}")
                    if trophies:
                        print(f"   🏆 Trophies unlocked: {len(trophies)}")
                        for trophy in trophies:
                            print(f"      - {trophy.get('trophy_name', 'Unknown')} ({trophy.get('coins_reward', 0)} coins)")
                else:
                    self.log_test("Progress Entry with Achievement System", False, f"Missing coins or Arabic message: {data}")
            except:
                self.log_test("Progress Entry with Achievement System", False, "Invalid JSON response")
        else:
            self.log_test("Progress Entry with Achievement System", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_fire_boy_special_achievement(self):
        """Test Fire Boy Special achievement (95%+ ball handling accuracy)"""
        if not self.test_player_id:
            self.log_test("Fire Boy Special Achievement", False, "No test player ID")
            return
            
        test_data = {
            "player_id": self.test_player_id,
            "metric_type": "ball_handling",
            "metric_name": "دقة التحكم بالكرة",
            "value": 96.5  # Over 95% should trigger Fire Boy Special
        }
        
        success, response = self.make_request('POST', 'progress', test_data, 200)
        if success:
            try:
                data = response.json()
                trophies = data.get('trophies_unlocked', [])
                
                # Check for Fire Boy Special trophy
                fire_boy_trophy = None
                for trophy in trophies:
                    if trophy.get('trophy_type') == 'fire_boy':
                        fire_boy_trophy = trophy
                        break
                
                if fire_boy_trophy:
                    self.log_test("Fire Boy Special Achievement", True)
                    print(f"   🔥 Fire Boy Trophy: {fire_boy_trophy.get('trophy_name')} (+{fire_boy_trophy.get('coins_reward')} coins)")
                else:
                    self.log_test("Fire Boy Special Achievement", False, f"Fire Boy trophy not awarded: {trophies}")
            except:
                self.log_test("Fire Boy Special Achievement", False, "Invalid JSON response")
        else:
            self.log_test("Fire Boy Special Achievement", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_get_trophies(self):
        """Test retrieving player trophies"""
        if not self.test_player_id:
            self.log_test("Get Player Trophies", False, "No test player ID")
            return
            
        success, response = self.make_request('GET', f'trophies/{self.test_player_id}')
        if success:
            try:
                trophies = response.json()
                if isinstance(trophies, list):
                    self.log_test("Get Player Trophies", True)
                    print(f"   🏆 Total trophies: {len(trophies)}")
                    for trophy in trophies:
                        print(f"      - {trophy.get('trophy_name', 'Unknown')} {trophy.get('icon', '')}")
                else:
                    self.log_test("Get Player Trophies", False, "Response is not a list")
            except:
                self.log_test("Get Player Trophies", False, "Invalid JSON response")
        else:
            self.log_test("Get Player Trophies", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_create_group_training(self):
        """Test creating group training with Spotify integration"""
        if not self.test_player_id:
            self.log_test("Create Group Training", False, "No test player ID")
            return
            
        test_data = {
            "creator_id": self.test_player_id,
            "training_name": "محاربو يويو النار",
            "description": "تدريب جماعي ناري لتحطيم الأرقام القياسية",
            "invited_members": ["friend1", "friend2"],
            "spotify_playlist": "https://open.spotify.com/playlist/fire-workout"
        }
        
        success, response = self.make_request('POST', 'group-training', test_data, 200)
        if success:
            try:
                data = response.json()
                self.test_group_id = data.get('id')
                has_arabic_name = 'يويو' in data.get('training_name', '')
                has_spotify = data.get('spotify_playlist') is not None
                has_reward = data.get('completion_reward', 0) > 0
                
                if has_arabic_name and has_spotify and has_reward:
                    self.log_test("Create Group Training", True)
                    print(f"   Group ID: {self.test_group_id}")
                    print(f"   Completion reward: {data.get('completion_reward')} coins")
                else:
                    self.log_test("Create Group Training", False, f"Missing features: Arabic={has_arabic_name}, Spotify={has_spotify}, Reward={has_reward}")
            except:
                self.log_test("Create Group Training", False, "Invalid JSON response")
        else:
            self.log_test("Create Group Training", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_get_group_trainings(self):
        """Test retrieving group trainings"""
        if not self.test_player_id:
            self.log_test("Get Group Trainings", False, "No test player ID")
            return
            
        success, response = self.make_request('GET', f'group-training/{self.test_player_id}')
        if success:
            try:
                groups = response.json()
                if isinstance(groups, list):
                    self.log_test("Get Group Trainings", True)
                    print(f"   👥 Total groups: {len(groups)}")
                else:
                    self.log_test("Get Group Trainings", False, "Response is not a list")
            except:
                self.log_test("Get Group Trainings", False, "Invalid JSON response")
        else:
            self.log_test("Get Group Trainings", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_create_notification(self):
        """Test creating motivational notifications with Spotify"""
        if not self.test_player_id:
            self.log_test("Create Motivational Notification", False, "No test player ID")
            return
            
        test_data = {
            "player_id": self.test_player_id,
            "title": "⏰ إشعار التحفيز الناري",
            "message": "🔥 يويو! حان وقت إشعال النار في التدريب!",
            "notification_type": "motivation",
            "spotify_link": "https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP"
        }
        
        success, response = self.make_request('POST', 'notifications', test_data, 200)
        if success:
            try:
                data = response.json()
                has_arabic_title = 'إشعار' in data.get('title', '')
                has_fire_message = 'يويو' in data.get('message', '') and '🔥' in data.get('message', '')
                has_spotify = data.get('spotify_link') is not None
                
                if has_arabic_title and has_fire_message and has_spotify:
                    self.log_test("Create Motivational Notification", True)
                else:
                    self.log_test("Create Motivational Notification", False, f"Missing features: Arabic={has_arabic_title}, Fire={has_fire_message}, Spotify={has_spotify}")
            except:
                self.log_test("Create Motivational Notification", False, "Invalid JSON response")
        else:
            self.log_test("Create Motivational Notification", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_get_notifications(self):
        """Test retrieving notifications"""
        if not self.test_player_id:
            self.log_test("Get Notifications", False, "No test player ID")
            return
            
        success, response = self.make_request('GET', f'notifications/{self.test_player_id}')
        if success:
            try:
                notifications = response.json()
                if isinstance(notifications, list):
                    self.log_test("Get Notifications", True)
                    print(f"   🔔 Total notifications: {len(notifications)}")
                else:
                    self.log_test("Get Notifications", False, "Response is not a list")
            except:
                self.log_test("Get Notifications", False, "Invalid JSON response")
        else:
            self.log_test("Get Notifications", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_voice_notes(self):
        """Test voice notes functionality"""
        if not self.test_player_id:
            self.log_test("Voice Notes", False, "No test player ID")
            return
            
        test_data = {
            "player_id": self.test_player_id,
            "note_text": "مذكرة صوتية ناري: اليوم حققت رقم قياسي جديد في السرعة! 🔥",
            "audio_duration": 5.2
        }
        
        success, response = self.make_request('POST', 'voice-notes', test_data, 200)
        if success:
            try:
                data = response.json()
                has_arabic_text = 'ناري' in data.get('note_text', '')
                has_duration = data.get('audio_duration') is not None
                
                if has_arabic_text and has_duration:
                    self.log_test("Voice Notes", True)
                else:
                    self.log_test("Voice Notes", False, f"Missing features: Arabic={has_arabic_text}, Duration={has_duration}")
            except:
                self.log_test("Voice Notes", False, "Invalid JSON response")
        else:
            self.log_test("Voice Notes", False, f"HTTP {response.status_code if hasattr(response, 'status_code') else response}")

    def test_consistency_achievement(self):
        """Test consistency achievement by adding multiple speed entries"""
        if not self.test_player_id:
            self.log_test("Consistency Achievement", False, "No test player ID")
            return
            
        # Add multiple speed entries to trigger consistency achievement
        for i in range(4):  # We already added one, so 4 more makes 5 total
            test_data = {
                "player_id": self.test_player_id,
                "metric_type": "speed",
                "metric_name": f"عدو تدريبي {i+1}",
                "value": 4.5 + (i * 0.1)
            }
            
            success, response = self.make_request('POST', 'progress', test_data, 200)
            if not success:
                self.log_test("Consistency Achievement", False, f"Failed to add progress entry {i+1}")
                return
            
            time.sleep(0.1)  # Small delay between requests
        
        # Check if consistency achievement was awarded
        success, response = self.make_request('GET', f'trophies/{self.test_player_id}')
        if success:
            try:
                trophies = response.json()
                consistency_trophy = None
                for trophy in trophies:
                    if trophy.get('trophy_type') == 'consistency_king':
                        consistency_trophy = trophy
                        break
                
                if consistency_trophy:
                    self.log_test("Consistency Achievement", True)
                    print(f"   👑 Consistency Trophy: {consistency_trophy.get('trophy_name')}")
                else:
                    self.log_test("Consistency Achievement", False, "Consistency trophy not found")
            except:
                self.log_test("Consistency Achievement", False, "Invalid JSON response")
        else:
            self.log_test("Consistency Achievement", False, "Failed to retrieve trophies")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🔥 Starting Yoyo the Fire Boy Backend API Tests 🔥\n")
        
        # Basic API tests
        self.test_root_endpoint()
        self.test_create_assessment()
        
        # Training program tests
        self.test_ai_training_program()
        self.test_ronaldo_template()
        
        # Gamification tests
        self.test_progress_with_achievements()
        self.test_fire_boy_special_achievement()
        self.test_consistency_achievement()
        self.test_get_trophies()
        
        # Group training tests
        self.test_create_group_training()
        self.test_get_group_trainings()
        
        # Notification tests
        self.test_create_notification()
        self.test_get_notifications()
        
        # Voice notes test
        self.test_voice_notes()
        
        # Print results
        print(f"\n🏆 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("✅ All backend tests passed! Yoyo Fire Boy API is working perfectly! 🔥")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed. Backend needs attention.")
            return 1

def main():
    tester = YoyoFireBoyAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())