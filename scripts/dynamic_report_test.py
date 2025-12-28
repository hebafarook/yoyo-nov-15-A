#!/usr/bin/env python3
"""
Dynamic Player Report Endpoint Testing
Tests the new GET /api/reports/generate-dynamic/{player_name} endpoint
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone
import uuid

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://soccerpro-api.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DynamicReportTester:
    def __init__(self):
        self.session = None
        self.test_user_token = None
        self.test_player_name = "Flow Test Player"  # Use existing player name
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    async def register_test_user(self):
        """Register a test user for authentication"""
        try:
            unique_id = str(uuid.uuid4())[:8]
            test_data = {
                "username": f"reporttest{unique_id}",
                "email": f"reporttest{unique_id}@test.com",
                "password": "testpass123",
                "full_name": "Report Test User",
                "role": "player",
                "age": 17,
                "position": "Forward"
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=test_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_user_token = data.get('access_token')
                    self.log_test("User Registration", True, f"Registered user: {test_data['username']}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("User Registration", False, f"Status: {response.status}, Error: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False
            
    async def create_test_assessment(self):
        """Create a test assessment for the player with proper user_id"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Create assessment first
            create_data = {
                "player_name": self.test_player_name,
                "age": 17,
                "position": "Forward",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "assessment_date": datetime.now(timezone.utc).isoformat(),
                # Physical metrics
                "sprint_30m": 4.3,
                "yo_yo_test": 1650,
                "vo2_max": 56.5,
                "vertical_jump": 48,
                "body_fat": 11.2,
                # Technical metrics
                "ball_control": 4,
                "passing_accuracy": 78.5,
                "dribbling_success": 65.0,
                "shooting_accuracy": 68.0,
                "defensive_duels": 72.0,
                # Tactical metrics
                "game_intelligence": 4,
                "positioning": 3,
                "decision_making": 4,
                # Psychological metrics
                "coachability": 5,
                "mental_toughness": 4
            }
            
            async with self.session.post(f"{API_BASE}/assessments/authenticated", json=create_data, headers=headers) as response:
                if response.status == 200:
                    assessment_data = await response.json()
                    self.log_test("Assessment Creation", True, f"Created authenticated assessment for {self.test_player_name}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Assessment Creation", False, f"Status: {response.status}, Error: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Assessment Creation", False, f"Exception: {str(e)}")
            return False
            
    async def test_dynamic_report_endpoint(self):
        """Test the main dynamic report endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            async with self.session.get(f"{API_BASE}/reports/generate-dynamic/{self.test_player_name}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify required fields
                    required_fields = [
                        'success', 'player_name', 'age', 'position', 'overall_score',
                        'performance_level', 'metrics', 'trend', 'strengths', 'weaknesses', 'recommendations'
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        self.log_test("Dynamic Report Endpoint - Required Fields", False, f"Missing fields: {missing_fields}")
                        return False
                    else:
                        self.log_test("Dynamic Report Endpoint - Required Fields", True, "All required fields present")
                    
                    # Verify success field
                    if data.get('success') == True:
                        self.log_test("Dynamic Report Endpoint - Success Field", True, "success: true")
                    else:
                        self.log_test("Dynamic Report Endpoint - Success Field", False, f"success: {data.get('success')}")
                    
                    # Verify player data
                    if data.get('player_name') == self.test_player_name and data.get('age') == 17 and data.get('position') == "Forward":
                        self.log_test("Dynamic Report Endpoint - Player Data", True, f"Player: {data.get('player_name')}, Age: {data.get('age')}, Position: {data.get('position')}")
                    else:
                        self.log_test("Dynamic Report Endpoint - Player Data", False, f"Incorrect player data")
                    
                    # Verify overall score
                    overall_score = data.get('overall_score')
                    if isinstance(overall_score, (int, float)) and overall_score > 0:
                        self.log_test("Dynamic Report Endpoint - Overall Score", True, f"Overall score: {overall_score}")
                    else:
                        self.log_test("Dynamic Report Endpoint - Overall Score", False, f"Invalid overall score: {overall_score}")
                    
                    # Verify performance level
                    performance_level = data.get('performance_level')
                    valid_levels = ['Elite', 'Advanced', 'Standard', 'Needs Development']
                    if performance_level in valid_levels:
                        self.log_test("Dynamic Report Endpoint - Performance Level", True, f"Performance level: {performance_level}")
                    else:
                        self.log_test("Dynamic Report Endpoint - Performance Level", False, f"Invalid performance level: {performance_level}")
                    
                    # Verify metrics object
                    metrics = data.get('metrics', {})
                    required_metrics = ['sprint_30m', 'agility', 'reaction_time', 'endurance', 'ball_control', 'passing_accuracy']
                    
                    missing_metrics = []
                    for metric in required_metrics:
                        if metric not in metrics:
                            missing_metrics.append(metric)
                    
                    if missing_metrics:
                        self.log_test("Dynamic Report Endpoint - Metrics Object", False, f"Missing metrics: {missing_metrics}")
                    else:
                        self.log_test("Dynamic Report Endpoint - Metrics Object", True, "All 6 required metrics present")
                    
                    # Verify each metric has score and percent_of_standard
                    metrics_valid = True
                    for metric_name, metric_data in metrics.items():
                        if not isinstance(metric_data, dict):
                            metrics_valid = False
                            break
                        
                        # Check for score field (different naming conventions)
                        has_score = any(key in metric_data for key in ['score', 'score_ms', 'score_1_to_10', 'score_percent'])
                        has_percent = 'percent_of_standard' in metric_data
                        
                        if not (has_score and has_percent):
                            metrics_valid = False
                            break
                    
                    if metrics_valid:
                        self.log_test("Dynamic Report Endpoint - Metric Structure", True, "All metrics have score and percent_of_standard")
                    else:
                        self.log_test("Dynamic Report Endpoint - Metric Structure", False, "Some metrics missing score or percent_of_standard")
                    
                    # Verify trend object
                    trend = data.get('trend', {})
                    required_trend_fields = ['dates', 'overall_scores', 'sprint_30m_scores', 'passing_accuracy_scores']
                    
                    missing_trend_fields = []
                    for field in required_trend_fields:
                        if field not in trend:
                            missing_trend_fields.append(field)
                    
                    if missing_trend_fields:
                        self.log_test("Dynamic Report Endpoint - Trend Object", False, f"Missing trend fields: {missing_trend_fields}")
                    else:
                        self.log_test("Dynamic Report Endpoint - Trend Object", True, "All trend fields present")
                    
                    # Verify AI analysis arrays
                    strengths = data.get('strengths', [])
                    weaknesses = data.get('weaknesses', [])
                    recommendations = data.get('recommendations', [])
                    
                    if isinstance(strengths, list) and len(strengths) >= 3:
                        self.log_test("Dynamic Report Endpoint - Strengths Array", True, f"Strengths: {len(strengths)} items")
                    else:
                        self.log_test("Dynamic Report Endpoint - Strengths Array", False, f"Invalid strengths array: {len(strengths) if isinstance(strengths, list) else 'not a list'}")
                    
                    if isinstance(weaknesses, list) and len(weaknesses) >= 2:
                        self.log_test("Dynamic Report Endpoint - Weaknesses Array", True, f"Weaknesses: {len(weaknesses)} items")
                    else:
                        self.log_test("Dynamic Report Endpoint - Weaknesses Array", False, f"Invalid weaknesses array: {len(weaknesses) if isinstance(weaknesses, list) else 'not a list'}")
                    
                    if isinstance(recommendations, list) and 4 <= len(recommendations) <= 6:
                        self.log_test("Dynamic Report Endpoint - Recommendations Array", True, f"Recommendations: {len(recommendations)} items")
                    else:
                        self.log_test("Dynamic Report Endpoint - Recommendations Array", False, f"Invalid recommendations array: {len(recommendations) if isinstance(recommendations, list) else 'not a list'}")
                    
                    # Print sample data for verification
                    print(f"\n📊 SAMPLE REPORT DATA:")
                    print(f"Player: {data.get('player_name')} (Age: {data.get('age')}, Position: {data.get('position')})")
                    print(f"Overall Score: {data.get('overall_score')}")
                    print(f"Performance Level: {data.get('performance_level')}")
                    print(f"Metrics Count: {len(metrics)}")
                    print(f"Trend Data Points: {len(trend.get('dates', []))}")
                    print(f"Strengths: {len(strengths)}")
                    print(f"Weaknesses: {len(weaknesses)}")
                    print(f"Recommendations: {len(recommendations)}")
                    
                    return True
                    
                else:
                    error_text = await response.text()
                    self.log_test("Dynamic Report Endpoint", False, f"Status: {response.status}, Error: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Dynamic Report Endpoint", False, f"Exception: {str(e)}")
            return False
            
    async def test_no_assessment_scenario(self):
        """Test endpoint with player that has no assessment"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            non_existent_player = "Non Existent Player"
            
            async with self.session.get(f"{API_BASE}/reports/generate-dynamic/{non_existent_player}", headers=headers) as response:
                if response.status == 404:
                    self.log_test("No Assessment Scenario", True, "Correctly returns 404 for non-existent player")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("No Assessment Scenario", False, f"Expected 404, got {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("No Assessment Scenario", False, f"Exception: {str(e)}")
            return False
            
    async def test_unauthorized_access(self):
        """Test endpoint without authentication"""
        try:
            async with self.session.get(f"{API_BASE}/reports/generate-dynamic/{self.test_player_name}") as response:
                if response.status == 401:
                    self.log_test("Unauthorized Access", True, "Correctly returns 401 without authentication")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Unauthorized Access", False, f"Expected 401, got {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Unauthorized Access", False, f"Exception: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING DYNAMIC PLAYER REPORT ENDPOINT TESTING")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Setup phase
            if not await self.register_test_user():
                print("❌ Cannot proceed without user registration")
                return
                
            if not await self.create_test_assessment():
                print("❌ Cannot proceed without assessment data")
                return
            
            # Main tests
            await self.test_dynamic_report_endpoint()
            await self.test_no_assessment_scenario()
            await self.test_unauthorized_access()
            
        finally:
            await self.cleanup_session()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 ENDPOINT STATUS: {'✅ WORKING' if passed_tests >= total_tests * 0.8 else '❌ NEEDS ATTENTION'}")

async def main():
    """Main test execution"""
    tester = DynamicReportTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())