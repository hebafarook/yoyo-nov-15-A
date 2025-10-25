from typing import Dict, Any, List
import math

# Youth Handbook Standards - Age-based performance benchmarks
YOUTH_HANDBOOK_STANDARDS = {
    "12-14": {
        "sprint_30m": {"excellent": 4.5, "good": 4.8, "average": 5.1, "poor": 5.4},
        "yo_yo_test": {"excellent": 1400, "good": 1200, "average": 1000, "poor": 800},
        "vo2_max": {"excellent": 52, "good": 50, "average": 49, "poor": 48},
        "vertical_jump": {"excellent": 45, "good": 40, "average": 35, "poor": 30},
        "body_fat": {"excellent": 8, "good": 10, "average": 12, "poor": 15},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 85, "good": 80, "average": 75, "poor": 70},
        "dribbling_success": {"excellent": 80, "good": 70, "average": 60, "poor": 50},
        "shooting_accuracy": {"excellent": 75, "good": 70, "average": 65, "poor": 60},
        "defensive_duels": {"excellent": 85, "good": 75, "average": 65, "poor": 55},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    },
    "15-16": {
        "sprint_30m": {"excellent": 4.2, "good": 4.5, "average": 4.8, "poor": 5.1},
        "yo_yo_test": {"excellent": 1600, "good": 1400, "average": 1200, "poor": 1000},
        "vo2_max": {"excellent": 56, "good": 54, "average": 53, "poor": 52},
        "vertical_jump": {"excellent": 50, "good": 45, "average": 40, "poor": 35},
        "body_fat": {"excellent": 7, "good": 9, "average": 11, "poor": 14},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 88, "good": 83, "average": 78, "poor": 73},
        "dribbling_success": {"excellent": 83, "good": 73, "average": 63, "poor": 53},
        "shooting_accuracy": {"excellent": 78, "good": 73, "average": 68, "poor": 63},
        "defensive_duels": {"excellent": 88, "good": 78, "average": 68, "poor": 58},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    },
    "17-18": {
        "sprint_30m": {"excellent": 4.0, "good": 4.3, "average": 4.6, "poor": 4.9},
        "yo_yo_test": {"excellent": 1800, "good": 1600, "average": 1400, "poor": 1200},
        "vo2_max": {"excellent": 60, "good": 58, "average": 57, "poor": 56},
        "vertical_jump": {"excellent": 55, "good": 50, "average": 45, "poor": 40},
        "body_fat": {"excellent": 6, "good": 8, "average": 10, "poor": 13},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 90, "good": 85, "average": 80, "poor": 75},
        "dribbling_success": {"excellent": 85, "good": 75, "average": 65, "poor": 55},
        "shooting_accuracy": {"excellent": 80, "good": 75, "average": 70, "poor": 65},
        "defensive_duels": {"excellent": 90, "good": 80, "average": 70, "poor": 60},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    },
    "elite": {
        "sprint_30m": {"excellent": 3.8, "good": 4.0, "average": 4.2, "poor": 4.5},
        "yo_yo_test": {"excellent": 2200, "good": 2000, "average": 1800, "poor": 1600},
        "vo2_max": {"excellent": 65, "good": 62, "average": 60, "poor": 58},
        "vertical_jump": {"excellent": 65, "good": 60, "average": 55, "poor": 50},
        "body_fat": {"excellent": 5, "good": 7, "average": 9, "poor": 12},
        "ball_control": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "passing_accuracy": {"excellent": 92, "good": 88, "average": 84, "poor": 80},
        "dribbling_success": {"excellent": 88, "good": 80, "average": 72, "poor": 64},
        "shooting_accuracy": {"excellent": 85, "good": 80, "average": 75, "poor": 70},
        "defensive_duels": {"excellent": 92, "good": 84, "average": 76, "poor": 68},
        "game_intelligence": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "positioning": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "decision_making": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "coachability": {"excellent": 5, "good": 4, "average": 3, "poor": 2},
        "mental_toughness": {"excellent": 5, "good": 4, "average": 3, "poor": 2}
    }
}

def get_age_category(age: int) -> str:
    """Determine age category based on player age"""
    if age <= 14:
        return "12-14"
    elif age <= 16:
        return "15-16"
    elif age <= 18:
        return "17-18"
    else:
        return "elite"

def evaluate_performance(value: float, metric: str, age: int) -> str:
    """Evaluate performance level based on youth handbook standards"""
    age_category = get_age_category(age)
    standards = YOUTH_HANDBOOK_STANDARDS.get(age_category, {})
    metric_standards = standards.get(metric, {})
    
    if not metric_standards:
        return "average"
    
    # Handle metrics where lower is better (sprint times, body fat)
    lower_is_better = metric in ['sprint_30m', 'body_fat']
    
    if lower_is_better:
        if value <= metric_standards['excellent']:
            return "excellent"
        elif value <= metric_standards['good']:
            return "good"
        elif value <= metric_standards['average']:
            return "average"
        else:
            return "poor"
    else:
        if value >= metric_standards['excellent']:
            return "excellent"
        elif value >= metric_standards['good']:
            return "good"
        elif value >= metric_standards['average']:
            return "average"
        else:
            return "poor"

