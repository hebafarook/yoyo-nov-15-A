"""
Coach Drills Unit Tests
=======================

Tests for coach PDF drill upload and confirm functionality.
All tests use mocks - no real MongoDB/Redis required.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
import jwt
from datetime import datetime, timedelta
import os
import io

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'elite-soccer-ai-coach-secret-key-2024-change-in-production')
JWT_ALGORITHM = 'HS256'


def create_test_token(user_id: str, role: str, username: str = "test_user") -> str:
    """Create a JWT token for testing."""
    payload = {
        'user_id': user_id,
        'sub': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_coach_token():
    return create_test_token("coach-123", "coach", "test_coach")


def get_admin_token():
    return create_test_token("admin-123", "admin", "test_admin")


def get_player_token():
    return create_test_token("player-123", "player", "test_player")


def create_simple_pdf() -> bytes:
    """
    Create a simple PDF-like bytes for testing.
    Note: This creates minimal PDF structure that pdfplumber can parse.
    """
    # This is a minimal valid PDF with some text
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 178 >>
stream
BT
/F1 12 Tf
50 700 Td
(TECH01: Triangle Passing Drill) Tj
0 -20 Td
(Technical exercise for passing accuracy) Tj
0 -20 Td
(Duration: 15 minutes) Tj
0 -20 Td
(Equipment: cones, balls) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000497 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
576
%%EOF
"""
    return pdf_content


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

class TestCoachDrillsAuth:
    """Tests for coach drills authentication."""
    
    @pytest.fixture
    def app(self):
        """Create test app with coach drills router."""
        from fastapi import FastAPI
        from routes.coach_drills_routes import router
        
        app = FastAPI()
        app.include_router(router, prefix="/api")
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_upload_pdf_requires_auth(self, client):
        """Test that upload-pdf requires authentication (401/403)."""
        # Create a simple file upload
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        response = client.post("/api/coach/drills/upload-pdf", files=files)
        
        # Should return 401 or 403 for missing auth
        assert response.status_code in [401, 403]
    
    def test_upload_pdf_requires_coach_or_admin(self, client):
        """Test that upload-pdf requires coach or admin role (403)."""
        # Use player token
        headers = {"Authorization": f"Bearer {get_player_token()}"}
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        
        response = client.post(
            "/api/coach/drills/upload-pdf",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 403
        assert "Coach or admin access required" in response.json()['detail']
    
    def test_confirm_requires_auth(self, client):
        """Test that confirm requires authentication."""
        response = client.post(
            "/api/coach/drills/confirm",
            json={"drills": []}
        )
        
        assert response.status_code in [401, 403]
    
    def test_confirm_requires_coach_or_admin(self, client):
        """Test that confirm requires coach or admin role."""
        headers = {"Authorization": f"Bearer {get_player_token()}"}
        
        response = client.post(
            "/api/coach/drills/confirm",
            json={"drills": [{"drill_id": "test", "name": "Test", "section": "technical"}]},
            headers=headers
        )
        
        assert response.status_code == 403


# =============================================================================
# PDF PARSER TESTS
# =============================================================================

# Import parser directly to bypass services/__init__.py
import importlib.util
_parser_spec = importlib.util.spec_from_file_location(
    'drill_pdf_parser', 
    os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'drill_pdf_parser.py')
)
_parser_module = importlib.util.module_from_spec(_parser_spec)
_parser_spec.loader.exec_module(_parser_module)
DrillPDFParser = _parser_module.DrillPDFParser


