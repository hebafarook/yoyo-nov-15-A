import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Shield, AlertTriangle, Calendar, TrendingUp, Activity, Award, Brain } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ClubHome = ({ clubId }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, [clubId]);

  const fetchDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/dashboard`, { headers });
      setDashboardData(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      setLoading(false);
    }
  };

  if (loading || !dashboardData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
      </div>
    );
  }

  const { summary, alerts, injuries, upcoming_matches, ai_insights } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Club Dashboard</h2>
        <p className="text-gray-400">Real-time overview of your club's performance and safety</p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          icon={Users}
          label="Total Players"
          value={summary.total_players}
          color="blue"
          subtext="Active players"
        />
        <MetricCard
          icon={Users}
          label="Total Teams"
          value={summary.total_teams}
          color="purple"
          subtext="Active squads"
        />
        <MetricCard
          icon={AlertTriangle}
          label="Active Alerts"
          value={summary.active_alerts}
          color="red"
          trend={summary.red_flag_players > 0 ? 'warning' : 'good'}
          subtext={`${summary.red_flag_players} red flags`}
        />
        <MetricCard
          icon={Activity}
          label="Avg Weekly Load"
          value={summary.avg_weekly_load.toFixed(1)}
          color="green"
          subtext="Training intensity"
        />
      </div>

      {/* Safety Status & Upcoming Matches */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Safety Overview */}
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-6 h-6 text-green-400" />
            <h3 className="text-xl font-bold text-white">Safety Status</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                <span className="text-gray-300">Safe Players</span>
              </div>
              <span className="text-white font-bold">{summary.total_players - summary.red_flag_players - summary.caution_players}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                <span className="text-gray-300">Caution</span>
              </div>
              <span className="text-white font-bold">{summary.caution_players}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                <span className="text-gray-300">Red Flag</span>
              </div>
              <span className="text-white font-bold">{summary.red_flag_players}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Heart className="w-4 h-4 text-rose-400" />
                <span className="text-gray-300">Active Injuries</span>
              </div>
              <span className="text-white font-bold">{summary.active_injuries}</span>
            </div>
          </div>
        </div>

        {/* Upcoming Matches */}
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Calendar className="w-6 h-6 text-blue-400" />
            <h3 className="text-xl font-bold text-white">Upcoming Matches</h3>
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {upcoming_matches && upcoming_matches.length > 0 ? (
              upcoming_matches.slice(0, 5).map((match, idx) => (
                <div key={idx} className="bg-gray-700/50 rounded-lg p-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-white font-medium">{match.opponent}</p>
                      <p className="text-xs text-gray-400">{new Date(match.match_date).toLocaleDateString()}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      match.home_away === 'home' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                    }`}>
                      {match.home_away.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No upcoming matches</p>
            )}
          </div>
        </div>
      </div>

      {/* Alerts & AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Safety Alerts */}
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-red-400/20 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-red-400" />
            <h3 className="text-xl font-bold text-white">Active Alerts</h3>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {alerts && alerts.length > 0 ? (
              alerts.slice(0, 5).map((alert, idx) => (
                <div key={idx} className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-400 mt-1" />
                    <div className="flex-1">
                      <p className="text-white text-sm font-medium">{alert.title}</p>
                      <p className="text-gray-400 text-xs mt-1">{alert.description}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No active alerts</p>
            )}
          </div>
        </div>

        {/* AI Insights */}
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-purple-400/20 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-6 h-6 text-purple-400" />
            <h3 className="text-xl font-bold text-white">AI Insights</h3>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {ai_insights && ai_insights.length > 0 ? (
              ai_insights.slice(0, 5).map((insight, idx) => (
                <div key={idx} className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <Brain className="w-4 h-4 text-purple-400 mt-1" />
                    <div className="flex-1">
                      <p className="text-white text-sm font-medium">{insight.title}</p>
                      <p className="text-gray-400 text-xs mt-1">{insight.description}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-sm">No AI insights available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ icon: Icon, label, value, color, subtext, trend }) => {
  const colors = {
    blue: 'from-blue-500 to-cyan-500',
    purple: 'from-purple-500 to-pink-500',
    red: 'from-red-500 to-orange-500',
    green: 'from-green-500 to-emerald-500'
  };

  return (
    <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors[color]} flex items-center justify-center`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {trend && (
          <span className={`text-xs font-medium px-2 py-1 rounded ${
            trend === 'warning' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
          }`}>
            {trend === 'warning' ? '⚠️' : '✓'}
          </span>
        )}
      </div>
      <p className="text-gray-400 text-sm mb-1">{label}</p>
      <p className="text-3xl font-bold text-white mb-1">{value}</p>
      <p className="text-xs text-gray-500">{subtext}</p>
    </div>
  );
};

export default ClubHome;