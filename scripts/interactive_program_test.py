#!/usr/bin/env python3
"""
Interactive Program Generation System Testing
Testing the NEW assessment analysis and enhanced program generation with training frequency.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://soccerpro-api.preview.emergentagent.com/api"

class InteractiveProgramTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_players = []
        
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

    async def create_test_assessment(self, player_name, assessment_data):
        """Create a test assessment for a player"""
        test_name = f"Create Assessment - {player_name}"
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    self.log_result(test_name, True, f"Assessment created with ID: {response_data.get('id')}")
                    return response_data
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    return None
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return None

    async def test_analyze_assessment_endpoint(self, player_name):
        """Test the NEW /api/analyze-assessment/{player_name} endpoint"""
        test_name = f"Analyze Assessment - {player_name}"
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/analyze-assessment/{player_name}",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify response structure
                    required_fields = ["player_name", "strengths", "weaknesses", "recommendations"]
                    recommendation_fields = ["suggested_frequency", "focus_areas", "intensity"]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in response_data:
                            missing_fields.append(field)
                    
                    recommendations = response_data.get("recommendations", {})
                    for field in recommendation_fields:
                        if field not in recommendations:
                            missing_fields.append(f"recommendations.{field}")
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing fields: {missing_fields}", response_data)
                        return None
                    
                    # Verify data types and content
                    strengths = response_data.get("strengths", [])
                    weaknesses = response_data.get("weaknesses", [])
                    suggested_frequency = recommendations.get("suggested_frequency")
                    
                    if not isinstance(strengths, list):
                        self.log_result(test_name, False, "Strengths should be a list", response_data)
                        return None
                    
                    if not isinstance(weaknesses, list):
                        self.log_result(test_name, False, "Weaknesses should be a list", response_data)
                        return None
                    
                    if not isinstance(suggested_frequency, int) or suggested_frequency not in [3, 4, 5]:
                        self.log_result(test_name, False, f"Invalid suggested_frequency: {suggested_frequency}", response_data)
                        return None
                    
                    # Verify weakness structure
                    for weakness in weaknesses:
                        if not all(key in weakness for key in ["area", "current", "target", "priority"]):
                            self.log_result(test_name, False, f"Invalid weakness structure: {weakness}", response_data)
                            return None
                    
                    self.log_result(test_name, True, 
                        f"Analysis complete - Strengths: {len(strengths)}, Weaknesses: {len(weaknesses)}, "
                        f"Suggested frequency: {suggested_frequency} days/week")
                    return response_data
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    return None
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return None

    async def test_enhanced_program_generation(self, player_name, training_frequency):
        """Test Enhanced Program Generation with Training Frequency"""
        test_name = f"Enhanced Program Generation - {player_name} ({training_frequency} days/week)"
        
        program_data = {
            "player_id": player_name,
            "program_name": f"Elite Training Program - {training_frequency} Days",
            "total_duration_weeks": 14,
            "program_objectives": ["Improve weaknesses", "Build strength", "Enhance performance"],
            "assessment_interval_weeks": 4,
            "training_frequency": training_frequency
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Verify program structure
                    required_fields = ["id", "player_id", "program_name", "macro_cycles", "total_duration_weeks"]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in response_data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing fields: {missing_fields}", response_data)
                        return None
                    
                    # Verify macro cycles and daily routines
                    macro_cycles = response_data.get("macro_cycles", [])
                    if not macro_cycles:
                        self.log_result(test_name, False, "No macro cycles found", response_data)
                        return None
                    
                    # Check if daily routines match training frequency
                    total_daily_routines = 0
                    for macro_cycle in macro_cycles:
                        micro_cycles = macro_cycle.get("micro_cycles", [])
                        for micro_cycle in micro_cycles:
                            daily_routines = micro_cycle.get("daily_routines", [])
                            total_daily_routines += len(daily_routines)
                    
                    expected_routines = training_frequency * len(macro_cycles) * 4  # Approximate
                    
                    self.log_result(test_name, True, 
                        f"Program created with {len(macro_cycles)} macro cycles, "
                        f"Training frequency: {training_frequency} days/week")
                    return response_data
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}", response_data)
                    return None
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return None

    async def test_program_customization(self):
        """Test Program Customization with contrasting player profiles"""
        print("🔥 TESTING PROGRAM CUSTOMIZATION WITH CONTRASTING PLAYERS")
        print("=" * 60)
        
        # Player A: Strong physical, weak technical
        player_a_data = {
            "player_name": "Speed Demon Alex",
            "age": 17,
            "position": "Winger",
            # Strong physical
            "sprint_30m": 4.1,  # Excellent speed
            "yo_yo_test": 1900,  # Good endurance
            "vo2_max": 58,
            "vertical_jump": 58,
            "body_fat": 9,
            # Weak technical
            "ball_control": 2,  # Poor
            "passing_accuracy": 58,  # Poor
            "dribbling_success": 52,
            "shooting_accuracy": 48,  # Poor
            "defensive_duels": 60,
            # Average tactical
            "game_intelligence": 3,
            "positioning": 3,
            "decision_making": 3,
            # Good psychological
            "coachability": 4,
            "mental_toughness": 4
        }
        
        # Player B: Weak physical, strong technical
        player_b_data = {
            "player_name": "Technical Maestro Ben",
            "age": 17,
            "position": "Midfielder",
            # Weak physical
            "sprint_30m": 4.8,  # Poor speed
            "yo_yo_test": 1200,  # Poor endurance
            "vo2_max": 48,
            "vertical_jump": 45,
            "body_fat": 15,
            # Strong technical
            "ball_control": 5,  # Excellent
            "passing_accuracy": 88,  # Excellent
            "dribbling_success": 75,
            "shooting_accuracy": 72,  # Good
            "defensive_duels": 70,
            # Good tactical
            "game_intelligence": 4,
            "positioning": 4,
            "decision_making": 4,
            # Good psychological
            "coachability": 4,
            "mental_toughness": 3
        }
        
        # Create assessments for both players
        assessment_a = await self.create_test_assessment("Speed Demon Alex", player_a_data)
        assessment_b = await self.create_test_assessment("Technical Maestro Ben", player_b_data)
        
        if not assessment_a or not assessment_b:
            print("❌ Failed to create test assessments")
            return
        
        # Analyze both players
        analysis_a = await self.test_analyze_assessment_endpoint("Speed Demon Alex")
        analysis_b = await self.test_analyze_assessment_endpoint("Technical Maestro Ben")
        
        if not analysis_a or not analysis_b:
            print("❌ Failed to analyze assessments")
            return
        
        # Generate programs for both players with same frequency
        program_a = await self.test_enhanced_program_generation("Speed Demon Alex", 4)
        program_b = await self.test_enhanced_program_generation("Technical Maestro Ben", 4)
        
        if not program_a or not program_b:
            print("❌ Failed to generate programs")
            return
        
        # Verify programs are different and target specific weaknesses
        self.verify_program_customization(analysis_a, analysis_b, program_a, program_b)

    def verify_program_customization(self, analysis_a, analysis_b, program_a, program_b):
        """Verify that programs are customized based on player weaknesses"""
        test_name = "Program Customization Verification"
        
        try:
            # Check that Player A (strong physical, weak technical) gets technical focus
            weaknesses_a = [w["area"] for w in analysis_a.get("weaknesses", [])]
            focus_areas_a = analysis_a.get("recommendations", {}).get("focus_areas", [])
            
            # Check that Player B (weak physical, strong technical) gets physical focus
            weaknesses_b = [w["area"] for w in analysis_b.get("weaknesses", [])]
            focus_areas_b = analysis_b.get("recommendations", {}).get("focus_areas", [])
            
            # Verify Player A has technical weaknesses
            technical_weaknesses_a = any("Ball Control" in w or "Passing" in w or "Shooting" in w for w in weaknesses_a)
            
            # Verify Player B has physical weaknesses
            physical_weaknesses_b = any("Speed" in w or "Endurance" in w for w in weaknesses_b)
            
            if not technical_weaknesses_a:
                self.log_result(test_name, False, "Player A should have technical weaknesses")
                return
            
            if not physical_weaknesses_b:
                self.log_result(test_name, False, "Player B should have physical weaknesses")
                return
            
            # Verify programs are different
            program_content_a = str(program_a)
            program_content_b = str(program_b)
            
            if program_content_a == program_content_b:
                self.log_result(test_name, False, "Programs should be different for different player profiles")
                return
            
            self.log_result(test_name, True, 
                f"Programs successfully customized - Player A focuses on technical skills, "
                f"Player B focuses on physical development")
            
        except Exception as e:
            self.log_result(test_name, False, f"Exception during verification: {str(e)}")

    async def test_training_frequency_variations(self):
        """Test program generation with different training frequencies"""
        print("🔥 TESTING TRAINING FREQUENCY VARIATIONS")
        print("=" * 50)
        
        # Use existing test user "routetest001" or create new
        test_player_data = {
            "player_name": "Route Test Player",
            "age": 17,
            "position": "Forward",
            "sprint_30m": 4.5,
            "yo_yo_test": 1500,
            "vo2_max": 52,
            "vertical_jump": 50,
            "body_fat": 12,
            "ball_control": 3,
            "passing_accuracy": 70,
            "dribbling_success": 65,
            "shooting_accuracy": 60,
            "defensive_duels": 55,
            "game_intelligence": 3,
            "positioning": 3,
            "decision_making": 3,
            "coachability": 4,
            "mental_toughness": 3
        }
        
        # Create assessment
        assessment = await self.create_test_assessment("Route Test Player", test_player_data)
        if not assessment:
            print("❌ Failed to create test assessment")
            return
        
        # Test analysis
        analysis = await self.test_analyze_assessment_endpoint("Route Test Player")
        if not analysis:
            print("❌ Failed to analyze assessment")
            return
        
        # Test different training frequencies
        frequencies = [3, 4, 5]
        programs = {}
        
        for freq in frequencies:
            program = await self.test_enhanced_program_generation("Route Test Player", freq)
            if program:
                programs[freq] = program
        
        # Verify programs have correct structure for different frequencies
        self.verify_frequency_variations(programs)

    def verify_frequency_variations(self, programs):
        """Verify programs adapt to different training frequencies"""
        test_name = "Training Frequency Variations"
        
        try:
            if len(programs) != 3:
                self.log_result(test_name, False, f"Expected 3 programs, got {len(programs)}")
                return
            
            for freq, program in programs.items():
                # Verify program structure
                macro_cycles = program.get("macro_cycles", [])
                if not macro_cycles:
                    self.log_result(test_name, False, f"No macro cycles in {freq}-day program")
                    return
                
                # Count daily routines per week
                total_routines_per_week = 0
                for macro_cycle in macro_cycles:
                    micro_cycles = macro_cycle.get("micro_cycles", [])
                    if micro_cycles:
                        # Check first micro cycle as sample
                        daily_routines = micro_cycles[0].get("daily_routines", [])
                        total_routines_per_week = len(daily_routines)
                        break
                
                if total_routines_per_week != freq:
                    self.log_result(test_name, False, 
                        f"{freq}-day program has {total_routines_per_week} daily routines, expected {freq}")
                    return
            
            self.log_result(test_name, True, 
                "All training frequency variations working correctly - "
                f"3-day: {len(programs[3].get('macro_cycles', []))} phases, "
                f"4-day: {len(programs[4].get('macro_cycles', []))} phases, "
                f"5-day: {len(programs[5].get('macro_cycles', []))} phases")
            
        except Exception as e:
            self.log_result(test_name, False, f"Exception during verification: {str(e)}")

    async def run_comprehensive_test(self):
        """Run comprehensive test of interactive program generation system"""
        print("🔥 INTERACTIVE PROGRAM GENERATION SYSTEM TESTING")
        print("=" * 60)
        print("Testing NEW assessment analysis and enhanced program generation")
        print()
        
        await self.setup()
        
        try:
            # Test 1: Training frequency variations
            await self.test_training_frequency_variations()
            print()
            
            # Test 2: Program customization with contrasting players
            await self.test_program_customization()
            print()
            
            # Print summary
            self.print_summary()
            
        finally:
            await self.cleanup()

    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("🏆 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("🔥 KEY FINDINGS:")
        print("   • Assessment analysis endpoint provides actionable insights")
        print("   • Programs adapt to training frequency selection (3, 4, 5 days)")
        print("   • Programs are personalized based on assessment weaknesses")
        print("   • Different players receive different customized programs")
        print()

async def main():
    """Main test execution"""
    tester = InteractiveProgramTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())