"""
Migration Script: Convert Existing Assessments to Benchmarks
This ensures data persistence for existing users after the auto-save fix
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime, timezone

async def migrate_assessments():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    database_name = os.environ.get('DB_NAME', 'soccer_training_db')
    client = AsyncIOMotorClient(mongo_url)
    db = client[database_name]
    
    print("=" * 70)
    print("MIGRATION: Converting Assessments to Benchmarks")
    print("=" * 70)
    
    # Get all assessments
    assessments = await db.assessments.find().to_list(length=1000)
    print(f"\n📋 Found {len(assessments)} assessments to process")
    
    if len(assessments) == 0:
        print("✅ No assessments to migrate")
        client.close()
        return
    
    # Group assessments by player_name to identify baselines
    player_assessments = {}
    for assessment in assessments:
        player_name = assessment.get('player_name')
        if player_name:
            if player_name not in player_assessments:
                player_assessments[player_name] = []
            player_assessments[player_name].append(assessment)
    
    # Sort each player's assessments by date
    for player_name in player_assessments:
        player_assessments[player_name].sort(
            key=lambda x: x.get('created_at', x.get('assessment_date', '')))
    
    print(f"\n👥 Found {len(player_assessments)} unique players")
    
    # Check existing benchmarks to avoid duplicates
    existing_benchmarks = await db.benchmarks.find().to_list(length=1000)
    existing_assessment_ids = set(b.get('assessment_id') for b in existing_benchmarks if b.get('assessment_id'))
    
    print(f"\n📊 Existing benchmarks: {len(existing_benchmarks)}")
    print(f"   Assessment IDs already saved: {len(existing_assessment_ids)}")
    
    # Create benchmarks
    created_count = 0
    skipped_count = 0
    
    for player_name, assessments_list in player_assessments.items():
        print(f"\n👤 Processing {player_name}: {len(assessments_list)} assessment(s)")
        
        for idx, assessment in enumerate(assessments_list):
            assessment_id = assessment.get('id')
            
            # Skip if already exists as benchmark
            if assessment_id in existing_assessment_ids:
                print(f"   ⏭️  Skipping assessment {assessment_id} (already exists)")
                skipped_count += 1
                continue
            
            is_baseline = (idx == 0)  # First assessment is baseline
            
            try:
                benchmark_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": assessment.get('user_id'),  # May be None for old data
                    "player_name": player_name,
                    "assessment_id": assessment_id,
                    "age": assessment.get('age'),
                    "position": assessment.get('position'),
                    # Physical metrics
                    "sprint_30m": assessment.get('sprint_30m'),
                    "yo_yo_test": assessment.get('yo_yo_test'),
                    "vo2_max": assessment.get('vo2_max'),
                    "vertical_jump": assessment.get('vertical_jump'),
                    "body_fat": assessment.get('body_fat'),
                    # Technical metrics
                    "ball_control": assessment.get('ball_control'),
                    "passing_accuracy": assessment.get('passing_accuracy'),
                    "dribbling_success": assessment.get('dribbling_success'),
                    "shooting_accuracy": assessment.get('shooting_accuracy'),
                    "defensive_duels": assessment.get('defensive_duels'),
                    # Tactical metrics
                    "game_intelligence": assessment.get('game_intelligence'),
                    "positioning": assessment.get('positioning'),
                    "decision_making": assessment.get('decision_making'),
                    # Psychological metrics
                    "coachability": assessment.get('coachability'),
                    "mental_toughness": assessment.get('mental_toughness'),
                    # Calculated metrics
                    "overall_score": assessment.get('overall_score', 0),
                    "performance_level": "Average",  # Default
                    "is_baseline": is_baseline,
                    "benchmark_type": "baseline" if is_baseline else "regular",
                    "benchmark_date": assessment.get('created_at') or assessment.get('assessment_date') or datetime.now(timezone.utc).isoformat(),
                    "notes": f"Migrated from assessment on {datetime.now(timezone.utc).strftime('%Y-%m-%d')} {'(BASELINE)' if is_baseline else ''}"
                }
                
                await db.benchmarks.insert_one(benchmark_data)
                created_count += 1
                print(f"   ✅ Created benchmark for assessment {assessment_id} {'🏆 (BASELINE)' if is_baseline else ''}")
                
            except Exception as e:
                print(f"   ❌ Error creating benchmark for {assessment_id}: {e}")
    
    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print(f"✅ Created: {created_count} benchmarks")
    print(f"⏭️  Skipped: {skipped_count} (already existed)")
    print(f"📊 Total benchmarks now: {len(existing_benchmarks) + created_count}")
    print("\n💡 Users can now see their data after login!")
    
    client.close()

if __name__ == "__main__":
    print("\n🚀 Starting migration...")
    asyncio.run(migrate_assessments())
