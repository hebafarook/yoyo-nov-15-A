"""
Admin Drills Routes
===================

Admin-only endpoints for managing training drills.
Requires JWT authentication with role="admin".
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional, List
import logging
import jwt
import os

from data_models.drill_models import (
    DrillItem,
    DrillUploadRequest,
    DrillUploadResponse,
    DrillListResponse,
    DrillStatsResponse
)
from repositories.drill_repository import get_drill_repository, DrillRepository
from providers.drill_provider import get_drill_provider, DrillProvider

router = APIRouter(prefix="/admin/drills", tags=["admin-drills"])
logger = logging.getLogger(__name__)

security = HTTPBearer()

# JWT Configuration - same as .env
JWT_SECRET = os.environ.get('JWT_SECRET', 'elite-soccer-ai-coach-secret-key-2024-change-in-production')
JWT_ALGORITHM = 'HS256'


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


# =============================================================================
# AUTHENTICATION DEPENDENCY
# =============================================================================

async def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency that verifies the request is from an authenticated admin user.
    
    Returns:
        User info dict with user_id and role
    
    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If authenticated but not admin
    """
    # verify_token will raise 401 if token is invalid/missing
    user_info = verify_token(credentials)
    
    # Check role from JWT payload
    role = user_info.get('role', '')
    if role != 'admin':
        logger.warning(f"Non-admin user {user_info.get('user_id')} attempted admin action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_info


# =============================================================================
# ADMIN DRILL ENDPOINTS
# =============================================================================

@router.post("/upload", response_model=DrillUploadResponse)
async def upload_drills(
    request: DrillUploadRequest,
    admin: dict = Depends(require_admin)
):
    """
    Upload training drills (admin only).
    
    - Validates ALL drills first; if any invalid → reject whole upload (422)
    - Upserts by drill_id (same id updates existing drill)
    - All drills must pass Pydantic validation
    
    Auth:
    - No token → 401
    - Non-admin token → 403
    - Admin → allowed
    """
    try:
        repository = get_drill_repository()
        admin_id = admin.get('user_id')
        
        # Convert DrillItem models to dicts for storage
        drills_data = [drill.model_dump() for drill in request.drills]
        
        # Perform upsert
        result = await repository.upsert_many(drills_data, admin_id=admin_id)
        
        drill_ids = [d.drill_id for d in request.drills]
        
        logger.info(
            f"Admin {admin_id} uploaded {len(request.drills)} drills: "
            f"{result['inserted']} inserted, {result['updated']} updated"
        )
        
        return DrillUploadResponse(
            success=True,
            message=f"Successfully uploaded {len(request.drills)} drills",
            uploaded_count=result['inserted'],
            updated_count=result['updated'],
            drill_ids=drill_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drill upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload drills: {str(e)}"
        )


@router.get("", response_model=DrillListResponse)
async def list_drills(
    section: Optional[str] = Query(None, description="Filter by section"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    age: Optional[int] = Query(None, ge=5, le=100, description="Filter by age"),
    position: Optional[str] = Query(None, description="Filter by position"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    admin: dict = Depends(require_admin)
):
    """
    List all drills with optional filters (admin only).
    
    Supports filtering by:
    - section: technical, tactical, possession, speed_agility, cardio, gym, mobility, recovery, prehab
    - tag: any keyword tag
    - age: player age (returns drills suitable for this age)
    - position: player position
    
    Pagination via page and page_size.
    """
    try:
        provider = get_drill_provider()
        
        # Get all drills with filters
        drills = await provider.get_all_drills(
            section=section,
            tag=tag,
            age=age,
            position=position
        )
        
        # Paginate
        total = len(drills)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_drills = drills[start:end]
        
        # Get active source
        active_source = await provider.get_active_source()
        
        # Convert to DrillItem models (filter out _source and _original)
        drill_items = []
        for d in paginated_drills:
            # Remove internal fields
            clean = {k: v for k, v in d.items() if not k.startswith('_')}
            try:
                drill_items.append(DrillItem(**clean))
            except Exception:
                # If conversion fails, skip this drill
                logger.warning(f"Failed to convert drill: {d.get('drill_id')}")
                continue
        
        return DrillListResponse(
            drills=drill_items,
            total=total,
            source=active_source,
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List drills error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list drills: {str(e)}"
        )


@router.get("/stats", response_model=DrillStatsResponse)
async def get_drill_stats(
    admin: dict = Depends(require_admin)
):
    """
    Get drill statistics (admin only).
    
    Returns:
    - db_count: Number of drills in database
    - static_count: Number of static drills in code
    - source_mode: Current DRILLS_SOURCE setting (auto/db/static)
    - active_source: Which source is currently being used (database/static)
    - db_available: Whether database is accessible
    - sections: Count of drills per section
    """
    try:
        provider = get_drill_provider()
        stats = await provider.get_stats()
        
        return DrillStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drill stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get drill stats: {str(e)}"
        )


@router.get("/{drill_id}", response_model=DrillItem)
async def get_drill(
    drill_id: str,
    admin: dict = Depends(require_admin)
):
    """
    Get a single drill by ID (admin only).
    """
    try:
        provider = get_drill_provider()
        drill = await provider.get_drill(drill_id)
        
        if not drill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drill not found: {drill_id}"
            )
        
        # Remove internal fields
        clean = {k: v for k, v in drill.items() if not k.startswith('_')}
        return DrillItem(**clean)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get drill error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get drill: {str(e)}"
        )


@router.delete("/{drill_id}")
async def delete_drill(
    drill_id: str,
    hard_delete: bool = Query(False, description="Permanently delete instead of soft delete"),
    admin: dict = Depends(require_admin)
):
    """
    Delete a drill (admin only).
    
    By default, performs a soft delete (marks as inactive).
    Use hard_delete=true to permanently remove.
    """
    try:
        repository = get_drill_repository()
        
        success = await repository.delete_drill(drill_id, soft_delete=not hard_delete)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drill not found: {drill_id}"
            )
        
        action = "permanently deleted" if hard_delete else "deactivated"
        logger.info(f"Admin {admin.get('user_id')} {action} drill: {drill_id}")
        
        return {
            "success": True,
            "message": f"Drill {drill_id} {action}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete drill error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete drill: {str(e)}"
        )
