"""
Coach Drills Routes
===================

Endpoints for coaches to upload PDF drills with preview and confirm workflow.

2-Step Process:
1. POST /api/coach/drills/upload-pdf - Parse PDF, return preview (NO DB writes)
2. POST /api/coach/drills/confirm - Validate and save to DB

Auth: role in ["coach", "admin"] required.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List
import logging
import jwt
import os
import sys

# Import models directly to avoid circular imports
from data_models.drill_models import DrillItem, DrillUploadResponse
from data_models.drill_candidate_models import (
    DrillItemCandidate,
    PDFUploadResponse,
    DrillConfirmRequest,
    DrillConfirmResponse
)

# Import drill_pdf_parser directly to bypass services/__init__.py
import importlib.util
_parser_spec = importlib.util.spec_from_file_location(
    'drill_pdf_parser', 
    os.path.join(os.path.dirname(__file__), '..', 'services', 'drill_pdf_parser.py')
)
_parser_module = importlib.util.module_from_spec(_parser_spec)
_parser_spec.loader.exec_module(_parser_module)
get_drill_pdf_parser = _parser_module.get_drill_pdf_parser

from repositories.drill_repository import get_drill_repository

router = APIRouter(prefix="/coach/drills", tags=["coach-drills"])
logger = logging.getLogger(__name__)

security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'elite-soccer-ai-coach-secret-key-2024-change-in-production')
JWT_ALGORITHM = 'HS256'

# Allowed roles for coach drill operations
ALLOWED_ROLES = ["coach", "admin"]

# Max file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """
    Verify JWT token and extract user information.
    
    Returns:
        Dict with user_id, username, and role
    
    Raises:
        HTTPException 401: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        user_id = payload.get('user_id') or payload.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )
        
        return {
            'user_id': user_id,
            'username': payload.get('username', ''),
            'role': payload.get('role', 'player')
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def require_coach_or_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency that verifies the request is from a coach or admin.
    
    Returns:
        User info dict with user_id and role
    
    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If authenticated but not coach/admin
    """
    user_info = verify_token(credentials)
    
    role = user_info.get('role', '')
    if role not in ALLOWED_ROLES:
        logger.warning(f"User {user_info.get('user_id')} with role '{role}' attempted coach action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Coach or admin access required. Your role: {role}"
        )
    
    return user_info


# =============================================================================
# STEP 1: UPLOAD PDF (PREVIEW ONLY - NO DB WRITES)
# =============================================================================

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    user: dict = Depends(require_coach_or_admin)
):
    """
    Upload and parse PDF file to extract drill candidates.
    
    **IMPORTANT: This is a preview only - NO drills are written to the database.**
    
    The coach should review the parsed candidates, edit as needed, then call
    /confirm to actually save to the database.
    
    Auth: role in ["coach", "admin"] required.
    
    Returns:
        PDFUploadResponse with parsed candidates, errors, and metadata
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted"
        )
    
    # Read file content
    try:
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Parse PDF
    try:
        parser = get_drill_pdf_parser()
        result = parser.parse_pdf_bytes(content, filename=file.filename)
        
        logger.info(
            f"Coach {user.get('user_id')} uploaded PDF '{file.filename}': "
            f"{len(result['parsed'])} candidates parsed"
        )
        
        # Convert candidates to dicts for response
        parsed_dicts = [c.model_dump() for c in result['parsed']]
        
        return PDFUploadResponse(
            parsed=result['parsed'],
            errors=result['errors'],
            meta=result['meta']
        )
        
    except Exception as e:
        logger.error(f"PDF parsing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing PDF: {str(e)}"
        )


# =============================================================================
# STEP 2: CONFIRM (VALIDATE AND SAVE TO DB)
# =============================================================================

@router.post("/confirm", response_model=DrillConfirmResponse)
async def confirm_drills(
    request: DrillConfirmRequest,
    user: dict = Depends(require_coach_or_admin)
):
    """
    Confirm and save drills to database.
    
    **Validation Rules:**
    - ALL drills must be valid DrillItems
    - If ANY drill is invalid → 422 error, NO partial writes
    - Drills are upserted by drill_id (existing drills are updated)
    
    Auth: role in ["coach", "admin"] required.
    
    Returns:
        DrillConfirmResponse with insert/update counts
    """
    if not request.drills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No drills provided"
        )
    
    # Validate ALL drills first - no partial writes
    validated_drills = []
    validation_errors = []
    
    for i, drill_data in enumerate(request.drills):
        try:
            # Validate against DrillItem schema
            drill = DrillItem(**drill_data)
            validated_drills.append(drill)
        except Exception as e:
            validation_errors.append(f"Drill {i+1}: {str(e)}")
    
    # If any validation errors, reject entire batch
    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed - no drills were saved",
                "errors": validation_errors
            }
        )
    
    # Check for duplicate drill_ids within the batch
    drill_ids = [d.drill_id for d in validated_drills]
    if len(drill_ids) != len(set(drill_ids)):
        duplicates = [id for id in drill_ids if drill_ids.count(id) > 1]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Duplicate drill_ids in batch",
                "duplicates": list(set(duplicates))
            }
        )
    
    # All valid - upsert to database
    try:
        repository = get_drill_repository()
        
        # Convert to dicts for storage
        drills_data = [d.model_dump() for d in validated_drills]
        
        # Upsert all drills
        result = await repository.upsert_many(drills_data, admin_id=user.get('user_id'))
        
        logger.info(
            f"Coach {user.get('user_id')} confirmed {len(validated_drills)} drills: "
            f"{result['inserted']} inserted, {result['updated']} updated"
        )
        
        return DrillConfirmResponse(
            success=True,
            inserted=result['inserted'],
            updated=result['updated'],
            total=len(validated_drills),
            drill_ids=drill_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error during drill confirm: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# =============================================================================
# HELPER: GET PREVIEW TEMPLATE
# =============================================================================

@router.get("/sections")
async def get_valid_sections(
    user: dict = Depends(require_coach_or_admin)
):
    """
    Get list of valid drill sections for dropdown.
    
    Useful for frontend to populate section selector.
    """
    from data_models.drill_models import DrillSection
    
    return {
        "sections": [s.value for s in DrillSection],
        "intensities": ["low", "moderate", "high"]
    }
