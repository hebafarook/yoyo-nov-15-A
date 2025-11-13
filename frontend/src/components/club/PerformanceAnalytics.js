import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, BarChart3, Activity } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PerformanceAnalytics = ({ clubId }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [clubId]);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/analytics/overview`, { headers });
      setAnalytics(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (loading || !analytics) {
    return <div className="flex justify-center items-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
    </div>;
  }

  const radarData = [
    { metric: 'Physical', value: analytics.club_averages.physical },
    { metric: 'Technical', value: analytics.club_averages.technical },
    { metric: 'Tactical', value: analytics.club_averages.tactical },
    { metric: 'Mental', value: analytics.club_averages.mental }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Performance Analytics</h2>
        <p className="text-gray-400">Club-wide performance insights and trends</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-purple-400/20 shadow-2xl">
          <Activity className="w-12 h-12 text-purple-400 mb-3" />
          <p className="text-gray-400 text-sm">Physical</p>
          <p className="text-4xl font-bold text-white">{analytics.club_averages.physical.toFixed(1)}</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-blue-400/20 shadow-2xl">
          <BarChart3 className="w-12 h-12 text-blue-400 mb-3" />
          <p className="text-gray-400 text-sm">Technical</p>
          <p className="text-4xl font-bold text-white">{analytics.club_averages.technical.toFixed(1)}</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <TrendingUp className="w-12 h-12 text-green-400 mb-3" />
          <p className="text-gray-400 text-sm">Tactical</p>
          <p className="text-4xl font-bold text-white">{analytics.club_averages.tactical.toFixed(1)}</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-pink-400/20 shadow-2xl">
          <Brain className="w-12 h-12 text-pink-400 mb-3" />
          <p className="text-gray-400 text-sm">Mental</p>
          <p className="text-4xl font-bold text-white">{analytics.club_averages.mental.toFixed(1)}</p>
        </div>
      </div>

      <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
        <h3 className="text-xl font-bold text-white mb-4">Club Performance Profile</h3>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#374151" />
            <PolarAngleAxis dataKey="metric" stroke="#9CA3AF" />
            <PolarRadiusAxis domain={[0, 5]} stroke="#9CA3AF" />
            <Radar name="Club Average" dataKey="value" stroke="#4DFF91" fill="#4DFF91" fillOpacity={0.3} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
        <h3 className="text-xl font-bold text-white mb-4">Team Performance Breakdown</h3>
        <div className="space-y-4">
          {analytics.team_analytics && analytics.team_analytics.map((team) => (
            <div key={team.team_id} className="bg-gray-700/50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-white font-medium">{team.team_name}</h4>
                <span className="text-green-400 font-bold">{team.avg_overall.toFixed(1)}</span>
              </div>
              <div className="flex gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Players: </span>
                  <span className="text-white">{team.player_count}</span>
                </div>
                <div>
                  <span className="text-gray-400">Attendance: </span>
                  <span className="text-white">{team.avg_attendance.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const Brain = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h2a2 2 0 0 1 2 2v1.28c.6.35 1 .99 1 1.72 0 1.1-.9 2-2 2h-1v3c0 .55-.45 1-1 1H9c-.55 0-1-.45-1-1v-3H7c-1.1 0-2-.9-2-2 0-.73.4-1.37 1-1.72V9c0-1.1.9-2 2-2h2V5.73C9.4 5.39 9 4.74 9 4a2 2 0 0 1 2-2h1z" />
  </svg>
);

export default PerformanceAnalytics;