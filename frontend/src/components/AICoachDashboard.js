import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

export default function AICoachDashboard({ playerId, user }) {
  const [activeTab, setActiveTab] = useState('predictive');
  
  // Predictive Analysis State
  const [predictiveData, setPredictiveData] = useState(null);
  const [loadingPredictive, setLoadingPredictive] = useState(false);
  
  // Form Analysis State
  const [cameraActive, setCameraActive] = useState(false);
  const [exerciseType, setExerciseType] = useState('squat');
  const [formAnalysis, setFormAnalysis] = useState(null);
  const [capturedFrame, setCapturedFrame] = useState(null);
  
  // Video Analysis State
  const [videoFile, setVideoFile] = useState(null);
  const [videoAnalysis, setVideoAnalysis] = useState(null);
  const [loadingVideo, setLoadingVideo] = useState(false);
  
  // AI Feedback State
  const [aiFeedback, setAiFeedback] = useState(null);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  // Load predictive analysis on mount
  useEffect(() => {
    if (playerId) {
      loadPredictiveAnalysis();
    }
  }, [playerId]);

  const loadPredictiveAnalysis = async () => {
    setLoadingPredictive(true);
    try {
      const response = await axios.post(`${API}/ai-coach/predictive-analysis`, {
        player_name: playerId,
        days_to_match: 7,
        goals: ['improve performance', 'reduce injury risk']
      });
      
      if (response.data.success) {
        setPredict iveData(response.data.analysis);
      }
    } catch (error) {
      console.error('Error loading predictive analysis:', error);
    } finally {
      setLoadingPredictive(false);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
      }
    } catch (error) {
      alert('Camera access denied. Please allow camera permissions.');
      console.error('Camera error:', error);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const captureAndAnalyzeFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    const frameBase64 = canvas.toDataURL('image/jpeg');
    setCapturedFrame(frameBase64);
    
    // Analyze frame
    try {
      const formData = new FormData();
      formData.append('frame_base64', frameBase64);
      formData.append('exercise_type', exerciseType);
      
      const response = await axios.post(`${API}/ai-coach/analyze-form-frame`, formData);
      
      setFormAnalysis(response.data);
      
      // Get AI coaching feedback if form issues detected
      if (response.data.pose_detected && response.data.issues.length > 0) {
        getAICoachingFeedback(response.data);
      }
    } catch (error) {
      console.error('Error analyzing frame:', error);
      alert('Error analyzing form. Please try again.');
    }
  };

  const getAICoachingFeedback = async (formData) => {
    setLoadingFeedback(true);
    try {
      const feedbackForm = new FormData();
      feedbackForm.append('player_name', playerId);
      feedbackForm.append('form_issues', formData.issues.join(', '));
      feedbackForm.append('exercise_type', exerciseType);
      feedbackForm.append('form_score', formData.form_score);
      
      const response = await axios.post(`${API}/ai-coach/ai-coaching-feedback`, feedbackForm);
      
      setAiFeedback(response.data.ai_feedback);
    } catch (error) {
      console.error('Error getting AI feedback:', error);
    } finally {
      setLoadingFeedback(false);
    }
  };

  const handleVideoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setVideoFile(file);
    setLoadingVideo(true);
    
    try {
      const formData = new FormData();
      formData.append('video', file);
      formData.append('exercise_type', exerciseType);
      
      const response = await axios.post(`${API}/ai-coach/analyze-video`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setVideoAnalysis(response.data);
    } catch (error) {
      console.error('Error analyzing video:', error);
      alert('Error analyzing video. Please try again.');
    } finally {
      setLoadingVideo(false);
    }
  };

  const getRiskColor = (score) => {
    if (score < 35) return 'text-green-600';
    if (score < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getReadinessColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 65) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className=\"p-6 max-w-7xl mx-auto\">
      <div className=\"mb-6\">
        <h1 className=\"text-3xl font-bold text-[--text-primary]\">AI Coach & Analysis</h1>
        <p className=\"text-[--text-muted] mt-2\">
          Advanced predictive models, computer vision form analysis, and AI coaching feedback
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className=\"grid w-full grid-cols-3\">
          <TabsTrigger value=\"predictive\">📊 Predictive Analytics</TabsTrigger>
          <TabsTrigger value=\"form\">👁️ Form Analysis</TabsTrigger>
          <TabsTrigger value=\"video\">🎥 Video Analysis</TabsTrigger>
        </TabsList>

        {/* PREDICTIVE ANALYTICS TAB */}
        <TabsContent value=\"predictive\" className=\"space-y-6 mt-6\">
          <div className=\"flex justify-between items-center\">
            <h2 className=\"text-2xl font-bold\">Predictive Models</h2>
            <Button onClick={loadPredictiveAnalysis} disabled={loadingPredictive}>
              {loadingPredictive ? 'Loading...' : '🔄 Refresh Analysis'}
            </Button>
          </div>

          {loadingPredictive && (
            <div className=\"text-center py-12\">
              <div className=\"animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto\"></div>
              <p className=\"mt-4 text-[--text-muted]\">Generating AI predictions...</p>
            </div>
          )}

          {predictiveData && !loadingPredictive && (
            <div className=\"grid grid-cols-1 md:grid-cols-2 gap-6\">
              {/* Injury Risk */}
              <Card>
                <CardHeader>
                  <CardTitle>⚠️ Injury Risk Prediction</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-4\">
                    <div className=\"text-center\">
                      <div className={`text-6xl font-bold ${getRiskColor(predictiveData.injury_risk.risk_score)}`}>
                        {predictiveData.injury_risk.risk_score}
                      </div>
                      <div className=\"text-xl font-semibold mt-2\">
                        {predictiveData.injury_risk.risk_level} Risk
                      </div>
                    </div>
                    
                    <Progress value={predictiveData.injury_risk.risk_score} className=\"h-3\" />
                    
                    <div className=\"space-y-2\">
                      <h4 className=\"font-semibold\">Risk Factors:</h4>
                      {Object.entries(predictiveData.injury_risk.risk_factors).map(([factor, value]) => (
                        value > 0 && (
                          <div key={factor} className=\"flex justify-between text-sm\">
                            <span className=\"capitalize\">{factor.replace('_', ' ')}:</span>
                            <span className=\"font-semibold\">{Math.round(value)}</span>
                          </div>
                        )
                      ))}
                    </div>
                    
                    <div className=\"bg-yellow-50 p-3 rounded-lg\">
                      <h4 className=\"font-semibold mb-2 text-sm\">Recommendations:</h4>
                      <ul className=\"text-sm space-y-1\">
                        {predictiveData.injury_risk.recommendations.map((rec, idx) => (
                          <li key={idx}>• {rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Match Readiness */}
              <Card>
                <CardHeader>
                  <CardTitle>🎯 Match Readiness Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-4\">
                    <div className=\"text-center\">
                      <div className={`text-6xl font-bold ${getReadinessColor(predictiveData.match_readiness.readiness_score)}`}>
                        {predictiveData.match_readiness.readiness_score}
                      </div>
                      <div className=\"text-xl font-semibold mt-2\">
                        {predictiveData.match_readiness.status}
                      </div>
                    </div>
                    
                    <Progress value={predictiveData.match_readiness.readiness_score} className=\"h-3\" />
                    
                    <div className=\"space-y-2\">
                      <h4 className=\"font-semibold\">Component Breakdown:</h4>
                      {Object.entries(predictiveData.match_readiness.components).map(([component, value]) => (
                        <div key={component} className=\"flex justify-between text-sm\">
                          <span className=\"capitalize\">{component.replace('_', ' ')}:</span>
                          <span className=\"font-semibold\">{value}/100</span>
                        </div>
                      ))}
                    </div>
                    
                    {predictiveData.match_readiness.recommendations.length > 0 && (
                      <div className=\"bg-blue-50 p-3 rounded-lg\">
                        <h4 className=\"font-semibold mb-2 text-sm\">Match Prep:</h4>
                        <ul className=\"text-sm space-y-1\">
                          {predictiveData.match_readiness.recommendations.map((rec, idx) => (
                            <li key={idx}>• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Performance Forecast */}
              <Card>
                <CardHeader>
                  <CardTitle>📈 Performance Forecast</CardTitle>
                </CardHeader>
                <CardContent>
                  {predictiveData.performance_forecast.forecast_available ? (
                    <div className=\"space-y-4\">
                      <div className=\"grid grid-cols-2 gap-4\">
                        <div className=\"text-center p-4 bg-gray-50 rounded-lg\">
                          <div className=\"text-2xl font-bold text-blue-600\">
                            {predictiveData.performance_forecast.current_score}
                          </div>
                          <div className=\"text-sm text-gray-600 mt-1\">Current Score</div>
                          <div className=\"text-xs text-gray-500 mt-1\">
                            {predictiveData.performance_forecast.current_category}
                          </div>
                        </div>
                        <div className=\"text-center p-4 bg-green-50 rounded-lg\">
                          <div className=\"text-2xl font-bold text-green-600\">
                            {predictiveData.performance_forecast.predicted_score_12_weeks}
                          </div>
                          <div className=\"text-sm text-gray-600 mt-1\">12-Week Prediction</div>
                          <div className=\"text-xs text-gray-500 mt-1\">
                            {predictiveData.performance_forecast.predicted_category}
                          </div>
                        </div>
                      </div>
                      
                      <div className=\"text-center py-2\">
                        <div className=\"text-lg font-semibold\">
                          +{predictiveData.performance_forecast.improvement_rate_per_week} points/week
                        </div>
                        <div className=\"text-sm text-gray-600\">Average improvement rate</div>
                      </div>
                      
                      {predictiveData.performance_forecast.breakthrough_week && (
                        <Alert>
                          <AlertDescription>
                            🎯 Predicted breakthrough to next level in Week {predictiveData.performance_forecast.breakthrough_week}
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  ) : (
                    <div className=\"text-center py-8 text-gray-500\">
                      <p>{predictiveData.performance_forecast.message}</p>
                      <p className=\"text-sm mt-2\">Complete more assessments to enable forecasting</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Optimal Training Load */}
              <Card>
                <CardHeader>
                  <CardTitle>💪 Optimal Training Load</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className=\"space-y-4\">
                    <div className=\"grid grid-cols-2 gap-4\">
                      <div className=\"text-center p-4 bg-purple-50 rounded-lg\">
                        <div className=\"text-2xl font-bold text-purple-600\">
                          {predictiveData.optimal_training_load.recommended_weekly_load}m
                        </div>
                        <div className=\"text-sm text-gray-600 mt-1\">Recommended Load</div>
                      </div>
                      <div className=\"text-center p-4 bg-orange-50 rounded-lg\">
                        <div className=\"text-lg font-bold text-orange-600\">
                          {predictiveData.optimal_training_load.intensity_focus}
                        </div>
                        <div className=\"text-sm text-gray-600 mt-1\">Intensity Focus</div>
                      </div>
                    </div>
                    
                    <div className=\"bg-gray-50 p-3 rounded-lg\">
                      <h4 className=\"font-semibold mb-2 text-sm\">Weekly Structure:</h4>
                      <div className=\"text-sm space-y-1\">
                        <p>• High Intensity: {predictiveData.optimal_training_load.weekly_structure.high_intensity_days} days</p>
                        <p>• Moderate: {predictiveData.optimal_training_load.weekly_structure.moderate_days} days</p>
                        <p>• Recovery: {predictiveData.optimal_training_load.weekly_structure.recovery_days} days</p>
                        <p>• Rest: {predictiveData.optimal_training_load.weekly_structure.rest_days} day</p>
                      </div>
                    </div>
                    
                    {predictiveData.optimal_training_load.cautions.length > 0 && (
                      <div className=\"bg-yellow-50 p-3 rounded-lg\">
                        <ul className=\"text-sm space-y-1\">
                          {predictiveData.optimal_training_load.cautions.map((caution, idx) => (
                            <li key={idx}>• {caution}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {!predictiveData && !loadingPredictive && (
            <Card>
              <CardContent className=\"text-center py-12\">
                <p className=\"text-gray-500 mb-4\">No predictive analysis available yet</p>
                <Button onClick={loadPredictiveAnalysis}>
                  Generate Analysis
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* FORM ANALYSIS TAB */}
        <TabsContent value=\"form\" className=\"space-y-6 mt-6\">
          <Card>
            <CardHeader>
              <CardTitle>📱 Live Form Analysis with Mobile Camera</CardTitle>
            </CardHeader>
            <CardContent>
              <div className=\"space-y-4\">
                <div>
                  <label className=\"block text-sm font-medium mb-2\">Exercise Type:</label>
                  <select 
                    value={exerciseType}
                    onChange={(e) => setExerciseType(e.target.value)}
                    className=\"w-full p-2 border rounded\"
                  >
                    <option value=\"squat\">Squat</option>
                    <option value=\"lunge\">Lunge</option>
                    <option value=\"sprint\">Sprint Form</option>
                  </select>
                </div>

                <div className=\"flex gap-2\">
                  {!cameraActive ? (
                    <Button onClick={startCamera} className=\"flex-1\">
                      📷 Start Camera
                    </Button>
                  ) : (
                    <>
                      <Button onClick={captureAndAnalyzeFrame} className=\"flex-1\">
                        📸 Capture & Analyze
                      </Button>
                      <Button onClick={stopCamera} variant=\"outline\">
                        ⏹️ Stop
                      </Button>
                    </>
                  )}
                </div>

                <div className=\"relative bg-black rounded-lg overflow-hidden\" style={{ aspectRatio: '16/9' }}>
                  <video 
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className=\"w-full h-full object-cover\"
                  />
                  <canvas ref={canvasRef} className=\"hidden\" />
                </div>

                {formAnalysis && formAnalysis.pose_detected && (
                  <div className=\"space-y-4\">
                    <Card>
                      <CardHeader>
                        <CardTitle className=\"flex items-center justify-between\">
                          <span>Form Analysis Result</span>
                          <span className={`text-2xl font-bold ${
                            formAnalysis.form_score >= 85 ? 'text-green-600' :
                            formAnalysis.form_score >= 70 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {formAnalysis.form_score}/100
                          </span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className=\"space-y-3\">
                          <div>
                            <span className=\"font-semibold\">Verdict: </span>
                            <span className={`text-lg ${
                              formAnalysis.verdict === 'Excellent' ? 'text-green-600' :
                              formAnalysis.verdict === 'Good' ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>
                              {formAnalysis.verdict}
                            </span>
                          </div>

                          {formAnalysis.issues.length > 0 && (
                            <div>
                              <h4 className=\"font-semibold mb-2\">⚠️ Detected Issues:</h4>
                              <ul className=\"space-y-1 text-sm\">
                                {formAnalysis.issues.map((issue, idx) => (
                                  <li key={idx} className=\"text-red-600\">• {issue}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {formAnalysis.corrections.length > 0 && (
                            <div>
                              <h4 className=\"font-semibold mb-2\">✅ Corrections:</h4>
                              <ul className=\"space-y-1 text-sm\">
                                {formAnalysis.corrections.map((correction, idx) => (
                                  <li key={idx} className=\"text-green-700\">• {correction}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {Object.keys(formAnalysis.angles).length > 0 && (
                            <div>
                              <h4 className=\"font-semibold mb-2\">📐 Joint Angles:</h4>
                              <div className=\"grid grid-cols-2 gap-2 text-sm\">
                                {Object.entries(formAnalysis.angles).map(([joint, angle]) => (
                                  <div key={joint} className=\"flex justify-between\">
                                    <span className=\"capitalize\">{joint.replace('_', ' ')}:</span>
                                    <span className=\"font-mono\">{angle}°</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    {formAnalysis.annotated_frame && (
                      <Card>
                        <CardHeader>
                          <CardTitle>Pose Visualization</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <img 
                            src={formAnalysis.annotated_frame} 
                            alt=\"Annotated pose\"
                            className=\"w-full rounded-lg\"
                          />
                        </CardContent>
                      </Card>
                    )}

                    {aiFeedback && (
                      <Card>
                        <CardHeader>
                          <CardTitle>🤖 AI Coach Feedback</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className=\"prose prose-sm max-w-none\">
                            <p className=\"whitespace-pre-wrap\">{aiFeedback}</p>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {loadingFeedback && (
                      <div className=\"text-center py-4\">
                        <div className=\"animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto\"></div>
                        <p className=\"mt-2 text-sm text-gray-500\">AI Coach is analyzing your form...</p>
                      </div>
                    )}
                  </div>
                )}

                {formAnalysis && !formAnalysis.pose_detected && (
                  <Alert>
                    <AlertDescription>
                      No pose detected in frame. Please ensure:
                      • You're in good lighting
                      • Full body is visible in frame
                      • Camera has clear view
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* VIDEO ANALYSIS TAB */}
        <TabsContent value=\"video\" className=\"space-y-6 mt-6\">
          <Card>
            <CardHeader>
              <CardTitle>🎥 Upload Video for Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className=\"space-y-4\">
                <div>
                  <label className=\"block text-sm font-medium mb-2\">Exercise Type:</label>
                  <select 
                    value={exerciseType}
                    onChange={(e) => setExerciseType(e.target.value)}
                    className=\"w-full p-2 border rounded\"
                  >
                    <option value=\"squat\">Squat</option>
                    <option value=\"lunge\">Lunge</option>
                    <option value=\"sprint\">Sprint Form</option>
                  </select>
                </div>

                <div>
                  <label className=\"block text-sm font-medium mb-2\">Upload Video:</label>
                  <input
                    type=\"file\"
                    accept=\"video/*\"
                    onChange={handleVideoUpload}
                    className=\"w-full p-2 border rounded\"
                  />
                </div>

                {loadingVideo && (
                  <div className=\"text-center py-12\">
                    <div className=\"animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto\"></div>
                    <p className=\"mt-4 text-[--text-muted]\">Analyzing video... This may take a minute.</p>
                  </div>
                )}

                {videoAnalysis && videoAnalysis.success && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Video Analysis Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className=\"space-y-4\">
                        <div className=\"grid grid-cols-3 gap-4\">
                          <div className=\"text-center p-4 bg-blue-50 rounded-lg\">
                            <div className=\"text-3xl font-bold text-blue-600\">
                              {videoAnalysis.rep_count}
                            </div>
                            <div className=\"text-sm text-gray-600 mt-1\">Reps Counted</div>
                          </div>
                          <div className=\"text-center p-4 bg-green-50 rounded-lg\">
                            <div className=\"text-3xl font-bold text-green-600\">
                              {videoAnalysis.average_form_score}
                            </div>
                            <div className=\"text-sm text-gray-600 mt-1\">Avg Form Score</div>
                          </div>
                          <div className=\"text-center p-4 bg-purple-50 rounded-lg\">
                            <div className=\"text-3xl font-bold text-purple-600\">
                              {videoAnalysis.analyzed_frames}
                            </div>
                            <div className=\"text-sm text-gray-600 mt-1\">Frames Analyzed</div>
                          </div>
                        </div>

                        {videoAnalysis.common_issues && videoAnalysis.common_issues.length > 0 && (
                          <div>
                            <h4 className=\"font-semibold mb-2\">Most Common Issues:</h4>
                            <ul className=\"space-y-2\">
                              {videoAnalysis.common_issues.map(([issue, count], idx) => (
                                <li key={idx} className=\"flex justify-between items-center\">
                                  <span className=\"text-sm\">{issue}</span>
                                  <span className=\"bg-red-100 text-red-800 px-3 py-1 rounded-full text-xs font-semibold\">
                                    {count} times
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
"