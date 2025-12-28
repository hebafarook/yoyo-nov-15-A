"""
Drill Provider
==============

Provides drills from database (primary) with fallback to static exercise_database.py.
This is the single source of truth for drill selection in training services.
"""

from typing import Optional, List, Dict, Any
from repositories.drill_repository import DrillRepository, get_drill_repository
from exercise_database import EXERCISE_DATABASE
import logging
import os

logger = logging.getLogger(__name__)


class DrillProvider:
    """
    Provider for drill selection with DB-first fallback strategy.
    
    Priority:
    1. Database drills (when available)
    2. Static EXERCISE_DATABASE (fallback)
    
    The provider transparently handles:
    - Database connectivity issues
    - Missing drills in database
    - Category mapping between DB and static
    """
    
    def __init__(self, repository: Optional[DrillRepository] = None):
        self._repository = repository
        self._use_db = os.environ.get('DRILL_DB_ENABLED', 'true').lower() == 'true'
    
    @property
    def repository(self) -> DrillRepository:
        """Lazy load repository."""
        if self._repository is None:
            self._repository = get_drill_repository()
        return self._repository
    
    async def get_drill(self, drill_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single drill by ID.
        
        Tries database first, falls back to static.
        """
        # Try database first
        if self._use_db:
            try:
                drill = await self.repository.find_by_id(drill_id)
                if drill:
                    logger.debug(f"Drill '{drill_id}' loaded from database")
                    return drill
            except Exception as e:
                logger.warning(f"DB lookup failed for drill '{drill_id}': {e}")
        
        # Fallback to static
        if drill_id in EXERCISE_DATABASE:
            logger.debug(f"Drill '{drill_id}' loaded from static database")
            static_drill = EXERCISE_DATABASE[drill_id].copy()
            static_drill['drill_id'] = drill_id  # Add drill_id for consistency
            return static_drill
        
        return None
    
    async def get_drills_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all drills in a category.
        
        Merges database and static drills, with DB taking precedence.
        """
        drills = {}
        
        # Get static drills first
        for drill_id, drill_data in EXERCISE_DATABASE.items():
            if drill_data.get('category', '').lower() == category.lower():
                drill = drill_data.copy()
                drill['drill_id'] = drill_id
                drill['_source'] = 'static'
                drills[drill_id] = drill
        
        # Get database drills (override static)
        if self._use_db:
            try:
                db_drills = await self.repository.find_by_category(category)
                for drill in db_drills:
                    drill['_source'] = 'database'
                    drills[drill['drill_id']] = drill
                logger.debug(f"Loaded {len(db_drills)} DB drills for category '{category}'")
            except Exception as e:
                logger.warning(f"DB lookup failed for category '{category}': {e}")
        
        return list(drills.values())
    
    async def get_drills_by_categories(self, categories: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get drills for multiple categories.
        
        Returns dict mapping category -> list of drills.
        """
        result = {}
        for category in categories:
            result[category] = await self.get_drills_by_category(category)
        return result
    
    async def get_all_drills(self) -> List[Dict[str, Any]]:
        """
        Get all available drills (merged DB + static).
        """
        drills = {}
        
        # Get all static drills
        for drill_id, drill_data in EXERCISE_DATABASE.items():
            drill = drill_data.copy()
            drill['drill_id'] = drill_id
            drill['_source'] = 'static'
            drills[drill_id] = drill
        
        # Get database drills (override static)
        if self._use_db:
            try:
                db_drills = await self.repository.find_all()
                for drill in db_drills:
                    drill['_source'] = 'database'
                    drills[drill['drill_id']] = drill
                logger.info(f"Loaded {len(db_drills)} drills from database")
            except Exception as e:
                logger.warning(f"DB drill load failed: {e}")
        
        return list(drills.values())
    
    async def search_drills(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        intensity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search drills with filters.
        
        Searches both DB and static, with DB taking precedence.
        """
        drills = {}
        
        # Search static drills
        for drill_id, drill_data in EXERCISE_DATABASE.items():
            matches = True
            
            if category and drill_data.get('category', '').lower() != category.lower():
                matches = False
            
            if intensity and drill_data.get('intensity', '').lower() != intensity.lower():
                matches = False
            
            if query:
                query_lower = query.lower()
                searchable = f"{drill_data.get('name', '')} {drill_data.get('description', '')} {drill_data.get('purpose', '')}".lower()
                if query_lower not in searchable:
                    matches = False
            
            if matches:
                drill = drill_data.copy()
                drill['drill_id'] = drill_id
                drill['_source'] = 'static'
                drills[drill_id] = drill
        
        # Search database drills (override static)
        if self._use_db:
            try:
                db_drills = await self.repository.search_drills(
                    query=query,
                    category=category,
                    intensity=intensity
                )
                for drill in db_drills:
                    drill['_source'] = 'database'
                    drills[drill['drill_id']] = drill
            except Exception as e:
                logger.warning(f"DB drill search failed: {e}")
        
        return list(drills.values())
    
    async def get_drill_count(self) -> Dict[str, int]:
        """
        Get count of drills from each source.
        """
        static_count = len(EXERCISE_DATABASE)
        db_count = 0
        
        if self._use_db:
            try:
                db_count = await self.repository.count_drills()
            except Exception as e:
                logger.warning(f"DB count failed: {e}")
        
        return {
            "static": static_count,
            "database": db_count,
            "total": static_count + db_count  # Note: may have overlap
        }
    
    def get_static_drill_ids(self) -> List[str]:
        """Get list of drill IDs from static database."""
        return list(EXERCISE_DATABASE.keys())
    
    async def is_db_available(self) -> bool:
        """Check if database is available for drill storage."""
        if not self._use_db:
            return False
        try:
            await self.repository.count_drills()
            return True
        except Exception:
            return False


# Singleton instance
_drill_provider: Optional[DrillProvider] = None


def get_drill_provider() -> DrillProvider:
    """Get or create the drill provider singleton."""
    global _drill_provider
    if _drill_provider is None:
        _drill_provider = DrillProvider()
    return _drill_provider
