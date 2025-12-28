"""
Admin Drills Unit Tests
=======================

Tests for admin drill upload functionality:
- Authentication: 401 for no token, 403 for non-admin, 200 for admin
- Upload validation and upsert behavior
- Provider fallback logic
- Stats and list endpoints
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
import jwt
from datetime import datetime, timedelta
import os

# Test fixtures
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-here')
ALGORITHM = "HS256"


def create_test_token(user_id: str, username: str, role: str) -> str:
    """Create a JWT token for testing."""
    payload = {
        'sub': user_id,
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_admin_token():
    """Get an admin JWT token."""
    return create_test_token("admin-user-123", "admin_user", "admin")


def get_player_token():
    """Get a player (non-admin) JWT token."""
    return create_test_token("player-user-456", "player_user", "player")


def get_coach_token():
    """Get a coach (non-admin) JWT token."""
    return create_test_token("coach-user-789", "coach_user", "coach")


# =============================================================================
# DRILL MODELS TESTS
# =============================================================================

class TestDrillModels:
    """Tests for drill Pydantic models."""
    
    def test_drill_item_required_fields(self):
        """Test that DrillItem requires drill_id, name, and section."""
        from models.drill_models import DrillItem
        
        # Valid drill
        drill = DrillItem(
            drill_id="test_drill_1",
            name="Test Drill",
            section="technical"
        )
        assert drill.drill_id == "test_drill_1"
        assert drill.name == "Test Drill"
        assert drill.section == "technical"
    
    def test_drill_item_section_validation(self):
        """Test that section must be one of the valid values."""
        from models.drill_models import DrillItem
        from pydantic import ValidationError
        
        # Valid sections
        valid_sections = [
            "technical", "tactical", "possession", "speed_agility",
            "cardio", "gym", "mobility", "recovery", "prehab"
        ]
        
        for section in valid_sections:
            drill = DrillItem(
                drill_id=f"drill_{section}",
                name=f"{section} drill",
                section=section
            )
            assert drill.section == section
        
        # Invalid section should raise error
        with pytest.raises(ValidationError):
            DrillItem(
                drill_id="invalid_drill",
                name="Invalid Drill",
                section="invalid_section"
            )
    
    def test_drill_item_optional_fields(self):
        """Test optional fields with defaults."""
        from models.drill_models import DrillItem
        
        drill = DrillItem(
            drill_id="test_drill_2",
            name="Test Drill",
            section="tactical"
        )
        
        # Check defaults
        assert drill.tags == []
        assert drill.age_min is None
        assert drill.age_max is None
        assert drill.sex == "any"
        assert drill.positions == ["any"]
        assert drill.intensity is None
        assert drill.equipment == []
        assert drill.coaching_points == []
        assert drill.contraindications == []
        assert drill.is_active is True
    
    def test_drill_item_age_range_validation(self):
        """Test that age_max must be >= age_min."""
        from models.drill_models import DrillItem
        from pydantic import ValidationError
        
        # Valid age range
        drill = DrillItem(
            drill_id="age_drill",
            name="Age Drill",
            section="technical",
            age_min=10,
            age_max=18
        )
        assert drill.age_min == 10
        assert drill.age_max == 18
        
        # Invalid age range (max < min)
        with pytest.raises(ValidationError):
            DrillItem(
                drill_id="invalid_age",
                name="Invalid Age",
                section="technical",
                age_min=18,
                age_max=10
            )
    
    def test_drill_upload_request_unique_ids(self):
        """Test that DrillUploadRequest rejects duplicate drill_ids."""
        from models.drill_models import DrillUploadRequest, DrillItem
        from pydantic import ValidationError
        
        # Valid - unique IDs
        request = DrillUploadRequest(drills=[
            DrillItem(drill_id="drill_1", name="Drill 1", section="technical"),
            DrillItem(drill_id="drill_2", name="Drill 2", section="tactical")
        ])
        assert len(request.drills) == 2
        
        # Invalid - duplicate IDs
        with pytest.raises(ValidationError) as exc_info:
            DrillUploadRequest(drills=[
                DrillItem(drill_id="drill_dup", name="Drill 1", section="technical"),
                DrillItem(drill_id="drill_dup", name="Drill 2", section="tactical")
            ])
        assert "Duplicate drill_ids" in str(exc_info.value)


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

class TestAdminDrillsAuth:
    """Tests for admin drills authentication."""
    
    @pytest.fixture
    def app(self):
        """Create test app with admin drills router."""
        from fastapi import FastAPI
        from routes.admin_drills_routes import router
        
        app = FastAPI()
        app.include_router(router, prefix="/api")
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_upload_without_token_returns_401(self, client):
        """Test that upload without token returns 401."""
        response = client.post(
            "/api/admin/drills/upload",
            json={"drills": []}
        )
        # FastAPI returns 403 for missing credentials with HTTPBearer
        assert response.status_code in [401, 403]
    
    def test_upload_with_invalid_token_returns_401(self, client):
        """Test that upload with invalid token returns 401."""
        response = client.post(
            "/api/admin/drills/upload",
            json={"drills": []},
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    @patch('routes.admin_drills_routes.verify_token')
    def test_upload_with_non_admin_token_returns_403(self, mock_verify, client):
        """Test that upload with non-admin token returns 403."""
        # Mock verify_token to return non-admin user
        mock_verify.return_value = {
            'user_id': 'player-123',
            'username': 'player_user',
            'role': 'player'
        }
        
        response = client.post(
            "/api/admin/drills/upload",
            json={"drills": [
                {"drill_id": "test", "name": "Test", "section": "technical"}
            ]},
            headers={"Authorization": f"Bearer {get_player_token()}"}
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()['detail']
    
    @patch('routes.admin_drills_routes.verify_token')
    @patch('routes.admin_drills_routes.get_drill_repository')
    def test_upload_with_admin_token_returns_200(self, mock_repo, mock_verify, client):
        """Test that upload with admin token returns 200 and calls repository."""
        # Mock verify_token to return admin user
        mock_verify.return_value = {
            'user_id': 'admin-123',
            'username': 'admin_user',
            'role': 'admin'
        }
        
        # Mock repository
        mock_repository = MagicMock()
        mock_repository.upsert_many = AsyncMock(return_value={'inserted': 2, 'updated': 0})
        mock_repo.return_value = mock_repository
        
        response = client.post(
            "/api/admin/drills/upload",
            json={"drills": [
                {"drill_id": "drill_1", "name": "Drill 1", "section": "technical"},
                {"drill_id": "drill_2", "name": "Drill 2", "section": "tactical"}
            ]},
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['uploaded_count'] == 2
        assert data['updated_count'] == 0
        assert len(data['drill_ids']) == 2
        
        # Verify repository was called
        mock_repository.upsert_many.assert_called_once()
    
    @patch('routes.admin_drills_routes.verify_token')
    def test_stats_with_non_admin_returns_403(self, mock_verify, client):
        """Test that stats endpoint with non-admin returns 403."""
        mock_verify.return_value = {
            'user_id': 'coach-123',
            'username': 'coach_user',
            'role': 'coach'
        }
        
        response = client.get(
            "/api/admin/drills/stats",
            headers={"Authorization": f"Bearer {get_coach_token()}"}
        )
        assert response.status_code == 403
    
    @patch('routes.admin_drills_routes.verify_token')
    def test_list_with_non_admin_returns_403(self, mock_verify, client):
        """Test that list endpoint with non-admin returns 403."""
        mock_verify.return_value = {
            'user_id': 'player-123',
            'role': 'player'
        }
        
        response = client.get(
            "/api/admin/drills",
            headers={"Authorization": f"Bearer {get_player_token()}"}
        )
        assert response.status_code == 403


# =============================================================================
# REPOSITORY TESTS
# =============================================================================

class TestDrillRepository:
    """Tests for drill repository operations."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        mock = MagicMock()
        mock.drills = MagicMock()
        return mock
    
    @pytest.mark.asyncio
    async def test_upsert_drill_insert(self, mock_db):
        """Test inserting a new drill."""
        from repositories.drill_repository import DrillRepository
        
        repo = DrillRepository()
        repo._db = mock_db
        
        # Mock find_one to return None (drill doesn't exist)
        mock_db.drills.find_one = AsyncMock(return_value=None)
        mock_db.drills.insert_one = AsyncMock()
        
        result = await repo.upsert_drill(
            {"drill_id": "new_drill", "name": "New Drill", "section": "technical"},
            admin_id="admin-123"
        )
        
        assert result['action'] == 'inserted'
        assert result['drill_id'] == 'new_drill'
        mock_db.drills.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upsert_drill_update(self, mock_db):
        """Test updating an existing drill."""
        from repositories.drill_repository import DrillRepository
        
        repo = DrillRepository()
        repo._db = mock_db
        
        # Mock find_one to return existing drill
        mock_db.drills.find_one = AsyncMock(return_value={
            "drill_id": "existing_drill",
            "name": "Old Name",
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "original-admin"
        })
        mock_db.drills.update_one = AsyncMock()
        
        result = await repo.upsert_drill(
            {"drill_id": "existing_drill", "name": "New Name", "section": "tactical"},
            admin_id="admin-456"
        )
        
        assert result['action'] == 'updated'
        assert result['drill_id'] == 'existing_drill'
        mock_db.drills.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upsert_many(self, mock_db):
        """Test upserting multiple drills."""
        from repositories.drill_repository import DrillRepository
        
        repo = DrillRepository()
        repo._db = mock_db
        
        # First drill is new, second exists
        mock_db.drills.find_one = AsyncMock(side_effect=[None, {"drill_id": "drill_2"}])
        mock_db.drills.insert_one = AsyncMock()
        mock_db.drills.update_one = AsyncMock()
        
        result = await repo.upsert_many([
            {"drill_id": "drill_1", "name": "Drill 1", "section": "technical"},
            {"drill_id": "drill_2", "name": "Drill 2", "section": "tactical"}
        ], admin_id="admin-123")
        
        assert result['inserted'] == 1
        assert result['updated'] == 1


