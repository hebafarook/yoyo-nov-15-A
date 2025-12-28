from fastapi import FastAPI, APIRouter, HTTPException, status
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import random

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
database_name = os.environ.get('DB_NAME', 'soccer_training_db')
client = AsyncIOMotorClient(mongo_url)
db = client[database_name]

# Create the main app
app = FastAPI(
    title="Elite Soccer Player AI Coach API",
    description="Comprehensive soccer player development platform with AI-powered training programs",
    version="1.0.0"
)

# Register central error handlers
from utils.error_handlers import register_exception_handlers
register_exception_handlers(app)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure CORS (single source of truth)
from utils.cors_config import configure_cors
configure_cors(app)

# Import all models and routes
from models import *
from routes.assessment_routes import router as assessment_router
from routes.assessment_routes_public import router as assessment_public_router
from routes.training_routes import router as training_router
from routes.elite_training_routes import router as elite_training_router
from routes.vo2_routes import router as vo2_router
from routes.progress_routes import router as progress_router
from routes.auth_routes import router as auth_router
from routes.admin_drills_routes import router as admin_drills_router
from utils.database import prepare_for_mongo, parse_from_mongo
from utils.llm_integration import generate_training_program

# Include all routers
api_router.include_router(assessment_router, prefix="/assessments", tags=["assessments"])
api_router.include_router(assessment_public_router, prefix="/assessments", tags=["assessments-public"])
api_router.include_router(training_router, prefix="/training", tags=["training"])
api_router.include_router(elite_training_router, tags=["elite-training"])
api_router.include_router(vo2_router, prefix="/vo2-benchmarks", tags=["vo2-benchmarks"])
api_router.include_router(progress_router, prefix="/progress", tags=["progress"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(admin_drills_router, tags=["admin-drills"])

# Import Coach Drills routes
from routes.coach_drills_routes import router as coach_drills_router
api_router.include_router(coach_drills_router, tags=["coach-drills"])

# YoYo Report v2 routes (presentation layer)
try:
    from api.routes.report_v2 import router as report_v2_router
    api_router.include_router(report_v2_router, prefix="/v2/report", tags=["yoyo-report-v2"])
except ImportError:
    logger.warning("Could not import YoYo Report v2 routes")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Elite Soccer Player AI Coach API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8001)),
        reload=os.environ.get("ENVIRONMENT") == "development"
    )