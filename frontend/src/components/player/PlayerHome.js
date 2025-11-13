import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, Circle, Bell, TrendingUp, Calendar, Award, Flame, Heart, MessageSquare, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayerHome = ({ onStartSession, onTakeAssessment }) => {
  const { user } = useAuth();
  const [currentRoutine, setCurrentRoutine] = useState(null);
  const [dailyProgress, setDailyProgress] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      fetchPlayerData();
    }
  }, [user]);

  const [aiInsights, setAiInsights] = useState(null);
  const [playerProfile, setPlayerProfile] = useState(null);
  const [coachComments, setCoachComments] = useState([]);
  const [injuryReports, setInjuryReports] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState(null);

  const fetchPlayerData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch current routine
      const routineRes = await axios.get(`${BACKEND_URL}/api/current-routine/${user.id}`, { headers });
      setCurrentRoutine(routineRes.data);

      // Fetch daily progress history (last 7 days)
      const progressRes = await axios.get(`${BACKEND_URL}/api/daily-progress/${user.id}`, { headers });
      setDailyProgress(progressRes.data || []);

      // Fetch performance summary with strengths/weaknesses from assessment
      try {
        const summaryRes = await axios.get(`${BACKEND_URL}/api/player-performance-summary/${user.id}`, { headers });
        setPerformanceMetrics(summaryRes.data);
      } catch (err) {
        console.log('Performance summary not available:', err);
        setPerformanceMetrics(null);
      }

      // Fetch AI insights
      try {
        const insightsRes = await axios.post(`${BACKEND_URL}/api/ai-coach/player-insights`, 
          null,
          { 
            headers,
            params: { player_id: user.id }
          }
        );
        setAiInsights(insightsRes.data);
      } catch (err) {
        console.log('AI insights not available:', err);
      }

      // Fetch player profile with extended info
      try {
        const profileRes = await axios.get(`${BACKEND_URL}/api/auth/profile`, { headers });
        setPlayerProfile(profileRes.data);
      } catch (err) {
        console.log('Profile not available:', err);
      }

      // Fetch coach comments (mock for now)
      setCoachComments([
        { id: 1, coach: 'Coach Mike', date: '2024-01-10', comment: 'Great improvement in passing accuracy. Keep working on your weak foot.', type: 'positive' },
        { id: 2, coach: 'Coach Sarah', date: '2024-01-08', comment: 'Need to focus more on defensive positioning during matches.', type: 'improvement' },
        { id: 3, coach: 'Coach Mike', date: '2024-01-05', comment: 'Excellent work ethic in training. Speed drills showing results.', type: 'positive' }
      ]);

      // Fetch injury reports (mock for now)
      setInjuryReports([
        { id: 1, date: '2024-01-12', injury: 'Minor ankle strain', status: 'Recovered', severity: 'low', notes: 'Full training resumed' },
        { id: 2, date: '2023-12-20', injury: 'Hamstring tightness', status: 'Recovered', severity: 'medium', notes: 'Completed rehab protocol' }
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching player data:', error);
      setLoading(false);
    }
  };

  // Calculate streak from daily progress
  const calculateStreak = () => {
    if (!dailyProgress.length) return 0;
    let streak = 0;
    const today = new Date();
    for (let i = 0; i < dailyProgress.length; i++) {
      const progressDate = new Date(dailyProgress[i].date);
      const daysDiff = Math.floor((today - progressDate) / (1000 * 60 * 60 * 24));
      if (daysDiff === i) {
        streak++;
      } else {
        break;
      }
    }
    return streak;
  };

  // Calculate 7-day completion rate
  const calculate7DayCompletion = () => {
    if (!dailyProgress.length) return 0;
    const last7Days = dailyProgress.slice(0, 7);
    const totalExercises = last7Days.reduce((sum, day) => sum + (day.completed_exercises?.length || 0), 0);
    const completedExercises = last7Days.reduce((sum, day) => {
      return sum + (day.completed_exercises?.filter(ex => ex.completed).length || 0);
    }, 0);
    return totalExercises > 0 ? Math.round((completedExercises / totalExercises) * 100) : 0;
  };

  const player = {
    name: user?.username || user?.full_name || 'Player',
    level: 'Gold',
    avatar: (user?.username || 'P').substring(0, 2).toUpperCase(),
    streak: calculateStreak(),
    todayFocus: currentRoutine?.focus || 'Loading...',
    sessionTime: currentRoutine?.duration ? `${currentRoutine.duration} min` : '45-60 min'
  };

  const dailyChecklist = currentRoutine?.exercises?.map((ex, idx) => ({
    id: idx + 1,
    task: ex.name || ex.title,
    completed: false // Will be updated from daily progress
  })) || [];

  const upcomingSessions = [
    { id: 1, date: 'Today', time: '16:00', type: 'Technical', title: currentRoutine?.title || 'Training Session' },
    { id: 2, date: 'Tomorrow', time: '17:00', type: 'Conditioning', title: 'Speed & Agility' },
    { id: 3, date: 'Thu', time: '16:00', type: 'Match Prep', title: 'Team Tactical' }
  ];

  const lastAssessmentScore = performanceMetrics?.overall_score || 'N/A';
  const completionRate = calculate7DayCompletion();

  const quickStats = [
    { label: 'Last Assessment', value: lastAssessmentScore, color: 'text-green-600' },
    { label: '7-Day Completion', value: `${completionRate}%`, color: 'text-blue-600' },
    { label: 'Active Days', value: player.streak, color: 'text-yellow-600' }
  ];

  const notifications = [
    { id: 1, text: 'New training program available', icon: Calendar, time: '1h ago' },
    { id: 2, text: 'Check your progress', icon: Award, time: '3h ago' }
  ];

  const completedCount = dailyChecklist.filter(item => item.completed).length;
  const progressPercent = dailyChecklist.length > 0 ? Math.round((completedCount / dailyChecklist.length) * 100) : 0;

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Top Bar */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center text-2xl font-bold text-blue-600">
              {player.avatar}
            </div>
            <div>
              <h2 className="text-2xl font-bold">{player.name}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs font-medium">
                  {player.level} Level
                </span>
                <div className="flex items-center gap-1">
                  <Flame className="w-4 h-4" />
                  <span className="text-sm font-bold">{player.streak} day streak</span>
                </div>
              </div>
            </div>
          </div>
          <button className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition">
            <Bell className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Today's Focus Card */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-2xl font-bold text-gray-800 mb-2">Today's Focus</h3>
            <p className="text-lg text-gray-600">{player.todayFocus}</p>
            <p className="text-sm text-gray-500 mt-1">⏱️ {player.sessionTime}</p>
          </div>
          <button
            onClick={onStartSession}
            className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition flex items-center gap-2 shadow-lg"
          >
            <Play className="w-5 h-5" />
            Start Session
          </button>
        </div>
      </div>

      {/* Daily Checklist */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800">Daily Checklist</h3>
          <span className="text-sm font-medium text-gray-600">{completedCount}/{dailyChecklist.length} completed</span>
        </div>
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>
        <div className="space-y-3">
          {dailyChecklist.map((item) => (
            <div key={item.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
              {item.completed ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <Circle className="w-6 h-6 text-gray-400" />
              )}
              <span className={`text-sm font-medium ${
                item.completed ? 'text-gray-500 line-through' : 'text-gray-800'
              }`}>
                {item.task}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Sessions */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Upcoming Sessions</h3>
        <div className="space-y-3">
          {upcomingSessions.map((session) => (
            <div key={session.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800">{session.title}</h4>
                  <p className="text-sm text-gray-600">{session.date} at {session.time}</p>
                </div>
              </div>
              <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-xs font-medium">
                {session.type}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        {quickStats.map((stat, idx) => (
          <div key={idx} className="bg-white rounded-2xl p-4 shadow-lg border border-gray-200 text-center">
            <div className={`text-3xl font-bold ${stat.color} mb-1`}>{stat.value}</div>
            <div className="text-xs text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* AI Insights */}
      {aiInsights && (
        <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-6 shadow-lg border-2 border-purple-200">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-800">AI Coach Insights</h3>
          </div>
          
          <div className="bg-white rounded-xl p-4 mb-4">
            <p className="text-sm text-gray-700 leading-relaxed">{aiInsights.insights}</p>
          </div>

          {aiInsights.recommendations && aiInsights.recommendations.length > 0 && (
            <div className="bg-white rounded-xl p-4 mb-4">
              <h4 className="font-semibold text-gray-800 mb-2 text-sm">Recommendations:</h4>
              <ul className="space-y-2">
                {aiInsights.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-purple-600 font-bold">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-4 text-white">
            <p className="text-sm italic">"{aiInsights.motivational_message}"</p>
          </div>
        </div>
      )}

      {/* Player Profile Card */}
      <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-6 shadow-lg border-2 border-yellow-400">
        <h3 className="text-xl font-bold text-white mb-4">📋 Player Profile</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white/10 rounded-xl p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-200">Height</p>
            <p className="text-lg font-bold text-white">{playerProfile?.height || user?.height || '175 cm'}</p>
          </div>
          <div className="bg-white/10 rounded-xl p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-200">Weight</p>
            <p className="text-lg font-bold text-white">{playerProfile?.weight || user?.weight || '68 kg'}</p>
          </div>
          <div className="bg-white/10 rounded-xl p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-200">Position</p>
            <p className="text-lg font-bold text-white">{user?.position || 'Forward'}</p>
          </div>
          <div className="bg-white/10 rounded-xl p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-200">Dominant Foot</p>
            <p className="text-lg font-bold text-white">{user?.dominant_foot || playerProfile?.dominant_foot || 'Right'}</p>
          </div>
          <div className="bg-white/10 rounded-xl p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-200">Date Joined</p>
            <p className="text-lg font-bold text-white">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Jan 2024'}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Performance Snapshot */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-indigo-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">⚡ Quick Performance Snapshot</h3>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => onTakeAssessment && onTakeAssessment()}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition text-sm font-semibold"
            >
              Take Assessment
            </button>
          </div>
        </div>
        
        {performanceMetrics && performanceMetrics.has_assessment ? (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              {/* Physical Score - Clickable */}
              <button
                onClick={() => setSelectedMetric({
                  name: 'Physical',
                  score: Math.round(performanceMetrics.physical_score * 20),
                  strengths: performanceMetrics.physical_strengths || [],
                  weaknesses: performanceMetrics.physical_weaknesses || [],
                  color: 'purple'
                })}
                className="bg-purple-50 hover:bg-purple-100 rounded-xl p-4 text-center transition cursor-pointer border-2 border-transparent hover:border-purple-300"
              >
                <p className="text-sm text-purple-600 font-medium mb-1">Physical</p>
                <p className="text-3xl font-bold text-purple-900">{Math.round(performanceMetrics.physical_score * 20) || '--'}</p>
                <p className="text-xs text-gray-500 mt-1">Click for details</p>
              </button>

              {/* Technical Score - Clickable */}
              <button
                onClick={() => setSelectedMetric({
                  name: 'Technical',
                  score: Math.round(performanceMetrics.technical_score * 20),
                  strengths: performanceMetrics.technical_strengths || [],
                  weaknesses: performanceMetrics.technical_weaknesses || [],
                  color: 'blue'
                })}
                className="bg-blue-50 hover:bg-blue-100 rounded-xl p-4 text-center transition cursor-pointer border-2 border-transparent hover:border-blue-300"
              >
                <p className="text-sm text-blue-600 font-medium mb-1">Technical</p>
                <p className="text-3xl font-bold text-blue-900">{Math.round(performanceMetrics.technical_score * 20) || '--'}</p>
                <p className="text-xs text-gray-500 mt-1">Click for details</p>
              </button>

              {/* Tactical Score - Clickable */}
              <button
                onClick={() => setSelectedMetric({
                  name: 'Tactical',
                  score: Math.round(performanceMetrics.tactical_score * 20),
                  strengths: performanceMetrics.tactical_strengths || [],
                  weaknesses: performanceMetrics.tactical_weaknesses || [],
                  color: 'green'
                })}
                className="bg-green-50 hover:bg-green-100 rounded-xl p-4 text-center transition cursor-pointer border-2 border-transparent hover:border-green-300"
              >
                <p className="text-sm text-green-600 font-medium mb-1">Tactical</p>
                <p className="text-3xl font-bold text-green-900">{Math.round(performanceMetrics.tactical_score * 20) || '--'}</p>
                <p className="text-xs text-gray-500 mt-1">Click for details</p>
              </button>

              {/* Mental Score - Clickable */}
              <button
                onClick={() => setSelectedMetric({
                  name: 'Mental',
                  score: Math.round(performanceMetrics.psychological_score * 20),
                  strengths: performanceMetrics.mental_strengths || [],
                  weaknesses: performanceMetrics.mental_weaknesses || [],
                  color: 'orange'
                })}
                className="bg-orange-50 hover:bg-orange-100 rounded-xl p-4 text-center transition cursor-pointer border-2 border-transparent hover:border-orange-300"
              >
                <p className="text-sm text-orange-600 font-medium mb-1">Mental</p>
                <p className="text-3xl font-bold text-orange-900">{Math.round(performanceMetrics.psychological_score * 20) || '--'}</p>
                <p className="text-xs text-gray-500 mt-1">Click for details</p>
              </button>
            </div>

            {/* Next Assessment Date */}
            {performanceMetrics.last_assessment_date && (
              <div className="bg-blue-50 rounded-lg p-3 mb-4">
                <p className="text-sm text-blue-900">
                  <strong>Last Assessment:</strong> {new Date(performanceMetrics.last_assessment_date).toLocaleDateString()}
                  <span className="ml-4 text-blue-700">
                    <strong>Next Recommended:</strong> {new Date(new Date(performanceMetrics.last_assessment_date).getTime() + 28*24*60*60*1000).toLocaleDateString()} (4 weeks)
                  </span>
                </p>
              </div>
            )}

            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4">
              <h4 className="font-bold text-gray-800 mb-2">🎯 Current Focus Areas</h4>
              <ul className="space-y-2 text-sm">
                {performanceMetrics.focus_areas?.map((area, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-indigo-600 rounded-full"></span>
                    <span className="text-gray-700">{area}</span>
                  </li>
                )) || (
                  <>
                    <li className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-indigo-600 rounded-full"></span>
                      <span className="text-gray-700">Complete assessment to get personalized focus areas</span>
                    </li>
                  </>
                )}
              </ul>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">No performance data yet. Complete your first assessment!</p>
            <button 
              onClick={() => onTakeAssessment && onTakeAssessment()}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-blue-900 transition"
            >
              Take Assessment Now
            </button>
          </div>
        )}
      </div>

      {/* Metric Detail Modal */}
      {selectedMetric && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className={`bg-gradient-to-r from-${selectedMetric.color}-600 to-${selectedMetric.color}-800 p-6 text-white rounded-t-2xl`}>
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">{selectedMetric.name} Performance</h2>
                <button
                  onClick={() => setSelectedMetric(null)}
                  className="w-8 h-8 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition"
                >
                  <span className="text-2xl">×</span>
                </button>
              </div>
              <div className="mt-4">
                <p className="text-4xl font-bold">{selectedMetric.score}/100</p>
                <p className="text-white/90 mt-1">Current Score</p>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Strengths */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-2xl">💪</span> Strengths
                </h3>
                <div className="space-y-2">
                  {selectedMetric.strengths.map((strength, idx) => (
                    <div key={idx} className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{strength}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Weaknesses / Areas for Improvement */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <span className="text-2xl">🎯</span> Areas for Improvement
                </h3>
                <div className="space-y-2">
                  {selectedMetric.weaknesses.map((weakness, idx) => (
                    <div key={idx} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{weakness}</span>
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => setSelectedMetric(null)}
                className="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Injury Reports */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-red-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
            <Heart className="w-6 h-6 text-red-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-800">🏥 Injury & Health Reports</h3>
        </div>
        
        {injuryReports.length > 0 ? (
          <div className="space-y-3">
            {injuryReports.map((report) => (
              <div key={report.id} className={`p-4 rounded-xl border-2 ${
                report.severity === 'low' ? 'bg-green-50 border-green-200' :
                report.severity === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                'bg-red-50 border-red-200'
              }`}>
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-bold text-gray-800">{report.injury}</h4>
                    <p className="text-xs text-gray-600">{new Date(report.date).toLocaleDateString()}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    report.status === 'Recovered' ? 'bg-green-600 text-white' :
                    report.status === 'In Recovery' ? 'bg-yellow-600 text-white' :
                    'bg-red-600 text-white'
                  }`}>
                    {report.status}
                  </span>
                </div>
                <p className="text-sm text-gray-700">{report.notes}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-2" />
            <p className="text-sm text-gray-600 font-medium">No injuries reported - Keep up the good health! 💪</p>
          </div>
        )}
      </div>

      {/* Coach Comments & Notes */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-indigo-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
            <MessageSquare className="w-6 h-6 text-indigo-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-800">💬 Coach Comments & Notes</h3>
        </div>
        
        <div className="space-y-3">
          {coachComments.map((comment) => (
            <div key={comment.id} className={`p-4 rounded-xl border-l-4 ${
              comment.type === 'positive' ? 'bg-green-50 border-green-500' :
              comment.type === 'improvement' ? 'bg-yellow-50 border-yellow-500' :
              'bg-blue-50 border-blue-500'
            }`}>
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-bold text-gray-800">{comment.coach}</h4>
                  <p className="text-xs text-gray-600">{new Date(comment.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
                </div>
                {comment.type === 'positive' && <span className="text-2xl">⭐</span>}
                {comment.type === 'improvement' && <span className="text-2xl">📈</span>}
              </div>
              <p className="text-sm text-gray-700 italic">"{comment.comment}"</p>
            </div>
          ))}
        </div>

        {/* Add Note Button */}
        <button className="w-full mt-4 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition">
          + Add Personal Note
        </button>
      </div>

      {/* Notifications */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">🔔 Recent Updates</h3>
        <div className="space-y-3">
          {notifications.map((notif) => {
            const Icon = notif.icon;
            return (
              <div key={notif.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Icon className="w-5 h-5 text-purple-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">{notif.text}</p>
                  <p className="text-xs text-gray-500">{notif.time}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PlayerHome;