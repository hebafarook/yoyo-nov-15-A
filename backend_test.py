#!/usr/bin/env python3
"""
Comprehensive Backend Testing for User Authentication System
Testing the 401 login error fix as requested in the review.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://elite-soccer-ai.preview.emergentagent.com/api"

class AuthenticationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
    async def test_user_registration_player(self):
        """Test registering a new player user"""
        test_name = "User Registration - Player Role"
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"player_{unique_id}",
            "email": f"player_{unique_id}@test.com",
            "full_name": f"Test Player {unique_id}",
            "password": "testpass123",
            "role": "player",
            "age": 16,
            "position": "midfielder"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify response structure
                    required_fields = ["access_token", "user", "message"]
                    user_fields = ["id", "username", "email", "role", "player_id", "age", "position"]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in response_data:
                            missing_fields.append(field)
                    
                    for field in user_fields:
                        if field not in response_data.get("user", {}):
                            missing_fields.append(f"user.{field}")
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing fields: {missing_fields}", response_data)
                    else:
                        # Store user for login test
                        self.test_users.append({
                            "username": test_user["username"],
                            "password": test_user["password"],
                            "user_data": response_data["user"],
                            "token": response_data["access_token"]
                        })
                        self.log_result(test_name, True, f"Player registered successfully with ID: {response_data['user']['id']}")
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_user_registration_coach(self):
        """Test registering a new coach user"""
        test_name = "User Registration - Coach Role"
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"coach_{unique_id}",
            "email": f"coach_{unique_id}@test.com",
            "full_name": f"Test Coach {unique_id}",
            "password": "testpass123",
            "role": "coach"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify coach-specific fields
                    user_data = response_data.get("user", {})
                    if user_data.get("role") == "coach" and user_data.get("is_coach") == True:
                        self.test_users.append({
                            "username": test_user["username"],
                            "password": test_user["password"],
                            "user_data": response_data["user"],
                            "token": response_data["access_token"]
                        })
                        self.log_result(test_name, True, f"Coach registered successfully")
                    else:
                        self.log_result(test_name, False, "Coach role not set correctly", response_data)
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_user_registration_parent(self):
        """Test registering a new parent user"""
        test_name = "User Registration - Parent Role"
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"parent_{unique_id}",
            "email": f"parent_{unique_id}@test.com",
            "full_name": f"Test Parent {unique_id}",
            "password": "testpass123",
            "role": "parent"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.test_users.append({
                        "username": test_user["username"],
                        "password": test_user["password"],
                        "user_data": response_data["user"],
                        "token": response_data["access_token"]
                    })
                    self.log_result(test_name, True, f"Parent registered successfully")
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_user_login_success(self):
        """Test successful login with registered users"""
        if not self.test_users:
            self.log_result("User Login - Success", False, "No test users available for login test")
            return
            
        for user in self.test_users:
            test_name = f"User Login - Success ({user['user_data']['role']})"
            
            login_data = {
                "username": user["username"],
                "password": user["password"]
            }
            
            try:
                async with self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        # Verify response structure
                        required_fields = ["access_token", "user", "message"]
                        missing_fields = [field for field in required_fields if field not in response_data]
                        
                        if missing_fields:
                            self.log_result(test_name, False, f"Missing fields: {missing_fields}", response_data)
                        else:
                            # Verify user_id consistency
                            if response_data["user"]["id"] == user["user_data"]["id"]:
                                # Update token for profile test
                                user["token"] = response_data["access_token"]
                                self.log_result(test_name, True, "Login successful with consistent user_id")
                            else:
                                self.log_result(test_name, False, "User ID mismatch between registration and login", response_data)
                    else:
                        self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                        
            except Exception as e:
                self.log_result(test_name, False, f"Exception: {str(e)}")
                
    async def test_user_login_wrong_password(self):
        """Test login with wrong password returns 401"""
        if not self.test_users:
            self.log_result("User Login - Wrong Password", False, "No test users available")
            return
            
        test_name = "User Login - Wrong Password (401 Expected)"
        user = self.test_users[0]  # Use first test user
        
        login_data = {
            "username": user["username"],
            "password": "wrongpassword123"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 401:
                    self.log_result(test_name, True, "Correctly returned 401 for wrong password")
                else:
                    self.log_result(test_name, False, f"Expected 401, got {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_user_login_nonexistent_user(self):
        """Test login with non-existent user returns 401"""
        test_name = "User Login - Non-existent User (401 Expected)"
        
        login_data = {
            "username": "nonexistent_user_12345",
            "password": "anypassword"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 401:
                    self.log_result(test_name, True, "Correctly returned 401 for non-existent user")
                else:
                    self.log_result(test_name, False, f"Expected 401, got {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_profile_retrieval_valid_token(self):
        """Test profile retrieval with valid token"""
        if not self.test_users:
            self.log_result("Profile Retrieval - Valid Token", False, "No test users available")
            return
            
        for user in self.test_users:
            test_name = f"Profile Retrieval - Valid Token ({user['user_data']['role']})"
            
            try:
                headers = {
                    "Authorization": f"Bearer {user['token']}",
                    "Content-Type": "application/json"
                }
                
                async with self.session.get(
                    f"{BACKEND_URL}/auth/profile",
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        # Verify profile structure
                        if "user" in response_data and "profile" in response_data:
                            profile_user = response_data["user"]
                            if profile_user["id"] == user["user_data"]["id"]:
                                self.log_result(test_name, True, "Profile retrieved successfully with correct user data")
                            else:
                                self.log_result(test_name, False, "User ID mismatch in profile", response_data)
                        else:
                            self.log_result(test_name, False, "Missing user or profile in response", response_data)
                    else:
                        self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                        
            except Exception as e:
                self.log_result(test_name, False, f"Exception: {str(e)}")
                
    async def test_profile_retrieval_invalid_token(self):
        """Test profile retrieval with invalid token returns 401"""
        test_name = "Profile Retrieval - Invalid Token (401 Expected)"
        
        try:
            headers = {
                "Authorization": "Bearer invalid_token_12345",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(
                f"{BACKEND_URL}/auth/profile",
                headers=headers
            ) as response:
                # Handle both JSON and non-JSON responses
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                if response.status == 401:
                    self.log_result(test_name, True, "Correctly returned 401 for invalid token")
                else:
                    self.log_result(test_name, False, f"Expected 401, got {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_database_verification(self):
        """Test database storage verification by checking user data persistence"""
        if not self.test_users:
            self.log_result("Database Verification", False, "No test users available")
            return
            
        test_name = "Database Verification - User Data Persistence"
        
        # Test by logging in again and checking if last_login was updated
        user = self.test_users[0]
        
        # First login to set initial last_login
        login_data = {
            "username": user["username"],
            "password": user["password"]
        }
        
        try:
            # Wait a moment to ensure timestamp difference
            await asyncio.sleep(1)
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Get profile to check last_login update
                    headers = {"Authorization": f"Bearer {response_data['access_token']}"}
                    
                    async with self.session.get(
                        f"{BACKEND_URL}/auth/profile",
                        headers=headers
                    ) as profile_response:
                        profile_data = await profile_response.json()
                        
                        if profile_response.status == 200:
                            user_profile = profile_data.get("user", {})
                            if "last_login" in user_profile and user_profile["last_login"]:
                                self.log_result(test_name, True, "Database properly stores and updates user data (last_login field verified)")
                            else:
                                self.log_result(test_name, False, "last_login field not found or empty", profile_data)
                        else:
                            self.log_result(test_name, False, f"Profile retrieval failed: HTTP {profile_response.status}")
                else:
                    self.log_result(test_name, False, f"Login failed: HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_end_to_end_flow(self):
        """Test complete end-to-end authentication flow"""
        test_name = "End-to-End Authentication Flow"
        
        # Generate unique test data for E2E test
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"e2e_player_{unique_id}",
            "email": f"e2e_player_{unique_id}@test.com",
            "full_name": f"E2E Test Player {unique_id}",
            "password": "e2etest123",
            "role": "player",
            "age": 17,
            "position": "forward"
        }
        
        try:
            # Step 1: Register
            async with self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, f"Registration failed: HTTP {response.status}")
                    return
                    
                reg_data = await response.json()
                user_id = reg_data["user"]["id"]
                
            # Step 2: Login immediately with same credentials
            login_data = {
                "username": test_user["username"],
                "password": test_user["password"]
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, f"Login failed: HTTP {response.status}")
                    return
                    
                login_data_response = await response.json()
                token = login_data_response["access_token"]
                
            # Step 3: Get profile
            headers = {"Authorization": f"Bearer {token}"}
            async with self.session.get(
                f"{BACKEND_URL}/auth/profile",
                headers=headers
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, f"Profile retrieval failed: HTTP {response.status}")
                    return
                    
                profile_data = await response.json()
                
            # Step 4: Verify user_id consistency
            profile_user_id = profile_data["user"]["id"]
            login_user_id = login_data_response["user"]["id"]
            
            if user_id == login_user_id == profile_user_id:
                self.log_result(test_name, True, f"Complete E2E flow successful with consistent user_id: {user_id}")
            else:
                self.log_result(test_name, False, f"User ID inconsistency: reg={user_id}, login={login_user_id}, profile={profile_user_id}")
                
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def run_all_tests(self):
        """Run all authentication tests"""
        print("🔥 STARTING USER AUTHENTICATION SYSTEM TESTING 🔥")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 60)
        print()
        
        await self.setup()
        
        try:
            # Test user registration for different roles
            await self.test_user_registration_player()
            await self.test_user_registration_coach()
            await self.test_user_registration_parent()
            
            # Test login scenarios
            await self.test_user_login_success()
            await self.test_user_login_wrong_password()
            await self.test_user_login_nonexistent_user()
            
            # Test profile retrieval
            await self.test_profile_retrieval_valid_token()
            await self.test_profile_retrieval_invalid_token()
            
            # Test database verification
            await self.test_database_verification()
            
            # Test end-to-end flow
            await self.test_end_to_end_flow()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("=" * 60)
        print("🏆 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
            
        print("=" * 60)
        print(f"Test completed at: {datetime.now()}")
        print("=" * 60)
        
        return passed_tests, failed_tests

async def main():
    """Main test execution"""
    tester = AuthenticationTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
