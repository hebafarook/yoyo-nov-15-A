#!/usr/bin/env python3
"""
Comprehensive Training Program Testing
Testing various scenarios to ensure robustness
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://elite-soccer-ai-1.preview.emergentagent.com/api"

class ComprehensiveProgramTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
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
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
        
    async def test_program_creation_without_assessment(self):
        """Test program creation for non-existent player"""
        test_name = "Program Creation - No Assessment"
        
        program_data = {
            "player_id": "Non Existent Player",
            "program_name": "Test Program",
            "total_duration_weeks": 12,
            "program_objectives": ["Test objective"],
            "assessment_interval_weeks": 4,
            "training_frequency": 5
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 404:
                    self.log_result(test_name, True, "Correctly returned 404 for non-existent player")
                else:
                    self.log_result(test_name, False, f"Expected 404, got {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_multiple_assessments_same_player(self):
        """Test program creation with multiple assessments for same player"""
        test_name = "Multiple Assessments - Same Player"
        
        player_name = f"Multi Test Player {str(uuid.uuid4())[:8]}"
        
        # Create first assessment
        assessment1 = {
            "player_name": player_name,
            "age": 16,
            "position": "Midfielder",
            "sprint_30m": 4.8,
            "yo_yo_test": 1400,
            "vo2_max": 52.0,
            "vertical_jump": 48,
            "body_fat": 14.0,
            "ball_control": 2,
            "passing_accuracy": 60.0,
            "dribbling_success": 55.0,
            "shooting_accuracy": 50.0,
            "defensive_duels": 50.0,
            "game_intelligence": 2,
            "positioning": 2,
            "decision_making": 3,
            "coachability": 3,
            "mental_toughness": 2
        }
        
        # Create second assessment (improved)
        assessment2 = {
            "player_name": player_name,
            "age": 16,
            "position": "Midfielder",
            "sprint_30m": 4.4,
            "yo_yo_test": 1600,
            "vo2_max": 55.0,
            "vertical_jump": 52,
            "body_fat": 12.0,
            "ball_control": 4,
            "passing_accuracy": 75.0,
            "dribbling_success": 70.0,
            "shooting_accuracy": 65.0,
            "defensive_duels": 65.0,
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            "coachability": 4,
            "mental_toughness": 4
        }
        
        try:
            # Create first assessment
            async with self.session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment1,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, "Failed to create first assessment")
                    return
                    
            # Wait a moment
            await asyncio.sleep(0.5)
            
            # Create second assessment
            async with self.session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment2,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, "Failed to create second assessment")
                    return
                    
            # Now try to create program - should use latest assessment
            program_data = {
                "player_id": player_name,
                "program_name": "Multi Assessment Program",
                "total_duration_weeks": 14,
                "program_objectives": ["Improve based on latest assessment"],
                "assessment_interval_weeks": 4,
                "training_frequency": 4
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.log_result(test_name, True, f"Program created successfully using latest assessment")
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_program_retrieval(self):
        """Test retrieving existing programs"""
        test_name = "Program Retrieval"
        
        # Create a test player and assessment first
        player_name = f"Retrieval Test Player {str(uuid.uuid4())[:8]}"
        
        assessment = {
            "player_name": player_name,
            "age": 18,
            "position": "Defender",
            "sprint_30m": 4.2,
            "yo_yo_test": 1800,
            "vo2_max": 58.0,
            "vertical_jump": 55,
            "body_fat": 10.0,
            "ball_control": 4,
            "passing_accuracy": 80.0,
            "dribbling_success": 65.0,
            "shooting_accuracy": 55.0,
            "defensive_duels": 75.0,
            "game_intelligence": 4,
            "positioning": 5,
            "decision_making": 4,
            "coachability": 5,
            "mental_toughness": 4
        }
        
        try:
            # Create assessment
            async with self.session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, "Failed to create assessment")
                    return
                    
            # Create program
            program_data = {
                "player_id": player_name,
                "program_name": "Retrieval Test Program",
                "total_duration_weeks": 16,
                "program_objectives": ["Test retrieval"],
                "assessment_interval_weeks": 4,
                "training_frequency": 5
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, "Failed to create program")
                    return
                    
            # Now retrieve the program
            async with self.session.get(
                f"{BACKEND_URL}/periodized-programs/{player_name}",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data:
                    if response_data.get("player_id") == player_name:
                        self.log_result(test_name, True, f"Program retrieved successfully for {player_name}")
                    else:
                        self.log_result(test_name, False, "Player ID mismatch in retrieved program", response_data)
                else:
                    self.log_result(test_name, False, f"HTTP {response.status} or null response", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_assessment_analysis_edge_cases(self):
        """Test assessment analysis with edge case data"""
        test_name = "Assessment Analysis - Edge Cases"
        
        # Create assessment with extreme values
        player_name = f"Edge Case Player {str(uuid.uuid4())[:8]}"
        
        assessment = {
            "player_name": player_name,
            "age": 12,  # Minimum age
            "position": "Goalkeeper",
            "sprint_30m": 6.0,  # Very slow
            "yo_yo_test": 800,   # Very low endurance
            "vo2_max": 40.0,     # Low VO2
            "vertical_jump": 25, # Low jump
            "body_fat": 20.0,    # High body fat
            "ball_control": 1,   # Minimum skill
            "passing_accuracy": 30.0,  # Very low
            "dribbling_success": 25.0,
            "shooting_accuracy": 20.0,
            "defensive_duels": 30.0,
            "game_intelligence": 1,
            "positioning": 1,
            "decision_making": 1,
            "coachability": 1,
            "mental_toughness": 1
        }
        
        try:
            # Create assessment
            async with self.session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_result(test_name, False, "Failed to create edge case assessment")
                    return
                    
            # Get analysis
            async with self.session.get(
                f"{BACKEND_URL}/analyze-assessment/{player_name}",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Should have many weaknesses and appropriate recommendations
                    weaknesses = response_data.get("weaknesses", [])
                    recommendations = response_data.get("recommendations", {})
                    
                    if len(weaknesses) > 5 and "program_duration" in recommendations:
                        self.log_result(test_name, True, f"Analysis handled edge case correctly with {len(weaknesses)} weaknesses identified")
                    else:
                        self.log_result(test_name, False, "Analysis didn't properly identify weaknesses", response_data)
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            
    async def test_program_with_different_frequencies(self):
        """Test program creation with different training frequencies"""
        test_name = "Program Creation - Different Frequencies"
        
        frequencies = [3, 4, 5]
        success_count = 0
        
        for freq in frequencies:
            player_name = f"Freq Test Player {freq}d {str(uuid.uuid4())[:8]}"
            
            # Create assessment
            assessment = {
                "player_name": player_name,
                "age": 15,
                "position": "Winger",
                "sprint_30m": 4.6,
                "yo_yo_test": 1500,
                "vo2_max": 53.0,
                "vertical_jump": 50,
                "body_fat": 13.0,
                "ball_control": 3,
                "passing_accuracy": 68.0,
                "dribbling_success": 72.0,
                "shooting_accuracy": 58.0,
                "defensive_duels": 45.0,
                "game_intelligence": 3,
                "positioning": 3,
                "decision_making": 3,
                "coachability": 4,
                "mental_toughness": 3
            }
            
            try:
                # Create assessment
                async with self.session.post(
                    f"{BACKEND_URL}/assessments",
                    json=assessment,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        continue
                        
                # Create program with specific frequency
                program_data = {
                    "player_id": player_name,
                    "program_name": f"Frequency Test Program {freq}d",
                    "total_duration_weeks": 12,
                    "program_objectives": [f"Test {freq} days per week"],
                    "assessment_interval_weeks": 4,
                    "training_frequency": freq
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/periodized-programs",
                    json=program_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        success_count += 1
                        
            except Exception:
                continue
                
        if success_count == len(frequencies):
            self.log_result(test_name, True, f"All {len(frequencies)} frequency variations worked")
        else:
            self.log_result(test_name, False, f"Only {success_count}/{len(frequencies)} frequencies worked")
            
    async def run_all_tests(self):
        """Run all comprehensive training program tests"""
        print("🔥 COMPREHENSIVE TRAINING PROGRAM TESTING 🔥")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now()}")
        print("=" * 60)
        print()
        
        await self.setup()
        
        try:
            await self.test_program_creation_without_assessment()
            await self.test_multiple_assessments_same_player()
            await self.test_program_retrieval()
            await self.test_assessment_analysis_edge_cases()
            await self.test_program_with_different_frequencies()
            
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
    tester = ComprehensiveProgramTester()
    passed, failed = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())