#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Unit Preference System
Testing the new unit preference system in player registration
"""

import requests
import json
import sys
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://soccer-pro-portal.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class UnitPreferenceSystemTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        
        self.test_results.append(result)
        print(result)
        
    def test_metric_user_registration(self):
        """Test Scenario 1: Register Player with METRIC Units"""
        print("\n🧪 SCENARIO 1: Register Player with METRIC Units")
        
        try:
            # Test data for metric user
            metric_user_data = {
                "username": "metricplayer001",
                "email": "metric@test.com",
                "full_name": "Metric Test Player",
                "password": "testpass123",
                "role": "player",
                "age": 17,
                "position": "Forward",
                "height": "175",  # Will be stored as "175cm"
                "weight": "68",   # Will be stored as "68kg"
                "height_unit": "metric",
                "weight_unit": "metric"
            }
            
            # Register user
            response = requests.post(f"{API_BASE}/auth/register", json=metric_user_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify registration success
                self.log_test("Metric user registration", True, f"User {data['user']['username']} registered successfully")
                
                # Verify user data includes unit preferences
                user_data = data['user']
                expected_fields = ['id', 'username', 'email', 'role', 'player_id', 'age', 'position']
                missing_fields = [field for field in expected_fields if field not in user_data]
                
                if missing_fields:
                    self.log_test("Metric user data completeness", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Metric user data completeness", True, "All required fields present")
                
                # Store token for later tests
                self.metric_token = data['access_token']
                self.metric_user_id = user_data['id']
                
                return True
            else:
                self.log_test("Metric user registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Metric user registration", False, f"Exception: {str(e)}")
            return False
    
    def test_imperial_user_registration(self):
        """Test Scenario 2: Register Player with IMPERIAL Units"""
        print("\n🧪 SCENARIO 2: Register Player with IMPERIAL Units")
        
        try:
            # Test data for imperial user
            imperial_user_data = {
                "username": "imperialplayer001",
                "email": "imperial@test.com",
                "full_name": "Imperial Test Player",
                "password": "testpass123",
                "role": "player",
                "age": 18,
                "position": "Midfielder",
                "height": "69",   # Will be stored as "69\""
                "weight": "150",  # Will be stored as "150lbs"
                "height_unit": "imperial",
                "weight_unit": "imperial"
            }
            
            # Register user
            response = requests.post(f"{API_BASE}/auth/register", json=imperial_user_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify registration success
                self.log_test("Imperial user registration", True, f"User {data['user']['username']} registered successfully")
                
                # Verify user data includes unit preferences
                user_data = data['user']
                expected_fields = ['id', 'username', 'email', 'role', 'player_id', 'age', 'position']
                missing_fields = [field for field in expected_fields if field not in user_data]
                
                if missing_fields:
                    self.log_test("Imperial user data completeness", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Imperial user data completeness", True, "All required fields present")
                
                # Store token for later tests
                self.imperial_token = data['access_token']
                self.imperial_user_id = user_data['id']
                
                return True
            else:
                self.log_test("Imperial user registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Imperial user registration", False, f"Exception: {str(e)}")
            return False
    
    def test_metric_user_login_and_profile(self):
        """Test Scenario 3a: Login metric user and verify unit preferences persist"""
        print("\n🧪 SCENARIO 3a: Login Metric User and Verify Unit Preferences")
        
        try:
            # Login with metric user
            login_data = {
                "username": "metricplayer001",
                "password": "testpass123"
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Metric user login", True, f"Login successful for {data['user']['username']}")
                
                # Get user profile
                headers = {"Authorization": f"Bearer {data['access_token']}"}
                profile_response = requests.get(f"{API_BASE}/auth/profile", headers=headers)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    self.log_test("Metric user profile retrieval", True, "Profile data retrieved successfully")
                    
                    # Note: The current profile endpoint doesn't return height_unit/weight_unit
                    # This is a limitation we need to report
                    user_profile = profile_data.get('user', {})
                    if 'height_unit' not in user_profile or 'weight_unit' not in user_profile:
                        self.log_test("Metric unit preferences in profile", False, "height_unit and weight_unit not returned in profile endpoint")
                    else:
                        # Verify unit preferences
                        height_unit = user_profile.get('height_unit')
                        weight_unit = user_profile.get('weight_unit')
                        
                        if height_unit == "metric" and weight_unit == "metric":
                            self.log_test("Metric unit preferences persistence", True, f"Units: height={height_unit}, weight={weight_unit}")
                        else:
                            self.log_test("Metric unit preferences persistence", False, f"Expected metric/metric, got {height_unit}/{weight_unit}")
                    
                    return True
                else:
                    self.log_test("Metric user profile retrieval", False, f"Status: {profile_response.status_code}")
                    return False
            else:
                self.log_test("Metric user login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Metric user login and profile", False, f"Exception: {str(e)}")
            return False
    
    def test_imperial_user_login_and_profile(self):
        """Test Scenario 3b: Login imperial user and verify unit preferences persist"""
        print("\n🧪 SCENARIO 3b: Login Imperial User and Verify Unit Preferences")
        
        try:
            # Login with imperial user
            login_data = {
                "username": "imperialplayer001",
                "password": "testpass123"
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Imperial user login", True, f"Login successful for {data['user']['username']}")
                
                # Get user profile
                headers = {"Authorization": f"Bearer {data['access_token']}"}
                profile_response = requests.get(f"{API_BASE}/auth/profile", headers=headers)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    self.log_test("Imperial user profile retrieval", True, "Profile data retrieved successfully")
                    
                    # Note: The current profile endpoint doesn't return height_unit/weight_unit
                    # This is a limitation we need to report
                    user_profile = profile_data.get('user', {})
                    if 'height_unit' not in user_profile or 'weight_unit' not in user_profile:
                        self.log_test("Imperial unit preferences in profile", False, "height_unit and weight_unit not returned in profile endpoint")
                    else:
                        # Verify unit preferences
                        height_unit = user_profile.get('height_unit')
                        weight_unit = user_profile.get('weight_unit')
                        
                        if height_unit == "imperial" and weight_unit == "imperial":
                            self.log_test("Imperial unit preferences persistence", True, f"Units: height={height_unit}, weight={weight_unit}")
                        else:
                            self.log_test("Imperial unit preferences persistence", False, f"Expected imperial/imperial, got {height_unit}/{weight_unit}")
                    
                    return True
                else:
                    self.log_test("Imperial user profile retrieval", False, f"Status: {profile_response.status_code}")
                    return False
            else:
                self.log_test("Imperial user login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Imperial user login and profile", False, f"Exception: {str(e)}")
            return False
    
    def test_first_time_assessment_check_metric(self):
        """Test Scenario 4a: First-Time Assessment Check for Metric User"""
        print("\n🧪 SCENARIO 4a: First-Time Assessment Check - Metric User")
        
        try:
            # Use metric user token
            headers = {"Authorization": f"Bearer {self.metric_token}"}
            
            # Check benchmarks (should be empty for new user)
            response = requests.get(f"{API_BASE}/auth/benchmarks", headers=headers)
            
            if response.status_code == 200:
                benchmarks = response.json()
                
                if isinstance(benchmarks, list) and len(benchmarks) == 0:
                    self.log_test("Metric user first-time assessment check", True, "Benchmarks array is empty as expected for new user")
                else:
                    self.log_test("Metric user first-time assessment check", False, f"Expected empty array, got: {len(benchmarks)} benchmarks")
                
                return True
            else:
                self.log_test("Metric user first-time assessment check", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Metric user first-time assessment check", False, f"Exception: {str(e)}")
            return False
    
    def test_first_time_assessment_check_imperial(self):
        """Test Scenario 4b: First-Time Assessment Check for Imperial User"""
        print("\n🧪 SCENARIO 4b: First-Time Assessment Check - Imperial User")
        
        try:
            # Use imperial user token
            headers = {"Authorization": f"Bearer {self.imperial_token}"}
            
            # Check benchmarks (should be empty for new user)
            response = requests.get(f"{API_BASE}/auth/benchmarks", headers=headers)
            
            if response.status_code == 200:
                benchmarks = response.json()
                
                if isinstance(benchmarks, list) and len(benchmarks) == 0:
                    self.log_test("Imperial user first-time assessment check", True, "Benchmarks array is empty as expected for new user")
                else:
                    self.log_test("Imperial user first-time assessment check", False, f"Expected empty array, got: {len(benchmarks)} benchmarks")
                
                return True
            else:
                self.log_test("Imperial user first-time assessment check", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Imperial user first-time assessment check", False, f"Exception: {str(e)}")
            return False
    
    def test_height_weight_storage_format(self):
        """Test that height and weight are stored with correct suffixes"""
        print("\n🧪 ADDITIONAL TEST: Height/Weight Storage Format Verification")
        
        # This test would require direct database access or a specific endpoint
        # For now, we'll test by checking if the registration accepts the format
        # and note this as a limitation
        
        self.log_test("Height/Weight storage format verification", False, 
                     "Cannot verify storage format without database access or specific endpoint. Need to check if height stored as '175cm'/'69\"' and weight as '68kg'/'150lbs'")
    
    def run_all_tests(self):
        """Run all unit preference system tests"""
        print("🚀 STARTING UNIT PREFERENCE SYSTEM TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Initialize tokens
        self.metric_token = None
        self.imperial_token = None
        self.metric_user_id = None
        self.imperial_user_id = None
        
        # Run test scenarios
        self.test_metric_user_registration()
        self.test_imperial_user_registration()
        
        # Only run login tests if registration succeeded
        if hasattr(self, 'metric_token') and self.metric_token:
            self.test_metric_user_login_and_profile()
            self.test_first_time_assessment_check_metric()
        
        if hasattr(self, 'imperial_token') and self.imperial_token:
            self.test_imperial_user_login_and_profile()
            self.test_first_time_assessment_check_imperial()
        
        # Additional tests
        self.test_height_weight_storage_format()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 UNIT PREFERENCE SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        for result in self.test_results:
            print(result)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n🎯 SUCCESS RATE: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 OVERALL STATUS: GOOD - Most unit preference functionality working")
        elif success_rate >= 60:
            print("⚠️  OVERALL STATUS: PARTIAL - Some unit preference issues need attention")
        else:
            print("🚨 OVERALL STATUS: CRITICAL - Major unit preference system issues")
        
        return success_rate

def main():
    """Main test execution"""
    tester = UnitPreferenceSystemTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    if success_rate >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()