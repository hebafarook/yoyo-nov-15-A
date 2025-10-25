import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def get_llm_client():
    """Get LLM client with Emergent integration"""
    try:
        # Get the Emergent LLM key from environment
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        return LlmChat(api_key=api_key)
    except Exception as e:
        logger.error(f"Error initializing LLM client: {e}")
        raise

async def generate_training_program(assessment_data: Dict[str, Any], week_number: int = 1, language: str = "en") -> str:
    """Generate AI-powered training program based on assessment data"""
    try:
        llm_client = get_llm_client()
        
        # Create assessment text
        assessment_text = f"""
        Player: {assessment_data['player_name']}
        Age: {assessment_data['age']} years
        Position: {assessment_data['position']}
        
        Current Week: {week_number}/14
        
        Physical Metrics (20%):
        - 30m Sprint: {assessment_data['sprint_30m']} seconds
        - Yo-Yo Test: {assessment_data['yo_yo_test']} meters
        - VO2 Max: {assessment_data['vo2_max']} ml/kg/min
        - Vertical Jump: {assessment_data['vertical_jump']} cm
        - Body Fat: {assessment_data['body_fat']}%
        
        Technical Skills (40%):
        - Ball Control: {assessment_data['ball_control']}/5
        - Passing Accuracy: {assessment_data['passing_accuracy']}%
        - Dribbling Success: {assessment_data['dribbling_success']}%
        - Shooting Accuracy: {assessment_data['shooting_accuracy']}%
        - Defensive Duels: {assessment_data['defensive_duels']}%
        
        Tactical Awareness (30%):
        - Game Intelligence: {assessment_data['game_intelligence']}/5
        - Positioning: {assessment_data['positioning']}/5
        - Decision Making: {assessment_data['decision_making']}/5
        
        Psychological (10%):
        - Coachability: {assessment_data['coachability']}/5
        - Mental Toughness: {assessment_data['mental_toughness']}/5
        """
        
        if language == "ar":
            prompt = f"""
            أنشئ برنامج تدريبي نخبوي متقدم وقابل للتكيف لـ يويو الفتى الناري للأسبوع {week_number}! 🔥👑

            {assessment_text}

            يرجى إنشاء برنامج نخبوي مليء بالطاقة والحماس يتضمن:
            1. تمارين سرعة متقدمة (30% من التدريب)
            2. تطوير المهارات التقنية تحت الضغط (40% من التدريب) 
            3. ذكاء تكتيكي وقراءة اللعب (20% من التدريب)
            4. القوة الذهنية والثقة (10% من التدريب)
            
            اجعل البرنامج:
            - مُخصص لنقاط القوة والضعف المحددة
            - متدرج في الصعوبة حسب الأسبوع
            - يحتوي على تمارين ممتعة ومبتكرة
            - يركز على تطوير اللاعب لمستوى النخبة
            
            قدم البرنامج بتنسيق منظم مع:
            - جدول أسبوعي مفصل (5 أيام تدريب)
            - أهداف واضحة لكل يوم
            - تعليمات مفصلة للتمارين
            - نصائح تحفيزية بأسلوب يويو الناري
            """
        else:
            prompt = f"""
            Create an elite advanced and adaptive training program for Yoyo the Fire Boy for week {week_number}! 🔥👑

            {assessment_text}

            Please create an elite program full of energy and enthusiasm that includes:
            1. Advanced speed exercises (30% of training)
            2. Technical skills development under pressure (40% of training)
            3. Tactical intelligence and game reading (20% of training)
            4. Mental strength and confidence (10% of training)
            
            Make the program:
            - Customized to identified strengths and weaknesses
            - Progressive in difficulty according to the week
            - Contains fun and innovative exercises
            - Focuses on developing the player to elite level
            
            Present the program in an organized format with:
            - Detailed weekly schedule (5 training days)
            - Clear objectives for each day
            - Detailed exercise instructions
            - Motivational tips in Yoyo the Fire Boy style
            """
        
        messages = [UserMessage(content=prompt)]
        response = await llm_client.chat_async(messages)
        
        return response.content
        
    except Exception as e:
        logger.error(f"Error generating training program: {e}")
        # Return a fallback program
        return generate_fallback_program(assessment_data, week_number, language)