class TestDrillPDFParser:
    """Tests for drill PDF parser service."""
    
    def test_infer_drill_id(self):
        """Test drill ID inference."""
        parser = DrillPDFParser()
        
        # Should find drill IDs
        assert parser.infer_drill_id("TECH01 - Passing Drill") == "TECH01"
        assert parser.infer_drill_id("SPD123: Sprint Training") == "SPD123"
        assert parser.infer_drill_id("TAC99 Positioning") == "TAC99"
        
        # Should return None for no match
        assert parser.infer_drill_id("Just a passing drill") is None
    
    def test_infer_section(self):
        """Test section inference from keywords."""
        parser = DrillPDFParser()
        
        assert parser.infer_section("Technical passing and dribbling drill") == "technical"
        assert parser.infer_section("High intensity sprint training") == "speed_agility"
        assert parser.infer_section("Recovery and foam rolling session") == "recovery"
        assert parser.infer_section("Tactical positioning exercise") == "tactical"
        assert parser.infer_section("ACL prevention prehab routine") == "prehab"
    
    def test_infer_tags(self):
        """Test tag inference."""
        parser = DrillPDFParser()
        
        tags = parser.infer_tags("Passing and dribbling with first touch focus")
        assert "passing" in tags
        assert "dribbling" in tags
        assert "first_touch" in tags
    
    def test_infer_duration(self):
        """Test duration extraction."""
        from services.drill_pdf_parser import DrillPDFParser
        
        parser = DrillPDFParser()
        
        assert parser.infer_duration("Duration: 15 minutes") == 15
        assert parser.infer_duration("20 min session") == 20
        assert parser.infer_duration("No duration here") is None
    
    def test_infer_sets_reps(self):
        """Test sets and reps extraction."""
        from services.drill_pdf_parser import DrillPDFParser
        
        parser = DrillPDFParser()
        
        sets, reps = parser.infer_sets_reps("3 sets of 10 reps")
        assert sets == 3
        assert reps == 10
        
        sets, reps = parser.infer_sets_reps("4 sets")
        assert sets == 4
        assert reps is None
    
    def test_parse_chunk_creates_candidate(self):
        """Test that parse_chunk creates a DrillItemCandidate."""
        from services.drill_pdf_parser import DrillPDFParser
        
        parser = DrillPDFParser()
        
        chunk = {
            'text': 'TECH01: Triangle Passing Drill\nTechnical exercise for passing accuracy.\nDuration: 15 minutes\nEquipment: cones, balls',
            'page_number': 1
        }
        
        candidate = parser.parse_chunk(chunk)
        
        assert candidate.drill_id == "TECH01"
        assert "Triangle" in (candidate.name or "")
        assert candidate.section == "technical"
        assert candidate.duration_min == 15
        assert "cone" in candidate.equipment or "ball" in candidate.equipment
        assert candidate.raw_text is not None
        assert candidate.confidence > 0
    
    def test_parse_chunk_needs_review_when_missing_fields(self):
        """Test that candidates need review when missing critical fields."""
        from services.drill_pdf_parser import DrillPDFParser
        
        parser = DrillPDFParser()
        
        # Chunk with no drill ID
        chunk = {
            'text': 'Some random text about soccer training without clear structure',
            'page_number': 1
        }
        
        candidate = parser.parse_chunk(chunk)
        
        assert candidate.needs_review is True
        assert len(candidate.parse_warnings) > 0


# =============================================================================
# UPLOAD PDF ENDPOINT TESTS
# =============================================================================

