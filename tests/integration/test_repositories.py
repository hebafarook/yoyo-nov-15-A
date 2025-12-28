"""Integration tests for repository layer."""

import pytest
import os
from motor.motor_asyncio import AsyncIOMotorClient
from repositories.user_repository import UserRepository
from repositories.assessment_repository import AssessmentRepository
from datetime import datetime


@pytest.fixture(scope="module")
async def test_db():
    """Setup test database connection."""
    # Use test database
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['test_soccer_db']
    
    yield db
    
    # Cleanup: Drop test database
    await client.drop_database('test_soccer_db')
    client.close()


@pytest.mark.integration
@pytest.mark.database
class TestUserRepository:
    """Integration tests for UserRepository."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, test_db):
        """Test creating a user in database."""
        # Override repository collection to use test db
        repo = UserRepository()
        original_collection = repo.collection
        repo.collection = test_db.users
        
        try:
            user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'full_name': 'Test User',
                'hashed_password': 'hashed',
                'role': 'player',
                'is_active': True
            }
            
            created_user = await repo.create(user_data)
            
            # Verify user was created
            assert created_user['username'] == 'testuser'
            assert 'id' in created_user
            
            # Verify user exists in database
            found_user = await repo.find_by_email('test@example.com')
            assert found_user is not None
            assert found_user['username'] == 'testuser'
        
        finally:
            repo.collection = original_collection
    
    @pytest.mark.asyncio
    async def test_find_by_email(self, test_db):
        """Test finding user by email."""
        repo = UserRepository()
        original_collection = repo.collection
        repo.collection = test_db.users
        
        try:
            # Create a user
            await repo.create({
                'username': 'emailtest',
                'email': 'emailtest@example.com',
                'full_name': 'Email Test',
                'hashed_password': 'hashed',
                'role': 'player'
            })
            
            # Find by email
            user = await repo.find_by_email('emailtest@example.com')
            assert user is not None
            assert user['username'] == 'emailtest'
            
            # Try non-existent email
            user = await repo.find_by_email('nonexistent@example.com')
            assert user is None
        
        finally:
            repo.collection = original_collection
    
    @pytest.mark.asyncio
    async def test_is_email_taken(self, test_db):
        """Test checking if email is taken."""
        repo = UserRepository()
        original_collection = repo.collection
        repo.collection = test_db.users
        
        try:
            # Email should not be taken initially
            is_taken = await repo.is_email_taken('unique@example.com')
            assert is_taken is False
            
            # Create user with that email
            await repo.create({
                'username': 'uniqueuser',
                'email': 'unique@example.com',
                'full_name': 'Unique User',
                'hashed_password': 'hashed',
                'role': 'player'
            })
            
            # Now email should be taken
            is_taken = await repo.is_email_taken('unique@example.com')
            assert is_taken is True
        
        finally:
            repo.collection = original_collection


@pytest.mark.integration
@pytest.mark.database
class TestAssessmentRepository:
    """Integration tests for AssessmentRepository."""
    
    @pytest.mark.asyncio
    async def test_create_assessment(self, test_db):
        """Test creating an assessment."""
        repo = AssessmentRepository()
        original_collection = repo.collection
        repo.collection = test_db.benchmarks
        
        try:
            assessment_data = {
                'user_id': 'user123',
                'player_name': 'Test Player',
                'age': 17,
                'position': 'Forward',
                'sprint_30m': 4.2,
                'ball_control': 4,
                'assessment_date': datetime.now().isoformat(),
                'is_baseline': True
            }
            
            created = await repo.create(assessment_data)
            assert created['player_name'] == 'Test Player'
            assert 'id' in created
        
        finally:
            repo.collection = original_collection
    
    @pytest.mark.asyncio
    async def test_find_by_user(self, test_db):
        """Test finding assessments by user."""
        repo = AssessmentRepository()
        original_collection = repo.collection
        repo.collection = test_db.benchmarks
        
        try:
            user_id = 'testuser456'
            
            # Create multiple assessments for user
            for i in range(3):
                await repo.create({
                    'user_id': user_id,
                    'player_name': 'Test Player',
                    'age': 17,
                    'position': 'Forward',
                    'sprint_30m': 4.2 + (i * 0.1),
                    'assessment_date': datetime.now().isoformat()
                })
            
            # Find assessments
            assessments = await repo.find_by_user(user_id)
            assert len(assessments) == 3
        
        finally:
            repo.collection = original_collection
    
    @pytest.mark.asyncio
    async def test_count_user_assessments(self, test_db):
        """Test counting user assessments."""
        repo = AssessmentRepository()
        original_collection = repo.collection
        repo.collection = test_db.benchmarks
        
        try:
            user_id = 'countuser789'
            
            # Initially should be 0
            count = await repo.count_user_assessments(user_id)
            assert count == 0
            
            # Create assessments
            for i in range(5):
                await repo.create({
                    'user_id': user_id,
                    'player_name': 'Count Test',
                    'age': 17,
                    'position': 'Midfielder',
                    'assessment_date': datetime.now().isoformat()
                })
            
            # Count should be 5
            count = await repo.count_user_assessments(user_id)
            assert count == 5
        
        finally:
            repo.collection = original_collection
