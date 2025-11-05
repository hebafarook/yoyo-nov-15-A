"""
Migration Script: Link Existing Programs to Users
Links programs to users via benchmarks (which have user_id)
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def link_programs_to_users():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    database_name = os.environ.get('DB_NAME', 'soccer_training_db')
    client = AsyncIOMotorClient(mongo_url)
    db = client[database_name]
    
    print("=" * 70)
    print("LINKING PROGRAMS TO USERS VIA BENCHMARKS")
    print("=" * 70)
    
    # Get all benchmarks with user_id
    benchmarks = await db.benchmarks.find({"user_id": {"$ne": None}}).to_list(length=1000)
    
    # Create mapping: player_name -> user_id
    player_to_user = {}
    for benchmark in benchmarks:
        player_name = benchmark.get('player_name')
        user_id = benchmark.get('user_id')
        if player_name and user_id:
            if player_name not in player_to_user:
                player_to_user[player_name] = user_id
    
    print(f"\n📊 Found {len(player_to_user)} players with user_id linkage")
    
    # Get all programs without user_id
    programs = await db.periodized_programs.find({"user_id": None}).to_list(length=1000)
    
    print(f"📋 Found {len(programs)} programs without user_id")
    
    linked_count = 0
    no_link_count = 0
    
    for program in programs:
        player_id = program.get('player_id')
        
        if player_id in player_to_user:
            user_id = player_to_user[player_id]
            
            # Update program with user_id
            await db.periodized_programs.update_one(
                {'_id': program['_id']},
                {'$set': {'user_id': user_id}}
            )
            
            print(f"✅ Linked program for {player_id} to user {user_id}")
            linked_count += 1
        else:
            print(f"⚠️  No user found for player: {player_id}")
            no_link_count += 1
    
    print("\n" + "=" * 70)
    print("LINKAGE COMPLETE")
    print("=" * 70)
    print(f"✅ Linked: {linked_count} programs")
    print(f"⚠️  Not linked: {no_link_count} programs (no user found)")
    
    client.close()

if __name__ == "__main__":
    print("\n🚀 Starting program-user linkage...")
    asyncio.run(link_programs_to_users())
