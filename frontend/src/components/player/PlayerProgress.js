import React, { useState, useEffect } from 'react';
import { TrendingUp, Award, Calendar } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayerProgress = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overall');
  const [benchmarks, setBenchmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [consistencyData, setConsistencyData] = useState([]);
  const [technicalData, setTechnicalData] = useState([]);
  const [skillProfile, setSkillProfile] = useState([]);
  const [dailyProgress, setDailyProgress] = useState([]);

  useEffect(() => {
    if (user?.id) {
      fetchProgressData();
    }
  }, [user]);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch all benchmarks (assessments)
      const benchmarksRes = await axios.get(`${BACKEND_URL}/api/auth/benchmarks`, { headers });
      const allBenchmarks = benchmarksRes.data || [];
      
      // Sort by date
      allBenchmarks.sort((a, b) => new Date(a.saved_at) - new Date(b.saved_at));
      setBenchmarks(allBenchmarks);

      // Fetch daily progress for consistency tracking
      try {
        const progressRes = await axios.get(`${BACKEND_URL}/api/daily-progress/${user.id}`, { headers });
        setDailyProgress(progressRes.data || []);
      } catch (err) {
        console.log('Daily progress not available:', err);
      }

      // Process benchmarks into chart data
      if (allBenchmarks.length > 0) {
        // Technical data over time
        const techData = allBenchmarks.map(benchmark => {
          const data = benchmark.assessment_data || {};
          return {
            date: new Date(benchmark.saved_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            ballControl: (data.ball_control || 3) * 20,
            passing: data.passing_accuracy || 60,
            dribbling: data.dribbling_success || 60,
            shooting: data.shooting_accuracy || 55
          };
        });
        setTechnicalData(techData);

        // Skill profile comparison (latest vs first)
        if (allBenchmarks.length >= 1) {
          const latest = allBenchmarks[allBenchmarks.length - 1].assessment_data || {};
          const first = allBenchmarks[0].assessment_data || {};
          
          const profile = [
            { 
              skill: 'Speed', 
              current: latest.sprint_30m ? Math.max(0, 100 - (latest.sprint_30m - 4.0) * 20) : 70,
              baseline: first.sprint_30m ? Math.max(0, 100 - (first.sprint_30m - 4.0) * 20) : 65
            },
            { 
              skill: 'Endurance', 
              current: latest.yo_yo_test ? (latest.yo_yo_test / 2000) * 100 : 70,
              baseline: first.yo_yo_test ? (first.yo_yo_test / 2000) * 100 : 65
            },
            { 
              skill: 'Ball Control', 
              current: (latest.ball_control || 3) * 20,
              baseline: (first.ball_control || 3) * 20
            },
            { 
              skill: 'Passing', 
              current: latest.passing_accuracy || 65,
              baseline: first.passing_accuracy || 60
            },
            { 
              skill: 'Tactical', 
              current: (latest.positioning || 3) * 20,
              baseline: (first.positioning || 3) * 20
            },
            { 
              skill: 'Mental', 
              current: (latest.mental_toughness || 3) * 20,
              baseline: (first.mental_toughness || 3) * 20
            }
          ];
          setSkillProfile(profile);
        }

        // Training consistency from daily progress
        if (dailyProgress.length > 0) {
          const weeklyData = dailyProgress.slice(0, 6).reverse().map((day, idx) => {
            const completed = day.completed_exercises?.filter(ex => ex.completed).length || 0;
            const total = day.completed_exercises?.length || 1;
            return {
              week: `W${idx + 1}`,
              completion: Math.round((completed / total) * 100)
            };
          });
          setConsistencyData(weeklyData);
        }
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching progress data:', error);
      setLoading(false);
    }
  };

  const achievements = benchmarks.map((benchmark, idx) => ({
    id: benchmark.id,
    title: `Assessment #${idx + 1}`,
    icon: idx === 0 ? '🎯' : '📈',
    earned: new Date(benchmark.saved_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }));

  const coachFeedback = [
    '"Keep up the consistent training!" - AI Coach',
    '"Great improvement in your weak areas" - AI Coach',
    '"Remember to focus on recovery" - AI Coach'
  ];

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-6 text-white shadow-lg border-2 border-yellow-400">
        <h2 className="text-3xl font-bold mb-2">📊 My Progress</h2>
        <p className="text-white/90">See how you're improving over time</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {['overall', 'technical', 'physical'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 rounded-xl font-medium whitespace-nowrap transition ${
              activeTab === tab
                ? 'bg-yellow-400 text-indigo-900 shadow-lg font-bold'
                : 'bg-white text-gray-700 hover:bg-purple-50 border border-gray-200'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Overall Tab */}
      {activeTab === 'overall' && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Training Consistency</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={consistencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="completion" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Skill Profile Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={skillProfile}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis domain={[0, 100]} />
                <Radar name="Now" dataKey="current" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                <Radar name="3 Months Ago" dataKey="threeMonthsAgo" stroke="#9ca3af" fill="#9ca3af" fillOpacity={0.2} />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Technical Tab */}
      {activeTab === 'technical' && (
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Technical Scores Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={technicalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="assessment" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="dribbling" fill="#3b82f6" />
              <Bar dataKey="passing" fill="#8b5cf6" />
              <Bar dataKey="shooting" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Achievements */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <Award className="w-6 h-6 text-yellow-500" />
          <h3 className="text-xl font-bold text-gray-800">Achievements</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {achievements.map((achievement) => (
            <div key={achievement.id} className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-4 text-center border border-yellow-200">
              <div className="text-4xl mb-2">{achievement.icon}</div>
              <div className="font-bold text-gray-800 text-sm mb-1">{achievement.title}</div>
              <div className="text-xs text-gray-600">{achievement.earned}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Coach Feedback */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Coach Feedback</h3>
        <div className="space-y-3">
          {coachFeedback.map((feedback, idx) => (
            <div key={idx} className="bg-blue-50 rounded-xl p-4">
              <p className="text-gray-700 italic">{feedback}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PlayerProgress;