#!/usr/bin/env python3
"""
YoYo Report v2 API Testing
==========================

Tests the new YoYo Report v2 presentation-layer endpoints.
This tests the read-only formatting endpoints that present existing data.

Test Credentials:
- Username: yoyo_test
- Password: Test123!
- User ID: a09c6343-daa9-4cf7-8846-0c425544bd4d

Endpoints to Test:
1. GET /api/v2/report/yoyo/{player_id} - Full report
2. GET /api/v2/report/yoyo/{player_id}/sections - Sections only
3. GET /api/v2/report/yoyo/{player_id}/json - JSON only
4. Authentication tests (401/403 without auth)
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://soccer-onboarding.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_USERNAME = "yoyo_test"
TEST_PASSWORD = "Test123!"
TEST_PLAYER_ID = "a09c6343-daa9-4cf7-8846-0c425544bd4d"

# Expected section titles in exact order
EXPECTED_SECTION_TITLES = [
    "Identity & Biology",
    "Performance Snapshot", 
    "Strengths & Weaknesses",
    "Development Identity",
    "Benchmarks (Now → Target → Elite)",
    "Training Mode",
    "Training Program",
    "Return-to-Play Engine",
    "Safety Governor",
    "AI Object (JSON)",
    "Goal State"
]

# Expected JSON keys
EXPECTED_JSON_KEYS = [
    'player_id', 'name', 'age', 'gender', 'position', 'dominant_leg',
    'mode', 'profile_label', 'weekly_sessions', 'total_weeks',
    'benchmarks', 'safety_rules', 'sub_program', 'matches'
]

# Expected sub_program keys
EXPECTED_SUB_PROGRAM_KEYS = ['phases', 'weekly_microcycle', 'expanded_sections']

# Expected expanded_sections keys (9 keys)
EXPECTED_EXPANDED_SECTIONS_KEYS = [
    'technical', 'tactical', 'possession', 'cardio', 'gym',
    'speed_agility', 'mobility', 'recovery', 'prehab'
]

class YoYoReportV2Tester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            print(f"\n🔐 Authenticating with username: {TEST_USERNAME}")
            
            # Try login endpoint
            login_data = {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    self.log_test("Authentication", True, f"Successfully authenticated as {TEST_USERNAME}")
                    return True
                else:
                    self.log_test("Authentication", False, f"No access_token in response: {data}")
                    return False
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_unauthenticated_access(self):
        """Test that endpoints require authentication"""
        print(f"\n🚫 Testing unauthenticated access...")
        
        # Create session without auth
        unauth_session = requests.Session()
        
        try:
            response = unauth_session.get(f"{API_BASE}/v2/report/yoyo/{TEST_PLAYER_ID}")
            
            if response.status_code in [401, 403]:
                self.log_test("Unauthenticated Access Protection", True, 
                            f"Correctly returned {response.status_code} for unauthenticated request")
            else:
                self.log_test("Unauthenticated Access Protection", False, 
                            f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Unauthenticated Access Protection", False, f"Error: {str(e)}")
    
    def test_full_yoyo_report(self) -> Optional[Dict[str, Any]]:
        """Test GET /api/v2/report/yoyo/{player_id}"""
        print(f"\n📊 Testing full YoYo Report v2 endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/v2/report/yoyo/{TEST_PLAYER_ID}")
            
            if response.status_code != 200:
                self.log_test("Full YoYo Report - HTTP Status", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return None
            
            self.log_test("Full YoYo Report - HTTP Status", True, "Returns HTTP 200")
            
            # Parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Full YoYo Report - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return None
            
            self.log_test("Full YoYo Report - JSON Parse", True, "Valid JSON response")
            
            # Check top-level structure
            if not data.get('success'):
                self.log_test("Full YoYo Report - Success Flag", False, f"success=False: {data}")
                return None
            
            self.log_test("Full YoYo Report - Success Flag", True, "success=True")
            
            # Check for report object
            if 'report' not in data:
                self.log_test("Full YoYo Report - Report Object", False, "Missing 'report' key")
                return None
            
            report = data['report']
            self.log_test("Full YoYo Report - Report Object", True, "Has 'report' object")
            
            # Check report_sections
            if 'report_sections' not in report:
                self.log_test("Full YoYo Report - Report Sections", False, "Missing 'report_sections'")
                return None
            
            sections = report['report_sections']
            
            # Check sections count
            if len(sections) != 11:
                self.log_test("Full YoYo Report - Section Count", False, 
                            f"Expected 11 sections, got {len(sections)}")
                return None
            
            self.log_test("Full YoYo Report - Section Count", True, "Has exactly 11 sections")
            
            # Check section order and titles
            section_titles_correct = True
            for i, section in enumerate(sections):
                expected_number = i + 1
                expected_title = EXPECTED_SECTION_TITLES[i]
                
                if section.get('section_number') != expected_number:
                    self.log_test("Full YoYo Report - Section Numbers", False, 
                                f"Section {i+1} has wrong number: {section.get('section_number')}")
                    section_titles_correct = False
                    break
                
                if section.get('section_title') != expected_title:
                    self.log_test("Full YoYo Report - Section Titles", False, 
                                f"Section {i+1} has wrong title. Expected '{expected_title}', got '{section.get('section_title')}'")
                    section_titles_correct = False
                    break
            
            if section_titles_correct:
                self.log_test("Full YoYo Report - Section Order", True, "All sections in correct order with correct titles")
            
            # Check report_json
            if 'report_json' not in report:
                self.log_test("Full YoYo Report - Report JSON", False, "Missing 'report_json'")
                return None
            
            report_json = report['report_json']
            self.log_test("Full YoYo Report - Report JSON", True, "Has 'report_json' object")
            
            # Check required JSON keys
            missing_keys = []
            for key in EXPECTED_JSON_KEYS:
                if key not in report_json:
                    missing_keys.append(key)
            
            if missing_keys:
                self.log_test("Full YoYo Report - JSON Keys", False, 
                            f"Missing required keys: {missing_keys}")
            else:
                self.log_test("Full YoYo Report - JSON Keys", True, "All required JSON keys present")
            
            # Check sub_program structure
            if 'sub_program' in report_json:
                sub_program = report_json['sub_program']
                
                # Check sub_program keys
                missing_sub_keys = []
                for key in EXPECTED_SUB_PROGRAM_KEYS:
                    if key not in sub_program:
                        missing_sub_keys.append(key)
                
                if missing_sub_keys:
                    self.log_test("Full YoYo Report - Sub Program Keys", False, 
                                f"Missing sub_program keys: {missing_sub_keys}")
                else:
                    self.log_test("Full YoYo Report - Sub Program Keys", True, "All sub_program keys present")
                
                # Check expanded_sections
                if 'expanded_sections' in sub_program:
                    expanded = sub_program['expanded_sections']
                    missing_expanded = []
                    for key in EXPECTED_EXPANDED_SECTIONS_KEYS:
                        if key not in expanded:
                            missing_expanded.append(key)
                    
                    if missing_expanded:
                        self.log_test("Full YoYo Report - Expanded Sections", False, 
                                    f"Missing expanded_sections keys: {missing_expanded}")
                    else:
                        self.log_test("Full YoYo Report - Expanded Sections", True, 
                                    f"All 9 expanded_sections keys present: {list(expanded.keys())}")
            
            # Check validation
            if 'validation' in data:
                validation = data['validation']
                if validation.get('valid'):
                    self.log_test("Full YoYo Report - Validation", True, "Report structure validation passed")
                else:
                    self.log_test("Full YoYo Report - Validation", False, 
                                f"Validation errors: {validation.get('errors', [])}")
            
            # Check specific data from assessment (Section 2 - Performance Snapshot)
            section_2 = sections[1]  # Performance Snapshot
            if section_2.get('section_title') == "Performance Snapshot":
                content = section_2.get('content', {})
                physical_metrics = content.get('physical_metrics', {})
                technical_metrics = content.get('technical_metrics', {})
                
                # Check for specific values mentioned in requirements
                sprint_30m = physical_metrics.get('sprint_30m', {}).get('value')
                yo_yo_test = physical_metrics.get('yo_yo_test', {}).get('value')
                ball_control = technical_metrics.get('ball_control', {}).get('value')
                overall_score = content.get('overall_score')
                
                performance_data = []
                if sprint_30m not in [None, "N/A"]:
                    performance_data.append(f"Sprint 30m: {sprint_30m}")
                if yo_yo_test not in [None, "N/A"]:
                    performance_data.append(f"Yo-Yo Test: {yo_yo_test}")
                if ball_control not in [None, "N/A"]:
                    performance_data.append(f"Ball Control: {ball_control}")
                if overall_score not in [None, "N/A"]:
                    performance_data.append(f"Overall Score: {overall_score}")
                
                if performance_data:
                    self.log_test("Full YoYo Report - Performance Data", True, 
                                f"Performance metrics found: {', '.join(performance_data)}")
                else:
                    self.log_test("Full YoYo Report - Performance Data", False, 
                                "No performance metrics found in Section 2")
            
            return data
            
        except Exception as e:
            self.log_test("Full YoYo Report - Exception", False, f"Error: {str(e)}")
            return None
    
    def test_sections_only_endpoint(self):
        """Test GET /api/v2/report/yoyo/{player_id}/sections"""
        print(f"\n📋 Testing sections-only endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/v2/report/yoyo/{TEST_PLAYER_ID}/sections")
            
            if response.status_code != 200:
                self.log_test("Sections Only - HTTP Status", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            self.log_test("Sections Only - HTTP Status", True, "Returns HTTP 200")
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Sections Only - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return
            
            # Check structure
            if not data.get('success'):
                self.log_test("Sections Only - Success Flag", False, f"success=False: {data}")
                return
            
            if 'sections' not in data:
                self.log_test("Sections Only - Sections Key", False, "Missing 'sections' key")
                return
            
            if 'meta' not in data:
                self.log_test("Sections Only - Meta Key", False, "Missing 'meta' key")
                return
            
            # Should NOT have full report_json
            if 'json' in data or 'report_json' in data:
                self.log_test("Sections Only - Lighter Payload", False, 
                            "Should not include full JSON object for lighter payload")
            else:
                self.log_test("Sections Only - Lighter Payload", True, 
                            "Correctly excludes full JSON object")
            
            sections = data['sections']
            if len(sections) == 11:
                self.log_test("Sections Only - Section Count", True, "Returns 11 sections")
            else:
                self.log_test("Sections Only - Section Count", False, 
                            f"Expected 11 sections, got {len(sections)}")
            
        except Exception as e:
            self.log_test("Sections Only - Exception", False, f"Error: {str(e)}")
    
    def test_json_only_endpoint(self):
        """Test GET /api/v2/report/yoyo/{player_id}/json"""
        print(f"\n🔧 Testing JSON-only endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/v2/report/yoyo/{TEST_PLAYER_ID}/json")
            
            if response.status_code != 200:
                self.log_test("JSON Only - HTTP Status", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            self.log_test("JSON Only - HTTP Status", True, "Returns HTTP 200")
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("JSON Only - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return
            
            # Check structure
            if not data.get('success'):
                self.log_test("JSON Only - Success Flag", False, f"success=False: {data}")
                return
            
            if 'json' not in data:
                self.log_test("JSON Only - JSON Key", False, "Missing 'json' key")
                return
            
            if 'meta' not in data:
                self.log_test("JSON Only - Meta Key", False, "Missing 'meta' key")
                return
            
            # Should NOT have sections
            if 'sections' in data or 'report_sections' in data:
                self.log_test("JSON Only - Machine Readable", False, 
                            "Should not include sections for machine-readable endpoint")
            else:
                self.log_test("JSON Only - Machine Readable", True, 
                            "Correctly excludes sections for machine-readable data")
            
            # Check JSON structure
            json_obj = data['json']
            required_keys_present = all(key in json_obj for key in EXPECTED_JSON_KEYS)
            
            if required_keys_present:
                self.log_test("JSON Only - Required Keys", True, "All required JSON keys present")
            else:
                missing = [key for key in EXPECTED_JSON_KEYS if key not in json_obj]
                self.log_test("JSON Only - Required Keys", False, f"Missing keys: {missing}")
            
        except Exception as e:
            self.log_test("JSON Only - Exception", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n" + "="*60)
        print(f"YoYo Report v2 API Test Summary")
        print(f"="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 Test completed at: {datetime.now().isoformat()}")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    print("🚀 Starting YoYo Report v2 API Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Player ID: {TEST_PLAYER_ID}")
    
    tester = YoYoReportV2Tester()
    
    # Step 1: Test unauthenticated access
    tester.test_unauthenticated_access()
    
    # Step 2: Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed. Cannot proceed with authenticated tests.")
        tester.print_summary()
        return False
    
    # Step 3: Test full YoYo Report endpoint
    full_report_data = tester.test_full_yoyo_report()
    
    # Step 4: Test sections-only endpoint
    tester.test_sections_only_endpoint()
    
    # Step 5: Test JSON-only endpoint
    tester.test_json_only_endpoint()
    
    # Step 6: Print summary
    success = tester.print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)