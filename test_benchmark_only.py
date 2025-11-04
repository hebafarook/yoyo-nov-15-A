#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class BenchmarkTester:
    def __init__(self, base_url="https://elite-soccer-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.access_token = None
        self.user_id = None
        self.test_username = None
        self.first_benchmark_id = None
        self.second_benchmark_id = None
        self.third_benchmark_id = None

    def run_test_with_auth(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test with authentication headers"""
        url = f"{self.api_url}/{endpoint}"
        if not headers:
            headers = {}
        headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

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

    def test_user_registration(self):
        """Test user registration for authentication"""
        timestamp = str(int(time.time()))
        user_data = {
            "username": f"testcoach_benchmark_{timestamp}",
            "email": f"testcoach_{timestamp}@benchmark.com",
            "full_name": "Test Coach Benchmark",
            "password": "securepassword123",
            "is_coach": True
        }
        
        success, response = self.run_test_with_auth(
            "Register Test User for Benchmarks",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            self.user_id = response['user']['id']
            self.test_username = user_data['username']
            print(f"   Access Token: {self.access_token[:20]}...")
            print(f"   User ID: {self.user_id}")
        
        return success

    def test_save_first_benchmark_baseline(self):
        """Test saving first assessment benchmark (should auto-detect as baseline)"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        benchmark_data = {
            "user_id": self.user_id,
            "player_name": "Lionel Martinez",
            "assessment_id": "test-assessment-001",
            "age": 16,
            "position": "Midfielder",
            "sprint_30m": 4.2,
            "yo_yo_test": 2400,
            "vo2_max": 55.0,
            "vertical_jump": 50,
            "body_fat": 12.0,
            "ball_control": 4,
            "passing_accuracy": 85.0,
            "dribbling_success": 75.0,
            "shooting_accuracy": 70.0,
            "defensive_duels": 65.0,
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4,
            "overall_score": 78.5,
            "performance_level": "Advanced",
            "benchmark_type": "regular",
            "notes": "First benchmark test"
        }
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Save First Benchmark (Baseline Auto-Detection)",
            "POST",
            "auth/save-benchmark",
            200,
            data=benchmark_data,
            headers=headers
        )
        
        if success:
            self.first_benchmark_id = response.get('id')
            print(f"   Benchmark ID: {self.first_benchmark_id}")
            print(f"   Is Baseline: {response.get('is_baseline')}")
            print(f"   Benchmark Type: {response.get('benchmark_type')}")
            
            # Verify it's marked as baseline
            if response.get('is_baseline') != True:
                print("❌ ERROR: First benchmark should be auto-detected as baseline")
                return False
            if response.get('benchmark_type') != "baseline":
                print("❌ ERROR: First benchmark type should be 'baseline'")
                return False
        
        return success

    def test_save_second_benchmark_regular(self):
        """Test saving second assessment benchmark (should be regular with improvement calculation)"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        benchmark_data = {
            "user_id": self.user_id,
            "player_name": "Lionel Martinez",
            "assessment_id": "test-assessment-002",
            "age": 16,
            "position": "Midfielder",
            "sprint_30m": 4.0,  # Improved
            "yo_yo_test": 2500,  # Improved
            "vo2_max": 57.0,  # Improved
            "vertical_jump": 52,  # Improved
            "body_fat": 11.5,  # Improved
            "ball_control": 4,
            "passing_accuracy": 87.0,  # Improved
            "dribbling_success": 78.0,  # Improved
            "shooting_accuracy": 72.0,  # Improved
            "defensive_duels": 68.0,  # Improved
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4,
            "overall_score": 81.2,  # Improved
            "performance_level": "Advanced",
            "benchmark_type": "regular",
            "notes": "Second benchmark showing improvement"
        }
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Save Second Benchmark (Regular with Improvement)",
            "POST",
            "auth/save-benchmark",
            200,
            data=benchmark_data,
            headers=headers
        )
        
        if success:
            self.second_benchmark_id = response.get('id')
            print(f"   Benchmark ID: {self.second_benchmark_id}")
            print(f"   Is Baseline: {response.get('is_baseline')}")
            print(f"   Has Improvement Data: {response.get('improvement_from_baseline') is not None}")
            
            # Verify it's NOT baseline and has improvement data
            if response.get('is_baseline') != False:
                print("❌ ERROR: Second benchmark should NOT be baseline")
                return False
            if response.get('improvement_from_baseline') is None:
                print("❌ ERROR: Second benchmark should have improvement_from_baseline data")
                return False
        
        return success

    def test_get_all_benchmarks(self):
        """Test retrieving all benchmarks for user"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get All User Benchmarks",
            "GET",
            "auth/benchmarks",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Total Benchmarks: {len(response)}")
            if len(response) >= 2:
                print(f"   First (newest): {response[0].get('benchmark_type')} - {response[0].get('overall_score')}")
                print(f"   Last (oldest): {response[-1].get('benchmark_type')} - {response[-1].get('overall_score')}")
        
        return success

    def test_get_baseline_benchmark(self):
        """Test retrieving baseline benchmark for specific player"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get Baseline Benchmark for Player",
            "GET",
            "auth/benchmarks/baseline?player_name=Lionel Martinez",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Baseline ID: {response.get('id')}")
            print(f"   Is Baseline: {response.get('is_baseline')}")
            print(f"   Benchmark Type: {response.get('benchmark_type')}")
            
            # Verify it's actually the baseline
            if response.get('is_baseline') != True:
                print("❌ ERROR: Retrieved benchmark is not marked as baseline")
                return False
        
        return success

    def test_get_player_progress_analysis(self):
        """Test getting comprehensive progress analysis for player"""
        if not self.access_token:
            print("❌ Skipping - No access token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Get Player Progress Analysis",
            "GET",
            "auth/benchmarks/progress/Lionel Martinez",
            200,
            headers=headers
        )
        
        if success:
            print(f"   Player: {response.get('player_name')}")
            print(f"   Total Benchmarks: {response.get('total_benchmarks')}")
            print(f"   Baseline Score: {response.get('baseline_score')}")
            print(f"   Latest Score: {response.get('latest_score')}")
            print(f"   Overall Improvement: {response.get('overall_improvement')}%")
            print(f"   Timeline Entries: {len(response.get('improvement_timeline', []))}")
        
        return success

    def test_try_delete_baseline_benchmark(self):
        """Test trying to delete baseline benchmark (should fail with 400 error)"""
        if not self.access_token or not self.first_benchmark_id:
            print("❌ Skipping - No access token or baseline benchmark ID available")
            return False
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        success, response = self.run_test_with_auth(
            "Try to Delete Baseline Benchmark (Should Fail)",
            "DELETE",
            f"auth/benchmarks/{self.first_benchmark_id}",
            400,  # Should return 400 Bad Request
            headers=headers
        )
        
        if success:
            print(f"   Correctly prevented baseline deletion: {response.get('detail', 'No error message')}")
        
        return success

def main():
    print("🔥 Testing Assessment Benchmark System")
    print("=" * 60)
    
    tester = BenchmarkTester()
    
    # Test sequence
    test_results = []
    
    # Authentication setup
    test_results.append(tester.test_user_registration())
    
    # Core benchmark functionality
    test_results.append(tester.test_save_first_benchmark_baseline())
    test_results.append(tester.test_save_second_benchmark_regular())
    
    # Retrieval and analysis
    test_results.append(tester.test_get_all_benchmarks())
    test_results.append(tester.test_get_baseline_benchmark())
    test_results.append(tester.test_get_player_progress_analysis())
    
    # Protection testing
    test_results.append(tester.test_try_delete_baseline_benchmark())
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 ASSESSMENT BENCHMARK SYSTEM TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Assessment Benchmark System tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())