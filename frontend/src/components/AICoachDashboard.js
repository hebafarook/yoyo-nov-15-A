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
  const [predictiveData, setPredictiveData] = useState(null);
  const [loadingPredictive, setLoadingPredictive] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [exerciseType, setExerciseType] = useState('squat');
  const [formAnalysis, setFormAnalysis] = useState(null);
  const [aiFeedback, setAiFeedback] = useState(null);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  const [videoAnalysis, setVideoAnalysis] = useState(null);
  const [loadingVideo, setLoadingVideo] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

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
        goals: ['improve performance']
      });
      
      if (response.data.success) {
        setPredictiveData(response.data.analysis);
      }
    } catch (error) {
      console.error('Error loading predictive analysis:', error);
    } finally {
      setLoadingPredictive(false);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
      }
    } catch (error) {
      alert('Camera access denied');
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
    
    try {
      const formData = new FormData();
      formData.append('frame_base64', frameBase64);
      formData.append('exercise_type', exerciseType);
      const response = await axios.post(`${API}/ai-coach/analyze-form-frame`, formData);
      setFormAnalysis(response.data);
      
      if (response.data.pose_detected && response.data.issues.length > 0) {
        getAICoachingFeedback(response.data);
      }
    } catch (error) {
      console.error('Error analyzing frame:', error);
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
    setLoadingVideo(true);
    try {
      const formData = new FormData();
      formData.append('video', file);
      formData.append('exercise_type', exerciseType);
      const response = await axios.post(`${API}/ai-coach/analyze-video`, formData);
      setVideoAnalysis(response.data);
    } catch (error) {
      console.error('Error analyzing video:', error);
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
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-[--text-primary]">AI Coach & Analysis</h1>
        <p className="text-[--text-muted] mt-2">Advanced AI-powered training insights</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="predictive">📊 Predictive</TabsTrigger>
          <TabsTrigger value="form">👁️ Form Analysis</TabsTrigger>
          <TabsTrigger value="video">🎥 Video</TabsTrigger>
        </TabsList>

        <TabsContent value="predictive" className="space-y-6 mt-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Predictive Models</h2>
            <Button onClick={loadPredictiveAnalysis} disabled={loadingPredictive}>
              {loadingPredictive ? 'Loading...' : '🔄 Refresh'}
            </Button>
          </div>

          {loadingPredictive && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          )}

          {predictiveData && !loadingPredictive && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>⚠️ Injury Risk</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-4">
                    <div className={`text-6xl font-bold ${getRiskColor(predictiveData.injury_risk.risk_score)}`}>
                      {predictiveData.injury_risk.risk_score}
                    </div>
                    <div className="text-xl mt-2">{predictiveData.injury_risk.risk_level} Risk</div>
                  </div>
                  <Progress value={predictiveData.injury_risk.risk_score} className="h-3" />
                  <div className="mt-4">
                    <h4 className="font-semibold mb-2">Recommendations:</h4>
                    <ul className="text-sm space-y-1">
                      {predictiveData.injury_risk.recommendations.map((rec, idx) => (
                        <li key={idx}>• {rec}</li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>🎯 Match Readiness</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-4">
                    <div className={`text-6xl font-bold ${getReadinessColor(predictiveData.match_readiness.readiness_score)}`}>
                      {predictiveData.match_readiness.readiness_score}
                    </div>
                    <div className="text-xl mt-2">{predictiveData.match_readiness.status}</div>
                  </div>
                  <Progress value={predictiveData.match_readiness.readiness_score} className="h-3" />
                </CardContent>
              </Card>

              {predictiveData.performance_forecast.forecast_available && (
                <Card>
                  <CardHeader>
                    <CardTitle>📈 Performance Forecast</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded">
                        <div className="text-2xl font-bold">{predictiveData.performance_forecast.current_score}</div>
                        <div className="text-sm mt-1">Current</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded">
                        <div className="text-2xl font-bold">{predictiveData.performance_forecast.predicted_score_12_weeks}</div>
                        <div className="text-sm mt-1">12 Weeks</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader>
                  <CardTitle>💪 Optimal Load</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center p-4 bg-purple-50 rounded mb-4">
                    <div className="text-3xl font-bold">{predictiveData.optimal_training_load.recommended_weekly_load}m</div>
                    <div className="text-sm mt-1">Recommended Weekly Load</div>
                  </div>
                  <p className="text-sm">Intensity: {predictiveData.optimal_training_load.intensity_focus}</p>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="form" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>📱 Live Form Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Exercise:</label>
                  <select value={exerciseType} onChange={(e) => setExerciseType(e.target.value)} className="w-full p-2 border rounded">
                    <option value="squat">Squat</option>
                    <option value="lunge">Lunge</option>
                    <option value="sprint">Sprint</option>
                  </select>
                </div>

                <div className="flex gap-2">
                  {!cameraActive ? (
                    <Button onClick={startCamera} className="flex-1">📷 Start Camera</Button>
                  ) : (
                    <>
                      <Button onClick={captureAndAnalyzeFrame} className="flex-1">📸 Analyze</Button>
                      <Button onClick={stopCamera} variant="outline">⏹️ Stop</Button>
                    </>
                  )}
                </div>

                <div className="relative bg-black rounded overflow-hidden" style={{ aspectRatio: '16/9' }}>
                  <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                  <canvas ref={canvasRef} className="hidden" />
                </div>

                {formAnalysis && formAnalysis.pose_detected && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex justify-between">
                        <span>Result</span>
                        <span className={`text-2xl ${formAnalysis.form_score >= 85 ? 'text-green-600' : formAnalysis.form_score >= 70 ? 'text-yellow-600' : 'text-red-600'}`}>
                          {formAnalysis.form_score}/100
                        </span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="mb-3">
                        <span className="font-semibold">Verdict: </span>
                        <span className={`text-lg ${formAnalysis.verdict === 'Excellent' ? 'text-green-600' : formAnalysis.verdict === 'Good' ? 'text-yellow-600' : 'text-red-600'}`}>
                          {formAnalysis.verdict}
                        </span>
                      </div>
                      
                      {formAnalysis.issues.length > 0 && (
                        <div className="mb-3">
                          <h4 className="font-semibold mb-2">⚠️ Issues:</h4>
                          <ul className="text-sm space-y-1">
                            {formAnalysis.issues.map((issue, idx) => (
                              <li key={idx} className="text-red-600">• {issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {formAnalysis.corrections.length > 0 && (
                        <div>
                          <h4 className="font-semibold mb-2">✅ Corrections:</h4>
                          <ul className="text-sm space-y-1">
                            {formAnalysis.corrections.map((correction, idx) => (
                              <li key={idx} className="text-green-700">• {correction}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {aiFeedback && (
                  <Card>
                    <CardHeader>
                      <CardTitle>🤖 AI Coach Feedback</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="whitespace-pre-wrap">{aiFeedback}</p>
                    </CardContent>
                  </Card>
                )}

                {loadingFeedback && (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-sm">AI analyzing...</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="video" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>🎥 Upload Video</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Exercise:</label>
                  <select value={exerciseType} onChange={(e) => setExerciseType(e.target.value)} className="w-full p-2 border rounded">
                    <option value="squat">Squat</option>
                    <option value="lunge">Lunge</option>
                    <option value="sprint">Sprint</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Upload:</label>
                  <input type="file" accept="video/*" onChange={handleVideoUpload} className="w-full p-2 border rounded" />
                </div>

                {loadingVideo && (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4">Analyzing video...</p>
                  </div>
                )}

                {videoAnalysis && videoAnalysis.success && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center p-4 bg-blue-50 rounded">
                          <div className="text-3xl font-bold">{videoAnalysis.rep_count}</div>
                          <div className="text-sm mt-1">Reps</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded">
                          <div className="text-3xl font-bold">{videoAnalysis.average_form_score}</div>
                          <div className="text-sm mt-1">Avg Score</div>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded">
                          <div className="text-3xl font-bold">{videoAnalysis.analyzed_frames}</div>
                          <div className="text-sm mt-1">Frames</div>
                        </div>
                      </div>
                      
                      {videoAnalysis.common_issues && videoAnalysis.common_issues.length > 0 && (
                        <div className="mt-4">
                          <h4 className="font-semibold mb-2">Common Issues:</h4>
                          <ul className="space-y-2">
                            {videoAnalysis.common_issues.map(([issue, count], idx) => (
                              <li key={idx} className="flex justify-between">
                                <span className="text-sm">{issue}</span>
                                <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">{count}x</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
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
