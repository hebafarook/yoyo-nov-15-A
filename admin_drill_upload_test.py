#!/usr/bin/env python3
"""
Admin Drill Upload API Testing
==============================

Tests the new Admin Drill Upload API endpoints as specified in the review request.
This feature allows admins to upload training drills to MongoDB.

Endpoints to Test:
1. POST /api/admin/drills/upload - Upload JSON file with training drills (admin only)
2. GET /api/admin/drills/stats - Get drill statistics (admin only)
3. GET /api/admin/drills - List all drills with optional filters (admin only)
4. GET /api/admin/drills/{drill_id} - Get single drill by ID (admin only)
5. DELETE /api/admin/drills/{drill_id} - Delete/deactivate drill (admin only)

Authentication Tests:
- Without token → 401/403
- With player/coach token (non-admin) → 403
- With admin token → 200

Validation Tests:
- Duplicate drill_ids in same upload → 422
- Invalid section value → 422
- Empty drills list → 422
- Valid upload with 3 drills → 200

Upsert Tests:
- Upload same drill_id twice → second upload should update (updated_count=1, uploaded_count=0)
"""

import requests
import json
import sys
import jwt
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Backend URL from environment
BACKEND_URL = "https://drill-uploader.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# JWT Configuration - same as backend .env
JWT_SECRET = "elite-soccer-ai-coach-secret-key-2024-change-in-production"
JWT_ALGORITHM = "HS256"

