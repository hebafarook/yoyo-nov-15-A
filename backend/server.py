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
import random

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

# Models - Updated for Youth Handbook Standards
class PlayerAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_name: str
    age: int
    position: str
    # Physical performance metrics (from Youth Handbook)
    sprint_30m: float  # seconds - 30m sprint test
    yo_yo_test: int  # meters - Yo-Yo Intermittent Recovery Test  
    vo2_max: float  # ml/kg/min - Aerobic capacity
    vertical_jump: int  # cm - Vertical jump test
    body_fat: float  # percentage - Body fat percentage
    # Technical skills metrics (from Youth Handbook)
    ball_control: int  # 1-5 scale - Overall ball control assessment
    passing_accuracy: float  # percentage - Passing accuracy under pressure
    dribbling_success: float  # percentage - 1v1 dribbling success rate
    shooting_accuracy: float  # percentage - Shooting accuracy test
    defensive_duels: float  # percentage - Defensive duels won
    # Assessment metadata
    assessment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retest_scheduled: Optional[datetime] = None
    previous_assessment_id: Optional[str] = None  # For tracking progress between retests
    # Gamification
    total_coins: int = Field(default=0)
    level: int = Field(default=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssessmentCreate(BaseModel):
    player_name: str
    age: int
    position: str
    # Physical metrics
    sprint_30m: float
    yo_yo_test: int
    vo2_max: float
    vertical_jump: int
    body_fat: float
    # Technical metrics
    ball_control: int
    passing_accuracy: float
    dribbling_success: float
    shooting_accuracy: float
    defensive_duels: float

class TrainingProgram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    program_type: str  # "AI_Generated", "Ronaldo_Template", "Custom"
    program_content: str
    weekly_schedule: Dict[str, Any]
    milestones: List[Dict[str, Any]]
    is_group: bool = Field(default=False)
    group_members: List[str] = Field(default_factory=list)
    spotify_playlist: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrainingProgramCreate(BaseModel):
    player_id: str
    program_type: str
    is_group: Optional[bool] = False
    spotify_playlist: Optional[str] = None

class ProgressEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    metric_type: str  # "speed", "agility", "flexibility", "ball_handling"
    metric_name: str
    value: float
    coins_earned: int = Field(default=0)
    achievement_unlocked: Optional[str] = None
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

class Trophy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    trophy_name: str
    trophy_type: str  # "speed", "agility", "consistency", "group", "milestone"
    description: str
    coins_reward: int
    icon: str  # emoji or icon name
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroupTraining(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    training_name: str
    description: str
    members: List[str] = Field(default_factory=list)
    invited_members: List[str] = Field(default_factory=list)
    spotify_playlist: Optional[str] = None
    target_date: Optional[datetime] = None
    completion_reward: int = Field(default=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroupTrainingCreate(BaseModel):
    creator_id: str
    training_name: str
    description: str
    invited_members: List[str] = Field(default_factory=list)
    spotify_playlist: Optional[str] = None
    target_date: Optional[datetime] = None

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    title: str
    message: str
    notification_type: str  # "motivation", "wakeup", "achievement", "group"
    spotify_link: Optional[str] = None
    is_read: bool = Field(default=False)
    scheduled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationCreate(BaseModel):
    player_id: str
    title: str
    message: str
    notification_type: str
    spotify_link: Optional[str] = None
    scheduled_at: Optional[datetime] = None

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

# Achievement System
async def check_and_award_achievements(player_id: str, progress_entry: ProgressEntry) -> List[Trophy]:
    """Check for achievements and award trophies and coins"""
    trophies_awarded = []
    
    # Get player's progress history
    progress_history = await db.progress.find({"player_id": player_id}).to_list(1000)
    existing_trophies = await db.trophies.find({"player_id": player_id}).to_list(1000)
    existing_trophy_types = [trophy["trophy_type"] for trophy in existing_trophies]
    
    # Speed Achievement
    if progress_entry.metric_type == "speed" and "speed_master" not in existing_trophy_types:
        if progress_entry.value <= 4.0:  # Under 4 seconds for 40m
            trophy = Trophy(
                player_id=player_id,
                trophy_name="سيد السرعة",
                trophy_type="speed_master",
                description="حقق وقت أقل من 4 ثوان في عدو 40 متر",
                coins_reward=200,
                icon="🏃‍♂️"
            )
            trophies_awarded.append(trophy)
    
    # Consistency Achievement
    speed_entries = [p for p in progress_history if p.get("metric_type") == "speed"]
    if len(speed_entries) >= 5 and "consistency_king" not in existing_trophy_types:
        trophy = Trophy(
            player_id=player_id,
            trophy_name="ملك الثبات",
            trophy_type="consistency_king",
            description="سجل 5 إدخالات تقدم في السرعة",
            coins_reward=150,
            icon="👑"
        )
        trophies_awarded.append(trophy)
    
    # Fire Boy Special Achievement
    if progress_entry.metric_type == "ball_handling" and progress_entry.value >= 95 and "fire_boy" not in existing_trophy_types:
        trophy = Trophy(
            player_id=player_id,
            trophy_name="يويو الفتى الناري",
            trophy_type="fire_boy",
            description="حقق دقة 95% أو أكثر في التحكم بالكرة",
            coins_reward=500,
            icon="🔥"
        )
        trophies_awarded.append(trophy)
    
    # Save trophies and update coins
    total_coins_earned = 0
    for trophy in trophies_awarded:
        trophy_data = prepare_for_mongo(trophy.dict())
        await db.trophies.insert_one(trophy_data)
        total_coins_earned += trophy.coins_reward
    
    # Update player coins
    if total_coins_earned > 0:
        await db.assessments.update_one(
            {"id": player_id},
            {"$inc": {"total_coins": total_coins_earned}}
        )
    
    return trophies_awarded

# AI Training Program Generator in Arabic
async def generate_ai_training_program(assessment: PlayerAssessment) -> str:
    try:
        # Initialize LLM Chat
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"training_{assessment.id}",
            system_message="أنت مدرب يويو الفتى الناري، خبير تدريب كرة قدم محترف ومحفز. أنشئ برامج تدريبية ممتعة ومحفزة للشباب. يجب أن تجيب باللغة العربية فقط مع طاقة عالية وحماس."
        ).with_model("openai", "gpt-4o")

        # Create assessment summary in Arabic
        assessment_text = f"""
        بيانات تقييم يويو الفتى الناري:
        الاسم: {assessment.player_name}
        العمر: {assessment.age} سنة
        المركز: {assessment.position}
        المستوى: {assessment.level}
        العملات المجمعة: {assessment.total_coins}
        
        مقاييس السرعة:
        - عدو 40 متر: {assessment.sprint_40m} ثانية
        - عدو 100 متر: {assessment.sprint_100m} ثانية
        
        مقاييس الرشاقة:
        - تدريب المخاريط: {assessment.cone_drill} ثانية
        - تدريب السلم: {assessment.ladder_drill} ثانية
        - الجري المكوكي: {assessment.shuttle_run} ثانية
        
        مقاييس المرونة:
        - الجلوس والوصول: {assessment.sit_reach} سم
        - مرونة الكتف: {assessment.shoulder_flexibility} درجة
        - مرونة الورك: {assessment.hip_flexibility} درجة
        
        مقاييس التحكم بالكرة:
        - عدد الشقلبات: {assessment.juggling_count}
        - وقت المراوغة: {assessment.dribbling_time} ثانية
        - دقة التمرير: {assessment.passing_accuracy}%
        - دقة التسديد: {assessment.shooting_accuracy}%
        """

        prompt = f"""
        أنشئ برنامج تدريبي ناري ومحفز لـ يويو الفتى الناري لمدة 8 أسابيع! 🔥

        {assessment_text}

        يرجى إنشاء برنامج مليء بالطاقة والحماس يتضمن:
        1. تحليل نقاط القوة والضعف بطريقة محفزة
        2. تمارين ممتعة ومتحدية لكل نقطة ضعف
        3. أهداف أسبوعية قابلة للتحقيق مع مكافآت
        4. تحديات يومية صغيرة
        5. نصائح من أساطير كرة القدم
        6. كلمات تحفيزية قوية

        اجعل البرنامج مليئاً بالحماس والتشجيع! استخدم الرموز التعبيرية والكلمات المحفزة.
        
        يجب أن يكون الرد باللغة العربية فقط ومناسب ليويو الفتى الناري الشجاع!
        """

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response

    except Exception as e:
        logging.error(f"خطأ في إنشاء برنامج التدريب بالذكاء الاصطناعي: {e}")
        return "خطأ في إنشاء برنامج التدريب. يرجى المحاولة مرة أخرى."

# Routes
@api_router.get("/")
async def root():
    return {"message": "مرحباً بك في عالم يويو الفتى الناري! 🔥⚽"}

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
            raise HTTPException(status_code=404, detail="لم يتم العثور على تقييم يويو")
        return PlayerAssessment(**parse_from_mongo(assessment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/training-programs", response_model=TrainingProgram)
async def create_training_program(program: TrainingProgramCreate):
    try:
        # Get player assessment
        assessment = await db.assessments.find_one({"id": program.player_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="لم يتم العثور على تقييم يويو")
        
        assessment_obj = PlayerAssessment(**parse_from_mongo(assessment))
        
        # Generate program content based on type
        if program.program_type == "AI_Generated":
            program_content = await generate_ai_training_program(assessment_obj)
            weekly_schedule = {
                "Monday": "تدريب السرعة الناري 🔥",
                "Tuesday": "تحدي التحكم بالكرة ⚽",
                "Wednesday": "يوم المرونة والتعافي 🧘‍♂️",
                "Thursday": "مهارات يويو الفنية ✨",
                "Friday": "معركة محاكاة المباراة ⚔️",
                "Saturday": "تحدي نقاط الضعف 💪",
                "Sunday": "يوم راحة المحارب 😴"
            }
            milestones = [
                {"week": 2, "target": "فتح إنجاز السرعة الأولى 🏃‍♂️", "coins": 50},
                {"week": 4, "target": "كسب لقب محارب الرشاقة ⚡", "coins": 100},
                {"week": 6, "target": "إتقان مهارات يويو الناري 🔥", "coins": 150},
                {"week": 8, "target": "أن تصبح أسطورة يويو 👑", "coins": 300}
            ]
        elif program.program_type == "Ronaldo_Template":
            program_content = """
            🔥 برنامج يويو الفتى الناري المستوحى من رونالدو الأسطورة! 🔥
            
            هذا البرنامج الناري مبني على أسرار تدريب رونالدو:
            - الطاقة الانفجارية والسرعة البرقية ⚡
            - قوة العضلات الأساسية والمرونة المذهلة 💪
            - الدقة الفنية الساحرة ✨
            - العقلية الفولاذية 🧠
            
            🌟 الأسبوع 1-2: بناء أساسات المحارب الناري
            - تمارين القلب النارية يومياً لمدة ساعة 🏃‍♂️
            - تقوية العضلات الأساسية (200 تمرين معدة، بلانك ناري) 🔥
            - تدريبات التحكم بالكرة السحرية (1000 لمسة يومياً) ⚽
            - روتين المرونة الذهبية (30 دقيقة يوغا) 🧘‍♂️
            
            ⚡ الأسبوع 3-4: إشعال الطاقة الكامنة
            - فترات العدو الصاروخية (10x100 متر) 🚀
            - تمارين البليومتريك المتفجرة 💥
            - مهارات الكرة الأسطورية 🌟
            - تدريب الأثقال الناري (التركيز على الساقين) 🦵
            
            🎯 الأسبوع 5-6: إتقان فنون الساحر
            - تمرين الضربات الحرة الذهبية (50 محاولة يومياً) ⚽
            - تدريبات دقة التسديد القاتلة 🎯
            - التمرير والإنهاء الساحر ✨
            - معارك محاكاة المباراة الحقيقية ⚔️
            
            👑 الأسبوع 7-8: تحقيق المجد الأسطوري
            - تدريب الوحش عالي الكثافة 🔥
            - الإعداد النهائي للمنافسة 🏆
            - قوة التصور الذهني الفولاذية 🧠
            - تحسين التعافي الذهبي ✨
            """
            weekly_schedule = {
                "Monday": "يوم القوة والسرعة الناري 🔥",
                "Tuesday": "تحدي المهارات الفنية ✨",
                "Wednesday": "يوم العضلات الأساسية والمرونة 💪",
                "Thursday": "إتقان سحر الكرة ⚽",
                "Friday": "الإعداد الناري للمعركة ⚔️",
                "Saturday": "يوم المجد والمنافسة 🏆",
                "Sunday": "التعافي الذهبي للمحارب ✨"
            }
            milestones = [
                {"week": 2, "target": "إتقان 1000 لمسة سحرية ⚽", "coins": 100},
                {"week": 4, "target": "تحطيم الرقم القياسي في العدو ⚡", "coins": 150},
                {"week": 6, "target": "إتقان 80% من الضربات الحرة 🎯", "coins": 200},
                {"week": 8, "target": "أن تصبح أسطورة مثل رونالدو 👑", "coins": 500}
            ]
        else:
            program_content = "برنامج تدريب يويو المخصص سيتم تحديده قريباً! 🔥"
            weekly_schedule = {}
            milestones = []

        program_obj = TrainingProgram(
            player_id=program.player_id,
            program_type=program.program_type,
            program_content=program_content,
            weekly_schedule=weekly_schedule,
            milestones=milestones,
            is_group=program.is_group or False,
            spotify_playlist=program.spotify_playlist
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

@api_router.post("/progress", response_model=Dict[str, Any])
async def add_progress_entry(progress: ProgressEntryCreate):
    try:
        # Calculate coins based on improvement
        coins_earned = random.randint(10, 50)  # Base coins
        
        progress_obj = ProgressEntry(**progress.dict(), coins_earned=coins_earned)
        progress_data = prepare_for_mongo(progress_obj.dict())
        await db.progress.insert_one(progress_data)
        
        # Check for achievements
        trophies = await check_and_award_achievements(progress.player_id, progress_obj)
        
        return {
            "progress": progress_obj,
            "coins_earned": coins_earned,
            "trophies_unlocked": trophies,
            "message": f"مبروك يويو! حصلت على {coins_earned} عملة ذهبية! 🔥"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/progress/{player_id}", response_model=List[ProgressEntry])
async def get_progress(player_id: str):
    try:
        progress_entries = await db.progress.find({"player_id": player_id}).sort("date", -1).to_list(1000)
        return [ProgressEntry(**parse_from_mongo(entry)) for entry in progress_entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trophies/{player_id}", response_model=List[Trophy])
async def get_player_trophies(player_id: str):
    try:
        trophies = await db.trophies.find({"player_id": player_id}).sort("unlocked_at", -1).to_list(1000)
        return [Trophy(**parse_from_mongo(trophy)) for trophy in trophies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/group-training", response_model=GroupTraining)
async def create_group_training(group: GroupTrainingCreate):
    try:
        group_obj = GroupTraining(**group.dict())
        group_data = prepare_for_mongo(group_obj.dict())
        await db.group_trainings.insert_one(group_data)
        
        # Send invitations to members
        for member_id in group.invited_members:
            notification = Notification(
                player_id=member_id,
                title="دعوة للتدريب الجماعي! 🔥",
                message=f"يويو يدعوك للانضمام إلى '{group.training_name}'",
                notification_type="group",
                spotify_link=group.spotify_playlist
            )
            notification_data = prepare_for_mongo(notification.dict())
            await db.notifications.insert_one(notification_data)
            
        return group_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/group-training/{player_id}", response_model=List[GroupTraining])
async def get_group_trainings(player_id: str):
    try:
        groups = await db.group_trainings.find({
            "$or": [
                {"creator_id": player_id},
                {"members": player_id},
                {"invited_members": player_id}
            ]
        }).to_list(1000)
        return [GroupTraining(**parse_from_mongo(group)) for group in groups]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications", response_model=Notification)
async def create_notification(notification: NotificationCreate):
    try:
        notification_obj = Notification(**notification.dict())
        notification_data = prepare_for_mongo(notification_obj.dict())
        await db.notifications.insert_one(notification_data)
        return notification_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications/{player_id}", response_model=List[Notification])
async def get_notifications(player_id: str):
    try:
        notifications = await db.notifications.find({"player_id": player_id}).sort("created_at", -1).to_list(1000)
        return [Notification(**parse_from_mongo(notification)) for notification in notifications]
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
    format='%(asctime)s - %(name)s - %(levelevel)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()