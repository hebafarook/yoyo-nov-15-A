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
        """Test 3: Create assessment for the player"""
        try:
            assessment_data = {
                "player_name": "Report Test Player",
                "age": 17,
                "position": "Forward",
                # Physical metrics (20%)
                "sprint_30m": 4.3,
                "yo_yo_test": 1800,
                "vo2_max": 58.5,
                "vertical_jump": 55,
                "body_fat": 10.2,
                # Technical metrics (40%)
                "ball_control": 4,
                "passing_accuracy": 82.5,
                "dribbling_success": 68.0,
                "shooting_accuracy": 72.0,
                "defensive_duels": 75.0,
                # Tactical metrics (30%)
                "game_intelligence": 4,
                "positioning": 3,
                "decision_making": 4,
                # Psychological metrics (10%)
                "coachability": 5,
                "mental_toughness": 4
            }
            
            async with self.session.post(f"{API_BASE}/assessments", json=assessment_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.assessment_id = data.get("id")
                    
                    if self.assessment_id:
                        self.log_result(
                            "Assessment Creation", 
                            True, 
                            f"Successfully created assessment for {assessment_data['player_name']}",
                            {
                                "assessment_id": self.assessment_id,
                                "overall_score": data.get("overall_score"),
                                "performance_level": data.get("performance_level")
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
            
    async def test_save_report_endpoint(self):
        """Test 4: Test save-report endpoint with JWT authentication"""
        try:
            if not self.jwt_token:
                self.log_result("Save Report Test", False, "No JWT token available for authentication")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            report_data = {
                "player_name": "Report Test Player",
                "assessment_id": self.assessment_id,
                "report_data": {
                    "assessment_summary": {
                        "player_name": "Report Test Player",
                        "age": 17,
                        "position": "Forward",
                        "overall_score": 4.2,
                        "performance_level": "Good"
                    },
                    "strengths": ["Mental toughness", "Coachability", "Ball control"],
                    "weaknesses": ["Positioning", "Sprint speed"],
                    "recommendations": ["Focus on tactical positioning drills", "Speed training program"]
                },
                "report_type": "milestone",
                "title": "Test Assessment Report",
                "notes": "Test save functionality"
            }
            
            async with self.session.post(f"{API_BASE}/auth/save-report", json=report_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    report_id = data.get("id")
                    
                    if report_id:
                        self.log_result(
                            "Save Report Endpoint", 
                            True, 
                            "Successfully saved assessment report",
                            {
                                "report_id": report_id,
                                "report_type": data.get("report_type"),
                                "title": data.get("title")
                            }
                        )
                        return True
                    else:
                        self.log_result("Save Report Endpoint", False, "No report ID returned")
                        return False
                elif response.status == 401:
                    self.log_result("Save Report Endpoint", False, "Authentication failed (401) - JWT token invalid or expired")
                    return False
                elif response.status == 404:
                    self.log_result("Save Report Endpoint", False, "Endpoint not found (404) - save-report endpoint may not exist")
                    return False
                else:
                    error_text = await response.text()
                    self.log_result("Save Report Endpoint", False, f"Save report failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Save Report Endpoint", False, f"Save report error: {str(e)}")
            return False
            
    async def test_save_benchmark_endpoint(self):
        """Test 5: Test save-benchmark endpoint with JWT authentication"""
        try:
            if not self.jwt_token or not self.user_data:
                self.log_result("Save Benchmark Test", False, "No JWT token or user data available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            benchmark_data = {
                "user_id": self.user_data.get("id"),
                "player_name": "Report Test Player",
                "assessment_id": self.assessment_id,
                "age": 17,
                "position": "Forward",
                # Physical metrics
                "sprint_30m": 4.3,
                "yo_yo_test": 1800,
                "vo2_max": 58.5,
                "vertical_jump": 55,
                "body_fat": 10.2,
                # Technical metrics
                "ball_control": 4,
                "passing_accuracy": 82.5,
                "dribbling_success": 68.0,
                "shooting_accuracy": 72.0,
                "defensive_duels": 75.0,
                # Tactical metrics
                "game_intelligence": 4,
                "positioning": 3,
                "decision_making": 4,
                # Psychological metrics
                "coachability": 5,
                "mental_toughness": 4,
                # Calculated metrics
                "overall_score": 4.2,
                "performance_level": "Good",
                "benchmark_type": "milestone",
                "notes": "Test benchmark save"
            }
            
            async with self.session.post(f"{API_BASE}/auth/save-benchmark", json=benchmark_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    benchmark_id = data.get("id")
                    
                    if benchmark_id:
                        self.log_result(
                            "Save Benchmark Endpoint", 
                            True, 
                            "Successfully saved assessment benchmark",
                            {
                                "benchmark_id": benchmark_id,
                                "is_baseline": data.get("is_baseline"),
                                "benchmark_type": data.get("benchmark_type")
                            }
                        )
                        return True
                    else:
                        self.log_result("Save Benchmark Endpoint", False, "No benchmark ID returned")
                        return False
                elif response.status == 401:
                    self.log_result("Save Benchmark Endpoint", False, "Authentication failed (401) - JWT token invalid")
                    return False
                elif response.status == 403:
                    self.log_result("Save Benchmark Endpoint", False, "Authorization failed (403) - User not authorized")
                    return False
                elif response.status == 404:
                    self.log_result("Save Benchmark Endpoint", False, "Endpoint not found (404) - save-benchmark endpoint may not exist")
                    return False
                elif response.status == 422:
                    error_text = await response.text()
                    self.log_result("Save Benchmark Endpoint", False, f"Invalid request format (422)", {"error": error_text})
                    return False
                else:
                    error_text = await response.text()
                    self.log_result("Save Benchmark Endpoint", False, f"Save benchmark failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Save Benchmark Endpoint", False, f"Save benchmark error: {str(e)}")
            return False
            
    async def test_verify_saved_reports(self):
        """Test 6: Verify saved reports can be retrieved"""
        try:
            if not self.jwt_token:
                self.log_result("Verify Saved Reports", False, "No JWT token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.jwt_token}"
            }
            
            async with self.session.get(f"{API_BASE}/auth/saved-reports", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        report = data[0]
                        self.log_result(
                            "Verify Saved Reports", 
                            True, 
                            f"Successfully retrieved {len(data)} saved report(s)",
                            {
                                "report_count": len(data),
                                "first_report_id": report.get("id"),
                                "player_name": report.get("player_name")
                            }
                        )
                        return True
                    else:
                        self.log_result("Verify Saved Reports", False, "No saved reports found")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Verify Saved Reports", False, f"Failed to retrieve saved reports with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Verify Saved Reports", False, f"Verify saved reports error: {str(e)}")
            return False
            
    async def test_verify_saved_benchmarks(self):
        """Test 7: Verify saved benchmarks can be retrieved"""
        try:
            if not self.jwt_token:
                self.log_result("Verify Saved Benchmarks", False, "No JWT token available")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.jwt_token}"
            }
            
            async with self.session.get(f"{API_BASE}/auth/benchmarks", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        benchmark = data[0]
                        self.log_result(
                            "Verify Saved Benchmarks", 
                            True, 
                            f"Successfully retrieved {len(data)} benchmark(s)",
                            {
                                "benchmark_count": len(data),
                                "first_benchmark_id": benchmark.get("id"),
                                "player_name": benchmark.get("player_name"),
                                "is_baseline": benchmark.get("is_baseline")
                            }
                        )
                        return True
                    else:
                        self.log_result("Verify Saved Benchmarks", False, "No saved benchmarks found")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Verify Saved Benchmarks", False, f"Failed to retrieve benchmarks with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("Verify Saved Benchmarks", False, f"Verify saved benchmarks error: {str(e)}")
            return False
            
    async def test_authentication_errors(self):
        """Test 8: Test authentication error handling"""
        try:
            # Test with invalid token
            invalid_headers = {
                "Authorization": "Bearer invalid_token_12345",
                "Content-Type": "application/json"
            }
            
            report_data = {
                "player_name": "Test Player",
                "assessment_id": "test_id",
                "report_data": {},
                "report_type": "test"
            }
            
            async with self.session.post(f"{API_BASE}/auth/save-report", json=report_data, headers=invalid_headers) as response:
                if response.status == 401:
                    self.log_result(
                        "Authentication Error Handling", 
                        True, 
                        "Correctly rejected invalid JWT token with 401 status"
                    )
                    return True
                else:
                    self.log_result("Authentication Error Handling", False, f"Expected 401 for invalid token, got {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Authentication Error Handling", False, f"Authentication error test failed: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all assessment report save functionality tests"""
        print("🔥 ASSESSMENT REPORT SAVE FUNCTIONALITY TESTING 🔥")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Test sequence
            tests = [
                ("User Registration", self.test_user_registration),
                ("User Login", self.test_user_login),
                ("Assessment Creation", self.test_create_assessment),
                ("Save Report Endpoint", self.test_save_report_endpoint),
                ("Save Benchmark Endpoint", self.test_save_benchmark_endpoint),
                ("Verify Saved Reports", self.test_verify_saved_reports),
                ("Verify Saved Benchmarks", self.test_verify_saved_benchmarks),
                ("Authentication Error Handling", self.test_authentication_errors)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                print(f"\n🧪 Running: {test_name}")
                success = await test_func()
                if success:
                    passed += 1
                    
            # Summary
            print("\n" + "=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            
            success_rate = (passed / total) * 100
            print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
            
            if success_rate >= 85:
                print("🎉 EXCELLENT: Assessment report save functionality is working well!")
            elif success_rate >= 70:
                print("✅ GOOD: Most functionality working, minor issues to address")
            else:
                print("⚠️  NEEDS ATTENTION: Significant issues found in save functionality")
                
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
    tester = AssessmentReportSaveTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())