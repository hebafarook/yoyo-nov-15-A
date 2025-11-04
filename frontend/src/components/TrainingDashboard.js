import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Calendar, Clock, Target, TrendingUp, CheckCircle, 
  PlayCircle, PauseCircle, Star, MessageSquare,
  BarChart3, Award, Timer, Users, BookOpen, AlertCircle,
  Trophy, Activity, Zap, Brain
} from 'lucide-react';
import axios from 'axios';
import { YOUTH_HANDBOOK_STANDARDS, evaluatePerformance, getAgeCategory } from '../AssessmentStandards';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingDashboard = ({ playerId }) => {
  const [assessmentData, setAssessmentData] = useState(null);
  const [assessmentAnalysis, setAssessmentAnalysis] = useState(null);
  const [programRecommendation, setProgramRecommendation] = useState(null);
  const [periodizedProgram, setPeriodizedProgram] = useState(null);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [currentWeek, setCurrentWeek] = useState(0);
  const [dailyProgress, setDailyProgress] = useState([]);
  const [completedExercises, setCompletedExercises] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeExercise, setActiveExercise] = useState(null);
  const [exerciseTimer, setExerciseTimer] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [selectedFrequency, setSelectedFrequency] = useState(5); // Default 5 days/week
  const [showAnalysis, setShowAnalysis] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [playerId]);

  useEffect(() => {
    let interval = null;
    if (isTimerRunning && activeExercise) {
      interval = setInterval(() => {
        setExerciseTimer(timer => timer + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, activeExercise]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      console.log('=== LOADING DASHBOARD DATA ===');
      console.log('playerId:', playerId);
      
      // Load player's most recent assessment
      const assessmentResponse = await axios.get(`${API}/assessments/player/${playerId}`);
      console.log('Assessment response:', assessmentResponse.data);
      
      if (assessmentResponse.data && assessmentResponse.data.length > 0) {
        const latestAssessment = assessmentResponse.data[0];
        console.log('Latest assessment:', latestAssessment);
        setAssessmentData(latestAssessment);
        
        // Load detailed assessment analysis from backend
        try {
          const analysisResponse = await axios.get(`${API}/analyze-assessment/${playerId}`);
          console.log('Assessment analysis:', analysisResponse.data);
          setAssessmentAnalysis(analysisResponse.data);
          
          // Set suggested training frequency
          if (analysisResponse.data?.recommendations?.suggested_frequency) {
            setSelectedFrequency(analysisResponse.data.recommendations.suggested_frequency);
          }
        } catch (analysisError) {
          console.log('Could not load assessment analysis:', analysisError.message);
        }
        
        // Calculate program recommendation based on assessment
        const recommendation = calculateProgramRecommendation(latestAssessment);
        console.log('Program recommendation:', recommendation);
        setProgramRecommendation(recommendation);
      } else {
        console.log('No assessments found for player:', playerId);
      }
      
      // Load periodized program if exists
      try {
        const programResponse = await axios.get(`${API}/periodized-programs/${playerId}`);
        if (programResponse.data) {
          console.log('Existing program found:', programResponse.data);
          setPeriodizedProgram(programResponse.data);
          setShowAnalysis(false); // Hide analysis if program already exists
        }
      } catch (progError) {
        // Program might not exist yet, that's okay
        console.log('No existing program found:', progError.message);
      }
      
      // Load daily progress
      try {
        const progressResponse = await axios.get(`${API}/progress/daily-progress/${playerId}`);
        console.log('Daily progress:', progressResponse.data);
        setDailyProgress(progressResponse.data || []);
      } catch (progError) {
        // Progress might not exist yet
        console.log('No progress data found:', progError.message);
      }
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateProgramRecommendation = (assessment) => {
    const ageCategory = getAgeCategory(assessment.age);
    const standards = YOUTH_HANDBOOK_STANDARDS[ageCategory];
    
    // Calculate gaps for each category
    const gaps = {
      physical: calculateCategoryGap('physical', assessment, standards),
      technical: calculateCategoryGap('technical', assessment, standards),
      tactical: calculateCategoryGap('tactical', assessment, standards),
      psychological: calculateCategoryGap('psychological', assessment, standards)
    };
    
    // Find areas needing most improvement
    const weakestAreas = Object.entries(gaps)
      .sort((a, b) => b[1].gapPercentage - a[1].gapPercentage)
      .slice(0, 2)
      .map(([area]) => area);
    
    // Calculate recommended program length (weeks)
    const avgGap = Object.values(gaps).reduce((sum, g) => sum + g.gapPercentage, 0) / 4;
    let programWeeks = 8; // minimum
    if (avgGap > 40) programWeeks = 16;
    else if (avgGap > 25) programWeeks = 12;
    
    // Determine phases based on gaps
    const phases = [];
    if (avgGap > 30) {
      phases.push({
        name: 'Foundation Phase',
        duration: Math.ceil(programWeeks * 0.4),
        focus: ['Physical conditioning', 'Basic technique refinement'],
        objectives: ['Build fitness base', 'Correct movement patterns']
      });
    }
    
    phases.push({
      name: 'Development Phase',
      duration: Math.ceil(programWeeks * 0.4),
      focus: weakestAreas.map(area => `${area.charAt(0).toUpperCase() + area.slice(1)} skills`),
      objectives: ['Progressive overload', 'Skill integration']
    });
    
    phases.push({
      name: 'Peak Performance Phase',
      duration: Math.floor(programWeeks * 0.2),
      focus: ['Game-like scenarios', 'Competition preparation'],
      objectives: ['Peak conditioning', 'Tactical mastery']
    });
    
    return {
      totalWeeks: programWeeks,
      phases,
      gaps,
      weakestAreas,
      targetLevel: getNextPerformanceLevel(assessment.overall_score)
    };
  };

  const calculateCategoryGap = (category, assessment, standards) => {
    const metrics = {
      physical: ['sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat'],
      technical: ['ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels'],
      tactical: ['game_intelligence', 'positioning', 'decision_making'],
      psychological: ['coachability', 'mental_toughness']
    };
    
    const categoryMetrics = metrics[category];
    let totalGap = 0;
    let validMetrics = 0;
    
    categoryMetrics.forEach(metric => {
      const value = assessment[metric];
      if (value !== undefined && value !== null) {
        const performance = evaluatePerformance(value, metric, assessment.age);
        const performanceScore = getPerformanceScore(performance);
        const gap = 5 - performanceScore; // Gap from excellence (5)
        totalGap += gap;
        validMetrics++;
      }
    });
    
    const avgGap = validMetrics > 0 ? totalGap / validMetrics : 0;
    return {
      gapScore: avgGap,
      gapPercentage: (avgGap / 5) * 100,
      rating: avgGap > 2 ? 'Needs Significant Work' : avgGap > 1 ? 'Room for Improvement' : 'Strong'
    };
  };

  const getPerformanceScore = (performance) => {
    const scores = { excellent: 5, good: 4, average: 3, 'below average': 2, poor: 1 };
    return scores[performance] || 3;
  };

  const getNextPerformanceLevel = (currentScore) => {
    if (currentScore < 40) return 'Beginner → Intermediate';
    if (currentScore < 60) return 'Intermediate → Advanced';
    if (currentScore < 80) return 'Advanced → Elite';
    return 'Elite → Professional';
  };

  const generateProgram = async () => {
    try {
      setIsLoading(true);
      
      console.log('=== GENERATE PROGRAM DEBUG ===');
      console.log('assessmentData:', assessmentData);
      console.log('programRecommendation:', programRecommendation);
      console.log('playerId:', playerId);
      
      if (!assessmentData || !programRecommendation) {
        alert('Please complete an assessment first. Assessment data is missing.');
        return;
      }
      
      if (!playerId) {
        alert('Player ID is missing. Please ensure you have completed an assessment.');
        return;
      }
      
      // Calculate dynamic duration based on selected training frequency
      let calculatedDuration = programRecommendation.totalWeeks; // default
      
      if (assessmentAnalysis?.recommendations?.program_duration_options) {
        const durationOptions = assessmentAnalysis.recommendations.program_duration_options;
        if (selectedFrequency === 3) {
          calculatedDuration = durationOptions["3_days"].weeks;
        } else if (selectedFrequency === 4) {
          calculatedDuration = durationOptions["4_days"].weeks;
        } else if (selectedFrequency === 5) {
          calculatedDuration = durationOptions["5_days"].weeks;
        }
      }
      
      // Create the program using the backend endpoint with dynamic duration
      const programData = {
        player_id: playerId,
        program_name: `${playerId}'s Elite Training Program`,
        total_duration_weeks: calculatedDuration,
        program_objectives: [
          `Improve from ${assessmentData.performance_level} to ${programRecommendation.targetLevel}`,
          `Focus on ${programRecommendation.weakestAreas.join(' and ')}`,
          'Build comprehensive soccer skills',
          'Peak performance preparation'
        ],
        assessment_interval_weeks: 4,
        training_frequency: selectedFrequency  // 3, 4, or 5 days per week
      };
      
      console.log('Sending program data to backend:', programData);
      const response = await axios.post(`${API}/periodized-programs`, programData);
      console.log('Backend response:', response.data);
      
      if (response.data) {
        setPeriodizedProgram(response.data);
        alert('✅ Training program generated successfully!\n\nYour personalized ' + programRecommendation.totalWeeks + '-week program is ready.');
      }
      
    } catch (error) {
      console.error('Error generating program:', error);
      console.error('Full error response:', error.response);
      
      let errorMessage = 'Error generating training program';
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage += ':\n' + error.response.data.detail.map(err => 
            typeof err === 'object' ? `${err.loc?.join('.')} - ${err.msg}` : err
          ).join('\n');
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage += ': ' + error.response.data.detail;
        } else {
          errorMessage += ': ' + JSON.stringify(error.response.data.detail);
        }
      } else if (error.message) {
        errorMessage += ': ' + error.message;
      }
      
      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const startExercise = (exercise) => {
    setActiveExercise(exercise);
    setExerciseTimer(0);
    setIsTimerRunning(true);
  };

  const pauseExercise = () => {
    setIsTimerRunning(false);
  };

  const completeExercise = async (exercise, feedback) => {
    try {
      setIsTimerRunning(false);
      const timeSpent = exerciseTimer;
      
      const completion = {
        player_id: playerId,
        exercise_id: exercise.id,
        routine_id: periodizedProgram?.macro_cycles?.[currentPhase]?.micro_cycles?.[currentWeek]?.daily_routines?.[0]?.id || 'temp-routine',
        completed: true,
        feedback: feedback.notes,
        difficulty_rating: feedback.difficulty,
        performance_rating: feedback.performance,
        notes: feedback.notes,
        time_taken: Math.floor(timeSpent / 60)
      };
      
      setCompletedExercises(prev => [...prev, completion]);
      setActiveExercise(null);
      setExerciseTimer(0);
      
      console.log('Exercise completed:', completion);
      
    } catch (error) {
      console.error('Error completing exercise:', error);
      alert('Error completing exercise. Please try again.');
    }
  };

  const submitDailyProgress = async () => {
    try {
      if (completedExercises.length === 0) {
        alert('Please complete at least one exercise before saving.');
        return;
      }

      const routineId = periodizedProgram?.macro_cycles?.[currentPhase]?.micro_cycles?.[currentWeek]?.daily_routines?.[0]?.id || 'temp-routine';

      const progressData = {
        player_id: playerId,
        routine_id: routineId,
        completed_exercises: completedExercises,
        overall_rating: 4,
        energy_level: 4,
        motivation_level: 4,
        daily_notes: "Training session completed",
        total_time_spent: completedExercises.reduce((total, ex) => total + (ex.time_taken || 0), 0)
      };
      
      await axios.post(`${API}/daily-progress`, progressData);
      
      await loadDashboardData();
      setCompletedExercises([]);
      
      alert('Daily progress saved successfully!');
      
    } catch (error) {
      console.error('Error saving daily progress:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';
      alert(`Error saving progress: ${errorMessage}`);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getIntensityColor = (intensity) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      maximum: 'bg-red-100 text-red-800'
    };
    return colors[intensity] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">Training Program Dashboard</h1>
        <p className="text-blue-100">Personalized Training Based on Your Assessment</p>
      </div>

      {/* Assessment Results & Program Recommendation */}
      {assessmentData && programRecommendation && (
        <Card className="border-2 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Assessment Results & Program Recommendation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Current Performance */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <Activity className="w-8 h-8 mx-auto mb-2 text-red-600" />
                <div className="text-2xl font-bold">{Math.round(assessmentData.overall_score || 0)}</div>
                <div className="text-sm text-gray-600">Overall Score</div>
                <Badge className={`mt-2 ${programRecommendation.gaps.physical.gapPercentage > 30 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                  {programRecommendation.gaps.physical.rating}
                </Badge>
              </div>

              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Zap className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold">{Math.round(100 - programRecommendation.gaps.technical.gapPercentage)}%</div>
                <div className="text-sm text-gray-600">Technical Skills</div>
                <Badge className="mt-2 bg-blue-100 text-blue-800">
                  {programRecommendation.gaps.technical.rating}
                </Badge>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Brain className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold">{Math.round(100 - programRecommendation.gaps.tactical.gapPercentage)}%</div>
                <div className="text-sm text-gray-600">Tactical Awareness</div>
                <Badge className="mt-2 bg-green-100 text-green-800">
                  {programRecommendation.gaps.tactical.rating}
                </Badge>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Trophy className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <div className="text-2xl font-bold">{Math.round(100 - programRecommendation.gaps.psychological.gapPercentage)}%</div>
                <div className="text-sm text-gray-600">Mental Strength</div>
                <Badge className="mt-2 bg-purple-100 text-purple-800">
                  {programRecommendation.gaps.psychological.rating}
                </Badge>
              </div>
            </div>

            {/* Assessment Analysis - NEW */}
            {assessmentAnalysis && showAnalysis && (
              <div className="bg-white p-6 rounded-lg border-2 border-green-300 shadow-lg">
                <h3 className="text-2xl font-bold mb-4 flex items-center gap-2 text-green-700">
                  <BarChart3 className="w-6 h-6" />
                  Your Performance Analysis
                </h3>
                
                {/* Strengths Section */}
                {assessmentAnalysis.strengths && assessmentAnalysis.strengths.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-green-600 mb-2 flex items-center gap-2">
                      <Trophy className="w-5 h-5" />
                      Your Strengths
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {assessmentAnalysis.strengths.map((strength, idx) => (
                        <div key={idx} className="bg-green-50 p-3 rounded-lg border border-green-200">
                          <div className="font-medium text-sm">{strength.area}</div>
                          <Badge className="mt-1 bg-green-100 text-green-800 text-xs">{strength.level}</Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Weaknesses Section */}
                {assessmentAnalysis.weaknesses && assessmentAnalysis.weaknesses.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-orange-600 mb-2 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5" />
                      Areas for Improvement
                    </h4>
                    <div className="space-y-2">
                      {assessmentAnalysis.weaknesses.map((weakness, idx) => (
                        <div key={idx} className="bg-orange-50 p-3 rounded-lg border border-orange-200">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{weakness.area}</div>
                              <div className="text-sm text-gray-600">
                                Current: <span className="font-semibold">{weakness.current}</span> → 
                                Target: <span className="font-semibold text-green-600">{weakness.target}</span>
                              </div>
                            </div>
                            <Badge className={
                              weakness.priority === 'Critical' ? 'bg-red-100 text-red-800' :
                              weakness.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                              'bg-yellow-100 text-yellow-800'
                            }>
                              {weakness.priority}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Training Recommendations */}
                {assessmentAnalysis.recommendations && (
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-blue-700 mb-3">Training Recommendations</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Focus Areas</div>
                        <div className="flex flex-wrap gap-2">
                          {assessmentAnalysis.recommendations.focus_areas.map((area, idx) => (
                            <Badge key={idx} className="bg-blue-100 text-blue-800">{area}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Intensity Level</div>
                        <div className="font-semibold text-blue-700">
                          {assessmentAnalysis.recommendations.intensity}
                        </div>
                      </div>
                    </div>
                    
                    {/* Training Frequency Selector - NEW */}
                    <div className="border-t border-blue-200 pt-4 mt-4">
                      <label className="block text-sm font-semibold text-gray-700 mb-3">
                        Select Your Training Frequency
                      </label>
                      <div className="grid grid-cols-3 gap-3">
                        {[3, 4, 5].map((freq) => {
                          const durationKey = `${freq}_days`;
                          const durationInfo = assessmentAnalysis.recommendations.program_duration_options?.[durationKey];
                          
                          return (
                            <button
                              key={freq}
                              onClick={() => setSelectedFrequency(freq)}
                              className={`p-4 rounded-lg border-2 transition-all ${
                                selectedFrequency === freq
                                  ? 'border-blue-600 bg-blue-600 text-white shadow-lg'
                                  : 'border-gray-300 bg-white hover:border-blue-400'
                              }`}
                            >
                              <div className="text-2xl font-bold">{freq}</div>
                              <div className="text-sm">days/week</div>
                              {durationInfo && (
                                <div className={`text-xs mt-1 font-semibold ${
                                  selectedFrequency === freq ? 'text-blue-100' : 'text-blue-600'
                                }`}>
                                  {durationInfo.weeks} weeks
                                  <br />
                                  ({durationInfo.months} months)
                                </div>
                              )}
                              {freq === assessmentAnalysis.recommendations.suggested_frequency && (
                                <Badge className="mt-2 bg-green-100 text-green-800 text-xs">
                                  Recommended
                                </Badge>
                              )}
                            </button>
                          );
                        })}
                      </div>
                      <p className="text-xs text-gray-600 mt-3 text-center">
                        {selectedFrequency === 3 && "Slower progress - Good for beginners or busy schedules"}
                        {selectedFrequency === 4 && "Balanced progress - Recommended for most players"}
                        {selectedFrequency === 5 && "Fastest progress - For dedicated athletes"}
                      </p>
                      {assessmentAnalysis.recommendations.duration_explanation && (
                        <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
                          <strong>Timeline:</strong> {assessmentAnalysis.recommendations.duration_explanation}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Program Recommendation */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border-2 border-blue-300">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Recommended Training Program
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="text-sm text-gray-600 mb-2">Program Duration</div>
                  <div className="text-3xl font-bold text-blue-600">{programRecommendation.totalWeeks} Weeks</div>
                  <div className="text-sm text-gray-600 mt-1">
                    {programRecommendation.phases.length} Training Phases
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-600 mb-2">Target Progression</div>
                  <div className="text-lg font-semibold text-purple-600">
                    {programRecommendation.targetLevel}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Focus Areas: {programRecommendation.weakestAreas.map(area => 
                      area.charAt(0).toUpperCase() + area.slice(1)
                    ).join(', ')}
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t">
                <div className="text-sm font-semibold mb-2">Program Phases:</div>
                <div className="space-y-2">
                  {programRecommendation.phases.map((phase, idx) => (
                    <div key={idx} className="flex items-start gap-3 text-sm">
                      <Badge className="mt-0.5">{phase.duration}w</Badge>
                      <div>
                        <div className="font-semibold">{phase.name}</div>
                        <div className="text-gray-600">Focus: {phase.focus.join(', ')}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {!periodizedProgram && (
                <div className="mt-6 text-center">
                  <Button 
                    onClick={generateProgram}
                    disabled={isLoading}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating Your Program...
                      </>
                    ) : (
                      <>
                        <PlayCircle className="w-5 h-5 mr-2" />
                        Generate My Training Program
                      </>
                    )}
                  </Button>
                  <p className="text-sm text-gray-600 mt-2">
                    Click to create your personalized {programRecommendation.totalWeeks}-week training program
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Phase-Based Training Program */}
      {periodizedProgram && periodizedProgram.macro_cycles && (
        <Card>
          <CardHeader>
            <CardTitle>Training Program - Phase by Phase</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={`phase-${currentPhase}`} onValueChange={(val) => setCurrentPhase(parseInt(val.replace('phase-', '')))}>
              <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${periodizedProgram.macro_cycles.length}, 1fr)` }}>
                {periodizedProgram.macro_cycles.map((phase, idx) => (
                  <TabsTrigger key={idx} value={`phase-${idx}`}>
                    {phase.name}
                  </TabsTrigger>
                ))}
              </TabsList>

              {periodizedProgram.macro_cycles.map((phase, phaseIdx) => (
                <TabsContent key={phaseIdx} value={`phase-${phaseIdx}`} className="space-y-6">
                  {/* Phase Overview */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-bold text-lg mb-2">{phase.name}</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <div className="text-sm text-gray-600">Duration</div>
                        <div className="font-semibold">{phase.duration_weeks} weeks</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Start Date</div>
                        <div className="font-semibold">{new Date(phase.start_date).toLocaleDateString()}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Assessment Date</div>
                        <div className="font-semibold">{new Date(phase.assessment_date).toLocaleDateString()}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-semibold mb-1">Objectives:</div>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {phase.objectives.map((obj, i) => (
                          <li key={i}>{obj}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Weekly Plans */}
                  <div>
                    <h4 className="font-bold mb-3">Weekly Plans</h4>
                    <Tabs value={`week-${currentWeek}`} onValueChange={(val) => setCurrentWeek(parseInt(val.replace('week-', '')))}>
                      <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${Math.min(phase.micro_cycles.length, 6)}, 1fr)` }}>
                        {phase.micro_cycles.map((week, idx) => (
                          <TabsTrigger key={idx} value={`week-${idx}`}>
                            Week {week.cycle_number}
                          </TabsTrigger>
                        ))}
                      </TabsList>

                      {phase.micro_cycles.map((week, weekIdx) => (
                        <TabsContent key={weekIdx} value={`week-${weekIdx}`} className="space-y-4">
                          {/* Week Overview */}
                          <div className="bg-green-50 p-4 rounded-lg">
                            <h5 className="font-bold mb-2">{week.name}</h5>
                            <div className="text-sm text-gray-700 mb-2">
                              <strong>Focus:</strong> {week.phase}
                            </div>
                            <div className="text-sm mb-2">
                              <strong>Objectives:</strong>
                              <ul className="list-disc list-inside ml-2">
                                {week.objectives.map((obj, i) => (
                                  <li key={i}>{obj}</li>
                                ))}
                              </ul>
                            </div>
                          </div>

                          {/* Daily Routines */}
                          <div className="space-y-4">
                            <h5 className="font-semibold">Daily Breakdown</h5>
                            {week.daily_routines && week.daily_routines.map((day, dayIdx) => (
                              <Card key={dayIdx} className="border-l-4 border-l-blue-500">
                                <CardHeader className="pb-3">
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <CardTitle className="text-lg">Day {day.day_number}</CardTitle>
                                      <div className="text-sm text-gray-600 mt-1">
                                        {day.total_duration} minutes • {day.phase} phase
                                      </div>
                                    </div>
                                    <Badge className={getIntensityColor(day.intensity_rating)}>
                                      {day.intensity_rating} intensity
                                    </Badge>
                                  </div>
                                </CardHeader>
                                <CardContent>
                                  <div className="mb-3">
                                    <div className="text-sm font-semibold mb-1">Focus Areas:</div>
                                    <div className="flex gap-2 flex-wrap">
                                      {day.focus_areas.map((focus, i) => (
                                        <Badge key={i} variant="outline">{focus}</Badge>
                                      ))}
                                    </div>
                                  </div>

                                  <div className="space-y-3">
                                    <div className="text-sm font-semibold">Exercises ({day.exercises.length}):</div>
                                    {day.exercises.map((exercise, exIdx) => (
                                      <div key={exIdx} className="border rounded-lg p-3 hover:bg-gray-50">
                                        <div className="flex justify-between items-start mb-2">
                                          <div className="flex-1">
                                            <div className="font-semibold">{exercise.name}</div>
                                            <div className="text-sm text-gray-600">{exercise.category}</div>
                                          </div>
                                          <div className="text-right">
                                            <div className="text-sm font-semibold">{exercise.duration} min</div>
                                            <Badge size="sm" className={getIntensityColor(exercise.intensity)}>
                                              {exercise.intensity}
                                            </Badge>
                                          </div>
                                        </div>
                                        
                                        <div className="text-sm text-gray-700 mb-2">
                                          <strong>Purpose:</strong> {exercise.purpose}
                                        </div>

                                        {exercise.instructions && exercise.instructions.length > 0 && (
                                          <details className="text-sm">
                                            <summary className="cursor-pointer font-semibold text-blue-600 hover:text-blue-800">
                                              View Instructions
                                            </summary>
                                            <ol className="list-decimal list-inside mt-2 space-y-1 ml-2">
                                              {exercise.instructions.map((instruction, i) => (
                                                <li key={i}>{instruction}</li>
                                              ))}
                                            </ol>
                                          </details>
                                        )}

                                        <div className="mt-3 flex gap-2">
                                          {activeExercise?.id === exercise.id ? (
                                            <>
                                              <Button size="sm" variant="outline" onClick={pauseExercise}>
                                                <PauseCircle className="w-4 h-4 mr-1" />
                                                Pause ({formatTime(exerciseTimer)})
                                              </Button>
                                              <Button 
                                                size="sm" 
                                                onClick={() => completeExercise(exercise, { 
                                                  notes: 'Completed', 
                                                  difficulty: 3, 
                                                  performance: 4 
                                                })}
                                              >
                                                <CheckCircle className="w-4 h-4 mr-1" />
                                                Complete
                                              </Button>
                                            </>
                                          ) : (
                                            <Button size="sm" onClick={() => startExercise(exercise)}>
                                              <PlayCircle className="w-4 h-4 mr-1" />
                                              Start Exercise
                                            </Button>
                                          )}
                                        </div>
                                      </div>
                                    ))}
                                  </div>

                                  {completedExercises.length > 0 && (
                                    <div className="mt-4 pt-4 border-t">
                                      <Button onClick={submitDailyProgress} className="w-full">
                                        <CheckCircle className="w-4 h-4 mr-2" />
                                        Save Today's Progress ({completedExercises.length} exercises)
                                      </Button>
                                    </div>
                                  )}
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        </TabsContent>
                      ))}
                    </Tabs>
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* No Program Message */}
      {!periodizedProgram && (
        <Card>
          <CardContent className="p-12 text-center">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-xl font-semibold mb-2">No Training Program Found</h3>
            <p className="text-gray-600 mb-4">
              Complete an assessment and generate a training program to get started.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TrainingDashboard;
