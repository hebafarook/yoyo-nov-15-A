import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, Circle, Bell, TrendingUp, Calendar, Award, Flame } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayerHome = ({ onStartSession }) => {
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

      // Fetch performance metrics
      const metricsRes = await axios.get(`${BACKEND_URL}/api/performance-metrics/${user.id}`, { headers });
      setPerformanceMetrics(metricsRes.data);

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

      {/* Notifications */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Updates</h3>
        <div className="space-y-3">
          {notifications.map((notif) => {
            const Icon = notif.icon;
            return (
              <div key={notif.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Icon className="w-5 h-5 text-blue-600" />
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