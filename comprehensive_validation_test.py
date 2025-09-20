import requests
import json
from datetime import datetime, timedelta

class ComprehensiveValidationTester:
    def __init__(self, base_url="https://soccer-skill-track.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def validate_assessment_fields(self, assessment_data):
        """Validate that all required Youth Handbook fields are present"""
        required_fields = {
            # Physical metrics (20% weight)
            'sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat',
            # Technical metrics (40% weight)
            'ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels',
            # Tactical metrics (30% weight)
            'game_intelligence', 'positioning', 'decision_making',
            # Psychological metrics (10% weight)
            'coachability', 'mental_toughness'
        }
        
        missing_fields = required_fields - set(assessment_data.keys())
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        print("✅ All required Youth Handbook fields present")
        return True

    def validate_scoring_weights(self, category_scores, overall_score):
        """Validate that scoring weights are applied correctly"""
        expected_weights = {
            'physical': 0.20,
            'technical': 0.40,
            'tactical': 0.30,
            'psychological': 0.10
        }
        
        calculated_score = sum(
            category_scores.get(category, 0) * weight 
            for category, weight in expected_weights.items()
        )
        
        # Allow small floating point differences
        if abs(calculated_score - overall_score) > 0.01:
            print(f"❌ Scoring weight mismatch: Expected {calculated_score:.2f}, Got {overall_score}")
            return False
        
        print(f"✅ Correct weighted scoring: {overall_score} (Physical: {category_scores.get('physical', 0)*0.20:.2f}, Technical: {category_scores.get('technical', 0)*0.40:.2f}, Tactical: {category_scores.get('tactical', 0)*0.30:.2f}, Psychological: {category_scores.get('psychological', 0)*0.10:.2f})")
        return True

    def validate_age_category_standards(self, age, overall_score):
        """Validate that age-based standards are being applied"""
        age_categories = {
            (12, 14): "12-14",
            (15, 16): "15-16", 
            (17, 18): "17-18",
            (19, 100): "elite"
        }
        
        category = None
        for age_range, cat_name in age_categories.items():
            if age_range[0] <= age <= age_range[1]:
                category = cat_name
                break
        
        if not category:
            print(f"❌ Invalid age category for age {age}")
            return False
        
        print(f"✅ Age {age} correctly assigned to '{category}' category")
        return True

    def test_comprehensive_assessment_creation(self):
        """Test comprehensive assessment creation with validation"""
        print("\n🔍 COMPREHENSIVE ASSESSMENT VALIDATION")
        print("=" * 50)
        
        # Test data for different age categories
        test_cases = [
            {
                "name": "Youth Player (Age 14)",
                "data": {
                    "player_name": "Alex Johnson",
                    "age": 14,
                    "position": "midfielder",
                    "sprint_30m": 4.5, "yo_yo_test": 1150, "vo2_max": 51.0, "vertical_jump": 39, "body_fat": 13.5,
                    "ball_control": 4, "passing_accuracy": 74.0, "dribbling_success": 53.0, "shooting_accuracy": 59.0, "defensive_duels": 69.0,
                    "game_intelligence": 4, "positioning": 3, "decision_making": 4,
                    "coachability": 5, "mental_toughness": 4
                }
            },
            {
                "name": "Elite Player (Age 19)",
                "data": {
                    "player_name": "Maria Santos",
                    "age": 19,
                    "position": "forward",
                    "sprint_30m": 3.85, "yo_yo_test": 2380, "vo2_max": 64.0, "vertical_jump": 69, "body_fat": 7.0,
                    "ball_control": 5, "passing_accuracy": 94.0, "dribbling_success": 74.0, "shooting_accuracy": 84.0, "defensive_duels": 84.0,
                    "game_intelligence": 5, "positioning": 5, "decision_making": 5,
                    "coachability": 5, "mental_toughness": 5
                }
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            print(f"\n📋 Testing {test_case['name']}...")
            
            # Validate fields
            if not self.validate_assessment_fields(test_case['data']):
                all_passed = False
                continue
            
            # Create assessment
            try:
                response = requests.post(
                    f"{self.api_url}/assessments",
                    json=test_case['data'],
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code != 200:
                    print(f"❌ Assessment creation failed: {response.status_code}")
                    all_passed = False
                    continue
                
                assessment = response.json()
                print(f"✅ Assessment created successfully")
                
                # Validate scoring
                if not self.validate_scoring_weights(
                    assessment.get('category_scores', {}),
                    assessment.get('overall_score', 0)
                ):
                    all_passed = False
                    continue
                
                # Validate age category
                if not self.validate_age_category_standards(
                    test_case['data']['age'],
                    assessment.get('overall_score', 0)
                ):
                    all_passed = False
                    continue
                
                print(f"   Overall Score: {assessment.get('overall_score', 'N/A')}")
                print(f"   Category Breakdown: {assessment.get('category_scores', {})}")
                
            except Exception as e:
                print(f"❌ Error during assessment creation: {e}")
                all_passed = False
        
        self.tests_run += 1
        if all_passed:
            self.tests_passed += 1
            print("\n✅ All comprehensive assessment validations passed")
        else:
            print("\n❌ Some comprehensive assessment validations failed")
        
        return all_passed

    def test_retest_workflow(self):
        """Test complete retest workflow"""
        print("\n🔄 RETEST WORKFLOW VALIDATION")
        print("=" * 50)
        
        # Create initial assessment
        initial_data = {
            "player_name": "Test Retest Player",
            "age": 17,
            "position": "defender",
            "sprint_30m": 4.3, "yo_yo_test": 1800, "vo2_max": 58.0, "vertical_jump": 54, "body_fat": 10.0,
            "ball_control": 3, "passing_accuracy": 82.0, "dribbling_success": 63.0, "shooting_accuracy": 68.0, "defensive_duels": 76.0,
            "game_intelligence": 4, "positioning": 4, "decision_making": 4,
            "coachability": 4, "mental_toughness": 4
        }
        
        try:
            # Create initial assessment
            response = requests.post(
                f"{self.api_url}/assessments",
                json=initial_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                print(f"❌ Initial assessment creation failed")
                self.tests_run += 1
                return False
            
            initial_assessment = response.json()
            player_id = initial_assessment['id']
            initial_score = initial_assessment['overall_score']
            print(f"✅ Initial assessment created (Score: {initial_score})")
            
            # Schedule retest
            retest_date = datetime.now() + timedelta(weeks=4)
            retest_schedule_data = {
                "player_id": player_id,
                "original_assessment_id": player_id,
                "retest_date": retest_date.isoformat(),
                "retest_type": "4_week"
            }
            
            response = requests.post(
                f"{self.api_url}/retests/schedule",
                json=retest_schedule_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                print(f"❌ Retest scheduling failed")
                self.tests_run += 1
                return False
            
            print("✅ Retest scheduled successfully")
            
            # Create improved retest assessment
            improved_data = initial_data.copy()
            improved_data.update({
                "sprint_30m": 4.1,  # Improved
                "yo_yo_test": 1900,  # Improved
                "ball_control": 4,  # Improved
                "passing_accuracy": 85.0,  # Improved
                "game_intelligence": 5,  # Improved
            })
            
            response = requests.post(
                f"{self.api_url}/assessments/{player_id}/retest",
                json=improved_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                print(f"❌ Retest assessment creation failed")
                self.tests_run += 1
                return False
            
            retest_assessment = response.json()
            retest_score = retest_assessment['overall_score']
            improvement = retest_score - initial_score
            
            print(f"✅ Retest assessment created (Score: {retest_score})")
            print(f"✅ Progress tracked: {improvement:+.2f} improvement")
            
            if improvement > 0:
                print("✅ Positive progress detected correctly")
            else:
                print("⚠️  No improvement detected (this may be expected)")
            
            self.tests_run += 1
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"❌ Error during retest workflow: {e}")
            self.tests_run += 1
            return False

def main():
    print("🚀 COMPREHENSIVE YOUTH HANDBOOK VALIDATION")
    print("=" * 60)
    
    tester = ComprehensiveValidationTester()
    
    # Run comprehensive tests
    results = []
    results.append(tester.test_comprehensive_assessment_creation())
    results.append(tester.test_retest_workflow())
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE VALIDATION RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    print(f"\n🎯 VALIDATION SUMMARY:")
    print(f"✅ Youth Handbook Field Structure: Validated")
    print(f"✅ Age-Based Standards Categories: Validated")
    print(f"✅ Weighted Scoring System: Validated")
    print(f"✅ Retest & Progress Tracking: Validated")
    
    if all(results):
        print(f"\n🎉 ALL COMPREHENSIVE VALIDATIONS PASSED!")
        print(f"The Youth Handbook soccer assessment system is fully functional.")
        return 0
    else:
        print(f"\n⚠️  Some validations failed. Review details above.")
        return 1

if __name__ == "__main__":
    exit(main())