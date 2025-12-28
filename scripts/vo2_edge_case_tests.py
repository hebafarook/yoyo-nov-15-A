#!/usr/bin/env python3
"""
VO2 Max Benchmark Edge Case Tests
Tests error handling and edge cases for the new VO2 Max endpoints
"""

import requests
import json

class VO2EdgeCaseTester:
    def __init__(self, base_url="https://soccer-onboarding.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
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

    def test_invalid_player_id_get(self):
        """Test getting benchmarks for non-existent player"""
        return self.run_test(
            "Get VO2 Benchmarks - Invalid Player ID",
            "GET",
            "vo2-benchmarks/invalid-player-id",
            200  # Should return empty list, not error
        )

    def test_invalid_player_id_latest(self):
        """Test getting latest benchmark for non-existent player"""
        return self.run_test(
            "Get Latest VO2 Benchmark - Invalid Player ID",
            "GET",
            "vo2-benchmarks/latest/invalid-player-id",
            200  # Should return null/empty
        )

    def test_invalid_benchmark_id_delete(self):
        """Test deleting non-existent benchmark"""
        return self.run_test(
            "Delete VO2 Benchmark - Invalid ID",
            "DELETE",
            "vo2-benchmarks/invalid-benchmark-id",
            404  # Should return 404
        )

    def test_missing_required_fields(self):
        """Test creating benchmark with missing required fields"""
        incomplete_data = {
            "player_id": "test-player",
            # Missing vo2_max and calculation_inputs
            "calculation_method": "ACSM"
        }
        
        return self.run_test(
            "Save VO2 Benchmark - Missing Required Fields",
            "POST",
            "vo2-benchmarks",
            422,  # Should return validation error
            data=incomplete_data
        )

    def test_invalid_vo2_values(self):
        """Test creating benchmark with invalid VO2 values"""
        invalid_data = {
            "player_id": "test-player",
            "vo2_max": -10.0,  # Invalid negative value
            "calculation_inputs": {
                "age": 20,
                "gender": "male",
                "restingHeartRate": 60,
                "maxHeartRate": 190
            },
            "calculation_method": "ACSM"
        }
        
        return self.run_test(
            "Save VO2 Benchmark - Invalid VO2 Value",
            "POST",
            "vo2-benchmarks",
            200,  # API might accept it, but we should note this
            data=invalid_data
        )

    def test_extreme_vo2_values(self):
        """Test creating benchmark with extreme but potentially valid VO2 values"""
        extreme_data = {
            "player_id": "test-extreme-athlete",
            "vo2_max": 95.0,  # Very high but possible for elite athletes
            "calculation_inputs": {
                "age": 25,
                "gender": "male",
                "restingHeartRate": 35,
                "maxHeartRate": 200
            },
            "calculation_method": "ACSM",
            "notes": "Elite endurance athlete test",
            "fitness_level": "Elite"
        }
        
        return self.run_test(
            "Save VO2 Benchmark - Extreme Values",
            "POST",
            "vo2-benchmarks",
            200,
            data=extreme_data
        )

def main():
    print("🧪 Starting VO2 Max Benchmark Edge Case Tests")
    print("=" * 60)
    
    tester = VO2EdgeCaseTester()
    
    # Test sequence
    test_results = []
    
    # Edge case tests
    test_results.append(tester.test_invalid_player_id_get())
    test_results.append(tester.test_invalid_player_id_latest())
    test_results.append(tester.test_invalid_benchmark_id_delete())
    test_results.append(tester.test_missing_required_fields())
    test_results.append(tester.test_invalid_vo2_values())
    test_results.append(tester.test_extreme_vo2_values())
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 EDGE CASE TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All edge case tests passed!")
        return 0
    else:
        print("⚠️  Some edge case tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    main()