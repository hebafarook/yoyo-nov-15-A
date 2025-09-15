from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class PlayerAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_name: str
    age: int
    position: str
    # Speed metrics
    sprint_40m: float  # seconds
    sprint_100m: float  # seconds
    # Agility metrics
    cone_drill: float  # seconds
    ladder_drill: float  # seconds
    shuttle_run: float  # seconds
    # Flexibility metrics
    sit_reach: float  # cm
    shoulder_flexibility: float  # degrees
    hip_flexibility: float  # degrees
    # Ball handling metrics
    juggling_count: int
    dribbling_time: float  # seconds
    passing_accuracy: float  # percentage
    shooting_accuracy: float  # percentage
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssessmentCreate(BaseModel):
    player_name: str
    age: int
    position: str
    sprint_40m: float
    sprint_100m: float
    cone_drill: float
    ladder_drill: float
    shuttle_run: float
    sit_reach: float
    shoulder_flexibility: float
    hip_flexibility: float
    juggling_count: int
    dribbling_time: float
    passing_accuracy: float
    shooting_accuracy: float

class TrainingProgram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    program_type: str  # "AI_Generated", "Ronaldo_Template", "Custom"
    program_content: str
    weekly_schedule: Dict[str, Any]
    milestones: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrainingProgramCreate(BaseModel):
    player_id: str
    program_type: str

class ProgressEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    metric_type: str  # "speed", "agility", "flexibility", "ball_handling"
    metric_name: str
    value: float
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProgressEntryCreate(BaseModel):
    player_id: str
    metric_type: str
    metric_name: str
    value: float

class VoiceNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    note_text: str
    audio_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VoiceNoteCreate(BaseModel):
    player_id: str
    note_text: str
    audio_duration: Optional[float] = None

# Helper function to prepare data for MongoDB
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

# Helper function to parse data from MongoDB
def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and key.endswith('_at'):
                try:
                    item[key] = datetime.fromisoformat(value)
                except:
                    pass
    return item

# AI Training Program Generator
async def generate_ai_training_program(assessment: PlayerAssessment) -> str:
    try:
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"training_{assessment.id}",
            system_message="You are a professional soccer training expert specializing in creating personalized training programs based on player assessments."
        ).with_model("openai", "gpt-4o")

        # Create assessment summary
        assessment_text = f"""
        Player Assessment Data:
        Name: {assessment.player_name}
        Age: {assessment.age}
        Position: {assessment.position}
        
        Speed Metrics:
        - 40m Sprint: {assessment.sprint_40m}s
        - 100m Sprint: {assessment.sprint_100m}s
        
        Agility Metrics:
        - Cone Drill: {assessment.cone_drill}s
        - Ladder Drill: {assessment.ladder_drill}s
        - Shuttle Run: {assessment.shuttle_run}s
        
        Flexibility Metrics:
        - Sit & Reach: {assessment.sit_reach}cm
        - Shoulder Flexibility: {assessment.shoulder_flexibility}°
        - Hip Flexibility: {assessment.hip_flexibility}°
        
        Ball Handling Metrics:
        - Juggling Count: {assessment.juggling_count}
        - Dribbling Time: {assessment.dribbling_time}s
        - Passing Accuracy: {assessment.passing_accuracy}%
        - Shooting Accuracy: {assessment.shooting_accuracy}%
        """

        prompt = f"""
        Based on the following player assessment, create a comprehensive 8-week training program focused on improving the player's weakest areas while maintaining strengths.

        {assessment_text}

        Please provide:
        1. A detailed analysis of strengths and weaknesses
        2. Specific training exercises for each weakness
        3. Weekly progression plan
        4. Key milestones to track
        5. Professional tips inspired by elite players like Ronaldo

        Format the response in a structured way with clear sections for each week.
        """

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response

    except Exception as e:
        logging.error(f"Error generating AI training program: {e}")
        return "Error generating training program. Please try again."

# Routes
@api_router.get("/")
async def root():
    return {"message": "Soccer Pro Training Tracker API"}

@api_router.post("/assessments", response_model=PlayerAssessment)
async def create_assessment(assessment: AssessmentCreate):
    try:
        assessment_dict = assessment.dict()
        assessment_obj = PlayerAssessment(**assessment_dict)
        assessment_data = prepare_for_mongo(assessment_obj.dict())
        await db.assessments.insert_one(assessment_data)
        return assessment_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessments", response_model=List[PlayerAssessment])
