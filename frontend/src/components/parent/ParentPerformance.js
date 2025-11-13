import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Activity, Zap, Heart } from 'lucide-react';

const ParentPerformance = ({ child }) => {
  const [selectedMetricGroup, setSelectedMetricGroup] = useState('physical');

  // Mock performance data
  const physicalData = [
    { date: 'Jan', sprint20m: 3.2, sprint30m: 4.5, agility: 8.1, endurance: 1400 },
    { date: 'Feb', sprint20m: 3.1, sprint30m: 4.4, agility: 7.9, endurance: 1500 },
    { date: 'Mar', sprint20m: 3.0, sprint30m: 4.3, agility: 7.7, endurance: 1600 },
  ];

  const technicalData = [
    { date: 'Jan', ballControl: 65, shootingAccuracy: 58, passingAccuracy: 72 },
    { date: 'Feb', ballControl: 70, shootingAccuracy: 62, passingAccuracy: 75 },
    { date: 'Mar', ballControl: 75, shootingAccuracy: 68, passingAccuracy: 78 },
  ];

  const mentalData = [
    { date: 'Jan', confidence: 70, motivation: 80, focus: 65 },
    { date: 'Feb', confidence: 75, motivation: 82, focus: 70 },
    { date: 'Mar', confidence: 80, motivation: 85, focus: 75 },
  ];

  const renderCharts = () => {
    if (selectedMetricGroup === 'physical') {
      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-gray-800 mb-4">Sprint Performance</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={physicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="sprint20m" stroke="#3b82f6" name="20m Sprint (s)" />
                <Line type="monotone" dataKey="sprint30m" stroke="#8b5cf6" name="30m Sprint (s)" />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-xs text-gray-600 mt-2">Lower times = better performance</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-gray-800 mb-4">Endurance (Yo-Yo Test)</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={physicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="endurance" stroke="#10b981" name="Distance (m)" />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-xs text-green-600 mt-2 font-medium">Trend: Improving (+200m in 2 months)</p>
          </div>
        </div>
      );
    }

    if (selectedMetricGroup === 'technical') {
      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-gray-800 mb-4">Ball Control & Passing</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={technicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="ballControl" stroke="#3b82f6" name="Ball Control" />
                <Line type="monotone" dataKey="passingAccuracy" stroke="#10b981" name="Passing Accuracy" />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-xs text-green-600 mt-2 font-medium">Trend: Steady improvement</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-gray-800 mb-4">Shooting Accuracy</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={technicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="shootingAccuracy" stroke="#ef4444" name="Accuracy %" />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-xs text-yellow-600 mt-2 font-medium">Trend: Progressing slowly, needs focus</p>
          </div>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-gray-800 mb-4">Mental Attributes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mentalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="confidence" stroke="#3b82f6" name="Confidence" />
              <Line type="monotone" dataKey="motivation" stroke="#10b981" name="Motivation" />
              <Line type="monotone" dataKey="focus" stroke="#f59e0b" name="Focus" />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-xs text-green-600 mt-2 font-medium">Trend: All metrics improving</p>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Performance Trends</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedMetricGroup('physical')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              selectedMetricGroup === 'physical' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Zap className="w-4 h-4" />
            Physical
          </button>
          <button
            onClick={() => setSelectedMetricGroup('technical')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              selectedMetricGroup === 'technical' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Activity className="w-4 h-4" />
            Technical
          </button>
          <button
            onClick={() => setSelectedMetricGroup('mental')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
              selectedMetricGroup === 'mental' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Heart className="w-4 h-4" />
            Mental
          </button>
        </div>
      </div>

      {/* Charts */}
      {renderCharts()}

      {/* AI Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow p-6">
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          AI Performance Summary
        </h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-green-600 rounded-full mt-2"></span>
            <span><strong>Biggest Improvement:</strong> 20m sprint time improved by 0.2s over 2 months</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-yellow-600 rounded-full mt-2"></span>
            <span><strong>Needs Attention:</strong> Left-foot shooting accuracy progressing slowly</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></span>
            <span><strong>Overall Trend:</strong> Consistent positive trajectory across most metrics</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ParentPerformance;