# =============================================================================
# PROVIDER TESTS
# =============================================================================

class TestDrillProvider:
    """Tests for drill provider fallback logic."""
    
    @pytest.mark.asyncio
    async def test_auto_mode_uses_db_when_available(self):
        """Test that auto mode uses DB when drills exist."""
        from providers.drill_provider import DrillProvider, reset_drill_provider
        
        reset_drill_provider()
        
        with patch.dict(os.environ, {'DRILLS_SOURCE': 'auto'}):
            mock_repo = MagicMock()
            mock_repo.count_drills = AsyncMock(return_value=10)
            mock_repo.find_all = AsyncMock(return_value=[
                {"drill_id": "db_drill", "name": "DB Drill", "section": "technical"}
            ])
            
            provider = DrillProvider(repository=mock_repo)
            
            should_use_db = await provider._should_use_db()
            assert should_use_db is True
            
            active_source = await provider.get_active_source()
            assert active_source == "database"
    
    @pytest.mark.asyncio
    async def test_auto_mode_falls_back_to_static(self):
        """Test that auto mode falls back to static when DB is empty."""
        from providers.drill_provider import DrillProvider, reset_drill_provider
        
        reset_drill_provider()
        
        with patch.dict(os.environ, {'DRILLS_SOURCE': 'auto'}):
            mock_repo = MagicMock()
            mock_repo.count_drills = AsyncMock(return_value=0)
            
            provider = DrillProvider(repository=mock_repo)
            
            should_use_db = await provider._should_use_db()
            assert should_use_db is False
            
            active_source = await provider.get_active_source()
            assert active_source == "static"
    
    @pytest.mark.asyncio
    async def test_db_mode_always_uses_db(self):
        """Test that db mode always uses database."""
        from providers.drill_provider import DrillProvider, reset_drill_provider
        
        reset_drill_provider()
        
        with patch.dict(os.environ, {'DRILLS_SOURCE': 'db'}):
            mock_repo = MagicMock()
            mock_repo.count_drills = AsyncMock(return_value=0)
            
            provider = DrillProvider(repository=mock_repo)
            
            should_use_db = await provider._should_use_db()
            assert should_use_db is True
    
    @pytest.mark.asyncio
    async def test_static_mode_never_uses_db(self):
        """Test that static mode never uses database."""
        from providers.drill_provider import DrillProvider, reset_drill_provider
        
        reset_drill_provider()
        
        with patch.dict(os.environ, {'DRILLS_SOURCE': 'static'}):
            mock_repo = MagicMock()
            mock_repo.count_drills = AsyncMock(return_value=100)
            
            provider = DrillProvider(repository=mock_repo)
            
            should_use_db = await provider._should_use_db()
            assert should_use_db is False
            
            active_source = await provider.get_active_source()
            assert active_source == "static"
    
    @pytest.mark.asyncio
    async def test_static_drill_conversion(self):
        """Test that static drills are converted to DrillItem format."""
        from providers.drill_provider import DrillProvider, reset_drill_provider
        
        reset_drill_provider()
        
        with patch.dict(os.environ, {'DRILLS_SOURCE': 'static'}):
            mock_repo = MagicMock()
            mock_repo.count_drills = AsyncMock(return_value=0)
            
            provider = DrillProvider(repository=mock_repo)
            
            # Get a known static drill
            drill = await provider.get_drill("sprint_intervals_30m")
            
            assert drill is not None
            assert drill['drill_id'] == "sprint_intervals_30m"
            assert drill['section'] == "speed_agility"  # Converted from "speed"
            assert drill['_source'] == "static"
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting drill statistics."""
        from providers.drill_provider import DrillProvider, reset_drill_provider
        
        reset_drill_provider()
        
        with patch.dict(os.environ, {'DRILLS_SOURCE': 'auto'}):
            mock_repo = MagicMock()
            mock_repo.count_drills = AsyncMock(return_value=25)
            mock_repo.count_by_section = AsyncMock(return_value={
                "technical": 10,
                "tactical": 8,
                "cardio": 7
            })
            
            provider = DrillProvider(repository=mock_repo)
            
            stats = await provider.get_stats()
            
            assert stats['db_count'] == 25
            assert stats['static_count'] > 0
            assert stats['source_mode'] == 'auto'
            assert stats['db_available'] is True
            assert 'technical' in stats['sections']


# =============================================================================
# UPLOAD VALIDATION TESTS
# =============================================================================

class TestUploadValidation:
    """Tests for drill upload validation."""
    
    def test_invalid_section_rejected(self):
        """Test that invalid sections are rejected."""
        from models.drill_models import DrillUploadRequest, DrillItem
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            DrillUploadRequest(drills=[
                DrillItem(
                    drill_id="invalid_section_drill",
                    name="Invalid",
                    section="not_a_valid_section"
                )
            ])
    
    def test_empty_drill_id_rejected(self):
        """Test that empty drill_id is rejected."""
        from models.drill_models import DrillItem
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            DrillItem(drill_id="", name="Test", section="technical")
    
    def test_empty_name_rejected(self):
        """Test that empty name is rejected."""
        from models.drill_models import DrillItem
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            DrillItem(drill_id="test", name="", section="technical")
    
    def test_empty_drills_list_rejected(self):
        """Test that empty drills list is rejected."""
        from models.drill_models import DrillUploadRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            DrillUploadRequest(drills=[])
    
    def test_intensity_validation(self):
        """Test that only valid intensity values are accepted."""
        from models.drill_models import DrillItem
        from pydantic import ValidationError
        
        # Valid intensities
        for intensity in ["low", "moderate", "high"]:
            drill = DrillItem(
                drill_id=f"drill_{intensity}",
                name=f"Drill {intensity}",
                section="cardio",
                intensity=intensity
            )
            assert drill.intensity == intensity
        
        # Invalid intensity
        with pytest.raises(ValidationError):
            DrillItem(
                drill_id="invalid_intensity",
                name="Invalid",
                section="cardio",
                intensity="extreme"
            )
    
    def test_age_bounds_validation(self):
        """Test age min/max bounds validation."""
        from models.drill_models import DrillItem
        from pydantic import ValidationError
        
        # Valid ages
        drill = DrillItem(
            drill_id="valid_age",
            name="Valid",
            section="technical",
            age_min=5,
            age_max=100
        )
        assert drill.age_min == 5
        assert drill.age_max == 100
        
        # Invalid age (too low)
        with pytest.raises(ValidationError):
            DrillItem(
                drill_id="invalid_age_low",
                name="Invalid",
                section="technical",
                age_min=3  # Below 5
            )
        
        # Invalid age (too high)
        with pytest.raises(ValidationError):
            DrillItem(
                drill_id="invalid_age_high",
                name="Invalid",
                section="technical",
                age_max=150  # Above 100
            )


# =============================================================================
# INTEGRATION TESTS (with mocked DB)
# =============================================================================

class TestAdminDrillsIntegration:
    """Integration tests for admin drills endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create test app."""
        from fastapi import FastAPI
        from routes.admin_drills_routes import router
        
        app = FastAPI()
        app.include_router(router, prefix="/api")
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @patch('routes.admin_drills_routes.verify_token')
    @patch('routes.admin_drills_routes.get_drill_repository')
    def test_full_upload_flow(self, mock_repo, mock_verify, client):
        """Test complete upload flow with validation."""
        # Setup admin auth
        mock_verify.return_value = {
            'user_id': 'admin-123',
            'username': 'admin',
            'role': 'admin'
        }
        
        # Setup repository
        mock_repository = MagicMock()
        mock_repository.upsert_many = AsyncMock(return_value={'inserted': 3, 'updated': 0})
        mock_repo.return_value = mock_repository
        
        # Upload drills
        response = client.post(
            "/api/admin/drills/upload",
            json={"drills": [
                {
                    "drill_id": "tech_pass_1",
                    "name": "Passing Drill 1",
                    "section": "technical",
                    "tags": ["passing", "accuracy"],
                    "age_min": 10,
                    "age_max": 18,
                    "intensity": "moderate",
                    "duration_min": 15,
                    "equipment": ["balls", "cones"],
                    "coaching_points": ["Keep head up", "Proper weight on pass"]
                },
                {
                    "drill_id": "tact_pos_1",
                    "name": "Positioning Drill 1",
                    "section": "tactical",
                    "tags": ["positioning", "awareness"],
                    "intensity": "low"
                },
                {
                    "drill_id": "cardio_run_1",
                    "name": "Interval Running",
                    "section": "cardio",
                    "intensity": "high",
                    "duration_min": 30
                }
            ]},
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['uploaded_count'] == 3
        assert len(data['drill_ids']) == 3
        assert "tech_pass_1" in data['drill_ids']
        
        # Verify upsert_many was called with correct data
        call_args = mock_repository.upsert_many.call_args
        assert len(call_args[0][0]) == 3  # 3 drills
    
    @patch('routes.admin_drills_routes.verify_token')
    @patch('routes.admin_drills_routes.get_drill_provider')
    def test_stats_endpoint(self, mock_provider, mock_verify, client):
        """Test stats endpoint."""
        mock_verify.return_value = {
            'user_id': 'admin-123',
            'role': 'admin'
        }
        
        mock_prov = MagicMock()
        mock_prov.get_stats = AsyncMock(return_value={
            'db_count': 50,
            'static_count': 10,
            'source_mode': 'auto',
            'active_source': 'database',
            'db_available': True,
            'sections': {'technical': 20, 'tactical': 15, 'cardio': 15}
        })
        mock_provider.return_value = mock_prov
        
        response = client.get(
            "/api/admin/drills/stats",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['db_count'] == 50
        assert data['static_count'] == 10
        assert data['source_mode'] == 'auto'
        assert data['active_source'] == 'database'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
