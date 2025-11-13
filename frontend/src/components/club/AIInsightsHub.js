import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Brain, Zap, Target, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AIInsightsHub = ({ clubId }) => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchInsights();
  }, [clubId]);

  const fetchInsights = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/ai/insights`, { headers });
      setInsights(res.data.insights || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching insights:', error);
      setLoading(false);
    }
  };

  const generateInsights = async () => {
    try {
      setGenerating(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${BACKEND_URL}/api/club/${clubId}/ai/generate-insights`, {}, { headers });
      await fetchInsights();
      setGenerating(false);
    } catch (error) {
      console.error('Error generating insights:', error);
      setGenerating(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
    </div>;
  }

  const priorityColors = {
    critical: { bg: 'bg-red-900/20', border: 'border-red-500/30', text: 'text-red-400' },
    high: { bg: 'bg-orange-900/20', border: 'border-orange-500/30', text: 'text-orange-400' },
    medium: { bg: 'bg-yellow-900/20', border: 'border-yellow-500/30', text: 'text-yellow-400' },
    low: { bg: 'bg-blue-900/20', border: 'border-blue-500/30', text: 'text-blue-400' }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">AI Insights & Alerts</h2>
          <p className="text-gray-400">Intelligent recommendations and predictions</p>
        </div>
        <button
          onClick={generateInsights}
          disabled={generating}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl font-medium hover:shadow-lg transition disabled:opacity-50"
        >
          <Brain className="w-5 h-5" />
          {generating ? 'Generating...' : 'Generate Insights'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {insights.map((insight) => {
          const colors = priorityColors[insight.priority] || priorityColors.low;
          return (
            <div key={insight.id} className={`${colors.bg} backdrop-blur-xl rounded-2xl p-6 border ${colors.border} shadow-2xl`}>
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0`}>
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-bold text-white">{insight.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${colors.text} bg-gray-900/50`}>
                      {insight.priority}
                    </span>
                  </div>
                  <p className="text-gray-300 text-sm mb-4">{insight.description}</p>
                  {insight.recommendations && insight.recommendations.length > 0 && (
                    <div className="bg-gray-900/50 rounded-lg p-3">
                      <p className="text-white text-sm font-medium mb-2">Recommendations:</p>
                      <ul className="space-y-1">
                        {insight.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-gray-400 text-xs flex items-start gap-2">
                            <Zap className="w-3 h-3 text-green-400 mt-0.5 flex-shrink-0" />
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {insights.length === 0 && (
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-12 border border-purple-400/20 text-center">
          <Brain className="w-16 h-16 text-purple-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">No AI Insights Yet</h3>
          <p className="text-gray-400 mb-6">Generate insights to get AI-powered recommendations for your club</p>
          <button
            onClick={generateInsights}
            disabled={generating}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl font-medium hover:shadow-lg transition"
          >
            Generate First Insights
          </button>
        </div>
      )}
    </div>
  );
};

export default AIInsightsHub;