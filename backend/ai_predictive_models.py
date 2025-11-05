"""
AI Predictive Models for Soccer Training
Includes: Injury Risk, Performance Forecasting, Match Readiness, Optimal Load
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import statistics
import math

class PredictiveAnalysis(BaseModel):
    injury_risk: Dict[str, Any]
    performance_forecast: Dict[str, Any]
    match_readiness: Dict[str, Any]
    optimal_training_load: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

class InjuryRiskPredictor:
    """Predicts injury risk based on training load, wellness, and fatigue patterns"""
    
    def predict(self, 
                training_loads: List[Dict],
                wellness_logs: List[Dict],
                recent_assessments: List[Dict]) -> Dict[str, Any]:
        """
        Calculate injury risk score (0-100)
        Higher score = Higher risk
        """
        
        risk_factors = {
            "load_spike": 0,
            "chronic_fatigue": 0,
            "recovery_deficit": 0,
            "biomechanical_risk": 0,
            "overtraining": 0
        }
        
        # 1. Training Load Analysis (ACWR - Acute:Chronic Workload Ratio)
        chronic = 0  # Initialize chronic variable
        if len(training_loads) >= 28:
            # Acute load (last 7 days)
            acute = sum(load.get('total_distance_m', 0) for load in training_loads[:7]) / 7
            # Chronic load (last 28 days)
            chronic = sum(load.get('total_distance_m', 0) for load in training_loads[:28]) / 28
            
            if chronic > 0:
                acwr = acute / chronic
                # Optimal ACWR: 0.8-1.3
                # High risk: <0.5 or >1.5
                if acwr > 1.5:
                    risk_factors["load_spike"] = min(30, (acwr - 1.5) * 30)  # Max 30 points
                elif acwr < 0.5:
                    risk_factors["load_spike"] = 15  # Detraining risk
        
        # 2. Wellness Analysis
        if wellness_logs:
            recent_wellness = wellness_logs[:7]  # Last 7 days
            avg_soreness = statistics.mean([w.get('soreness_1_5', 3) for w in recent_wellness])
            avg_sleep = statistics.mean([w.get('sleep_hours', 7) for w in recent_wellness])
            avg_mood = statistics.mean([w.get('mood_1_5', 3) for w in recent_wellness])
            
            # Poor soreness (1-2 = very sore)
            if avg_soreness <= 2:
                risk_factors["chronic_fatigue"] = 25
            
            # Poor sleep (<6h average)
            if avg_sleep < 6:
                risk_factors["recovery_deficit"] = 20
            
            # Poor mood (indicates overtraining)
            if avg_mood <= 2:
                risk_factors["overtraining"] = 15
        
        # 3. Movement Pattern Analysis from Assessments
        if recent_assessments:
            latest = recent_assessments[0]
            
            # Asymmetry indicators
            sprint_performance = latest.get('sprint_30m', 4.5)
            if sprint_performance > 5.0:  # Slow sprint = possible mobility issue
                risk_factors["biomechanical_risk"] = 15
            
            # Jump performance (power asymmetry)
            vertical_jump = latest.get('vertical_jump', 50)
            if vertical_jump < 40:  # Low power = injury risk
                risk_factors["biomechanical_risk"] += 10
        
        # Calculate total risk
        total_risk = sum(risk_factors.values())
        risk_level = "Low"
        if total_risk > 60:
            risk_level = "High"
        elif total_risk > 35:
            risk_level = "Moderate"
        
        return {
            "risk_score": min(100, total_risk),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": self._get_injury_recommendations(risk_factors, risk_level),
            "acwr_status": "Optimal" if 0.8 <= (acute/chronic if chronic > 0 else 1.0) <= 1.3 else "Sub-optimal"
        }
    
    def _get_injury_recommendations(self, factors: Dict, level: str) -> List[str]:
        recs = []
        
        if factors["load_spike"] > 20:
            recs.append("⚠️ Reduce training volume by 20-30% this week")
        
        if factors["chronic_fatigue"] > 15:
            recs.append("💤 Prioritize recovery: 8-9h sleep, active recovery days")
        
        if factors["recovery_deficit"] > 15:
            recs.append("🛌 Sleep optimization needed - target 8+ hours nightly")
        
        if factors["biomechanical_risk"] > 15:
            recs.append("🏃 Movement screening recommended - check for asymmetries")
        
        if factors["overtraining"] > 10:
            recs.append("🧘 Consider deload week - reduce intensity 40-50%")
        
        if level == "Low":
            recs.append("✅ Current training load is well-tolerated")
        
        return recs

class PerformanceForecaster:
    """Forecasts future performance based on assessment history"""
    
    def forecast(self, assessments: List[Dict], weeks_ahead: int = 12) -> Dict[str, Any]:
        """
        Predict performance trajectory based on historical assessments
        """
        
        if len(assessments) < 2:
            return {
                "forecast_available": False,
                "message": "Need at least 2 assessments for forecasting",
                "predicted_improvement": None
            }
        
        # Sort by date
        sorted_assessments = sorted(assessments, key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Calculate improvement rate
        improvements = []
        for i in range(len(sorted_assessments) - 1):
            current = sorted_assessments[i].get('overall_score', 0)
            previous = sorted_assessments[i + 1].get('overall_score', 0)
            improvement = current - previous
            improvements.append(improvement)
        
        avg_improvement_rate = statistics.mean(improvements) if improvements else 0
        
        # Current performance
        current_score = sorted_assessments[0].get('overall_score', 0)
        
        # Forecast (with diminishing returns)
        predicted_scores = []
        for week in range(1, weeks_ahead + 1):
            # Diminishing returns: each week contributes less
            diminishing_factor = 1 / (1 + 0.1 * week)
            predicted = current_score + (avg_improvement_rate * week * diminishing_factor)
            predicted_scores.append(min(100, max(0, predicted)))
        
        # Performance categories
        final_predicted = predicted_scores[-1]
        current_category = self._get_category(current_score)
        predicted_category = self._get_category(final_predicted)
        
        return {
            "forecast_available": True,
            "current_score": round(current_score, 1),
            "current_category": current_category,
            "predicted_score_12_weeks": round(final_predicted, 1),
            "predicted_category": predicted_category,
            "improvement_rate_per_week": round(avg_improvement_rate, 2),
            "weekly_predictions": [round(s, 1) for s in predicted_scores],
            "confidence": self._calculate_confidence(improvements),
            "breakthrough_week": self._find_breakthrough_week(predicted_scores, current_category)
        }
    
    def _get_category(self, score: float) -> str:
        if score >= 85:
            return "Elite"
        elif score >= 70:
            return "Advanced"
        elif score >= 55:
            return "Intermediate"
        elif score >= 40:
            return "Developing"
        else:
            return "Beginner"
    
    def _calculate_confidence(self, improvements: List[float]) -> str:
        if not improvements:
            return "Low"
        
        variance = statistics.variance(improvements) if len(improvements) > 1 else 0
        
        if variance < 5:
            return "High"
        elif variance < 15:
            return "Moderate"
        else:
            return "Low"
    
    def _find_breakthrough_week(self, predictions: List[float], current_category: str) -> Optional[int]:
        """Find week when player breaks through to next level"""
        thresholds = {"Beginner": 40, "Developing": 55, "Intermediate": 70, "Advanced": 85}
        
        if current_category not in thresholds:
            return None
        
        target = thresholds[current_category]
        
        for week, score in enumerate(predictions, 1):
            if score >= target:
                return week
        
        return None

class MatchReadinessCalculator:
    """Calculate match readiness score"""
    
    def calculate(self,
                  recent_assessment: Dict,
                  wellness: Dict,
                  training_load: Dict,
                  days_to_match: int) -> Dict[str, Any]:
        """
        Calculate 0-100 match readiness score
        """
        
        components = {
            "physical_readiness": 0,
            "technical_sharpness": 0,
            "tactical_preparedness": 0,
            "mental_state": 0,
            "recovery_status": 0
        }
        
        # 1. Physical Readiness (30 points)
        if recent_assessment:
            sprint = recent_assessment.get('sprint_30m', 5.0)
            endurance = recent_assessment.get('yo_yo_test', 1000)
            power = recent_assessment.get('vertical_jump', 40)
            
            # Sprint score (lower is better)
            sprint_score = max(0, 10 - (sprint - 4.0) * 2) if sprint >= 4.0 else 10
            # Endurance score
            endurance_score = min(10, endurance / 150)
            # Power score
            power_score = min(10, power / 6)
            
            components["physical_readiness"] = sprint_score + endurance_score + power_score
        
        # 2. Technical Sharpness (20 points)
        if recent_assessment:
            ball_control = recent_assessment.get('ball_control', 3)
            passing = recent_assessment.get('passing_accuracy', 60)
            shooting = recent_assessment.get('shooting_accuracy', 50)
            
            components["technical_sharpness"] = (
                ball_control * 4 + 
                passing / 5 + 
                shooting / 10
            )
        
        # 3. Tactical Preparedness (20 points)
        if recent_assessment:
            intelligence = recent_assessment.get('game_intelligence', 3)
            positioning = recent_assessment.get('positioning', 3)
            decision = recent_assessment.get('decision_making', 3)
            
            components["tactical_preparedness"] = (
                intelligence * 4 +
                positioning * 4 +
                decision * 4
            ) / 3
        
        # 4. Mental State (15 points)
        if wellness:
            mood = wellness.get('mood_1_5', 3)
            stress = wellness.get('stress_1_5', 3)
            
            components["mental_state"] = (mood * 3 + stress * 3) / 2 * 2.5
        
        # 5. Recovery Status (15 points)
        if wellness and training_load:
            sleep = wellness.get('sleep_hours', 7)
            soreness = wellness.get('soreness_1_5', 3)
            acwr = training_load.get('acwr', 1.0)
            
            sleep_score = min(5, sleep / 1.6)
            soreness_score = soreness * 2
            load_score = 5 if 0.8 <= acwr <= 1.3 else 2
            
            components["recovery_status"] = sleep_score + soreness_score + load_score
        
        # Calculate total
        total_score = sum(components.values())
        
        # Adjust for days to match
        if days_to_match <= 1:
            multiplier = 1.0  # Peak day
        elif days_to_match == 2:
            multiplier = 0.95  # Minor taper
        elif days_to_match >= 7:
            multiplier = 0.85  # Need more prep
        else:
            multiplier = 0.9
        
        final_score = total_score * multiplier
        
        # Status determination
        if final_score >= 80:
            status = "Match Ready"
            color = "green"
        elif final_score >= 65:
            status = "Nearly Ready"
            color = "yellow"
        else:
            status = "Not Ready"
            color = "red"
        
        return {
            "readiness_score": round(final_score, 1),
            "status": status,
            "color": color,
            "components": {k: round(v, 1) for k, v in components.items()},
            "days_to_match": days_to_match,
            "recommendations": self._get_match_recommendations(components, final_score, days_to_match)
        }
    
    def _get_match_recommendations(self, components: Dict, score: float, days: int) -> List[str]:
        recs = []
        
        if components["physical_readiness"] < 20:
            recs.append("⚡ Focus on activation and speed work")
        
        if components["recovery_status"] < 10:
            recs.append("💤 Prioritize recovery - light training only")
        
        if components["mental_state"] < 10:
            recs.append("🧠 Mental preparation needed - visualization, confidence building")
        
        if days <= 2 and score >= 75:
            recs.append("🔥 Peak readiness - trust your preparation")
        elif days <= 2 and score < 65:
            recs.append("⚠️ Manage expectations - focus on process not outcome")
        
        return recs

class OptimalLoadCalculator:
    """Calculate optimal training load recommendations"""
    
    def calculate(self,
                  current_fitness: float,
                  recent_loads: List[Dict],
                  goals: List[str],
                  injury_risk: float) -> Dict[str, Any]:
        """
        Recommend optimal training load for next week
        """
        
        # Calculate current chronic load
        if len(recent_loads) >= 4:
            chronic_load = sum(l.get('total_distance_m', 0) for l in recent_loads[:4]) / 4
        else:
            chronic_load = 8000  # Default
        
        # Base recommendation on current fitness
        if current_fitness >= 80:
            base_load = chronic_load * 1.05  # Maintain
        elif current_fitness >= 60:
            base_load = chronic_load * 1.10  # Moderate progression
        else:
            base_load = chronic_load * 1.15  # Aggressive improvement
        
        # Adjust for injury risk
        if injury_risk > 60:
            base_load *= 0.7  # Reduce significantly
        elif injury_risk > 35:
            base_load *= 0.85  # Moderate reduction
        
        # Adjust for goals
        if "speed" in str(goals).lower():
            intensity_focus = "High"
            volume_recommendation = "Moderate"
        elif "endurance" in str(goals).lower():
            intensity_focus = "Moderate"
            volume_recommendation = "High"
        else:
            intensity_focus = "Moderate"
            volume_recommendation = "Moderate"
        
        # Weekly structure
        weekly_plan = self._create_weekly_structure(base_load, intensity_focus)
        
        return {
            "recommended_weekly_load": round(base_load),
            "current_chronic_load": round(chronic_load),
            "load_progression": round((base_load / chronic_load - 1) * 100, 1),
            "intensity_focus": intensity_focus,
            "volume_recommendation": volume_recommendation,
            "weekly_structure": weekly_plan,
            "target_acwr": "1.0-1.2",
            "cautions": self._get_load_cautions(injury_risk, base_load, chronic_load)
        }
    
    def _create_weekly_structure(self, total_load: float, intensity: str) -> Dict:
        if intensity == "High":
            return {
                "high_intensity_days": 2,
                "moderate_days": 2,
                "recovery_days": 2,
                "rest_days": 1,
                "sample_week": "Mon: High | Tue: Recovery | Wed: Moderate | Thu: Recovery | Fri: High | Sat: Moderate | Sun: Rest"
            }
        else:
            return {
                "high_intensity_days": 1,
                "moderate_days": 3,
                "recovery_days": 2,
                "rest_days": 1,
                "sample_week": "Mon: Moderate | Tue: Recovery | Wed: High | Thu: Recovery | Fri: Moderate | Sat: Moderate | Sun: Rest"
            }
    
    def _get_load_cautions(self, risk: float, new_load: float, old_load: float) -> List[str]:
        cautions = []
        
        progression = (new_load / old_load - 1) * 100
        
        if progression > 15:
            cautions.append("⚠️ Load increase >15% - monitor fatigue closely")
        
        if risk > 50:
            cautions.append("🚨 High injury risk - conservative progression recommended")
        
        if not cautions:
            cautions.append("✅ Load progression within safe parameters")
        
        return cautions

class PredictiveModelEngine:
    """Main engine that coordinates all predictive models"""
    
    def __init__(self):
        self.injury_predictor = InjuryRiskPredictor()
        self.performance_forecaster = PerformanceForecaster()
        self.match_readiness = MatchReadinessCalculator()
        self.optimal_load = OptimalLoadCalculator()
    
    def generate_comprehensive_analysis(self,
                                       player_data: Dict[str, Any]) -> PredictiveAnalysis:
        """
        Generate complete predictive analysis
        """
        
        # Extract data
        assessments = player_data.get('assessments', [])
        training_loads = player_data.get('training_loads', [])
        wellness_logs = player_data.get('wellness_logs', [])
        upcoming_match = player_data.get('upcoming_match', {})
        
        # Get latest data
        latest_assessment = assessments[0] if assessments else {}
        latest_wellness = wellness_logs[0] if wellness_logs else {}
        latest_load = training_loads[0] if training_loads else {}
        
        # Run all models
        injury_analysis = self.injury_predictor.predict(
            training_loads, wellness_logs, assessments
        )
        
        performance_forecast = self.performance_forecaster.forecast(assessments)
        
        days_to_match = upcoming_match.get('days_to_match', 7)
        match_ready = self.match_readiness.calculate(
            latest_assessment, latest_wellness, latest_load, days_to_match
        )
        
        current_fitness = latest_assessment.get('overall_score', 60) if latest_assessment else 60
        optimal_load_rec = self.optimal_load.calculate(
            current_fitness,
            training_loads,
            player_data.get('goals', []),
            injury_analysis['risk_score']
        )
        
        # Generate comprehensive recommendations
        all_recommendations = [
            *injury_analysis['recommendations'],
            *match_ready['recommendations']
        ]
        
        # Add performance insights
        if performance_forecast.get('forecast_available'):
            if performance_forecast['improvement_rate_per_week'] > 0:
                all_recommendations.append(f"📈 On track to reach {performance_forecast['predicted_category']} level")
            else:
                all_recommendations.append("⚠️ Performance plateau detected - consider program adjustment")
        
        return PredictiveAnalysis(
            injury_risk=injury_analysis,
            performance_forecast=performance_forecast,
            match_readiness=match_ready,
            optimal_training_load=optimal_load_rec,
            recommendations=all_recommendations[:10],  # Top 10 recommendations
            timestamp=datetime.now(timezone.utc)
        )
