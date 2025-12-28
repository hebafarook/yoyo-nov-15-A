"""
Drill Provider
==============

Provides drills from database (primary) with fallback to static exercise_database.py.
This is the single source of truth for drill selection in training services.

Environment Variables:
- DRILLS_SOURCE: 'auto' | 'db' | 'static' (default: 'auto')
  - auto: Use DB if drills.count > 0, else static fallback
  - db: DB only (if empty/unavailable → error)
  - static: Static only (ignore DB)
- DRILLS_DB_FALLBACK: 'true' | 'false' (default: 'true', only used in auto mode)
"""

from typing import Optional, List, Dict, Any
from repositories.drill_repository import DrillRepository, get_drill_repository
from exercise_database import EXERCISE_DATABASE
import logging
import os
from enum import Enum

logger = logging.getLogger(__name__)


class DrillsSourceMode(str, Enum):
    """Drill source modes."""
    AUTO = "auto"
    DB = "db"
    STATIC = "static"


class DrillsNotAvailableError(Exception):
    """Raised when drills are not available in db-only mode."""
    def __init__(self, message: str = "No drills available in database and fallback is disabled"):
        self.message = message
        super().__init__(message)


class DrillProvider:
    """
    Provider for drill selection with configurable source strategy.
    
    Modes:
    - auto: Use DB if has drills, else fallback to static (default)
    - db: DB only, error if unavailable
    - static: Static only, ignore DB
    """
    
    def __init__(self, repository: Optional[DrillRepository] = None):
        self._repository = repository
        self._source_mode = self._get_source_mode()
        self._db_fallback = os.environ.get('DRILLS_DB_FALLBACK', 'true').lower() == 'true'
    
    def _get_source_mode(self) -> DrillsSourceMode:
        """Get the drill source mode from environment."""
        mode = os.environ.get('DRILLS_SOURCE', 'auto').lower()
        try:
            return DrillsSourceMode(mode)
        except ValueError:
            logger.warning(f"Invalid DRILLS_SOURCE '{mode}', defaulting to 'auto'")
            return DrillsSourceMode.AUTO
    
    @property
    def source_mode(self) -> str:
        """Get current source mode as string."""
        return self._source_mode.value
    
    @property
    def repository(self) -> DrillRepository:
        """Lazy load repository."""
        if self._repository is None:
            self._repository = get_drill_repository()
        return self._repository
    
    async def _get_db_count(self) -> int:
        """Get count of drills in database."""
        try:
            return await self.repository.count_drills()
        except Exception as e:
            logger.warning(f"DB count failed: {e}")
            return 0
    
    async def _should_use_db(self) -> bool:
        """
        Determine if DB should be used based on source mode.
        
        Returns:
            True if DB should be used, False for static
        """
        if self._source_mode == DrillsSourceMode.STATIC:
            return False
        
        if self._source_mode == DrillsSourceMode.DB:
            return True
        
        # Auto mode: use DB if has drills
        db_count = await self._get_db_count()
        return db_count > 0
    
    async def get_active_source(self) -> str:
        """Get which source is currently active."""
        if await self._should_use_db():
            return "database"
        return "static"
    
    def _convert_static_drill(self, drill_id: str, drill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert static drill format to DrillItem format.
        Maps old category names to new section names.
        """
        # Map old categories to new sections
        category_to_section = {
            "speed": "speed_agility",
            "agility": "speed_agility",
            "technical": "technical",
            "tactical": "tactical",
            "physical": "cardio",
            "psychological": "recovery",
            "possession": "possession",
            "shooting": "technical",
            "passing": "technical",
            "defending": "tactical",
            "conditioning": "cardio",
            "warmup": "mobility",
            "cooldown": "recovery",
            "strength": "gym",
            "flexibility": "mobility",
            "recovery": "recovery",
            "goalkeeper": "technical"
        }
        
        category = drill_data.get('category', 'technical').lower()
        section = category_to_section.get(category, 'technical')
        
        # Map intensity
        intensity_map = {
            "low": "low",
            "medium": "moderate",
            "high": "high",
            "maximum": "high"
        }
        old_intensity = drill_data.get('intensity', 'moderate').lower()
        intensity = intensity_map.get(old_intensity, 'moderate')
        
        return {
            "drill_id": drill_id,
            "name": drill_data.get('name', drill_id),
            "section": section,
            "tags": drill_data.get('tags', []),
            "intensity": intensity,
            "duration_min": drill_data.get('duration'),
            "equipment": drill_data.get('equipment_needed', []),
            "coaching_points": drill_data.get('instructions', []),
            "is_active": True,
            "_source": "static",
            # Preserve original data for compatibility
            "_original": {
                "description": drill_data.get('description'),
                "purpose": drill_data.get('purpose'),
                "expected_outcome": drill_data.get('expected_outcome'),
                "progression": drill_data.get('progression')
            }
        }
    
    async def get_drill(self, drill_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single drill by ID.
        
        In auto/db mode: tries DB first, falls back to static if allowed.
        In static mode: only checks static.
        """
        use_db = await self._should_use_db()
        
        # Try database first if in db/auto mode
        if use_db:
            try:
                drill = await self.repository.find_by_id(drill_id)
                if drill:
                    drill['_source'] = 'database'
                    logger.debug(f"Drill '{drill_id}' loaded from database")
                    return drill
            except Exception as e:
                logger.warning(f"DB lookup failed for drill '{drill_id}': {e}")
                if self._source_mode == DrillsSourceMode.DB:
                    raise DrillsNotAvailableError(f"Database error: {e}")
        
        # Check if we should fallback to static
        if self._source_mode == DrillsSourceMode.DB:
            # DB mode with no result = not found
            return None
        
        # Fallback to static (auto or static mode)
        if drill_id in EXERCISE_DATABASE:
            logger.debug(f"Drill '{drill_id}' loaded from static database")
            return self._convert_static_drill(drill_id, EXERCISE_DATABASE[drill_id])
        
        return None
    
    async def get_drills_by_section(self, section: str) -> List[Dict[str, Any]]:
        """
        Get all drills in a section.
        
        In auto mode with DB: returns DB drills only.
        In static mode: returns static drills mapped to section.
        """
        use_db = await self._should_use_db()
        
        if use_db:
            try:
                drills = await self.repository.find_by_section(section)
                for drill in drills:
                    drill['_source'] = 'database'
                logger.debug(f"Loaded {len(drills)} DB drills for section '{section}'")
                return drills
            except Exception as e:
                logger.warning(f"DB lookup failed for section '{section}': {e}")
                if self._source_mode == DrillsSourceMode.DB:
                    raise DrillsNotAvailableError(f"Database error: {e}")
        
        # Static mode or fallback
        drills = []
        for drill_id, drill_data in EXERCISE_DATABASE.items():
            converted = self._convert_static_drill(drill_id, drill_data)
            if converted['section'] == section:
                drills.append(converted)
        
        logger.debug(f"Loaded {len(drills)} static drills for section '{section}'")
        return drills
    
    async def get_all_drills(
        self,
        section: Optional[str] = None,
        tag: Optional[str] = None,
        age: Optional[int] = None,
        position: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all available drills with optional filters.
        """
        use_db = await self._should_use_db()
        
        if use_db:
            try:
                drills = await self.repository.find_all(
                    section=section,
                    tag=tag,
                    age=age,
                    position=position
                )
                for drill in drills:
                    drill['_source'] = 'database'
                logger.info(f"Loaded {len(drills)} drills from database")
                return drills
            except Exception as e:
                logger.warning(f"DB drill load failed: {e}")
                if self._source_mode == DrillsSourceMode.DB:
                    raise DrillsNotAvailableError(f"Database error: {e}")
        
        # Static mode or fallback
        drills = []
        for drill_id, drill_data in EXERCISE_DATABASE.items():
            converted = self._convert_static_drill(drill_id, drill_data)
            
            # Apply filters
            if section and converted['section'] != section:
                continue
            if tag and tag not in converted.get('tags', []):
                continue
            # Age and position filtering not supported for static drills
            
            drills.append(converted)
        
        logger.info(f"Loaded {len(drills)} drills from static database")
        return drills
    
    async def search_drills(
        self,
        query: Optional[str] = None,
        section: Optional[str] = None,
        intensity: Optional[str] = None,
        tags: Optional[List[str]] = None,
        exclude_contraindications: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search drills with filters.
        Useful for program generation to find suitable drills.
        """
        use_db = await self._should_use_db()
        
        if use_db:
            try:
                drills = await self.repository.search_drills(
                    query=query,
                    section=section,
                    intensity=intensity,
                    tags=tags,
                    contraindications_exclude=exclude_contraindications
                )
                for drill in drills:
                    drill['_source'] = 'database'
                return drills
            except Exception as e:
                logger.warning(f"DB drill search failed: {e}")
                if self._source_mode == DrillsSourceMode.DB:
                    raise DrillsNotAvailableError(f"Database error: {e}")
        
        # Static mode or fallback - basic filtering
        drills = []
        for drill_id, drill_data in EXERCISE_DATABASE.items():
            converted = self._convert_static_drill(drill_id, drill_data)
            
            # Apply filters
            if section and converted['section'] != section:
                continue
            if intensity and converted.get('intensity') != intensity:
                continue
            if tags and not any(t in converted.get('tags', []) for t in tags):
                continue
            if query:
                if query.lower() not in converted['name'].lower():
                    continue
            # Contraindication filtering not supported for static drills
            
            drills.append(converted)
        
        return drills
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about drill sources.
        """
        static_count = len(EXERCISE_DATABASE)
        db_count = 0
        db_available = False
        sections = {}
        
        try:
            db_count = await self.repository.count_drills()
            sections = await self.repository.count_by_section()
            db_available = True
        except Exception as e:
            logger.warning(f"DB stats failed: {e}")
        
        active_source = await self.get_active_source()
        
        return {
            "db_count": db_count,
            "static_count": static_count,
            "source_mode": self._source_mode.value,
            "active_source": active_source,
            "db_available": db_available,
            "sections": sections
        }
    
    def get_static_drill_ids(self) -> List[str]:
        """Get list of drill IDs from static database."""
        return list(EXERCISE_DATABASE.keys())
    
    async def is_db_available(self) -> bool:
        """Check if database is available for drill storage."""
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


def reset_drill_provider() -> None:
    """Reset the drill provider singleton (useful for testing)."""
    global _drill_provider
    _drill_provider = None
