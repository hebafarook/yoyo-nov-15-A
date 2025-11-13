import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, AlertTriangle, Activity, TrendingDown } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const SafetyCenter = ({ clubId }) => {
  const [safetyData, setSafetyData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSafetyData();
  }, [clubId]);

  const fetchSafetyData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/safety/overview`, { headers });
      setSafetyData(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching safety data:', error);
      setLoading(false);
    }
  };

  if (loading || !safetyData) {
    return <div className="flex justify-center items-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
    </div>;
  }

  const pieData = [
    { name: 'Safe', value: safetyData.safety_summary.safe, color: '#4DFF91' },
    { name: 'Caution', value: safetyData.safety_summary.caution, color: '#FBBF24' },
    { name: 'Red Flag', value: safetyData.safety_summary.red_flag, color: '#EF4444' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Safety & Training Load Center</h2>
        <p className="text-gray-400">Comprehensive workload and injury prevention monitoring</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <h3 className="text-xl font-bold text-white mb-4">Club Safety Score</h3>
          <div className="flex items-center justify-center mb-4">
            <div className="relative w-48 h-48">
              <svg className="transform -rotate-90 w-48 h-48">
                <circle cx="96" cy="96" r="80" stroke="#374151" strokeWidth="16" fill="none" />
                <circle cx="96" cy="96" r="80" stroke="#4DFF91" strokeWidth="16" fill="none"
                  strokeDasharray={`${(safetyData.safety_summary.safety_score / 100) * 502} 502`}
                  strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="text-5xl font-bold text-white">{safetyData.safety_summary.safety_score}</span>
                <span className="text-gray-400 text-sm">Safety Score</span>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mx-auto mb-1"></div>
              <p className="text-2xl font-bold text-white">{safetyData.safety_summary.safe}</p>
              <p className="text-xs text-gray-400">Safe</p>
            </div>
            <div className="text-center">
              <div className="w-3 h-3 bg-yellow-400 rounded-full mx-auto mb-1"></div>
              <p className="text-2xl font-bold text-white">{safetyData.safety_summary.caution}</p>
              <p className="text-xs text-gray-400">Caution</p>
            </div>
            <div className="text-center">
              <div className="w-3 h-3 bg-red-400 rounded-full mx-auto mb-1"></div>
              <p className="text-2xl font-bold text-white">{safetyData.safety_summary.red_flag}</p>
              <p className="text-xs text-gray-400">Red Flag</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <h3 className="text-xl font-bold text-white mb-4">Training Load Summary</h3>
          <div className="space-y-4">
            <div className="bg-gray-700/50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-400">Average Load</span>
                <Activity className="w-5 h-5 text-blue-400" />
              </div>
              <p className="text-3xl font-bold text-white">{safetyData.load_summary.average_load}</p>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-400">High Load Players</span>
                <TrendingDown className="w-5 h-5 text-red-400" />
              </div>
              <p className="text-3xl font-bold text-white">{safetyData.load_summary.high_load_count}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-red-400/20 shadow-2xl">
        <h3 className="text-xl font-bold text-white mb-4">Active Safety Alerts</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {safetyData.active_alerts && safetyData.active_alerts.length > 0 ? (
            safetyData.active_alerts.map((alert, idx) => (
              <div key={idx} className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 mt-1" />
                  <div className="flex-1">
                    <p className="text-white font-medium">{alert.title}</p>
                    <p className="text-gray-400 text-sm mt-1">{alert.description}</p>
                    <div className="flex gap-2 mt-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        alert.severity === 'critical' ? 'bg-red-500/30 text-red-300' :
                        alert.severity === 'high' ? 'bg-orange-500/30 text-orange-300' :
                        'bg-yellow-500/30 text-yellow-300'
                      }`}>
                        {alert.severity}
                      </span>
                      <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                        {alert.alert_type}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-400 text-center py-8">No active safety alerts</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SafetyCenter;