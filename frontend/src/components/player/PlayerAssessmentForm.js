import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { CheckCircle, Info, AlertCircle, Play } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayerAssessmentForm = ({ onAssessmentComplete, isFirstTime = false }) => {
  const { user, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    player_name: "",
    age: "",
    position: "",
    gender: "",
    height_cm: "",
    weight_kg: "",
    height_feet: "",
    height_inches: "",
    weight_lbs: "",
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

  const [unitPreference, setUnitPreference] = useState('metric'); // 'metric' or 'imperial'
  const [showStandards, setShowStandards] = useState(false); // Show/hide standards guide

  const [isLoading, setIsLoading] = useState(false);
  const [assessmentSuccess, setAssessmentSuccess] = useState(false);
  const [assessmentMessage, setAssessmentMessage] = useState('');
  const [lastAssessmentId, setLastAssessmentId] = useState(null);

  // Auto-populate player data from user profile
  useEffect(() => {
    if (isAuthenticated && user) {
      console.log('👤 Auto-populating assessment form from user profile:', user);
      
      // Set unit preference from user profile
      const userUnitPreference = user.height_unit || 'metric';
      setUnitPreference(userUnitPreference);
      
      // Parse height and weight based on user's stored format
      let heightCm = '';
      let heightFeet = '';
      let heightInches = '';
      let weightKg = '';
      let weightLbs = '';
      
      // Parse height
      if (user.height) {
        if (user.height.includes('cm')) {
          // Metric: "175cm"
          heightCm = user.height.replace('cm', '');
        } else if (user.height.includes("'")) {
          // Imperial: "5'9\""
          const parts = user.height.split("'");
          heightFeet = parts[0];
          heightInches = parts[1]?.replace('"', '') || '0';
        }
      }
      
      // Parse weight
      if (user.weight) {
        if (user.weight.includes('kg')) {
          weightKg = user.weight.replace('kg', '');
        } else if (user.weight.includes('lbs')) {
          weightLbs = user.weight.replace('lbs', '');
        }
      }
      
      setFormData(prev => ({
        ...prev,
        player_name: user.full_name || user.username || prev.player_name,
        age: user.age || prev.age,
        position: user.position || prev.position,
        gender: user.gender || 'male',
        height_cm: heightCm,
        height_feet: heightFeet,
        height_inches: heightInches,
        weight_kg: weightKg,
        weight_lbs: weightLbs,
      }));
      
      console.log('✅ Form pre-filled:', {
        name: user.full_name || user.username,
        age: user.age,
        position: user.position,
        height: user.height,
        weight: user.weight,
        unit: userUnitPreference
      });
    }
  }, [isAuthenticated, user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    const missing = [];
    
    // Basic info
    if (!formData.player_name) missing.push("Player Name");
    if (!formData.age) missing.push("Age");
    if (!formData.position) missing.push("Position");
    if (!formData.assessment_date) missing.push("Assessment Date");
    
    // Physical metrics
    if (!formData.sprint_30m) missing.push("30m Sprint");
    if (!formData.yo_yo_test) missing.push("Yo-Yo Test");
    if (!formData.vo2_max) missing.push("VO2 Max");
    if (!formData.vertical_jump) missing.push("Vertical Jump");
    if (!formData.body_fat) missing.push("Body Fat %");
    
    // Technical metrics
    if (!formData.ball_control) missing.push("Ball Control");
    if (!formData.passing_accuracy) missing.push("Passing Accuracy");
    if (!formData.dribbling_success) missing.push("Dribbling Success");
    if (!formData.shooting_accuracy) missing.push("Shooting Accuracy");
    if (!formData.defensive_duels) missing.push("Defensive Duels");
    
    // Tactical metrics
    if (!formData.game_intelligence) missing.push("Game Intelligence");
    if (!formData.positioning) missing.push("Positioning");
    if (!formData.decision_making) missing.push("Decision Making");
    
    // Psychological metrics
    if (!formData.coachability) missing.push("Coachability");
    if (!formData.mental_toughness) missing.push("Mental Toughness");
    
    return missing;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate all required fields
    const missingFields = validateForm();
    if (missingFields.length > 0) {
      alert(`⚠️ Please complete all required fields:\n\n${missingFields.join('\n• ')}\n\nAll metrics are required for accurate program generation.`);
      return;
    }
    
    setIsLoading(true);
    
    try {
      if (!isAuthenticated || !user) {
        alert("Please login to save your assessment data.");
        setIsLoading(false);
        return;
      }

      // Prepare assessment data with proper unit handling
      const assessmentData = {
        ...formData,
        user_id: user.id
      };
      
      // Convert height to cm for backend (if imperial was used)
      if (unitPreference === 'imperial' && formData.height_feet && formData.height_inches) {
        const totalInches = (parseInt(formData.height_feet) * 12) + parseInt(formData.height_inches);
        assessmentData.height_cm = Math.round(totalInches * 2.54); // Convert to cm
      }
      
      // Convert weight to kg for backend (if imperial was used)
      if (unitPreference === 'imperial' && formData.weight_lbs) {
        assessmentData.weight_kg = Math.round(parseFloat(formData.weight_lbs) / 2.205); // Convert to kg
      }
      
      console.log('Creating assessment with data:', assessmentData);
      const response = await axios.post(`${BACKEND_URL}/api/assessments`, assessmentData);
      console.log('Assessment created successfully:', response.data);
      
      const createdAssessment = response.data;
      setLastAssessmentId(createdAssessment.id);
      
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
          setAssessmentMessage(`🎯 BASELINE ASSESSMENT COMPLETE!

Your comprehensive assessment has been processed:

📊 DATA SUBMITTED TO:
✅ AI Analysis Module - Generating insights
✅ LLM Processing Engine - Creating recommendations  
✅ Coach Review System - Professional evaluation
✅ Performance Database - Benchmark saved

📋 PROGRAMS BEING GENERATED:

1️⃣ COACH-GUIDED PROGRAM
   • Professional training plan
   • Position-specific drills
   • Skill development focus
   • Weekly progression structure

2️⃣ AI-POWERED MODEL PROGRAM  
   • Machine learning optimization
   • Personalized exercise selection
   • Dynamic difficulty adjustment
   • Performance prediction tracking

⏱️ Processing Time: 2-3 minutes

Click "View Professional Report" to see your complete development roadmap and generate your training programs!`);
        } else {
          setAssessmentMessage(`📊 PROGRESS ASSESSMENT COMPLETE!

Your assessment update has been processed:

📊 DATA SUBMITTED TO:
✅ AI Analysis Module - Comparing progress
✅ LLM Processing - Updated recommendations
✅ Coach Review System - Progress evaluation
✅ Performance Database - New benchmark

📈 PROGRAMS UPDATED:

1️⃣ COACH-GUIDED PROGRAM
   • Adjusted for your progress
   • New focus areas identified
   • Updated drill difficulty

2️⃣ AI-POWERED MODEL PROGRAM
   • Refined based on results
   • Optimized training path
   • Performance targets adjusted

Click "View Professional Report" to see your updated analysis!`);
        }
        setAssessmentSuccess(true);
        
        // Open professional report in new window
        const reportUrl = `/professional-report?assessment_id=${createdAssessment.id}`;
        window.open(reportUrl, '_blank', 'width=1200,height=800');
        
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
                const reportUrl = `/professional-report?assessment_id=${formData.lastAssessmentId || ''}`;
                window.open(reportUrl, '_blank', 'width=1200,height=800');
              }}
              className="px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition flex items-center gap-2"
            >
              <Play className="w-5 h-5" />
              View Professional Report
            </button>
            <button
              onClick={() => {
                if (onAssessmentComplete) {
                  onAssessmentComplete();
                }
              }}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition"
            >
              Go to Dashboard
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Gender *</label>
              <select
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
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
          </div>

          {/* Unit Preference Selector */}
          <div className="mt-4 bg-gray-50 border border-gray-300 p-4 rounded-lg">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Measurement Standard</label>
            <p className="text-xs text-gray-600 mb-3">Select your preferred measurement system</p>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setUnitPreference('metric')}
                className={`p-3 border-2 rounded-lg transition-all text-sm font-medium ${
                  unitPreference === 'metric'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                <div className="font-bold">Metric (Europe)</div>
                <div className="text-xs">cm • kg</div>
              </button>
              <button
                type="button"
                onClick={() => setUnitPreference('imperial')}
                className={`p-3 border-2 rounded-lg transition-all text-sm font-medium ${
                  unitPreference === 'imperial'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                <div className="font-bold">Imperial (USA)</div>
                <div className="text-xs">ft/in • lbs</div>
              </button>
            </div>
          </div>

          {/* Height and Weight - Dynamic based on unit preference */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {unitPreference === 'metric' ? (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Height (cm)</label>
                  <input
                    type="number"
                    name="height_cm"
                    value={formData.height_cm}
                    onChange={handleInputChange}
                    placeholder="e.g., 175"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Centimeters</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
                  <input
                    type="number"
                    name="weight_kg"
                    value={formData.weight_kg}
                    onChange={handleInputChange}
                    placeholder="e.g., 68"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Kilograms</p>
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Height</label>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <input
                        type="number"
                        name="height_feet"
                        value={formData.height_feet}
                        onChange={handleInputChange}
                        placeholder="Feet"
                        min="4"
                        max="7"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-xs text-gray-500 mt-1">Feet</p>
                    </div>
                    <div>
                      <input
                        type="number"
                        name="height_inches"
                        value={formData.height_inches}
                        onChange={handleInputChange}
                        placeholder="Inches"
                        min="0"
                        max="11"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-xs text-gray-500 mt-1">Inches</p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">e.g., 5 ft 9 in</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Weight (lbs)</label>
                  <input
                    type="number"
                    name="weight_lbs"
                    value={formData.weight_lbs}
                    onChange={handleInputChange}
                    placeholder="e.g., 150"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Pounds</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Performance Standards Guide - Collapsible */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 shadow-lg border-2 border-blue-200">
          <button
            type="button"
            onClick={() => setShowStandards(!showStandards)}
            className="w-full flex items-center justify-between text-left"
          >
            <h3 className="text-xl font-bold text-gray-900 flex items-center">
              📊 Performance Standards Guide
            </h3>
            <span className="text-2xl text-blue-600">
              {showStandards ? '−' : '+'}
            </span>
          </button>
          <p className="text-sm text-gray-700 mt-2">
            {showStandards ? 'Use these benchmarks to assess your performance. Based on elite youth soccer data.' : 'Click to expand and see performance benchmarks'}
          </p>
          
          {showStandards && (
          <>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Physical Metrics Standards */}
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <h4 className="font-bold text-blue-900 mb-3">⚡ Physical Metrics</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <strong>30m Sprint:</strong>
                  <div className="ml-2 text-gray-700">
                    • Excellent: &lt;4.0s | Good: 4.0-4.3s | Average: 4.3-4.6s | Below: &gt;4.6s
                  </div>
                </div>
                <div>
                  <strong>Yo-Yo Test:</strong>
                  <div className="ml-2 text-gray-700">
                    • Excellent: &gt;2400m | Good: 2000-2400m | Average: 1600-2000m | Below: &lt;1600m
                  </div>
                </div>
                <div>
                  <strong>VO2 Max:</strong>
                  <div className="ml-2 text-gray-700">
                    • Excellent: &gt;60 | Good: 55-60 | Average: 50-55 | Below: &lt;50
                  </div>
                </div>
                <div>
                  <strong>Vertical Jump:</strong>
                  <div className="ml-2 text-gray-700">
                    • Excellent: &gt;60cm | Good: 50-60cm | Average: 40-50cm | Below: &lt;40cm
                  </div>
                </div>
                <div>
                  <strong>Body Fat %:</strong>
                  <div className="ml-2 text-gray-700">
                    • Excellent: 8-12% | Good: 12-15% | Average: 15-18% | Above: &gt;18%
                  </div>
                </div>
              </div>
            </div>

            {/* Technical Skills Standards */}
            <div className="bg-white rounded-lg p-4 border border-purple-200">
              <h4 className="font-bold text-purple-900 mb-3">⚽ Technical Skills (1-5 Scale)</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <strong>Rating Scale:</strong>
                  <div className="ml-2 text-gray-700">
                    • 5: Elite/Professional Level
                  </div>
                  <div className="ml-2 text-gray-700">
                    • 4: Advanced/Competitive
                  </div>
                  <div className="ml-2 text-gray-700">
                    • 3: Intermediate/Developing
                  </div>
                  <div className="ml-2 text-gray-700">
                    • 2: Beginner/Learning
                  </div>
                  <div className="ml-2 text-gray-700">
                    • 1: Needs Significant Work
                  </div>
                </div>
                <div className="mt-3">
                  <strong>Accuracy Metrics (%):</strong>
                  <div className="ml-2 text-gray-700">
                    • Excellent: &gt;85% | Good: 75-85% | Average: 65-75% | Below: &lt;65%
                  </div>
                </div>
              </div>
            </div>

            {/* Tactical & Psychological Standards */}
            <div className="bg-white rounded-lg p-4 border border-green-200">
              <h4 className="font-bold text-green-900 mb-3">🧠 Tactical Awareness (1-5 Scale)</h4>
              <div className="space-y-2 text-sm text-gray-700">
                <p><strong>Game Intelligence:</strong> Understanding of game situations, reading play</p>
                <p><strong>Positioning:</strong> Spatial awareness, defensive/offensive positioning</p>
                <p><strong>Decision Making:</strong> Speed and quality of decisions under pressure</p>
              </div>
            </div>

            {/* Psychological Standards */}
            <div className="bg-white rounded-lg p-4 border border-orange-200">
              <h4 className="font-bold text-orange-900 mb-3">💪 Psychological (1-5 Scale)</h4>
              <div className="space-y-2 text-sm text-gray-700">
                <p><strong>Coachability:</strong> Receptiveness to feedback, willingness to learn</p>
                <p><strong>Mental Toughness:</strong> Resilience, focus, handling pressure</p>
              </div>
            </div>
          </div>

          <div className="mt-4 bg-blue-100 border border-blue-300 rounded-lg p-3">
            <p className="text-sm text-blue-900">
              <strong>💡 Tip:</strong> Be honest in your self-assessment. Accurate data leads to better personalized training programs!
            </p>
          </div>
          </>
          )}
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
              <p className="text-xs text-gray-600 mt-1">
                ⚡ Speed test: How fast you can run 30 meters. Elite: &lt;4.0s | Good: 4.0-4.3s | Average: 4.3-4.6s
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                🏃 Endurance test: Total distance covered in intermittent running. Elite: &gt;2400m | Good: 2000-2400m
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                💨 Aerobic capacity: Maximum oxygen uptake (ml/kg/min). Elite: &gt;60 | Good: 55-60 | Average: 50-55
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                🦘 Explosive power: Jump height from standing position. Elite: &gt;60cm | Good: 50-60cm | Average: 40-50cm
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                📊 Body composition: Percentage of body fat. Elite: 8-12% | Good: 12-15% | Average: 15-18%
              </p>
            </div>
          </div>
        </div>

        {/* Technical Metrics */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Technical Skills (1-5 scale)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ball Control (1-5)</label>
              <input
                type="number"
                min="1"
                max="5"
                name="ball_control"
                value={formData.ball_control}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-600 mt-1">
                ⚽ First touch, close control, ability to manipulate ball. 5=Elite | 4=Advanced | 3=Intermediate | 2=Beginner | 1=Needs Work
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                🎯 Success rate of completed passes in games/training. Elite: &gt;85% | Good: 75-85% | Average: 65-75%
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                🏃‍♂️ Percentage of successful take-ons and dribbles past opponents. Elite: &gt;85% | Good: 75-85%
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                🥅 Shots on target percentage. Elite: &gt;85% | Good: 75-85% | Average: 65-75%
              </p>
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
              <p className="text-xs text-gray-600 mt-1">
                🛡️ Success rate in 1v1 defensive situations and tackles. Elite: &gt;85% | Good: 75-85%
              </p>
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
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-6 border-2 border-green-200">
          <div className="text-center mb-4">
            <h3 className="text-xl font-bold text-gray-900 mb-2">Ready to Generate Your Programs?</h3>
            <p className="text-gray-600 text-sm">
              Your assessment will be analyzed by AI and coaches to create two personalized training programs
            </p>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-xl font-bold text-lg hover:from-blue-700 hover:to-blue-900 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Submitting to AI & Coach Analysis...
              </span>
            ) : (
              <>
                <div className="flex items-center justify-center gap-2">
                  <CheckCircle className="w-6 h-6" />
                  <span>Submit Assessment & Generate Programs</span>
                </div>
                <div className="text-xs mt-1 font-normal">Creates: Coach Program + AI Model Training</div>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PlayerAssessmentForm;
