#!/usr/bin/env python3
"""
Error Debug Test - Capture specific error details
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

async def test_error_scenarios():
    """Test specific error scenarios"""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 DEBUGGING SPECIFIC ERROR SCENARIOS")
        print("=" * 50)
        
        # Test 1: Try to create program without assessment (should get 404)
        print("Test 1: Program creation without assessment")
        program_data = {
            "player_id": "Definitely Non Existent Player 12345",
            "program_name": "Test Program",
            "total_duration_weeks": 12,
            "program_objectives": ["Test objective"],
            "assessment_interval_weeks": 4,
            "training_frequency": 5
        }
        
        try:
            async with session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                print(f"Status: {response.status}")
                print(f"Response: {json.dumps(response_data, indent=2)}")
                print()
                
        except Exception as e:
            print(f"Exception: {str(e)}")
            print()
            
        # Test 2: Create assessment and then program (should work)
        print("Test 2: Normal flow - assessment then program")
        player_name = f"Debug Test Player {str(uuid.uuid4())[:8]}"
        
        assessment = {
            "player_name": player_name,
            "age": 17,
            "position": "Forward",
            "sprint_30m": 4.5,
            "yo_yo_test": 1600,
            "vo2_max": 55.0,
            "vertical_jump": 52,
            "body_fat": 12.0,
            "ball_control": 3,
            "passing_accuracy": 70.0,
            "dribbling_success": 65.0,
            "shooting_accuracy": 60.0,
            "defensive_duels": 55.0,
            "game_intelligence": 3,
            "positioning": 3,
            "decision_making": 4,
            "coachability": 4,
            "mental_toughness": 3
        }
        
        try:
            # Create assessment
            async with session.post(
                f"{BACKEND_URL}/assessments",
                json=assessment,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print("✅ Assessment created successfully")
                else:
                    print(f"❌ Assessment creation failed: {response.status}")
                    return
                    
            # Create program
            program_data = {
                "player_id": player_name,
                "program_name": "Debug Test Program",
                "total_duration_weeks": 12,
                "program_objectives": ["Debug test"],
                "assessment_interval_weeks": 4,
                "training_frequency": 5
            }
            
            async with session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=program_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                print(f"Program creation status: {response.status}")
                if response.status != 200:
                    print(f"Error response: {json.dumps(response_data, indent=2)}")
                else:
                    print("✅ Program created successfully")
                print()
                
        except Exception as e:
            print(f"Exception in normal flow: {str(e)}")
            print()
            
        # Test 3: Test with missing fields
        print("Test 3: Program creation with missing fields")
        incomplete_program = {
            "player_id": player_name,
            "program_name": "Incomplete Program"
            # Missing required fields
        }
        
        try:
            async with session.post(
                f"{BACKEND_URL}/periodized-programs",
                json=incomplete_program,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                print(f"Incomplete program status: {response.status}")
                print(f"Response: {json.dumps(response_data, indent=2)}")
                print()
                
        except Exception as e:
            print(f"Exception with incomplete data: {str(e)}")
            print()

if __name__ == "__main__":
    asyncio.run(test_error_scenarios())