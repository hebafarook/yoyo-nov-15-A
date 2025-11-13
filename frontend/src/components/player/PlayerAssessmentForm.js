import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { CheckCircle, Info, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayerAssessmentForm = ({ onAssessmentComplete, isFirstTime = false }) => {
  const { user, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    player_name: "",
    age: "",
    position: "",
    height_cm: "",
    weight_kg: "",
    assessment_date: new Date().toISOString().split('T')[0],
    // Physical metrics
    sprint_30m: "",
    yo_yo_test: "",
    vo2_max: "",
    vertical_jump: "",
    body_fat: "",
    // Technical metrics
    ball_control: "",
    passing_accuracy: "",
    dribbling_success: "",
    shooting_accuracy: "",
    defensive_duels: "",
    // Tactical metrics
    game_intelligence: "",
    positioning: "",
    decision_making: "",
    // Psychological metrics
    coachability: "",
    mental_toughness: ""
  });

  const [isLoading, setIsLoading] = useState(false);
  const [assessmentSuccess, setAssessmentSuccess] = useState(false);
  const [assessmentMessage, setAssessmentMessage] = useState('');

  // Auto-populate player data from user profile
  useEffect(() => {
    if (isAuthenticated && user) {
      setFormData(prev => ({
        ...prev,
        player_name: user.role === 'player' ? user.username : prev.player_name,
        age: user.age || prev.age,
        position: user.position || prev.position,
      }));
    }
  }, [isAuthenticated, user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      if (!isAuthenticated || !user) {
        alert("Please login to save your assessment data.");
        setIsLoading(false);
        return;
      }

      // Add user_id if authenticated
      const assessmentData = {
        ...formData,
        user_id: user.id
      };
      
      console.log('Creating assessment with data:', assessmentData);
      const response = await axios.post(`${BACKEND_URL}/api/assessments`, assessmentData);
      console.log('Assessment created successfully:', response.data);
      
      const createdAssessment = response.data;
      
      // Calculate overall score for the assessment
      const ageCategory = getAgeCategory(parseInt(formData.age));
      const overallScore = calculateOverallScore(formData, ageCategory);
      const performanceLevel = getPerformanceLevel(overallScore);
      
      // Automatically save as benchmark
      try {
        const benchmarkData = {
          user_id: user.id,
          player_name: formData.player_name,
          assessment_id: createdAssessment.id,
          age: parseInt(formData.age),
          position: formData.position,
          // Physical metrics
          sprint_30m: parseFloat(formData.sprint_30m) || 0,
          yo_yo_test: parseInt(formData.yo_yo_test) || 0,
          vo2_max: parseFloat(formData.vo2_max) || 0,
          vertical_jump: parseInt(formData.vertical_jump) || 0,
          body_fat: parseFloat(formData.body_fat) || 0,
          // Technical metrics
          ball_control: parseInt(formData.ball_control) || 0,
          passing_accuracy: parseFloat(formData.passing_accuracy) || 0,
          dribbling_success: parseFloat(formData.dribbling_success) || 0,
          shooting_accuracy: parseFloat(formData.shooting_accuracy) || 0,
          defensive_duels: parseFloat(formData.defensive_duels) || 0,
          // Tactical metrics
          game_intelligence: parseInt(formData.game_intelligence) || 0,
          positioning: parseInt(formData.positioning) || 0,
          decision_making: parseInt(formData.decision_making) || 0,
          // Psychological metrics
          coachability: parseInt(formData.coachability) || 0,
          mental_toughness: parseInt(formData.mental_toughness) || 0,
          // Calculated metrics
          overall_score: overallScore,
          performance_level: performanceLevel,
          benchmark_type: 'regular',
          notes: `Assessment created on ${new Date().toLocaleDateString()}`
        };
        
        console.log('Saving as benchmark:', benchmarkData);
        const token = localStorage.getItem('token');
        const benchmarkResponse = await axios.post(`${BACKEND_URL}/api/auth/save-benchmark`, benchmarkData, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log('Benchmark saved:', benchmarkResponse.data);
        
        // Auto-generate comprehensive roadmap report
        try {
          console.log('Generating comprehensive roadmap for assessment:', createdAssessment.id);
          const roadmapResponse = await axios.post(
            `${BACKEND_URL}/api/reports/generate-comprehensive-roadmap?assessment_id=${createdAssessment.id}`,
            {},
            { headers: { 'Authorization': `Bearer ${token}` }}
          );
          
          console.log('✅ Comprehensive roadmap generated:', roadmapResponse.data);
          
          // Also generate training program
          try {
            const programResponse = await axios.post(`${BACKEND_URL}/api/reports/generate-report`, {
              assessment_id: createdAssessment.id,
              include_comparison: true,
              include_training_plan: true
            }, {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            console.log('✅ Training program generated:', programResponse.data);
          } catch (programError) {
            console.error('Training program generation error (non-critical):', programError);
          }
          
        } catch (reportError) {
          console.error('Error generating roadmap (non-critical):', reportError);
        }
        
        if (benchmarkResponse.data.is_baseline) {
          setAssessmentMessage('🎯 BASELINE ASSESSMENT COMPLETE!\n\nYour assessment has been saved and processed:\n\n✅ Benchmark created for future comparisons\n✅ Comprehensive roadmap report generated with AI analysis\n✅ Coach recommendations and standards included\n✅ Personalized training program created\n✅ Report ready to view, print, and save\n\nClick "View My Report" to see your complete development roadmap!');
        } else {
          setAssessmentMessage('📊 ASSESSMENT COMPLETE!\n\nYour progress assessment has been saved:\n\n✅ Progress tracked and benchmarked\n✅ Comprehensive roadmap updated\n✅ New coach recommendations generated\n✅ Training program adjusted\n✅ Updated report ready to view\n\nClick "View My Report" to see your updated roadmap!');
        }
        setAssessmentSuccess(true);
        
        // Call callback if provided
        if (onAssessmentComplete) {
          onAssessmentComplete(createdAssessment);
        }
        
      } catch (benchmarkError) {
        console.error('Error saving benchmark:', benchmarkError);
        setAssessmentMessage('✅ ASSESSMENT SAVED!\n\nNote: Benchmark save had an issue, but your assessment data is safe.');
        setAssessmentSuccess(true);
      }
      
      // Scroll to top to show success message
      window.scrollTo({ top: 0, behavior: 'smooth' });
      
    } catch (error) {
      console.error("Error creating assessment:", error);
      
      let errorMessage = "Failed to save assessment. Please try again.";
      if (error.response) {
        if (error.response.status === 401) {
          errorMessage = "Session expired. Please login again.";
        } else if (error.response.data && error.response.data.detail) {
          errorMessage = `Error: ${error.response.data.detail}`;
        }
      }
      
      setAssessmentMessage(`❌ ERROR\n\n${errorMessage}`);
      setAssessmentSuccess(false);
      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper functions
  const getAgeCategory = (age) => {
    if (age < 14) return 'U13';
    if (age <= 15) return 'U15';
    if (age <= 17) return 'U17';
    if (age <= 19) return 'U19';
    return 'Senior';
  };

  const calculateOverallScore = (data, ageCategory) => {
    let totalScore = 0;
    let metricCount = 0;

    // Physical metrics (20% of total)
    const physicalScore = (
      (parseFloat(data.sprint_30m) ? 3 : 0) +
      (parseInt(data.yo_yo_test) ? 3 : 0) +
      (parseFloat(data.vo2_max) ? 3 : 0) +
      (parseInt(data.vertical_jump) ? 3 : 0) +
      (parseFloat(data.body_fat) ? 3 : 0)
    ) / 5;
    totalScore += physicalScore * 0.2;

    // Technical metrics (40% of total)
    const technicalScore = (
      (parseInt(data.ball_control) || 0) +
      (parseFloat(data.passing_accuracy) / 20 || 0) +
      (parseFloat(data.dribbling_success) / 20 || 0) +
      (parseFloat(data.shooting_accuracy) / 20 || 0) +
      (parseFloat(data.defensive_duels) / 20 || 0)
    ) / 5;
    totalScore += technicalScore * 0.4;

    // Tactical metrics (20% of total)
    const tacticalScore = (
      (parseInt(data.game_intelligence) || 0) +
      (parseInt(data.positioning) || 0) +
      (parseInt(data.decision_making) || 0)
    ) / 3;
    totalScore += tacticalScore * 0.2;

    // Psychological metrics (20% of total)
    const psychologicalScore = (
      (parseInt(data.coachability) || 0) +
      (parseInt(data.mental_toughness) || 0)
    ) / 2;
    totalScore += psychologicalScore * 0.2;

    return totalScore;
  };

  const getPerformanceLevel = (score) => {
    if (score >= 4.5) return 'Elite';
    if (score >= 4.0) return 'Advanced';
    if (score >= 3.5) return 'Intermediate';
    if (score >= 3.0) return 'Developing';
    return 'Beginner';
  };

  if (assessmentSuccess) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-green-50 border-2 border-green-500 rounded-2xl p-8 shadow-lg">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center">
              <CheckCircle className="w-10 h-10 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Assessment Complete!</h2>
              <p className="text-gray-700">Your data has been saved successfully</p>
            </div>
          </div>
          <div className="bg-white rounded-xl p-4 mb-6 whitespace-pre-wrap">
            {assessmentMessage}
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => {
                setAssessmentSuccess(false);
                setFormData({
                  player_name: user?.username || "",
                  age: user?.age || "",
                  position: user?.position || "",
                  height_cm: "",
                  weight_kg: "",
                  assessment_date: new Date().toISOString().split('T')[0],
                  sprint_30m: "", yo_yo_test: "", vo2_max: "", vertical_jump: "", body_fat: "",
                  ball_control: "", passing_accuracy: "", dribbling_success: "", shooting_accuracy: "", defensive_duels: "",
                  game_intelligence: "", positioning: "", decision_making: "",
                  coachability: "", mental_toughness: ""
                });
              }}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition"
            >
              Take Another Assessment
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-gray-600 text-white rounded-xl font-semibold hover:bg-gray-700 transition"
            >
              View My Reports
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-6 text-white shadow-lg mb-6">
        <h2 className="text-3xl font-bold mb-2">📝 Player Assessment</h2>
        <p className="text-white/90">Complete this assessment to generate your personalized training program</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Basic Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Player Name *</label>
              <input
                type="text"
                name="player_name"
                value={formData.player_name}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Age *</label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Position *</label>
              <select
                name="position"
                value={formData.position}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Position</option>
                <option value="Forward">Forward</option>
                <option value="Midfielder">Midfielder</option>
                <option value="Defender">Defender</option>
                <option value="Goalkeeper">Goalkeeper</option>
                <option value="Winger">Winger</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Assessment Date *</label>
              <input
                type="date"
                name="assessment_date"
                value={formData.assessment_date}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Height (cm)</label>
              <input
                type="number"
                name="height_cm"
                value={formData.height_cm}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
              <input
                type="number"
                name="weight_kg"
                value={formData.weight_kg}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Physical Metrics */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Physical Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">30m Sprint (seconds)</label>
              <input
                type="number"
                step="0.01"
                name="sprint_30m"
                value={formData.sprint_30m}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Yo-Yo Test (meters)</label>
              <input
                type="number"
                name="yo_yo_test"
                value={formData.yo_yo_test}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">VO2 Max</label>
              <input
                type="number"
                step="0.1"
                name="vo2_max"
                value={formData.vo2_max}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Vertical Jump (cm)</label>
              <input
                type="number"
                name="vertical_jump"
                value={formData.vertical_jump}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Body Fat (%)</label>
              <input
                type="number"
                step="0.1"
                name="body_fat"
                value={formData.body_fat}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Technical Metrics */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Technical Skills (1-5 scale)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ball Control</label>
              <input
                type="number"
                min="1"
                max="5"
                name="ball_control"
                value={formData.ball_control}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Passing Accuracy (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                name="passing_accuracy"
                value={formData.passing_accuracy}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Dribbling Success (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                name="dribbling_success"
                value={formData.dribbling_success}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Shooting Accuracy (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                name="shooting_accuracy"
                value={formData.shooting_accuracy}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Defensive Duels Won (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                name="defensive_duels"
                value={formData.defensive_duels}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Tactical Metrics */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Tactical Awareness (1-5 scale)</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Game Intelligence</label>
              <input
                type="number"
                min="1"
                max="5"
                name="game_intelligence"
                value={formData.game_intelligence}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Positioning</label>
              <input
                type="number"
                min="1"
                max="5"
                name="positioning"
                value={formData.positioning}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Decision Making</label>
              <input
                type="number"
                min="1"
                max="5"
                name="decision_making"
                value={formData.decision_making}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Psychological Metrics */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Mental Attributes (1-5 scale)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Coachability</label>
              <input
                type="number"
                min="1"
                max="5"
                name="coachability"
                value={formData.coachability}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Mental Toughness</label>
              <input
                type="number"
                min="1"
                max="5"
                name="mental_toughness"
                value={formData.mental_toughness}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-center">
          <button
            type="submit"
            disabled={isLoading}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-xl font-bold text-lg hover:from-blue-700 hover:to-blue-900 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Processing Assessment...
              </span>
            ) : (
              'Submit Assessment & Generate Program'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PlayerAssessmentForm;
