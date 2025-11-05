#!/usr/bin/env python3
"""
Assessment Report Save Functionality Test
Testing "Save to Profile" and "Save as Benchmark" buttons with proper authentication
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

class AssessmentReportSaveTest:
    def __init__(self):
        self.session = None
        self.user_data = None
        self.jwt_token = None
        self.assessment_id = None
        self.test_results = []
        
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
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
            
    async def test_user_registration(self):
        """Test 1: Register test user"""
        try:
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                "username": "reporttest001",
                "email": "reporttest001@test.com", 
                "password": "test123",
                "full_name": "Report Test User",
                "role": "player",
                "age": 17,
                "position": "Forward"
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_data = data.get("user", {})
                    self.jwt_token = data.get("access_token")
                    
                    if self.jwt_token and self.user_data:
                        self.log_result(
                            "User Registration", 
                            True, 
                            f"Successfully registered user: {self.user_data.get('username')}",
                            {"user_id": self.user_data.get("id"), "role": self.user_data.get("role")}
                        )
                        return True
                    else:
                        self.log_result("User Registration", False, "Missing JWT token or user data in response")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("User Registration", False, f"Registration failed with status {response.status}", {"error": error_text})
                    return False
                    
        except Exception as e:
            self.log_result("User Registration", False, f"Registration error: {str(e)}")
            return False
                        # Store user for login test
            
    async def test_user_login(self):
        """Test 2: Login with registered user"""
        try:
            login_data = {
                "username": "reporttest001",
                "password": "test123"
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
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
