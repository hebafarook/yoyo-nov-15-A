"""
Training Repository
===================

Database access layer for training-related operations.
Handles all MongoDB interactions for periodized programs and training programs.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from repositories.base import BaseRepository
from utils.database import db, prepare_for_mongo, parse_from_mongo
import logging

logger = logging.getLogger(__name__)


class TrainingRepository(BaseRepository):
    """Repository for training-related database operations."""
    
    def __init__(self):
        super().__init__(db.training_programs)
        self.periodized_programs = db.periodized_programs
        self.assessments = db.assessments
    
    # =========================================================================
    # PERIODIZED PROGRAMS
    # =========================================================================
    
    async def create_periodized_program(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new periodized program."""
        prepared_data = prepare_for_mongo(program_data)
        await self.periodized_programs.insert_one(prepared_data)
        logger.info(f"Periodized program created for player: {program_data.get('player_id')}")
        return program_data
    
    async def find_periodized_program_by_player(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Find the latest periodized program for a player."""
        doc = await self.periodized_programs.find_one(
            {"player_id": player_id},
            sort=[("created_at", -1)]
        )
        return parse_from_mongo(doc) if doc else None
    
    async def find_all_periodized_programs(self, player_id: str) -> List[Dict[str, Any]]:
        """Find all periodized programs for a player."""
        cursor = self.periodized_programs.find(
            {"player_id": player_id}
        ).sort("created_at", -1)
        docs = await cursor.to_list(length=1000)
        return [parse_from_mongo(doc) for doc in docs]
    
    # =========================================================================
    # TRAINING PROGRAMS (Legacy)
    # =========================================================================
    
    async def create_training_program(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new training program."""
        prepared_data = prepare_for_mongo(program_data)
        await self.collection.insert_one(prepared_data)
        logger.info(f"Training program created for player: {program_data.get('player_id')}")
        return program_data
    
    async def find_training_programs_by_player(self, player_id: str) -> List[Dict[str, Any]]:
        """Find all training programs for a player."""
        cursor = self.collection.find(
            {"player_id": player_id}
        ).sort("created_at", -1)
        docs = await cursor.to_list(length=1000)
        return [parse_from_mongo(doc) for doc in docs]
    
    async def find_training_program_by_id(self, program_id: str) -> Optional[Dict[str, Any]]:
        """Find a training program by ID."""
        doc = await self.collection.find_one({"id": program_id})
        return parse_from_mongo(doc) if doc else None
    
    # =========================================================================
    # ASSESSMENTS (for weakness analysis)
    # =========================================================================
    
    async def find_latest_assessment(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Find the latest assessment for a player."""
        doc = await self.assessments.find_one(
            {"player_name": player_name},
            sort=[("created_at", -1)]
        )
        return parse_from_mongo(doc) if doc else None
