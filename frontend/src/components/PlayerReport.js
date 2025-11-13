import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const PlayerReport = ({ playerName }) => {
  const { user } = useAuth();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReport();
  }, [playerName]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${BACKEND_URL}/api/report/generate-dynamic/${playerName}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.data.success) {
        setReportData(response.data);
      }
      setLoading(false);
    } catch (err) {
      console.error('Error fetching report:', err);
      setError(err.response?.data?.detail || 'Failed to load report');
      setLoading(false);
    }
  };

  const getPerformanceLevelColor = (level) => {
    const colors = {
      'Elite': '#10b981',
      'Advanced': '#3b82f6',
      'Standard': '#f59e0b',
      'Needs Development': '#ef4444'
    };
    return colors[level] || '#6b7280';
  };

  const getGaugeColor = (percent) => {
    if (percent >= 95) return '#10b981'; // Green
    if (percent >= 85) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const MetricGauge = ({ title, score, unit, percent, description }) => {
    const gaugeData = [{
      name: title,
      value: Math.min(percent, 110),
      fill: getGaugeColor(percent)
    }];

    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">{title}</h4>
        <div className="flex items-center justify-between">
          <div className="w-32 h-32">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                cx="50%"
                cy="50%"
                innerRadius="60%"
                outerRadius="100%"
                data={gaugeData}
                startAngle={180}
                endAngle={0}
              >
                <PolarAngleAxis type="number" domain={[0, 110]} angleAxisId={0} tick={false} />
                <RadialBar
                  background
                  dataKey="value"
                  cornerRadius={10}
                  fill={gaugeData[0].fill}
                />
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="text-2xl font-bold"
                  fill={gaugeData[0].fill}
                >
                  {percent}%
                </text>
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 ml-4">
            <div className="text-2xl font-bold text-gray-900">{score}{unit}</div>
            <div className="text-xs text-gray-500 mt-1">{description}</div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  if (!reportData) return null;

  const { player_name, age, position, overall_score, performance_level, metrics, trend, strengths, weaknesses, recommendations } = reportData;

  // Prepare trend data for chart
  const trendData = trend.dates.map((date, idx) => ({
    date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    Overall: trend.overall_scores[idx],
    Sprint: trend.sprint_30m_scores[idx],
    Passing: trend.passing_accuracy_scores[idx]
  }));

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 mb-6 text-white">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold mb-2">PLAYER PERFORMANCE REPORT</h1>
            <div className="text-xl opacity-90">
              <span className="font-semibold">{player_name}</span> • Age {age} • {position}
            </div>
          </div>
          <div className="text-right">
            <div className="text-6xl font-bold">{overall_score}</div>
            <div className="text-sm opacity-90 mt-1">OVERALL SCORE</div>
          </div>
        </div>
        <div className="mt-4">
          <span 
            className="inline-block px-4 py-2 rounded-full text-sm font-semibold"
            style={{ backgroundColor: getPerformanceLevelColor(performance_level) }}
          >
            {performance_level}
          </span>
        </div>
      </div>

      {/* Performance Metrics - Gauges */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">PERFORMANCE METRICS</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricGauge
            title="Sprint 30m"
            score={metrics.sprint_30m.score}
            unit="s"
            percent={metrics.sprint_30m.percent_of_standard}
            description="Acceleration and top-end speed"
          />
          <MetricGauge
            title="Agility Test"
            score={metrics.agility.score}
            unit=""
            percent={metrics.agility.percent_of_standard}
            description="Change-of-direction speed"
          />
          <MetricGauge
            title="Reaction Time"
            score={metrics.reaction_time.score_ms}
            unit="ms"
            percent={metrics.reaction_time.percent_of_standard}
            description="Neuromotor response speed"
          />
          <MetricGauge
            title="Endurance (Yo-Yo)"
            score={metrics.endurance.score}
            unit=""
            percent={metrics.endurance.percent_of_standard}
            description="Aerobic capacity"
          />
          <MetricGauge
            title="Ball Control"
            score={metrics.ball_control.score_1_to_10}
            unit="/10"
            percent={metrics.ball_control.percent_of_standard}
            description="First touch and ball mastery"
          />
          <MetricGauge
            title="Passing Accuracy"
            score={metrics.passing_accuracy.score_percent}
            unit="%"
            percent={metrics.passing_accuracy.percent_of_standard}
            description="Accurate passes to target"
          />
        </div>
      </div>

      {/* Assessment Trend Chart */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">ASSESSMENT TREND</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Overall" stroke="#3b82f6" strokeWidth={2} />
            <Line type="monotone" dataKey="Sprint" stroke="#ef4444" strokeWidth={2} />
            <Line type="monotone" dataKey="Passing" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
        <p className="text-sm text-gray-600 mt-4">
          {trend.overall_scores.length > 1 && trend.overall_scores[trend.overall_scores.length - 1] > trend.overall_scores[0]
            ? "✓ Player shows positive improvement trend across assessment periods"
            : "Maintain consistent training focus to establish upward performance trajectory"}
        </p>
      </div>

      {/* Strengths */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">STRENGTHS</h2>
        <ul className="space-y-3">
          {strengths.map((strength, idx) => (
            <li key={idx} className="flex items-start">
              <span className="inline-block w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></span>
              <span className="text-gray-700">{strength}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Weaknesses */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">WEAKNESSES</h2>
        <ul className="space-y-3">
          {weaknesses.map((weakness, idx) => (
            <li key={idx} className="flex items-start">
              <span className="inline-block w-2 h-2 bg-red-500 rounded-full mt-2 mr-3"></span>
              <span className="text-gray-700">{weakness}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">RECOMMENDATIONS</h2>
        <ul className="space-y-3">
          {recommendations.map((rec, idx) => (
            <li key={idx} className="flex items-start">
              <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded mr-3 mt-0.5">
                {idx + 1}
              </span>
              <span className="text-gray-700 flex-1">{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <button
          onClick={() => window.print()}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
        >
          Print Report
        </button>
        <button
          onClick={fetchReport}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Refresh Report
        </button>
      </div>
    </div>
  );
};

export default PlayerReport;
