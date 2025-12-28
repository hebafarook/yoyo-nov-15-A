#!/usr/bin/env python3
"""
Coach PDF Drill Upload Testing
==============================

Tests the 2-step Coach PDF Drill Upload process:
1. POST /api/coach/drills/upload-pdf - Parse PDF and return preview candidates (NO DB writes)
2. POST /api/coach/drills/confirm - Validate and save drills to DB
3. GET /api/coach/drills/sections - Get valid sections for dropdown

Authentication Tests:
- Without token → 401/403
- Player token → 403 (only coach/admin allowed)
- Coach token → 200
- Admin token → 200

File Validation Tests:
- Non-PDF file → 400
- Empty file → 400
- Valid PDF → 200 with parsed candidates

Validation Tests:
- Invalid section → 422 (whole batch rejected, NO partial writes)
- Duplicate drill_ids → 422
- Valid drills → 200 with upsert results
"""

import requests
import json
import sys
import jwt
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import io

# Backend URL from environment
BACKEND_URL = "https://drill-uploader.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# JWT Configuration
JWT_SECRET = "elite-soccer-ai-coach-secret-key-2024-change-in-production"
JWT_ALGORITHM = "HS256"

# Test PDF file path
TEST_PDF_PATH = "/tmp/test_drills.pdf"

