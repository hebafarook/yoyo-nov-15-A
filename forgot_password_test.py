#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Forgot Password Feature
Testing the NEW forgot password functionality as requested in the review.
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

class ForgotPasswordTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user = None
        self.reset_token = None
        
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
        
    async def test_1_register_test_user(self):
        """Test 1: Setup - Register a test user for forgot password testing"""
        test_name = "1. Register Test User for Forgot Password"
        
        try:
            user_data = {
                "username": "forgottest001",
                "email": "forgottest001@test.com",
                "password": "oldpassword123",
                "full_name": "Forgot Test User",
                "role": "player",
                "age": 18,
                "position": "Forward"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=user_data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify response contains expected fields
                    if ("access_token" in response_data and 
                        "user" in response_data and
                        response_data["user"]["username"] == "forgottest001" and
                        response_data["user"]["email"] == "forgottest001@test.com"):
                        
                        self.test_user = response_data["user"]
                        self.log_result(test_name, True, 
                                      f"User registered successfully: {self.test_user['username']}")
                        return True
                    else:
                        self.log_result(test_name, False, 
                                      "Response missing required fields", response_data)
                        return False
                else:
                    self.log_result(test_name, False, 
                                  f"Registration failed with status {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during registration: {str(e)}")
            return False
            
    async def test_2_forgot_password_request(self):
        """Test 2: Test forgot password request with valid email"""
        test_name = "2. Forgot Password Request (Valid Email)"
        
        try:
            # Use query parameter as shown in the review request
            url = f"{BACKEND_URL}/auth/forgot-password?email=forgottest001@test.com"
            
            async with self.session.post(url) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify response contains expected fields
                    if ("success" in response_data and 
                        response_data["success"] == True and
                        "reset_token" in response_data and
                        "username" in response_data and
                        "expires_in" in response_data):
                        
                        # Store reset token for next test
                        self.reset_token = response_data["reset_token"]
                        
                        # Verify token is UUID format
                        try:
                            uuid.UUID(self.reset_token)
                            token_valid_format = True
                        except ValueError:
                            token_valid_format = False
                        
                        if token_valid_format:
                            self.log_result(test_name, True, 
                                          f"Reset token generated: {self.reset_token[:8]}... (UUID format verified)")
                            return True
                        else:
                            self.log_result(test_name, False, 
                                          f"Reset token not in UUID format: {self.reset_token}")
                            return False
                    else:
                        self.log_result(test_name, False, 
                                      "Response missing required fields", response_data)
                        return False
                else:
                    self.log_result(test_name, False, 
                                  f"Forgot password request failed with status {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during forgot password request: {str(e)}")
            return False
            
    async def test_3_reset_password_valid_token(self):
        """Test 3: Test reset password with valid token"""
        test_name = "3. Reset Password with Valid Token"
        
        if not self.reset_token:
            self.log_result(test_name, False, "No reset token available from previous test")
            return False
            
        try:
            # Use query parameters as expected by the endpoint
            url = f"{BACKEND_URL}/auth/reset-password?reset_token={self.reset_token}&new_password=newpassword456"
            
            async with self.session.post(url) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify response contains success message
                    if ("success" in response_data and 
                        response_data["success"] == True and
                        "message" in response_data):
                        
                        self.log_result(test_name, True, 
                                      f"Password reset successful: {response_data['message']}")
                        return True
                    else:
                        self.log_result(test_name, False, 
                                      "Response missing success confirmation", response_data)
                        return False
                else:
                    self.log_result(test_name, False, 
                                  f"Password reset failed with status {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during password reset: {str(e)}")
            return False
            
    async def test_4_verify_old_password_fails(self):
        """Test 4: Verify old password no longer works"""
        test_name = "4. Verify Old Password Fails"
        
        try:
            login_data = {
                "username": "forgottest001",
                "password": "oldpassword123"  # Old password should fail
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_data = await response.json()
                
                if response.status == 401:
                    # This is expected - old password should fail
                    self.log_result(test_name, True, 
                                  "Old password correctly rejected with 401 Unauthorized")
                    return True
                elif response.status == 200:
                    # This is bad - old password still works
                    self.log_result(test_name, False, 
                                  "Old password still works - password was not changed!", response_data)
                    return False
                else:
                    self.log_result(test_name, False, 
                                  f"Unexpected status {response.status} when testing old password", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during old password test: {str(e)}")
            return False
            
    async def test_5_verify_new_password_works(self):
        """Test 5: Verify new password allows login"""
        test_name = "5. Verify New Password Works"
        
        try:
            login_data = {
                "username": "forgottest001",
                "password": "newpassword456"  # New password should work
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify response contains JWT token and user data
                    if ("access_token" in response_data and 
                        "user" in response_data and
                        response_data["user"]["username"] == "forgottest001"):
                        
                        self.log_result(test_name, True, 
                                      "New password works correctly - login successful with JWT token")
                        return True
                    else:
                        self.log_result(test_name, False, 
                                      "Login response missing required fields", response_data)
                        return False
                else:
                    self.log_result(test_name, False, 
                                  f"New password login failed with status {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during new password test: {str(e)}")
            return False
            
    async def test_6_invalid_token_rejected(self):
        """Test 6: Test invalid/fake token is rejected"""
        test_name = "6. Invalid Token Rejected"
        
        try:
            fake_token = str(uuid.uuid4())  # Generate fake UUID token
            # Use query parameters as expected by the endpoint
            url = f"{BACKEND_URL}/auth/reset-password?reset_token={fake_token}&new_password=shouldnotwork123"
            
            async with self.session.post(url) as response:
                response_data = await response.json()
                
                if response.status == 400:
                    # This is expected - fake token should be rejected
                    if "detail" in response_data and "Invalid or expired reset token" in response_data["detail"]:
                        self.log_result(test_name, True, 
                                      "Invalid token correctly rejected with 400 Bad Request")
                        return True
                    else:
                        self.log_result(test_name, False, 
                                      "Invalid token rejected but wrong error message", response_data)
                        return False
                else:
                    self.log_result(test_name, False, 
                                  f"Invalid token not properly rejected - status {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during invalid token test: {str(e)}")
            return False
            
    async def test_7_nonexistent_email_security(self):
        """Test 7: Test non-existent email doesn't reveal information"""
        test_name = "7. Non-existent Email Security"
        
        try:
            # Use query parameter for non-existent email
            url = f"{BACKEND_URL}/auth/forgot-password?email=nonexistent@test.com"
            
            async with self.session.post(url) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Should still return success for security (don't reveal if email exists)
                    if ("success" in response_data and 
                        response_data["success"] == True):
                        
                        # Should NOT contain reset_token for non-existent email
                        if "reset_token" not in response_data:
                            self.log_result(test_name, True, 
                                          "Non-existent email handled securely - no token revealed")
                            return True
                        else:
                            self.log_result(test_name, False, 
                                          "Security issue: reset token generated for non-existent email", response_data)
                            return False
                    else:
                        self.log_result(test_name, False, 
                                      "Non-existent email should return success for security", response_data)
                        return False
                else:
                    self.log_result(test_name, False, 
                                  f"Non-existent email request failed with status {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during non-existent email test: {str(e)}")
            return False
            
    async def test_8_used_token_rejected(self):
        """Test 8: Test that used token cannot be reused"""
        test_name = "8. Used Token Cannot Be Reused"
        
        if not self.reset_token:
            self.log_result(test_name, False, "No reset token available from previous test")
            return False
            
        try:
            # Try to use the same token again using query parameters
            url = f"{BACKEND_URL}/auth/reset-password?reset_token={self.reset_token}&new_password=anothernewpassword789"
            
            async with self.session.post(url) as response:
                response_data = await response.json()
                
                if response.status == 400:
                    # This is expected - used token should be rejected
                    if "detail" in response_data and "Invalid or expired reset token" in response_data["detail"]:
                        self.log_result(test_name, True, 
                                      "Used token correctly rejected - cannot be reused")
                        return True
                    else:
                        self.log_result(test_name, False, 
                                      "Used token rejected but wrong error message", response_data)
                        return False
                else:
                    self.log_result(test_name, False, 
                                  f"Used token not properly rejected - status {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception during used token test: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all forgot password tests in sequence"""
        print("🔥 FORGOT PASSWORD FEATURE TESTING STARTED 🔥")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        test_methods = [
            self.test_1_register_test_user,
            self.test_2_forgot_password_request,
            self.test_3_reset_password_valid_token,
            self.test_4_verify_old_password_fails,
            self.test_5_verify_new_password_works,
            self.test_6_invalid_token_rejected,
            self.test_7_nonexistent_email_security,
            self.test_8_used_token_rejected
        ]
        
        for test_method in test_methods:
            await test_method()
            
        # Print summary
        print("=" * 60)
        print("🔥 FORGOT PASSWORD TESTING SUMMARY 🔥")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Forgot Password feature is working correctly!")
        elif success_rate >= 75:
            print("✅ GOOD: Forgot Password feature mostly working with minor issues")
        elif success_rate >= 50:
            print("⚠️  NEEDS WORK: Forgot Password feature has significant issues")
        else:
            print("❌ CRITICAL: Forgot Password feature is not working properly")
            
        print()
        return success_rate >= 75  # Consider 75%+ as passing

async def main():
    """Main test execution"""
    tester = ForgotPasswordTester()
    
    try:
        await tester.setup()
        success = await tester.run_all_tests()
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        return 1
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)