def calculate_overall_score(assessment_data: Dict[str, Any]) -> float:
    """Calculate weighted overall score based on Youth Handbook methodology"""
    age = assessment_data.get('age', 18)
    
    # Define category weights
    weights = {
        'physical': 0.20,
        'technical': 0.40, 
        'tactical': 0.30,
        'psychological': 0.10
    }
    
    # Define metrics for each category
    categories = {
        'physical': ['sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat'],
        'technical': ['ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels'],
        'tactical': ['game_intelligence', 'positioning', 'decision_making'],
        'psychological': ['coachability', 'mental_toughness']
    }
    
    category_scores = {}
    
    for category, metrics in categories.items():
        total_score = 0
        valid_metrics = 0
        
        for metric in metrics:
            value = assessment_data.get(metric)
            if value is not None and value != "":
                performance = evaluate_performance(float(value), metric, age)
                score = get_performance_score(performance)
                total_score += score
                valid_metrics += 1
        
        if valid_metrics > 0:
            category_scores[category] = (total_score / valid_metrics) * 20  # Convert to 100-point scale
        else:
            category_scores[category] = 0
    
    # Calculate weighted overall score
    overall_score = sum(category_scores[cat] * weights[cat] for cat in weights.keys())
    
    return min(100, max(0, overall_score))  # Ensure score is between 0-100

def get_performance_score(performance: str) -> float:
    """Convert performance level to numerical score"""
    scores = {
        "excellent": 5.0,
        "good": 4.0,
        "average": 3.0,
        "poor": 2.0
    }
    return scores.get(performance, 3.0)

def get_performance_level(overall_score: float) -> str:
    """Determine performance level based on overall score"""
    if overall_score >= 85:
        return "Elite"
    elif overall_score >= 75:
        return "Advanced"
    elif overall_score >= 65:
        return "Intermediate"
    elif overall_score >= 50:
        return "Developing"
    else:
        return "Beginner"

def analyze_strengths_and_weaknesses(assessment_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Analyze player strengths and weaknesses based on assessment"""
    age = assessment_data.get('age', 18)
    strengths = []
    weaknesses = []
    
    # Define all metrics to analyze
    all_metrics = {
        'Sprint Speed (30m)': 'sprint_30m',
        'Endurance (Yo-Yo)': 'yo_yo_test', 
        'VO2 Max': 'vo2_max',
        'Vertical Jump': 'vertical_jump',
        'Body Fat': 'body_fat',
        'Ball Control': 'ball_control',
        'Passing Accuracy': 'passing_accuracy',
        'Dribbling Success': 'dribbling_success',
        'Shooting Accuracy': 'shooting_accuracy',
        'Defensive Duels': 'defensive_duels',
        'Game Intelligence': 'game_intelligence',
        'Positioning': 'positioning',
        'Decision Making': 'decision_making',
        'Coachability': 'coachability',
        'Mental Toughness': 'mental_toughness'
    }
    
    for display_name, metric_key in all_metrics.items():
        value = assessment_data.get(metric_key)
        if value is not None and value != "":
            performance = evaluate_performance(float(value), metric_key, age)
            
            if performance == "excellent":
                strengths.append(f"{display_name}: {value} (Excellent)")
            elif performance == "poor":
                weaknesses.append(f"{display_name}: {value} (Needs Improvement)")
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses
    }

def generate_training_recommendations(analysis: Dict[str, List[str]], performance_level: str) -> List[str]:
    """Generate training recommendations based on analysis"""
    recommendations = []
    
    # Base recommendations by performance level
    if performance_level == "Elite":
        recommendations.extend([
            "Focus on maintaining peak performance and mental preparation for competitions",
            "Consider advanced tactical training and leadership development"
        ])
    elif performance_level == "Advanced":
        recommendations.extend([
            "Work on consistency in high-pressure situations", 
            "Focus on specialized position-specific skills"
        ])
    elif performance_level == "Intermediate":
        recommendations.extend([
            "Increase training intensity and focus on technical refinement",
            "Develop tactical understanding through match analysis"
        ])
    else:
        recommendations.extend([
            "Focus on fundamental skills development and fitness base",
            "Increase training frequency and consistency"
        ])
    
    # Add weakness-specific recommendations
    weaknesses = analysis.get('weaknesses', [])
    for weakness in weaknesses[:3]:  # Limit to top 3 weaknesses
        if 'Sprint Speed' in weakness:
            recommendations.append("Implement speed training: 30m sprints, acceleration drills")
        elif 'Endurance' in weakness or 'Yo-Yo' in weakness:
            recommendations.append("Increase cardiovascular training: interval running, yo-yo test practice")
        elif 'Ball Control' in weakness:
            recommendations.append("Daily ball work: cone weaving, first touch drills")
        elif 'Mental Toughness' in weakness:
            recommendations.append("Mental training: visualization, pressure situation practice")
        elif 'Passing' in weakness:
            recommendations.append("Precision passing drills: short and long range accuracy")
    
    return recommendations[:5]  # Return top 5 recommendations