class CoachDrillUploadTester:
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
    
    def create_jwt_token(self, user_id: str, role: str, username: str = "test_user") -> str:
        """Create JWT token for testing"""
        payload = {
            "user_id": user_id,
            "role": role,
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def test_upload_pdf_requires_auth(self):
        """Test that upload-pdf endpoint requires authentication"""
        print(f"\n🚫 Testing upload-pdf without authentication...")
        
        # Create session without auth
        unauth_session = requests.Session()
        
        try:
            # Try to upload without token
            with open(TEST_PDF_PATH, 'rb') as f:
                files = {'file': ('test_drills.pdf', f, 'application/pdf')}
                response = unauth_session.post(f"{API_BASE}/coach/drills/upload-pdf", files=files)
            
            if response.status_code in [401, 403]:
                self.log_test("Upload PDF - No Auth Protection", True, 
                            f"Correctly returned {response.status_code} for unauthenticated request")
            else:
                self.log_test("Upload PDF - No Auth Protection", False, 
                            f"Expected 401/403, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Upload PDF - No Auth Protection", False, f"Error: {str(e)}")
    
    def test_upload_pdf_requires_coach_or_admin(self):
        """Test that upload-pdf requires coach or admin role"""
        print(f"\n👤 Testing upload-pdf with player token...")
        
        try:
            # Create player token
            player_token = self.create_jwt_token("player-456", "player", "test_player")
            
            # Create session with player token
            player_session = requests.Session()
            player_session.headers.update({'Authorization': f'Bearer {player_token}'})
            
            # Try to upload with player token
            with open(TEST_PDF_PATH, 'rb') as f:
                files = {'file': ('test_drills.pdf', f, 'application/pdf')}
                response = player_session.post(f"{API_BASE}/coach/drills/upload-pdf", files=files)
            
            if response.status_code == 403:
                self.log_test("Upload PDF - Player Role Rejection", True, 
                            "Correctly rejected player token with 403")
            else:
                self.log_test("Upload PDF - Player Role Rejection", False, 
                            f"Expected 403, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Upload PDF - Player Role Rejection", False, f"Error: {str(e)}")
    
    def test_upload_pdf_file_validation(self):
        """Test file validation for upload-pdf"""
        print(f"\n📄 Testing file validation...")
        
        # Create coach token
        coach_token = self.create_jwt_token("coach-123", "coach", "test_coach")
        coach_session = requests.Session()
        coach_session.headers.update({'Authorization': f'Bearer {coach_token}'})
        
        # Test 1: Non-PDF file
        try:
            fake_txt_content = b"This is not a PDF file"
            files = {'file': ('test.txt', io.BytesIO(fake_txt_content), 'text/plain')}
            response = coach_session.post(f"{API_BASE}/coach/drills/upload-pdf", files=files)
            
            if response.status_code == 400:
                self.log_test("Upload PDF - Non-PDF Rejection", True, 
                            "Correctly rejected non-PDF file with 400")
            else:
                self.log_test("Upload PDF - Non-PDF Rejection", False, 
                            f"Expected 400, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Upload PDF - Non-PDF Rejection", False, f"Error: {str(e)}")
        
        # Test 2: Empty file
        try:
            files = {'file': ('empty.pdf', io.BytesIO(b""), 'application/pdf')}
            response = coach_session.post(f"{API_BASE}/coach/drills/upload-pdf", files=files)
            
            if response.status_code == 400:
                self.log_test("Upload PDF - Empty File Rejection", True, 
                            "Correctly rejected empty file with 400")
            else:
                self.log_test("Upload PDF - Empty File Rejection", False, 
                            f"Expected 400, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Upload PDF - Empty File Rejection", False, f"Error: {str(e)}")
    
    def test_upload_pdf_returns_candidates(self) -> Optional[Dict[str, Any]]:
        """Test successful PDF upload and parsing"""
        print(f"\n📊 Testing successful PDF upload...")
        
        try:
            # Create coach token
            coach_token = self.create_jwt_token("coach-123", "coach", "test_coach")
            coach_session = requests.Session()
            coach_session.headers.update({'Authorization': f'Bearer {coach_token}'})
            
            # Upload valid PDF
            with open(TEST_PDF_PATH, 'rb') as f:
                files = {'file': ('test_drills.pdf', f, 'application/pdf')}
                response = coach_session.post(f"{API_BASE}/coach/drills/upload-pdf", files=files)
            
            if response.status_code != 200:
                self.log_test("Upload PDF - Success Response", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return None
            
            self.log_test("Upload PDF - Success Response", True, "Returns HTTP 200")
            
            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Upload PDF - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return None
            
            self.log_test("Upload PDF - JSON Parse", True, "Valid JSON response")
            
            # Check response structure
            required_keys = ['parsed', 'errors', 'meta']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                self.log_test("Upload PDF - Response Structure", False, 
                            f"Missing required keys: {missing_keys}")
                return None
            
            self.log_test("Upload PDF - Response Structure", True, "Has required keys: parsed, errors, meta")
            
            # Check parsed candidates
            parsed = data['parsed']
            if not isinstance(parsed, list):
                self.log_test("Upload PDF - Parsed Candidates", False, 
                            f"'parsed' should be a list, got {type(parsed)}")
                return None
            
            if len(parsed) == 0:
                self.log_test("Upload PDF - Parsed Candidates", False, 
                            "No drill candidates were parsed from PDF")
                return None
            
            self.log_test("Upload PDF - Parsed Candidates", True, 
                        f"Parsed {len(parsed)} drill candidates")
            
            # Check candidate structure
            first_candidate = parsed[0]
            expected_candidate_keys = ['raw_text', 'needs_review', 'confidence']
            missing_candidate_keys = [key for key in expected_candidate_keys if key not in first_candidate]
            
            if missing_candidate_keys:
                self.log_test("Upload PDF - Candidate Structure", False, 
                            f"Missing candidate keys: {missing_candidate_keys}")
            else:
                self.log_test("Upload PDF - Candidate Structure", True, 
                            "Candidates have required structure")
            
            # Check meta information
            meta = data['meta']
            if 'filename' in meta and 'pages' in meta:
                self.log_test("Upload PDF - Meta Information", True, 
                            f"Meta: {meta['filename']}, {meta['pages']} pages")
            else:
                self.log_test("Upload PDF - Meta Information", False, 
                            "Missing filename or pages in meta")
            
            return data
            
        except Exception as e:
            self.log_test("Upload PDF - Exception", False, f"Error: {str(e)}")
            return None
    
    def test_confirm_requires_auth(self):
        """Test that confirm endpoint requires authentication"""
        print(f"\n🚫 Testing confirm without authentication...")
        
        # Create session without auth
        unauth_session = requests.Session()
        
        try:
            # Try to confirm without token
            confirm_data = {
                "drills": [
                    {
                        "drill_id": "TEST01",
                        "name": "Test Drill",
                        "section": "technical"
                    }
                ]
            }
            response = unauth_session.post(f"{API_BASE}/coach/drills/confirm", json=confirm_data)
            
            if response.status_code in [401, 403]:
                self.log_test("Confirm - No Auth Protection", True, 
                            f"Correctly returned {response.status_code} for unauthenticated request")
            else:
                self.log_test("Confirm - No Auth Protection", False, 
                            f"Expected 401/403, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Confirm - No Auth Protection", False, f"Error: {str(e)}")
    
    def test_confirm_validates_all_or_none(self):
        """Test that confirm validates all drills and rejects batch if any invalid"""
        print(f"\n🔍 Testing confirm validation (all-or-none)...")
        
        try:
            # Create coach token
            coach_token = self.create_jwt_token("coach-123", "coach", "test_coach")
            coach_session = requests.Session()
            coach_session.headers.update({'Authorization': f'Bearer {coach_token}'})
            
            # Test 1: Invalid section should reject entire batch
            invalid_batch = {
                "drills": [
                    {
                        "drill_id": "VALID01",
                        "name": "Valid Drill",
                        "section": "technical"
                    },
                    {
                        "drill_id": "INVALID01",
                        "name": "Invalid Drill",
                        "section": "invalid_section"  # Invalid section
                    }
                ]
            }
            
            response = coach_session.post(f"{API_BASE}/coach/drills/confirm", json=invalid_batch)
            
            if response.status_code == 422:
                self.log_test("Confirm - Invalid Section Rejection", True, 
                            "Correctly rejected batch with invalid section (422)")
            else:
                self.log_test("Confirm - Invalid Section Rejection", False, 
                            f"Expected 422, got {response.status_code}: {response.text}")
            
            # Test 2: Duplicate drill_ids should reject batch
            duplicate_batch = {
                "drills": [
                    {
                        "drill_id": "DUPLICATE01",
                        "name": "First Drill",
                        "section": "technical"
                    },
                    {
                        "drill_id": "DUPLICATE01",  # Duplicate ID
                        "name": "Second Drill",
                        "section": "tactical"
                    }
                ]
            }
            
            response = coach_session.post(f"{API_BASE}/coach/drills/confirm", json=duplicate_batch)
            
            if response.status_code == 422:
                self.log_test("Confirm - Duplicate ID Rejection", True, 
                            "Correctly rejected batch with duplicate drill_ids (422)")
            else:
                self.log_test("Confirm - Duplicate ID Rejection", False, 
                            f"Expected 422, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Confirm - Validation Exception", False, f"Error: {str(e)}")
    
    def test_confirm_upserts(self):
        """Test that confirm successfully upserts valid drills"""
        print(f"\n💾 Testing confirm upsert functionality...")
        
        try:
            # Create coach token
            coach_token = self.create_jwt_token("coach-123", "coach", "test_coach")
            coach_session = requests.Session()
            coach_session.headers.update({'Authorization': f'Bearer {coach_token}'})
            
            # Test valid drill batch
            valid_batch = {
                "drills": [
                    {
                        "drill_id": f"COACH_TEST_{int(time.time())}_01",
                        "name": "Triangle Passing",
                        "section": "technical",
                        "tags": ["passing", "first_touch"],
                        "duration_min": 15,
                        "intensity": "moderate",
                        "equipment": ["cones", "balls"],
                        "coaching_points": ["Soft first touch", "Body position open"]
                    },
                    {
                        "drill_id": f"COACH_TEST_{int(time.time())}_02",
                        "name": "Speed Ladder",
                        "section": "speed_agility",
                        "tags": ["agility", "quick_feet"],
                        "duration_min": 10,
                        "intensity": "high",
                        "equipment": ["ladder"]
                    }
                ]
            }
            
            response = coach_session.post(f"{API_BASE}/coach/drills/confirm", json=valid_batch)
            
            if response.status_code != 200:
                self.log_test("Confirm - Valid Drills Success", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            self.log_test("Confirm - Valid Drills Success", True, "Returns HTTP 200")
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Confirm - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return
            
            # Check response structure
            required_keys = ['success', 'inserted', 'updated', 'total', 'drill_ids']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                self.log_test("Confirm - Response Structure", False, 
                            f"Missing required keys: {missing_keys}")
                return
            
            self.log_test("Confirm - Response Structure", True, "Has required response keys")
            
            # Check success flag
            if not data.get('success'):
                self.log_test("Confirm - Success Flag", False, f"success=False: {data}")
                return
            
            self.log_test("Confirm - Success Flag", True, "success=True")
            
            # Check counts
            total = data.get('total', 0)
            inserted = data.get('inserted', 0)
            updated = data.get('updated', 0)
            
            if total == 2 and (inserted + updated) == 2:
                self.log_test("Confirm - Upsert Counts", True, 
                            f"Total: {total}, Inserted: {inserted}, Updated: {updated}")
            else:
                self.log_test("Confirm - Upsert Counts", False, 
                            f"Expected total=2, got total={total}, inserted={inserted}, updated={updated}")
            
            # Check drill_ids
            drill_ids = data.get('drill_ids', [])
            if len(drill_ids) == 2:
                self.log_test("Confirm - Drill IDs", True, f"Returned {len(drill_ids)} drill IDs")
            else:
                self.log_test("Confirm - Drill IDs", False, 
                            f"Expected 2 drill IDs, got {len(drill_ids)}")
                
        except Exception as e:
            self.log_test("Confirm - Upsert Exception", False, f"Error: {str(e)}")
    
    def test_get_sections_requires_auth(self):
        """Test that sections endpoint requires authentication"""
        print(f"\n🚫 Testing sections without authentication...")
        
        # Create session without auth
        unauth_session = requests.Session()
        
        try:
            response = unauth_session.get(f"{API_BASE}/coach/drills/sections")
            
            if response.status_code in [401, 403]:
                self.log_test("Sections - No Auth Protection", True, 
                            f"Correctly returned {response.status_code} for unauthenticated request")
            else:
                self.log_test("Sections - No Auth Protection", False, 
                            f"Expected 401/403, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Sections - No Auth Protection", False, f"Error: {str(e)}")
    
    def test_get_sections_success(self):
        """Test successful sections retrieval"""
        print(f"\n📋 Testing sections endpoint...")
        
        try:
            # Create coach token
            coach_token = self.create_jwt_token("coach-123", "coach", "test_coach")
            coach_session = requests.Session()
            coach_session.headers.update({'Authorization': f'Bearer {coach_token}'})
            
            response = coach_session.get(f"{API_BASE}/coach/drills/sections")
            
            if response.status_code != 200:
                self.log_test("Sections - Success Response", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                return
            
            self.log_test("Sections - Success Response", True, "Returns HTTP 200")
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Sections - JSON Parse", False, f"Invalid JSON: {str(e)}")
                return
            
            # Check structure
            if 'sections' not in data:
                self.log_test("Sections - Response Structure", False, "Missing 'sections' key")
                return
            
            sections = data['sections']
            if not isinstance(sections, list) or len(sections) == 0:
                self.log_test("Sections - Valid Sections", False, 
                            f"Expected non-empty list, got {type(sections)} with {len(sections) if isinstance(sections, list) else 'N/A'} items")
                return
            
            self.log_test("Sections - Valid Sections", True, 
                        f"Returns {len(sections)} valid sections: {sections}")
            
            # Check for intensities
            if 'intensities' in data:
                intensities = data['intensities']
                self.log_test("Sections - Intensities", True, 
                            f"Returns intensities: {intensities}")
            else:
                self.log_test("Sections - Intensities", False, "Missing 'intensities' key")
                
        except Exception as e:
            self.log_test("Sections - Exception", False, f"Error: {str(e)}")
    
    def test_admin_token_access(self):
        """Test that admin token can access all endpoints"""
        print(f"\n👑 Testing admin token access...")
        
        try:
            # Create admin token
            admin_token = self.create_jwt_token("admin-789", "admin", "test_admin")
            admin_session = requests.Session()
            admin_session.headers.update({'Authorization': f'Bearer {admin_token}'})
            
            # Test upload-pdf with admin token
            with open(TEST_PDF_PATH, 'rb') as f:
                files = {'file': ('test_drills.pdf', f, 'application/pdf')}
                response = admin_session.post(f"{API_BASE}/coach/drills/upload-pdf", files=files)
            
            if response.status_code == 200:
                self.log_test("Admin Token - Upload PDF Access", True, 
                            "Admin can access upload-pdf endpoint")
            else:
                self.log_test("Admin Token - Upload PDF Access", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
            
            # Test sections with admin token
            response = admin_session.get(f"{API_BASE}/coach/drills/sections")
            
            if response.status_code == 200:
                self.log_test("Admin Token - Sections Access", True, 
                            "Admin can access sections endpoint")
            else:
                self.log_test("Admin Token - Sections Access", False, 
                            f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Token - Exception", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n" + "="*60)
        print(f"Coach PDF Drill Upload Test Summary")
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
    print("🚀 Starting Coach PDF Drill Upload Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test PDF: {TEST_PDF_PATH}")
    
    # Check if test PDF exists
    try:
        with open(TEST_PDF_PATH, 'rb') as f:
            pdf_size = len(f.read())
        print(f"Test PDF found: {pdf_size} bytes")
    except FileNotFoundError:
        print(f"❌ Test PDF not found at {TEST_PDF_PATH}")
        return False
    
    tester = CoachDrillUploadTester()
    
    # Authentication Tests
    print(f"\n🔐 AUTHENTICATION TESTS")
    tester.test_upload_pdf_requires_auth()
    tester.test_upload_pdf_requires_coach_or_admin()
    tester.test_confirm_requires_auth()
    tester.test_get_sections_requires_auth()
    
    # File Validation Tests
    print(f"\n📄 FILE VALIDATION TESTS")
    tester.test_upload_pdf_file_validation()
    
    # Functional Tests
    print(f"\n⚙️ FUNCTIONAL TESTS")
    upload_result = tester.test_upload_pdf_returns_candidates()
    tester.test_confirm_validates_all_or_none()
    tester.test_confirm_upserts()
    tester.test_get_sections_success()
    
    # Admin Access Tests
    print(f"\n👑 ADMIN ACCESS TESTS")
    tester.test_admin_token_access()
    
    # Print summary
    success = tester.print_summary()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)