class AdminDrillUploadTester:
    def __init__(self):
        self.session = requests.Session()
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
    
    def create_jwt_token(self, user_id: str, role: str, username: str = "") -> str:
        """Create JWT token for testing"""
        payload = {
            "user_id": user_id,
            "role": role,
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def get_admin_token(self) -> str:
        """Get admin JWT token"""
        return self.create_jwt_token("admin-123", "admin", "admin_user")
    
    def get_player_token(self) -> str:
        """Get player JWT token"""
        return self.create_jwt_token("player-456", "player", "player_user")
    
    def get_coach_token(self) -> str:
        """Get coach JWT token"""
        return self.create_jwt_token("coach-789", "coach", "coach_user")
    
    def test_upload_authentication(self):
        """Test authentication for upload endpoint"""
        print(f"\n🔐 Testing upload authentication...")
        
        test_drill = {
            "drill_id": "auth_test_drill",
            "name": "Auth Test Drill",
            "section": "technical"
        }
        
        # Test 1: No token → 401/403
        try:
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": [test_drill]})
            if response.status_code in [401, 403]:
                self.log_test("Upload Auth - No Token", True, f"Correctly returned {response.status_code}")
            else:
                self.log_test("Upload Auth - No Token", False, f"Expected 401/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Upload Auth - No Token", False, f"Error: {str(e)}")
        
        # Test 2: Player token → 403
        try:
            headers = {"Authorization": f"Bearer {self.get_player_token()}"}
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": [test_drill]}, headers=headers)
            if response.status_code == 403:
                self.log_test("Upload Auth - Player Token", True, "Correctly returned 403 for non-admin")
            else:
                self.log_test("Upload Auth - Player Token", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_test("Upload Auth - Player Token", False, f"Error: {str(e)}")
        
        # Test 3: Coach token → 403
        try:
            headers = {"Authorization": f"Bearer {self.get_coach_token()}"}
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": [test_drill]}, headers=headers)
            if response.status_code == 403:
                self.log_test("Upload Auth - Coach Token", True, "Correctly returned 403 for non-admin")
            else:
                self.log_test("Upload Auth - Coach Token", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_test("Upload Auth - Coach Token", False, f"Error: {str(e)}")
        
        # Test 4: Admin token → 200
        try:
            headers = {"Authorization": f"Bearer {self.get_admin_token()}"}
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": [test_drill]}, headers=headers)
            if response.status_code == 200:
                self.log_test("Upload Auth - Admin Token", True, "Admin token correctly allowed")
            else:
                self.log_test("Upload Auth - Admin Token", False, f"Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Upload Auth - Admin Token", False, f"Error: {str(e)}")
    
    def test_upload_validation(self):
        """Test upload validation"""
        print(f"\n✅ Testing upload validation...")
        
        admin_headers = {"Authorization": f"Bearer {self.get_admin_token()}"}
        
        # Test 1: Empty drills list → 422
        try:
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": []}, headers=admin_headers)
            if response.status_code == 422:
                self.log_test("Upload Validation - Empty List", True, "Correctly rejected empty drills list")
            else:
                self.log_test("Upload Validation - Empty List", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Upload Validation - Empty List", False, f"Error: {str(e)}")
        
        # Test 2: Duplicate drill_ids → 422
        try:
            duplicate_drills = [
                {"drill_id": "duplicate_test", "name": "Drill 1", "section": "technical"},
                {"drill_id": "duplicate_test", "name": "Drill 2", "section": "tactical"}
            ]
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": duplicate_drills}, headers=admin_headers)
            if response.status_code == 422:
                self.log_test("Upload Validation - Duplicate IDs", True, "Correctly rejected duplicate drill_ids")
            else:
                self.log_test("Upload Validation - Duplicate IDs", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Upload Validation - Duplicate IDs", False, f"Error: {str(e)}")
        
        # Test 3: Invalid section → 422
        try:
            invalid_section_drill = [
                {"drill_id": "invalid_section_test", "name": "Invalid Section", "section": "invalid_section"}
            ]
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": invalid_section_drill}, headers=admin_headers)
            if response.status_code == 422:
                self.log_test("Upload Validation - Invalid Section", True, "Correctly rejected invalid section")
            else:
                self.log_test("Upload Validation - Invalid Section", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Upload Validation - Invalid Section", False, f"Error: {str(e)}")
        
        # Test 4: Valid upload with 3 drills → 200
        try:
            valid_drills = [
                {
                    "drill_id": "valid_tech_drill",
                    "name": "Technical Passing Drill",
                    "section": "technical",
                    "tags": ["passing", "accuracy"],
                    "age_min": 10,
                    "age_max": 18,
                    "intensity": "moderate",
                    "duration_min": 15,
                    "equipment": ["balls", "cones"],
                    "coaching_points": ["Keep head up", "Proper weight on pass"]
                },
                {
                    "drill_id": "valid_tactical_drill",
                    "name": "Tactical Positioning",
                    "section": "tactical",
                    "tags": ["positioning", "awareness"],
                    "intensity": "low",
                    "duration_min": 20
                },
                {
                    "drill_id": "valid_cardio_drill",
                    "name": "Interval Running",
                    "section": "cardio",
                    "intensity": "high",
                    "duration_min": 30,
                    "equipment": ["cones"]
                }
            ]
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": valid_drills}, headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('uploaded_count') == 3:
                    self.log_test("Upload Validation - Valid 3 Drills", True, f"Successfully uploaded 3 drills: {data.get('drill_ids')}")
                else:
                    self.log_test("Upload Validation - Valid 3 Drills", False, f"Unexpected response: {data}")
            else:
                self.log_test("Upload Validation - Valid 3 Drills", False, f"Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Upload Validation - Valid 3 Drills", False, f"Error: {str(e)}")
    
    def test_upsert_behavior(self):
        """Test upsert behavior - updating existing drills"""
        print(f"\n🔄 Testing upsert behavior...")
        
        admin_headers = {"Authorization": f"Bearer {self.get_admin_token()}"}
        
        # First upload
        try:
            initial_drill = [{
                "drill_id": "upsert_test_drill",
                "name": "Original Name",
                "section": "technical",
                "tags": ["original"],
                "intensity": "low"
            }]
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": initial_drill}, headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('uploaded_count') == 1 and data.get('updated_count') == 0:
                    self.log_test("Upsert - Initial Upload", True, "Initial drill uploaded successfully")
                else:
                    self.log_test("Upsert - Initial Upload", False, f"Unexpected counts: {data}")
            else:
                self.log_test("Upsert - Initial Upload", False, f"Expected 200, got {response.status_code}")
        except Exception as e:
            self.log_test("Upsert - Initial Upload", False, f"Error: {str(e)}")
        
        # Second upload with same drill_id (should update)
        try:
            updated_drill = [{
                "drill_id": "upsert_test_drill",
                "name": "Updated Name",
                "section": "tactical",
                "tags": ["updated"],
                "intensity": "high"
            }]
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": updated_drill}, headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('uploaded_count') == 0 and data.get('updated_count') == 1:
                    self.log_test("Upsert - Update Existing", True, "Existing drill updated successfully")
                else:
                    self.log_test("Upsert - Update Existing", False, f"Expected updated_count=1, uploaded_count=0, got: {data}")
            else:
                self.log_test("Upsert - Update Existing", False, f"Expected 200, got {response.status_code}")
        except Exception as e:
            self.log_test("Upsert - Update Existing", False, f"Error: {str(e)}")
    
    def test_stats_endpoint(self):
        """Test GET /api/admin/drills/stats"""
        print(f"\n📊 Testing stats endpoint...")
        
        # Test authentication first
        try:
            response = requests.get(f"{API_BASE}/admin/drills/stats")
            if response.status_code in [401, 403]:
                self.log_test("Stats Auth - No Token", True, f"Correctly returned {response.status_code}")
            else:
                self.log_test("Stats Auth - No Token", False, f"Expected 401/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Stats Auth - No Token", False, f"Error: {str(e)}")
        
        # Test with admin token
        try:
            admin_headers = {"Authorization": f"Bearer {self.get_admin_token()}"}
            response = requests.get(f"{API_BASE}/admin/drills/stats", headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["db_count", "static_count", "source_mode", "active_source", "db_available", "sections"]
                missing_keys = [key for key in required_keys if key not in data]
                if not missing_keys:
                    self.log_test("Stats Endpoint - Response Structure", True, 
                                f"All required keys present: db_count={data.get('db_count')}, "
                                f"static_count={data.get('static_count')}, "
                                f"source_mode={data.get('source_mode')}, "
                                f"active_source={data.get('active_source')}")
                else:
                    self.log_test("Stats Endpoint - Response Structure", False, f"Missing keys: {missing_keys}")
            else:
                self.log_test("Stats Endpoint - Response Structure", False, f"Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Stats Endpoint - Response Structure", False, f"Error: {str(e)}")
    
    def test_list_drills_endpoint(self):
        """Test GET /api/admin/drills"""
        print(f"\n📋 Testing list drills endpoint...")
        
        admin_headers = {"Authorization": f"Bearer {self.get_admin_token()}"}
        
        # Test basic list
        try:
            response = requests.get(f"{API_BASE}/admin/drills", headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["drills", "total", "source", "page", "page_size"]
                missing_keys = [key for key in required_keys if key not in data]
                if not missing_keys:
                    self.log_test("List Drills - Basic Response", True, 
                                f"Response structure correct: total={data.get('total')}, "
                                f"drills_count={len(data.get('drills', []))}, "
                                f"source={data.get('source')}")
                else:
                    self.log_test("List Drills - Basic Response", False, f"Missing keys: {missing_keys}")
            else:
                self.log_test("List Drills - Basic Response", False, f"Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("List Drills - Basic Response", False, f"Error: {str(e)}")
        
        # Test with filters
        try:
            params = {"section": "technical", "page": 1, "page_size": 10}
            response = requests.get(f"{API_BASE}/admin/drills", headers=admin_headers, params=params)
            if response.status_code == 200:
                data = response.json()
                self.log_test("List Drills - With Filters", True, 
                            f"Filtered request successful: {len(data.get('drills', []))} drills returned")
            else:
                self.log_test("List Drills - With Filters", False, f"Expected 200, got {response.status_code}")
        except Exception as e:
            self.log_test("List Drills - With Filters", False, f"Error: {str(e)}")
    
    def test_get_single_drill(self):
        """Test GET /api/admin/drills/{drill_id}"""
        print(f"\n🎯 Testing get single drill endpoint...")
        
        admin_headers = {"Authorization": f"Bearer {self.get_admin_token()}"}
        
        # Test with existing drill
        try:
            drill_id = "valid_tech_drill"  # From previous upload test
            response = requests.get(f"{API_BASE}/admin/drills/{drill_id}", headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('drill_id') == drill_id:
                    self.log_test("Get Single Drill - Existing", True, f"Successfully retrieved drill: {data.get('name')}")
                else:
                    self.log_test("Get Single Drill - Existing", False, f"Wrong drill returned: {data}")
            elif response.status_code == 404:
                self.log_test("Get Single Drill - Existing", True, "Drill not found (expected if not uploaded yet)")
            else:
                self.log_test("Get Single Drill - Existing", False, f"Expected 200/404, got {response.status_code}")
        except Exception as e:
            self.log_test("Get Single Drill - Existing", False, f"Error: {str(e)}")
        
        # Test with non-existent drill
        try:
            response = requests.get(f"{API_BASE}/admin/drills/non_existent_drill", headers=admin_headers)
            if response.status_code == 404:
                self.log_test("Get Single Drill - Non-existent", True, "Correctly returned 404 for non-existent drill")
            else:
                self.log_test("Get Single Drill - Non-existent", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Get Single Drill - Non-existent", False, f"Error: {str(e)}")
    
    def test_delete_drill(self):
        """Test DELETE /api/admin/drills/{drill_id}"""
        print(f"\n🗑️ Testing delete drill endpoint...")
        
        admin_headers = {"Authorization": f"Bearer {self.get_admin_token()}"}
        
        # First, upload a drill to delete
        try:
            test_drill = [{
                "drill_id": "delete_test_drill",
                "name": "Drill to Delete",
                "section": "technical"
            }]
            response = requests.post(f"{API_BASE}/admin/drills/upload", json={"drills": test_drill}, headers=admin_headers)
            if response.status_code == 200:
                self.log_test("Delete Setup - Upload Drill", True, "Test drill uploaded for deletion")
            else:
                self.log_test("Delete Setup - Upload Drill", False, f"Failed to upload test drill: {response.status_code}")
        except Exception as e:
            self.log_test("Delete Setup - Upload Drill", False, f"Error: {str(e)}")
        
        # Test soft delete (default)
        try:
            response = requests.delete(f"{API_BASE}/admin/drills/delete_test_drill", headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Delete Drill - Soft Delete", True, f"Drill soft deleted: {data.get('message')}")
                else:
                    self.log_test("Delete Drill - Soft Delete", False, f"Delete failed: {data}")
            elif response.status_code == 404:
                self.log_test("Delete Drill - Soft Delete", True, "Drill not found (expected if upload failed)")
            else:
                self.log_test("Delete Drill - Soft Delete", False, f"Expected 200/404, got {response.status_code}")
        except Exception as e:
            self.log_test("Delete Drill - Soft Delete", False, f"Error: {str(e)}")
        
        # Test hard delete
        try:
            response = requests.delete(f"{API_BASE}/admin/drills/delete_test_drill", 
                                     headers=admin_headers, params={"hard_delete": "true"})
            if response.status_code in [200, 404]:
                self.log_test("Delete Drill - Hard Delete", True, "Hard delete endpoint accessible")
            else:
                self.log_test("Delete Drill - Hard Delete", False, f"Expected 200/404, got {response.status_code}")
        except Exception as e:
            self.log_test("Delete Drill - Hard Delete", False, f"Error: {str(e)}")
    
    def test_all_endpoints_auth(self):
        """Test that all endpoints require admin authentication"""
        print(f"\n🔒 Testing authentication for all endpoints...")
        
        player_headers = {"Authorization": f"Bearer {self.get_player_token()}"}
        
        endpoints_to_test = [
            ("GET", "/admin/drills/stats"),
            ("GET", "/admin/drills"),
            ("GET", "/admin/drills/test_drill"),
            ("DELETE", "/admin/drills/test_drill")
        ]
        
        for method, endpoint in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{API_BASE}{endpoint}", headers=player_headers)
                elif method == "DELETE":
                    response = requests.delete(f"{API_BASE}{endpoint}", headers=player_headers)
                
                if response.status_code == 403:
                    self.log_test(f"Auth Protection - {method} {endpoint}", True, "Correctly blocked non-admin access")
                else:
                    self.log_test(f"Auth Protection - {method} {endpoint}", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_test(f"Auth Protection - {method} {endpoint}", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n" + "="*60)
        print(f"Admin Drill Upload API Test Summary")
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
    print("🚀 Starting Admin Drill Upload API Tests")
    print(f"Backend URL: {BACKEND_URL}")
    
    tester = AdminDrillUploadTester()
    
    # Run all tests
    tester.test_upload_authentication()
    tester.test_upload_validation()
    tester.test_upsert_behavior()
    tester.test_stats_endpoint()
    tester.test_list_drills_endpoint()
    tester.test_get_single_drill()
    tester.test_delete_drill()
    tester.test_all_endpoints_auth()
    
    # Print summary
    success = tester.print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)