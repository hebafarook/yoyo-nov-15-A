import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Calendar, Clock, Target, TrendingUp, CheckCircle, 
  PlayCircle, PauseCircle, Star, MessageSquare,
  BarChart3, Award, Timer, Users, BookOpen
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingDashboard = ({ playerId }) => {
  const [currentRoutine, setCurrentRoutine] = useState(null);
  const [dailyProgress, setDailyProgress] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [completedExercises, setCompletedExercises] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeExercise, setActiveExercise] = useState(null);
  const [exerciseTimer, setExerciseTimer] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);

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
      
      // Load current routine
      const routineResponse = await axios.get(`${API}/current-routine/${playerId}`);
      setCurrentRoutine(routineResponse.data);
      
      // Load daily progress
      const progressResponse = await axios.get(`${API}/daily-progress/${playerId}`);
      setDailyProgress(progressResponse.data);
      
      // Load performance metrics
      const metricsResponse = await axios.get(`${API}/performance-metrics/${playerId}`);
      setPerformanceMetrics(metricsResponse.data);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
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
      // Stop timer
      setIsTimerRunning(false);
      const timeSpent = exerciseTimer;
      
      // Mark as completed
      const completion = {
        player_id: playerId,
        exercise_id: exercise.id,
        routine_id: currentRoutine.routine.id,
        completed: true,
        feedback: feedback.notes,
        difficulty_rating: feedback.difficulty,
        performance_rating: feedback.performance,
        notes: feedback.notes,
        time_taken: Math.floor(timeSpent / 60) // Convert to minutes
      };
      
      setCompletedExercises(prev => [...prev, completion]);
      setActiveExercise(null);
      setExerciseTimer(0);
      
      // Update UI to show completion
      console.log('Exercise completed:', completion);
      
    } catch (error) {
      console.error('Error completing exercise:', error);
      alert('Error completing exercise. Please try again.');
    }
  };

  const submitDailyProgress = async () => {
    try {
      if (!currentRoutine || !currentRoutine.routine) {
        alert('No training routine found. Please reload the page.');
        return;
      }

      if (completedExercises.length === 0) {
        alert('Please complete at least one exercise before saving.');
        return;
      }

      const progressData = {
        player_id: playerId,
        routine_id: currentRoutine.routine.id,
        completed_exercises: completedExercises,
        overall_rating: 4, // This could be from a form
        energy_level: 4,
        motivation_level: 4,
        daily_notes: "Training session completed",
        total_time_spent: completedExercises.reduce((total, ex) => total + (ex.time_taken || 0), 0)
      };
      
      console.log('Saving daily progress:', progressData);
      
      const response = await axios.post(`${API}/daily-progress`, progressData);
      
      console.log('Daily progress saved successfully:', response.data);
      
      // Reload data
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
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">Training Dashboard</h1>
        <p className="text-blue-100">
          {currentRoutine?.program_name || 'Elite Soccer Development Program'}
        </p>
        <div className="flex items-center gap-4 mt-4">
          <Badge className="bg-white/20 text-white">
            Phase {currentRoutine?.current_phase || 1}
          </Badge>
          <Badge className="bg-white/20 text-white">
            Week {currentRoutine?.current_week || 1}
          </Badge>
          <Badge className="bg-white/20 text-white">
            Day {currentRoutine?.current_day || 1}
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="today" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="today">Today's Training</TabsTrigger>
          <TabsTrigger value="progress">Progress Tracking</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
        </TabsList>

        {/* Today's Training Tab */}
        <TabsContent value="today" className="space-y-6">
          {currentRoutine?.routine ? (
            <>
              {/* Current Routine Overview */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Today's Training Session
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {currentRoutine.routine.total_duration} min
                      </div>
                      <div className="text-sm text-gray-600">Total Duration</div>
                    </div>
                    <div className="text-center">
                      <Badge className={getIntensityColor(currentRoutine.routine.intensity_rating)}>
                        {currentRoutine.routine.intensity_rating.toUpperCase()}
                      </Badge>
                      <div className="text-sm text-gray-600 mt-1">Intensity</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {completedExercises.length}/{currentRoutine.routine.exercises.length}
                      </div>
                      <div className="text-sm text-gray-600">Completed</div>
                    </div>
                  </div>

                  {/* Focus Areas */}
                  <div className="mb-6">
                    <h4 className="font-semibold mb-2">Today's Focus Areas:</h4>
                    <div className="flex flex-wrap gap-2">
                      {currentRoutine.routine.focus_areas.map((area, index) => (
                        <Badge key={index} variant="outline">
                          {area.replace('_', ' ').toUpperCase()}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Exercises List */}
                  <div className="space-y-4">
                    <h4 className="font-semibold text-lg">Exercises:</h4>
                    {currentRoutine.routine.exercises.map((exercise, index) => (
                      <ExerciseCard
                        key={exercise.id}
                        exercise={exercise}
                        index={index}
                        isCompleted={completedExercises.some(c => c.exercise_id === exercise.id)}
                        isActive={activeExercise?.id === exercise.id}
                        onStart={() => startExercise(exercise)}
                        onPause={pauseExercise}
                        onComplete={(feedback) => completeExercise(exercise, feedback)}
                        timer={activeExercise?.id === exercise.id ? exerciseTimer : 0}
                        isTimerRunning={isTimerRunning}
                      />
                    ))}
                  </div>

                  {/* Submit Progress */}
                  {completedExercises.length > 0 && (
                    <div className="mt-6 pt-6 border-t">
                      <Button 
                        onClick={submitDailyProgress}
                        className="w-full bg-green-600 hover:bg-green-700"
                        size="lg"
                      >
                        <CheckCircle className="w-5 h-5 mr-2" />
                        Complete Today's Training Session
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Award className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Rest Day</h3>
                <p className="text-gray-600">
                  Take time to recover. Your next training session will be available tomorrow.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Progress Tracking Tab */}
        <TabsContent value="progress" className="space-y-6">
          <ProgressTrackingView 
            dailyProgress={dailyProgress}
            performanceMetrics={performanceMetrics}
          />
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <PerformanceView 
            performanceMetrics={performanceMetrics}
          />
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar" className="space-y-6">
          <CalendarView 
            currentRoutine={currentRoutine}
            dailyProgress={dailyProgress}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Exercise Card Component
const ExerciseCard = ({ 
  exercise, 
  index, 
  isCompleted, 
  isActive, 
  onStart, 
  onPause, 
  onComplete, 
  timer, 
  isTimerRunning 
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState({
    difficulty: 3,
    performance: 3,
    notes: ''
  });

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className={`${isCompleted ? 'bg-green-50 border-green-200' : ''} ${isActive ? 'ring-2 ring-blue-500' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              isCompleted ? 'bg-green-500 text-white' : 
              isActive ? 'bg-blue-500 text-white' : 
              'bg-gray-200 text-gray-600'
            }`}>
              {isCompleted ? <CheckCircle className="w-4 h-4" /> : index + 1}
            </div>
            <div>
              <CardTitle className="text-lg">{exercise.name}</CardTitle>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {exercise.category.toUpperCase()}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {exercise.duration} min
                </Badge>
                <Badge className={`text-xs ${
                  exercise.intensity === 'maximum' ? 'bg-red-100 text-red-800' :
                  exercise.intensity === 'high' ? 'bg-orange-100 text-orange-800' :
                  exercise.intensity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {exercise.intensity.toUpperCase()}
                </Badge>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {isActive && (
              <div className="text-xl font-mono font-bold text-blue-600">
                {formatTime(timer)}
              </div>
            )}
            
            {!isCompleted && !isActive && (
              <Button onClick={onStart} size="sm">
                <PlayCircle className="w-4 h-4 mr-1" />
                Start
              </Button>
            )}
            
            {isActive && isTimerRunning && (
              <Button onClick={onPause} size="sm" variant="outline">
                <PauseCircle className="w-4 h-4 mr-1" />
                Pause
              </Button>
            )}
            
            {isActive && (
              <Button 
                onClick={() => setShowFeedback(true)} 
                size="sm" 
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="w-4 h-4 mr-1" />
                Complete
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <p className="text-gray-600 mb-3">{exercise.description}</p>
        
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => setShowDetails(!showDetails)}
          className="mb-3"
        >
          <BookOpen className="w-4 h-4 mr-1" />
          {showDetails ? 'Hide' : 'Show'} Instructions
        </Button>
        
        {showDetails && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
            <div>
              <h5 className="font-semibold text-sm mb-2">Step-by-Step Instructions:</h5>
              <ol className="list-decimal list-inside space-y-1 text-sm">
                {exercise.instructions.map((instruction, i) => (
                  <li key={i}>{instruction}</li>
                ))}
              </ol>
            </div>
            
            <div>
              <h5 className="font-semibold text-sm mb-1">Purpose:</h5>
              <p className="text-sm text-gray-600">{exercise.purpose}</p>
            </div>
            
            <div>
              <h5 className="font-semibold text-sm mb-1">Expected Outcome:</h5>
              <p className="text-sm text-gray-600">{exercise.expected_outcome}</p>
            </div>
            
            {exercise.equipment_needed.length > 0 && (
              <div>
                <h5 className="font-semibold text-sm mb-1">Equipment Needed:</h5>
                <div className="flex flex-wrap gap-1">
                  {exercise.equipment_needed.map((item, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {item.replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Feedback Modal */}
        {showFeedback && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Exercise Feedback</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Difficulty (1-5):</label>
                  <div className="flex gap-1 mt-1">
                    {[1,2,3,4,5].map(rating => (
                      <Button
                        key={rating}
                        size="sm"
                        variant={feedback.difficulty === rating ? "default" : "outline"}
                        onClick={() => setFeedback(f => ({...f, difficulty: rating}))}
                      >
                        {rating}
                      </Button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium">Performance (1-5):</label>
                  <div className="flex gap-1 mt-1">
                    {[1,2,3,4,5].map(rating => (
                      <Button
                        key={rating}
                        size="sm"
                        variant={feedback.performance === rating ? "default" : "outline"}
                        onClick={() => setFeedback(f => ({...f, performance: rating}))}
                      >
                        {rating}
                      </Button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium">Notes:</label>
                  <textarea
                    className="w-full mt-1 p-2 border rounded-md"
                    rows="3"
                    value={feedback.notes}
                    onChange={(e) => setFeedback(f => ({...f, notes: e.target.value}))}
                    placeholder="How did this exercise feel? Any observations?"
                  />
                </div>
                
                <div className="flex gap-2">
                  <Button 
                    onClick={() => {
                      onComplete(feedback);
                      setShowFeedback(false);
                    }}
                    className="flex-1"
                  >
                    Submit & Complete
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => setShowFeedback(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Additional view components would go here...
const ProgressTrackingView = ({ dailyProgress, performanceMetrics }) => (
  <div>Progress tracking visualization would go here...</div>
);

const PerformanceView = ({ performanceMetrics }) => (
  <div>Performance metrics visualization would go here...</div>
);

const CalendarView = ({ currentRoutine, dailyProgress }) => (
  <div>Calendar view would go here...</div>
);

export default TrainingDashboard;