class TestUploadPDFEndpoint:
    """Tests for upload-pdf endpoint."""
    
    @pytest.fixture
    def app(self):
        from fastapi import FastAPI
        from routes.coach_drills_routes import router
        
        app = FastAPI()
        app.include_router(router, prefix="/api")
        return app
    
    @pytest.fixture
    def client(self, app):
        return TestClient(app)
    
    def test_upload_pdf_rejects_non_pdf(self, client):
        """Test that non-PDF files are rejected."""
        headers = {"Authorization": f"Bearer {get_coach_token()}"}
        files = {"file": ("test.txt", b"not a pdf", "text/plain")}
        
        response = client.post(
            "/api/coach/drills/upload-pdf",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "PDF" in response.json()['detail']
    
    def test_upload_pdf_rejects_empty_file(self, client):
        """Test that empty files are rejected."""
        headers = {"Authorization": f"Bearer {get_coach_token()}"}
        files = {"file": ("test.pdf", b"", "application/pdf")}
        
        response = client.post(
            "/api/coach/drills/upload-pdf",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 400
    
    @patch('routes.coach_drills_routes.get_drill_pdf_parser')
    def test_upload_pdf_returns_candidates(self, mock_parser, client):
        """Test that upload-pdf returns parsed candidates."""
        from models.drill_candidate_models import DrillItemCandidate
        
        # Mock parser
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_pdf_bytes.return_value = {
            'parsed': [
                DrillItemCandidate(
                    drill_id="TECH01",
                    name="Test Drill",
                    section="technical",
                    raw_text="Test drill content",
                    needs_review=False,
                    confidence=0.85
                )
            ],
            'errors': [],
            'meta': {'pages': 1, 'filename': 'test.pdf'}
        }
        mock_parser.return_value = mock_parser_instance
        
        headers = {"Authorization": f"Bearer {get_coach_token()}"}
        files = {"file": ("test.pdf", create_simple_pdf(), "application/pdf")}
        
        response = client.post(
            "/api/coach/drills/upload-pdf",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'parsed' in data
        assert 'errors' in data
        assert 'meta' in data
        assert len(data['parsed']) == 1
        assert data['parsed'][0]['drill_id'] == "TECH01"


# =============================================================================
# CONFIRM ENDPOINT TESTS
# =============================================================================

class TestConfirmEndpoint:
    """Tests for confirm endpoint."""
    
    @pytest.fixture
    def app(self):
        from fastapi import FastAPI
        from routes.coach_drills_routes import router
        
        app = FastAPI()
        app.include_router(router, prefix="/api")
        return app
    
    @pytest.fixture
    def client(self, app):
        return TestClient(app)
    
    def test_confirm_validates_all_or_none(self, client):
        """Test that confirm rejects entire batch if any drill is invalid."""
        headers = {"Authorization": f"Bearer {get_coach_token()}"}
        
        # Mix of valid and invalid drills
        response = client.post(
            "/api/coach/drills/confirm",
            json={"drills": [
                {"drill_id": "valid_1", "name": "Valid Drill", "section": "technical"},
                {"drill_id": "invalid_section", "name": "Invalid", "section": "not_a_section"},
            ]},
            headers=headers
        )
        
        assert response.status_code == 422
        assert "Validation failed" in response.json()['detail']['message']
    
    def test_confirm_rejects_duplicate_ids(self, client):
        """Test that confirm rejects duplicate drill_ids."""
        headers = {"Authorization": f"Bearer {get_coach_token()}"}
        
        response = client.post(
            "/api/coach/drills/confirm",
            json={"drills": [
                {"drill_id": "dup_id", "name": "Drill 1", "section": "technical"},
                {"drill_id": "dup_id", "name": "Drill 2", "section": "tactical"},
            ]},
            headers=headers
        )
        
        assert response.status_code == 422
        assert "Duplicate" in str(response.json())
    
    @patch('routes.coach_drills_routes.get_drill_repository')
    def test_confirm_upserts_valid_drills(self, mock_repo, client):
        """Test that confirm calls repository upsert_many for valid drills."""
        # Mock repository
        mock_repository = MagicMock()
        mock_repository.upsert_many = AsyncMock(return_value={'inserted': 2, 'updated': 0})
        mock_repo.return_value = mock_repository
        
        headers = {"Authorization": f"Bearer {get_coach_token()}"}
        
        response = client.post(
            "/api/coach/drills/confirm",
            json={"drills": [
                {"drill_id": "drill_1", "name": "Drill 1", "section": "technical"},
                {"drill_id": "drill_2", "name": "Drill 2", "section": "tactical"},
            ]},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert data['inserted'] == 2
        assert data['total'] == 2
        
        # Verify repository was called
        mock_repository.upsert_many.assert_called_once()
    
    @patch('routes.coach_drills_routes.get_drill_repository')
    def test_confirm_admin_can_also_use(self, mock_repo, client):
        """Test that admin can also use confirm endpoint."""
        mock_repository = MagicMock()
        mock_repository.upsert_many = AsyncMock(return_value={'inserted': 1, 'updated': 0})
        mock_repo.return_value = mock_repository
        
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        
        response = client.post(
            "/api/coach/drills/confirm",
            json={"drills": [
                {"drill_id": "admin_drill", "name": "Admin Drill", "section": "cardio"},
            ]},
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()['success'] is True


# =============================================================================
# INTEGRATION-STYLE TESTS (with mocked repository)
# =============================================================================

class TestCoachDrillsIntegration:
    """Integration-style tests with mocked repository."""
    
    @pytest.fixture
    def app(self):
        from fastapi import FastAPI
        from routes.coach_drills_routes import router
        
        app = FastAPI()
        app.include_router(router, prefix="/api")
        return app
    
    @pytest.fixture
    def client(self, app):
        return TestClient(app)
    
    @patch('routes.coach_drills_routes.get_drill_pdf_parser')
    @patch('routes.coach_drills_routes.get_drill_repository')
    def test_full_upload_confirm_flow(self, mock_repo, mock_parser, client):
        """Test complete upload -> preview -> confirm flow."""
        from models.drill_candidate_models import DrillItemCandidate
        
        # Step 1: Mock parser for upload
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_pdf_bytes.return_value = {
            'parsed': [
                DrillItemCandidate(
                    drill_id="FLOW01",
                    name="Flow Test Drill",
                    section="technical",
                    tags=["passing"],
                    raw_text="Full flow test drill",
                    needs_review=False,
                    confidence=0.9
                )
            ],
            'errors': [],
            'meta': {'pages': 1, 'filename': 'flow.pdf'}
        }
        mock_parser.return_value = mock_parser_instance
        
        # Step 2: Mock repository for confirm
        mock_repository = MagicMock()
        mock_repository.upsert_many = AsyncMock(return_value={'inserted': 1, 'updated': 0})
        mock_repo.return_value = mock_repository
        
        headers = {"Authorization": f"Bearer {get_coach_token()}"}
        
        # Upload PDF (preview only - no DB writes)
        files = {"file": ("flow.pdf", create_simple_pdf(), "application/pdf")}
        upload_response = client.post(
            "/api/coach/drills/upload-pdf",
            files=files,
            headers=headers
        )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        assert len(upload_data['parsed']) == 1
        
        # Verify NO DB writes during upload
        mock_repository.upsert_many.assert_not_called()
        
        # Confirm drills (now writes to DB)
        confirm_response = client.post(
            "/api/coach/drills/confirm",
            json={"drills": [
                {
                    "drill_id": upload_data['parsed'][0]['drill_id'],
                    "name": upload_data['parsed'][0]['name'],
                    "section": upload_data['parsed'][0]['section'],
                    "tags": upload_data['parsed'][0]['tags']
                }
            ]},
            headers=headers
        )
        
        assert confirm_response.status_code == 200
        confirm_data = confirm_response.json()
        assert confirm_data['success'] is True
        assert confirm_data['inserted'] == 1
        
        # Verify DB write happened during confirm
        mock_repository.upsert_many.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
