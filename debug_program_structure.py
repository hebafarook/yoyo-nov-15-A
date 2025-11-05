#!/usr/bin/env python3
"""
Debug Program Structure
Investigate the structure of generated programs to understand the total training days issue
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend .env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.split('=', 1)[1].strip()
            break
    else:
        BACKEND_URL = "http://localhost:8001"

API_BASE = f"{BACKEND_URL}/api"

async def debug_program_structure():
    """Debug the structure of a generated program"""
    session = aiohttp.ClientSession()
    
    try:
        # Register user
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"debug{unique_id}",
            "email": f"debug{unique_id}@test.com", 
            "password": "test123",
            "full_name": "Debug User",
            "role": "player",
            "age": 18,
            "position": "Midfielder"
        }
        
        async with session.post(f"{API_BASE}/auth/register", json=user_data) as response:
            if response.status != 200:
                print("Failed to register user")
                return
            data = await response.json()
            jwt_token = data.get("access_token")
        
        # Create assessment
        assessment_data = {
            "player_name": "Debug Player",
            "age": 18,
            "position": "Midfielder",
            "sprint_30m": 4.2, "yo_yo_test": 1700, "vo2_max": 57.0, "vertical_jump": 52, "body_fat": 11.0,
            "ball_control": 3, "passing_accuracy": 75.0, "dribbling_success": 65.0, "shooting_accuracy": 60.0, "defensive_duels": 70.0,
            "game_intelligence": 3, "positioning": 3, "decision_making": 3,
            "coachability": 4, "mental_toughness": 4
        }
        
        async with session.post(f"{API_BASE}/assessments", json=assessment_data) as response:
            if response.status != 200:
                print("Failed to create assessment")
                return
        
        # Create 3-day program
        program_data = {
            "player_id": "Debug Player",
            "program_name": "Debug 3-Day Program",
            "total_duration_weeks": 12,
            "program_objectives": ["Debug test"],
            "training_frequency": 3
        }
        
        async with session.post(f"{API_BASE}/periodized-programs", json=program_data) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"Failed to create program: {error_text}")
                return
            
            program = await response.json()
            
            print("🔍 PROGRAM STRUCTURE ANALYSIS")
            print("=" * 50)
            
            # Analyze macro cycles
            macro_cycles = program.get("macro_cycles", [])
            print(f"Total Macro Cycles: {len(macro_cycles)}")
            
            total_weeks = 0
            total_days = 0
            
            for i, macro in enumerate(macro_cycles):
                print(f"\nMacro Cycle {i+1}: {macro.get('name', 'Unknown')}")
                print(f"  Duration: {macro.get('duration_weeks', 0)} weeks")
                
                micro_cycles = macro.get("micro_cycles", [])
                print(f"  Micro Cycles: {len(micro_cycles)}")
                
                for j, micro in enumerate(micro_cycles):
                    daily_routines = micro.get("daily_routines", [])
                    print(f"    Week {j+1}: {len(daily_routines)} daily routines")
                    total_weeks += 1
                    total_days += len(daily_routines)
                    
                    # Show day numbers for first few weeks
                    if j < 3:
                        day_numbers = [routine.get("day_number") for routine in daily_routines]
                        print(f"      Day numbers: {day_numbers}")
            
            print(f"\n📊 TOTALS:")
            print(f"Total Weeks: {total_weeks}")
            print(f"Total Training Days: {total_days}")
            print(f"Expected for 12 weeks × 3 days: {12 * 3}")
            print(f"Difference: {total_days - (12 * 3)}")
            
            # Check if week 5 exists
            if len(macro_cycles) > 0 and len(macro_cycles[0].get("micro_cycles", [])) >= 5:
                week_5 = macro_cycles[0]["micro_cycles"][4]
                week_5_routines = week_5.get("daily_routines", [])
                print(f"\n✅ Week 5 found: {len(week_5_routines)} daily routines")
            else:
                print(f"\n❌ Week 5 not found in first macro cycle")
                if len(macro_cycles) > 0:
                    first_macro_weeks = len(macro_cycles[0].get("micro_cycles", []))
                    print(f"   First macro cycle has {first_macro_weeks} weeks")
            
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(debug_program_structure())