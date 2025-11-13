import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FileText, BarChart3, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AssessmentsOverview = ({ clubId }) => {
  const [assessmentData, setAssessmentData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssessments();
  }, [clubId]);

  const fetchAssessments = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/assessments/overview`, { headers });
      setAssessmentData(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assessments:', error);
      setLoading(false);
    }
  };

  if (loading || !assessmentData) {
    return <div className="flex justify-center items-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
    </div>;
  }

  const chartData = Object.entries(assessmentData.assessments_by_team || {}).map(([team, count]) => ({
    team,
    assessments: count
  }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Assessments Overview</h2>
        <p className="text-gray-400">Club-wide assessment tracking and analysis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-cyan-400/20 shadow-2xl">
          <FileText className="w-12 h-12 text-cyan-400 mb-3" />
          <p className="text-gray-400 text-sm">Total Assessments</p>
          <p className="text-4xl font-bold text-white">{assessmentData.total_assessments}</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <TrendingUp className="w-12 h-12 text-green-400 mb-3" />
          <p className="text-gray-400 text-sm">Recent (30 days)</p>
          <p className="text-4xl font-bold text-white">{assessmentData.recent_assessments}</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-purple-400/20 shadow-2xl">
          <BarChart3 className="w-12 h-12 text-purple-400 mb-3" />
          <p className="text-gray-400 text-sm">Teams Assessed</p>
          <p className="text-4xl font-bold text-white">{Object.keys(assessmentData.assessments_by_team || {}).length}</p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <h3 className="text-xl font-bold text-white mb-4">Assessments by Team</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="team" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4DFF91' }} />
              <Bar dataKey="assessments" fill="#4DFF91" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default AssessmentsOverview;