async def get_assessments():
    try:
        assessments = await db.assessments.find().to_list(1000)
        return [PlayerAssessment(**parse_from_mongo(assessment)) for assessment in assessments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessments/{player_id}", response_model=PlayerAssessment)
async def get_assessment(player_id: str):
    try:
        assessment = await db.assessments.find_one({"id": player_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return PlayerAssessment(**parse_from_mongo(assessment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/training-programs", response_model=TrainingProgram)
async def create_training_program(program: TrainingProgramCreate):
    try:
        # Get player assessment
        assessment = await db.assessments.find_one({"id": program.player_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Player assessment not found")
        
        assessment_obj = PlayerAssessment(**parse_from_mongo(assessment))
        
        # Generate program content based on type
        if program.program_type == "AI_Generated":
            program_content = await generate_ai_training_program(assessment_obj)
            weekly_schedule = {
                "Monday": "Speed and Agility Training",
                "Tuesday": "Ball Handling Drills",
                "Wednesday": "Flexibility and Recovery",
                "Thursday": "Technical Skills",
                "Friday": "Match Simulation",
                "Saturday": "Individual Weaknesses Focus",
                "Sunday": "Rest Day"
            }
            milestones = [
                {"week": 2, "target": "10% improvement in weakest metric"},
                {"week": 4, "target": "15% improvement in agility"},
                {"week": 6, "target": "20% improvement in ball handling"},
                {"week": 8, "target": "Overall assessment improvement"}
            ]
        elif program.program_type == "Ronaldo_Template":
            program_content = """
            CRISTIANO RONALDO INSPIRED TRAINING PROGRAM
            
            This program is based on Ronaldo's training methodology focusing on:
            - Explosive power and speed
            - Core strength and flexibility
            - Technical precision
            - Mental resilience
            
            WEEK 1-2: Foundation Building
            - Daily 1-hour cardio (running/cycling)
            - Core strengthening (200 sit-ups, planks)
            - Ball control drills (1000 touches daily)
            - Flexibility routine (30 mins yoga)
            
            WEEK 3-4: Intensity Increase
            - Sprint intervals (10x100m)
            - Plyometric exercises
            - Advanced ball skills
            - Weight training (legs focus)
            
            WEEK 5-6: Technical Mastery
            - Free kick practice (50 attempts daily)
            - Shooting accuracy drills
            - Crossing and finishing
            - Match simulation
            
            WEEK 7-8: Peak Performance
            - High-intensity interval training
            - Competition preparation
            - Mental visualization
            - Recovery optimization
            """
            weekly_schedule = {
                "Monday": "Power and Speed",
                "Tuesday": "Technical Skills",
                "Wednesday": "Core and Flexibility",
                "Thursday": "Ball Mastery",
                "Friday": "Match Preparation",
                "Saturday": "Competition Day",
                "Sunday": "Active Recovery"
            }
            milestones = [
                {"week": 2, "target": "Master 1000 ball touches"},
                {"week": 4, "target": "Improve sprint time by 0.2s"},
                {"week": 6, "target": "80% free kick accuracy"},
                {"week": 8, "target": "Professional level fitness"}
            ]
        else:
            program_content = "Custom training program to be defined."
            weekly_schedule = {}
            milestones = []

        program_obj = TrainingProgram(
            player_id=program.player_id,
            program_type=program.program_type,
            program_content=program_content,
            weekly_schedule=weekly_schedule,
            milestones=milestones
        )
        
        program_data = prepare_for_mongo(program_obj.dict())
        await db.training_programs.insert_one(program_data)
        return program_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/training-programs/{player_id}", response_model=List[TrainingProgram])
async def get_training_programs(player_id: str):
    try:
        programs = await db.training_programs.find({"player_id": player_id}).to_list(1000)
        return [TrainingProgram(**parse_from_mongo(program)) for program in programs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/progress", response_model=ProgressEntry)
async def add_progress_entry(progress: ProgressEntryCreate):
    try:
        progress_obj = ProgressEntry(**progress.dict())
        progress_data = prepare_for_mongo(progress_obj.dict())
        await db.progress.insert_one(progress_data)
        return progress_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/progress/{player_id}", response_model=List[ProgressEntry])
async def get_progress(player_id: str):
    try:
        progress_entries = await db.progress.find({"player_id": player_id}).sort("date", -1).to_list(1000)
        return [ProgressEntry(**parse_from_mongo(entry)) for entry in progress_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/voice-notes", response_model=VoiceNote)
async def add_voice_note(note: VoiceNoteCreate):
    try:
        note_obj = VoiceNote(**note.dict())
        note_data = prepare_for_mongo(note_obj.dict())
        await db.voice_notes.insert_one(note_data)
        return note_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/voice-notes/{player_id}", response_model=List[VoiceNote])
async def get_voice_notes(player_id: str):
    try:
        notes = await db.voice_notes.find({"player_id": player_id}).sort("created_at", -1).to_list(1000)
        return [VoiceNote(**parse_from_mongo(note)) for note in notes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()