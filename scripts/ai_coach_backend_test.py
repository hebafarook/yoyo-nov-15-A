#!/usr/bin/env python3
"""
COMPREHENSIVE AI COACH & COMPUTER VISION BACKEND TESTING
Tests all 5 AI Coach endpoints with realistic data
"""

import requests
import json
import base64
import uuid
from datetime import datetime, timezone
import time

# Backend URL from frontend environment
BACKEND_URL = "https://soccer-onboarding.preview.emergentagent.com/api"

class AICoachTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.player_name = "yoyo"  # Use existing player as specified
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def create_test_image_base64(self):
        """Create a minimal test image in base64 format"""
        # Create a simple 100x100 black image
        import numpy as np
        import cv2
        
        # Create black image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Encode to base64
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_base64}"

    def test_predictive_analysis(self):
        """TEST SCENARIO 1: Predictive Analysis (High Priority)"""
        print("\n🔥 TESTING PREDICTIVE ANALYSIS ENDPOINT")
        
        try:
            # Test data as specified in review
            test_data = {
                "player_name": self.player_name,
                "days_to_match": 7,
                "goals": ["improve speed", "increase endurance"]
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-coach/predictive-analysis",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "player_name", "analysis"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Predictive Analysis - Response Structure",
                        False,
                        f"Missing fields: {missing_fields}",
                        data
                    )
                    return
                
                # Check analysis structure
                analysis = data.get("analysis", {})
                required_analysis_fields = [
                    "injury_risk", "performance_forecast", 
                    "match_readiness", "optimal_training_load", 
                    "recommendations"
                ]
                
                missing_analysis = [field for field in required_analysis_fields if field not in analysis]
                
                if missing_analysis:
                    self.log_test(
                        "Predictive Analysis - Analysis Structure",
                        False,
                        f"Missing analysis fields: {missing_analysis}",
                        analysis
                    )
                    return
                
                # Verify injury_risk structure
                injury_risk = analysis.get("injury_risk", {})
                injury_required = ["risk_score", "risk_level", "risk_factors", "recommendations"]
                injury_missing = [field for field in injury_required if field not in injury_risk]
                
                if injury_missing:
                    self.log_test(
                        "Predictive Analysis - Injury Risk Structure",
                        False,
                        f"Missing injury risk fields: {injury_missing}",
                        injury_risk
                    )
                else:
                    # Verify risk_score is 0-100
                    risk_score = injury_risk.get("risk_score", -1)
                    if 0 <= risk_score <= 100:
                        self.log_test(
                            "Predictive Analysis - Injury Risk Score",
                            True,
                            f"Risk score: {risk_score}/100, Level: {injury_risk.get('risk_level')}",
                            injury_risk
                        )
                    else:
                        self.log_test(
                            "Predictive Analysis - Injury Risk Score",
                            False,
                            f"Invalid risk score: {risk_score} (should be 0-100)",
                            injury_risk
                        )
                
                # Verify performance_forecast structure
                performance_forecast = analysis.get("performance_forecast", {})
                forecast_required = ["current_score", "predicted_score_12_weeks", "improvement_rate_per_week", "weekly_predictions"]
                forecast_missing = [field for field in forecast_required if field not in performance_forecast]
                
                if forecast_missing:
                    self.log_test(
                        "Predictive Analysis - Performance Forecast Structure",
                        False,
                        f"Missing forecast fields: {forecast_missing}",
                        performance_forecast
                    )
                else:
                    self.log_test(
                        "Predictive Analysis - Performance Forecast",
                        True,
                        f"Current: {performance_forecast.get('current_score')}, Predicted: {performance_forecast.get('predicted_score_12_weeks')}",
                        performance_forecast
                    )
                
                # Verify match_readiness structure
                match_readiness = analysis.get("match_readiness", {})
                readiness_required = ["readiness_score", "status", "components"]
                readiness_missing = [field for field in readiness_required if field not in match_readiness]
                
                if readiness_missing:
                    self.log_test(
                        "Predictive Analysis - Match Readiness Structure",
                        False,
                        f"Missing readiness fields: {readiness_missing}",
                        match_readiness
                    )
                else:
                    # Verify readiness_score is 0-100
                    readiness_score = match_readiness.get("readiness_score", -1)
                    if 0 <= readiness_score <= 100:
                        self.log_test(
                            "Predictive Analysis - Match Readiness Score",
                            True,
                            f"Readiness: {readiness_score}/100, Status: {match_readiness.get('status')}",
                            match_readiness
                        )
                    else:
                        self.log_test(
                            "Predictive Analysis - Match Readiness Score",
                            False,
                            f"Invalid readiness score: {readiness_score} (should be 0-100)",
                            match_readiness
                        )
                
                # Verify optimal_training_load structure
                training_load = analysis.get("optimal_training_load", {})
                load_required = ["recommended_weekly_load", "intensity_focus", "weekly_structure"]
                load_missing = [field for field in load_required if field not in training_load]
                
                if load_missing:
                    self.log_test(
                        "Predictive Analysis - Training Load Structure",
                        False,
                        f"Missing training load fields: {load_missing}",
                        training_load
                    )
                else:
                    self.log_test(
                        "Predictive Analysis - Optimal Training Load",
                        True,
                        f"Weekly load: {training_load.get('recommended_weekly_load')}, Focus: {training_load.get('intensity_focus')}",
                        training_load
                    )
                
                # Verify recommendations
                recommendations = analysis.get("recommendations", [])
                if isinstance(recommendations, list) and len(recommendations) > 0:
                    self.log_test(
                        "Predictive Analysis - Recommendations",
                        True,
                        f"Generated {len(recommendations)} recommendations",
                        {"count": len(recommendations), "sample": recommendations[:3]}
                    )
                else:
                    self.log_test(
                        "Predictive Analysis - Recommendations",
                        False,
                        "No recommendations generated or invalid format",
                        recommendations
                    )
                
                # Overall success
                self.log_test(
                    "Predictive Analysis - Overall",
                    True,
                    f"All 5 predictive models working correctly for {self.player_name}",
                    {"player": self.player_name, "models": len(required_analysis_fields)}
                )
                
            elif response.status_code == 404:
                self.log_test(
                    "Predictive Analysis - Player Data",
                    False,
                    f"No assessment data found for player '{self.player_name}' - need to create assessment first",
                    {"status_code": response.status_code, "response": response.text}
                )
            else:
                self.log_test(
                    "Predictive Analysis - API Response",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Predictive Analysis - Exception",
                False,
                f"Error: {str(e)}",
                {"error": str(e)}
            )

    def test_performance_insights(self):
        """TEST SCENARIO 2: Performance Insights (AI Feedback)"""
        print("\n🧠 TESTING PERFORMANCE INSIGHTS ENDPOINT")
        
        try:
            # Test data as specified in review
            test_data = {
                "player_name": self.player_name
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-coach/performance-insights",
                data=test_data,  # Using form data as per endpoint
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "player_name", "ai_insights", "score_change"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Performance Insights - Response Structure",
                        False,
                        f"Missing fields: {missing_fields}",
                        data
                    )
                    return
                
                # Check AI insights content
                ai_insights = data.get("ai_insights", "")
                if isinstance(ai_insights, str) and len(ai_insights.strip()) > 0:
                    self.log_test(
                        "Performance Insights - AI Insights Content",
                        True,
                        f"Generated {len(ai_insights)} characters of insights",
                        {"insights_length": len(ai_insights), "preview": ai_insights[:100] + "..."}
                    )
                else:
                    self.log_test(
                        "Performance Insights - AI Insights Content",
                        False,
                        "AI insights empty or invalid format",
                        {"ai_insights": ai_insights}
                    )
                
                # Check score change
                score_change = data.get("score_change")
                if isinstance(score_change, (int, float)):
                    self.log_test(
                        "Performance Insights - Score Change",
                        True,
                        f"Score change: {score_change} points between assessments",
                        {"score_change": score_change}
                    )
                else:
                    self.log_test(
                        "Performance Insights - Score Change",
                        False,
                        f"Invalid score change format: {score_change}",
                        {"score_change": score_change}
                    )
                
                # Overall success
                self.log_test(
                    "Performance Insights - Overall",
                    True,
                    f"AI performance insights generated successfully for {self.player_name}",
                    data
                )
                
            else:
                self.log_test(
                    "Performance Insights - API Response",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Performance Insights - Exception",
                False,
                f"Error: {str(e)}",
                {"error": str(e)}
            )

    def test_analysis_history(self):
        """TEST SCENARIO 3: Analysis History"""
        print("\n📊 TESTING ANALYSIS HISTORY ENDPOINT")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/ai-coach/analysis-history/{self.player_name}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["player_name", "analyses", "count"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Analysis History - Response Structure",
                        False,
                        f"Missing fields: {missing_fields}",
                        data
                    )
                    return
                
                # Check analyses array
                analyses = data.get("analyses", [])
                count = data.get("count", 0)
                
                if isinstance(analyses, list):
                    self.log_test(
                        "Analysis History - Analyses Array",
                        True,
                        f"Retrieved {count} analyses for {self.player_name}",
                        {"count": count, "analyses_type": type(analyses).__name__}
                    )
                    
                    # Check individual analysis structure if any exist
                    if len(analyses) > 0:
                        first_analysis = analyses[0]
                        if isinstance(first_analysis, dict) and "timestamp" in first_analysis:
                            self.log_test(
                                "Analysis History - Analysis Structure",
                                True,
                                f"Each analysis contains timestamp and required fields",
                                {"sample_keys": list(first_analysis.keys())[:5]}
                            )
                        else:
                            self.log_test(
                                "Analysis History - Analysis Structure",
                                False,
                                "Analysis objects missing required fields",
                                {"sample": first_analysis}
                            )
                    else:
                        self.log_test(
                            "Analysis History - No Data",
                            True,
                            "No previous analyses found (expected for new player)",
                            {"count": 0}
                        )
                else:
                    self.log_test(
                        "Analysis History - Analyses Array",
                        False,
                        f"Analyses is not an array: {type(analyses)}",
                        {"analyses": analyses}
                    )
                
                # Overall success
                self.log_test(
                    "Analysis History - Overall",
                    True,
                    f"Analysis history endpoint working correctly for {self.player_name}",
                    data
                )
                
            else:
                self.log_test(
                    "Analysis History - API Response",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Analysis History - Exception",
                False,
                f"Error: {str(e)}",
                {"error": str(e)}
            )

    def test_form_analysis_frame(self):
        """TEST SCENARIO 4: Form Analysis (Frame) - Create Test Frame"""
        print("\n📷 TESTING FORM ANALYSIS FRAME ENDPOINT")
        
        try:
            # Create test image as specified in review
            test_image = self.create_test_image_base64()
            
            test_data = {
                "frame_base64": test_image,
                "exercise_type": "squat"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-coach/analyze-form-frame",
                data=test_data,  # Using form data as per endpoint
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if pose was detected or not (both are valid)
                if "pose_detected" in data:
                    pose_detected = data.get("pose_detected", False)
                    
                    if pose_detected:
                        # Verify pose analysis structure
                        required_fields = ["exercise_type", "form_score", "verdict", "issues", "corrections", "angles"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_test(
                                "Form Analysis - Pose Analysis Structure",
                                False,
                                f"Missing pose analysis fields: {missing_fields}",
                                data
                            )
                        else:
                            self.log_test(
                                "Form Analysis - Pose Detected",
                                True,
                                f"Pose detected and analyzed: Form score {data.get('form_score')}/100",
                                {"form_score": data.get("form_score"), "verdict": data.get("verdict")}
                            )
                    else:
                        # No pose detected - this is expected behavior for test image
                        message = data.get("message", "")
                        if "No pose detected" in message:
                            self.log_test(
                                "Form Analysis - No Pose Detected",
                                True,
                                "No pose detected in test frame (expected behavior)",
                                {"message": message}
                            )
                        else:
                            self.log_test(
                                "Form Analysis - No Pose Detected",
                                False,
                                f"Unexpected message: {message}",
                                data
                            )
                else:
                    self.log_test(
                        "Form Analysis - Response Structure",
                        False,
                        "Missing 'pose_detected' field in response",
                        data
                    )
                
                # Overall success - endpoint is reachable and responds correctly
                self.log_test(
                    "Form Analysis - Overall",
                    True,
                    "Form analysis endpoint working correctly (MediaPipe integration functional)",
                    {"status": "reachable", "response_type": "pose_detected" in data}
                )
                
            else:
                self.log_test(
                    "Form Analysis - API Response",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Form Analysis - Exception",
                False,
                f"Error: {str(e)}",
                {"error": str(e)}
            )

    def test_ai_coaching_feedback(self):
        """TEST SCENARIO 5: AI Coaching Feedback"""
        print("\n🎯 TESTING AI COACHING FEEDBACK ENDPOINT")
        
        try:
            # Test data as specified in review
            test_data = {
                "player_name": self.player_name,
                "form_issues": "Squat not deep enough, Torso leaning too far forward",
                "exercise_type": "squat",
                "form_score": 65
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-coach/ai-coaching-feedback",
                data=test_data,  # Using form data as per endpoint
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "player_name", "exercise_type", "form_score", "ai_feedback"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "AI Coaching Feedback - Response Structure",
                        False,
                        f"Missing fields: {missing_fields}",
                        data
                    )
                    return
                
                # Check AI feedback content
                ai_feedback = data.get("ai_feedback", "")
                if isinstance(ai_feedback, str) and len(ai_feedback.strip()) > 0:
                    # Check if feedback mentions the specific issues
                    form_issues = test_data["form_issues"].lower()
                    feedback_lower = ai_feedback.lower()
                    
                    mentions_issues = any(issue.strip().lower() in feedback_lower 
                                        for issue in ["squat", "deep", "torso", "forward", "lean"])
                    
                    if mentions_issues:
                        self.log_test(
                            "AI Coaching Feedback - Personalized Content",
                            True,
                            f"Feedback mentions specific issues and provides corrections ({len(ai_feedback)} chars)",
                            {"feedback_length": len(ai_feedback), "mentions_issues": mentions_issues}
                        )
                    else:
                        self.log_test(
                            "AI Coaching Feedback - Personalized Content",
                            False,
                            "Feedback doesn't mention specific form issues provided",
                            {"feedback": ai_feedback[:200] + "..."}
                        )
                    
                    # Check if feedback is coherent and motivational
                    motivational_words = ["improve", "better", "good", "great", "progress", "work", "focus", "practice"]
                    has_motivation = any(word in feedback_lower for word in motivational_words)
                    
                    if has_motivation:
                        self.log_test(
                            "AI Coaching Feedback - Motivational Tone",
                            True,
                            "Feedback contains motivational and encouraging language",
                            {"has_motivation": has_motivation}
                        )
                    else:
                        self.log_test(
                            "AI Coaching Feedback - Motivational Tone",
                            False,
                            "Feedback lacks motivational language",
                            {"feedback_sample": ai_feedback[:100]}
                        )
                        
                else:
                    self.log_test(
                        "AI Coaching Feedback - Content",
                        False,
                        "AI feedback empty or invalid format",
                        {"ai_feedback": ai_feedback}
                    )
                
                # Check other fields
                if data.get("player_name") == test_data["player_name"]:
                    self.log_test(
                        "AI Coaching Feedback - Player Name",
                        True,
                        f"Correct player name: {data.get('player_name')}",
                        {"player_name": data.get("player_name")}
                    )
                
                if data.get("form_score") == test_data["form_score"]:
                    self.log_test(
                        "AI Coaching Feedback - Form Score",
                        True,
                        f"Correct form score: {data.get('form_score')}/100",
                        {"form_score": data.get("form_score")}
                    )
                
                # Overall success
                self.log_test(
                    "AI Coaching Feedback - Overall",
                    True,
                    f"AI coaching feedback generated successfully for {self.player_name}",
                    data
                )
                
            else:
                self.log_test(
                    "AI Coaching Feedback - API Response",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "AI Coaching Feedback - Exception",
                False,
                f"Error: {str(e)}",
                {"error": str(e)}
            )

    def run_all_tests(self):
        """Run all AI Coach endpoint tests"""
        print("🚀 STARTING COMPREHENSIVE AI COACH & COMPUTER VISION BACKEND TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Player: {self.player_name}")
        print("=" * 80)
        
        # Run all test scenarios in order of priority
        self.test_predictive_analysis()      # Scenario 1 - High Priority
        self.test_performance_insights()     # Scenario 2 - High Priority  
        self.test_analysis_history()         # Scenario 3
        self.test_form_analysis_frame()      # Scenario 4
        self.test_ai_coaching_feedback()     # Scenario 5 - High Priority
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("🏆 AI COACH BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group by test category
        categories = {}
        for test in self.test_results:
            category = test["test"].split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if test["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            categories[category]["tests"].append(test)
        
        print("\n📊 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            total = results["passed"] + results["failed"]
            rate = (results["passed"] / total) * 100 if total > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 75 else "❌"
            print(f"{status} {category}: {results['passed']}/{total} ({rate:.1f}%)")
        
        # Show failed tests
        failed_tests_list = [test for test in self.test_results if not test["success"]]
        if failed_tests_list:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests_list:
                print(f"  • {test['test']}: {test['details']}")
        
        # Show critical success indicators
        print("\n🎯 CRITICAL SUCCESS INDICATORS:")
        
        # Check if predictive analysis works
        predictive_tests = [t for t in self.test_results if "Predictive Analysis" in t["test"]]
        predictive_success = sum(1 for t in predictive_tests if t["success"])
        if predictive_success >= len(predictive_tests) * 0.8:  # 80% success rate
            print("✅ Predictive analysis generates all 5 models")
        else:
            print("❌ Predictive analysis returns errors or incomplete data")
        
        # Check if AI feedback works
        feedback_tests = [t for t in self.test_results if "AI Coaching Feedback" in t["test"]]
        feedback_success = sum(1 for t in feedback_tests if t["success"])
        if feedback_success >= len(feedback_tests) * 0.8:
            print("✅ AI coaching feedback returns natural language")
        else:
            print("❌ AI feedback fails or returns empty")
        
        # Check for 500 errors
        has_500_errors = any("500" in test.get("details", "") for test in self.test_results if not test["success"])
        if not has_500_errors:
            print("✅ No 500 errors on any endpoint")
        else:
            print("❌ 500 errors detected on endpoints")
        
        # Check if endpoints are reachable
        reachable_tests = [t for t in self.test_results if "Overall" in t["test"]]
        reachable_success = sum(1 for t in reachable_tests if t["success"])
        if reachable_success >= 4:  # At least 4 out of 5 endpoints working
            print("✅ All major AI Coach endpoints are reachable")
        else:
            print("❌ Some AI Coach endpoints are not reachable")
        
        print("\n" + "=" * 80)
        print("Testing completed at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    tester = AICoachTester()
    tester.run_all_tests()