def generate_fallback_program(assessment_data: Dict[str, Any], week_number: int, language: str = "en") -> str:
    """Generate a fallback training program when LLM is unavailable"""
    if language == "ar":
        return f"""
        برنامج تدريبي أسبوعي - الأسبوع {week_number}
        
        📋 أهداف الأسبوع:
        - تطوير السرعة والرشاقة
        - تحسين المهارات التقنية
        - بناء القوة البدنية
        - تعزيز الثقة بالنفس
        
        🏃‍♂️ اليوم الأول - السرعة والانطلاق:
        - إحماء: 10 دقائق جري خفيف
        - تمارين سرعة: 6 × 30 متر عدو
        - تمارين رشاقة: سلم السرعة
        - تهدئة: تمديد 10 دقائق
        
        ⚽ اليوم الثاني - المهارات التقنية:
        - إحماء مع الكرة: 15 دقيقة
        - تحكم بالكرة: تمرير دقيق
        - مراوغة: تمارين الأقماع
        - تسديد: تدريب على المرمى
        
        🏋️‍♂️ اليوم الثالث - القوة البدنية:
        - إحماء ديناميكي: 10 دقائق
        - تمارين القفز: 4 × 8 قفزات
        - تقوية الجذع: 15 دقيقة
        - استشفاء نشط: 10 دقائق
        
        🧠 اليوم الرابع - التكتيك والذكاء:
        - لعب مصغر: 4 ضد 4
        - تمارين اتخاذ القرار
        - تحليل مواقف اللعب
        - تدريب ذهني: 10 دقائق
        
        🔥 اليوم الخامس - المحاكاة:
        - مباراة تدريبية
        - تطبيق المهارات المكتسبة
        - تقييم الأداء
        - تحديد أهداف الأسبوع القادم
        
        💪 نصائح يويو الناري:
        - اعطي أقصى ما لديك في كل تمرين
        - لا تخف من ارتكاب الأخطاء، تعلم منها
        - استمع لمدربك واطلب النصيحة
        - حافظ على روحك القتالية دائماً
        """
    else:
        return f"""
        Weekly Training Program - Week {week_number}
        
        📋 Week Objectives:
        - Develop speed and agility
        - Improve technical skills
        - Build physical strength
        - Enhance confidence
        
        🏃‍♂️ Day 1 - Speed and Acceleration:
        - Warm-up: 10 minutes light jogging
        - Speed work: 6 × 30m sprints
        - Agility drills: Speed ladder
        - Cool-down: 10 minutes stretching
        
        ⚽ Day 2 - Technical Skills:
        - Ball warm-up: 15 minutes
        - Ball control: Precision passing
        - Dribbling: Cone weaving drills
        - Shooting: Goal practice
        
        🏋️‍♂️ Day 3 - Physical Strength:
        - Dynamic warm-up: 10 minutes
        - Jumping exercises: 4 × 8 jumps
        - Core strengthening: 15 minutes
        - Active recovery: 10 minutes
        
        🧠 Day 4 - Tactics and Intelligence:
        - Small-sided games: 4 vs 4
        - Decision-making drills
        - Game situation analysis
        - Mental training: 10 minutes
        
        🔥 Day 5 - Match Simulation:
        - Training match
        - Apply acquired skills
        - Performance evaluation
        - Set goals for next week
        
        💪 Yoyo Fire Boy Tips:
        - Give your maximum effort in every drill
        - Don't fear making mistakes, learn from them
        - Listen to your coach and ask for advice
        - Keep your fighting spirit always alive
        """

async def generate_adaptive_exercises(player_weaknesses: List[str], phase: str, week_number: int) -> Dict[str, Any]:
    """Generate adaptive exercises based on player weaknesses and training phase"""
    try:
        llm_client = get_llm_client()
        
        weaknesses_text = ", ".join(player_weaknesses)
        
        prompt = f"""
        Generate specific exercise recommendations for a soccer player with these weaknesses: {weaknesses_text}
        
        Training Phase: {phase}
        Week Number: {week_number}
        
        For each weakness, recommend:
        1. Specific exercise name
        2. Exercise difficulty level (beginner, intermediate, advanced)
        3. Recommended progression strategy
        4. Expected improvement timeline
        
        Format the response as JSON with this structure:
        {{
            "speed": [{{"exercise": "name", "level": "intermediate", "progression": "description"}}],
            "technical": [...],
            "tactical": [...],
            "reasoning": "Explanation of exercise selection"
        }}
        """
        
        messages = [UserMessage(content=prompt)]
        response = await llm_client.chat_async(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Return structured fallback if JSON parsing fails
            return generate_fallback_exercises(player_weaknesses, phase)
            
    except Exception as e:
        logger.error(f"Error generating adaptive exercises: {e}")
        return generate_fallback_exercises(player_weaknesses, phase)

def generate_fallback_exercises(player_weaknesses: List[str], phase: str) -> Dict[str, Any]:
    """Generate fallback exercise recommendations"""
    exercises = {
        "speed": [
            {
                "exercise": "30m Sprint Intervals",
                "level": "intermediate",
                "progression": "Increase intensity by 5% each week"
            }
        ],
        "technical": [
            {
                "exercise": "Ball Mastery Cone Weaving",
                "level": "intermediate", 
                "progression": "Reduce touches per cone weekly"
            }
        ],
        "tactical": [
            {
                "exercise": "4v4 Positional Play",
                "level": "intermediate",
                "progression": "Add decision-making pressure"
            }
        ],
        "reasoning": f"Selected exercises target identified weaknesses: {', '.join(player_weaknesses)} appropriate for {phase} phase"
    }
    
    return exercises