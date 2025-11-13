import React, { useState } from 'react';
import { FileText, TrendingUp, TrendingDown, Play } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts';

const PlayerAssessmentHistory = () => {
  const [selectedAssessment, setSelectedAssessment] = useState(null);

  const assessments = [
    {
      id: 1,
      date: '2024-03-15',
      type: 'Technical',
      score: 92,
      status: 'Reviewed by coach',
      breakdown: {
        dribbling: 95,
        passing: 88,
        shooting: 90,
        speed: 92,
        agility: 94,
        stamina: 90
      },
      aiSummary: 'You improved your sprint speed by 7% since last month. Great work on ball control!',
      coachComments: 'Excellent progress on weak foot. Keep working on tactical positioning.',
      videoUrl: '#'
    },
    {
      id: 2,
      date: '2024-02-15',
      type: 'Physical',
      score: 88,
      status: 'Reviewed by coach',
      breakdown: {
        dribbling: 90,
        passing: 85,
        shooting: 87,
        speed: 85,
        agility: 90,
        stamina: 88
      },
      aiSummary: 'Solid baseline performance. Focus on acceleration for next assessment.',
      coachComments: 'Good stamina levels. Work on explosive movements.',
      videoUrl: '#'
    },
    {
      id: 3,
      date: '2024-01-20',
      type: 'Match Performance',
      score: 85,
      status: 'Pending',
      breakdown: {
        dribbling: 88,
        passing: 82,
        shooting: 85,
        speed: 83,
        agility: 87,
        stamina: 85
      },
      aiSummary: 'Good match performance. Opportunities to improve passing accuracy.',
      coachComments: 'Pending coach review',
      videoUrl: null
    }
  ];

  if (selectedAssessment) {
    const radarData = Object.keys(selectedAssessment.breakdown).map(key => ({
      skill: key.charAt(0).toUpperCase() + key.slice(1),
      value: selectedAssessment.breakdown[key]
    }));

    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <button
          onClick={() => setSelectedAssessment(null)}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Back to Assessments
        </button>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-1">Assessment Report</h2>
              <p className="text-gray-600">{selectedAssessment.date} • {selectedAssessment.type}</p>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-blue-600 mb-1">{selectedAssessment.score}</div>
              <div className="text-sm text-gray-600">Overall Score</div>
            </div>
          </div>

          {/* Radar Chart */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Performance Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis domain={[0, 100]} />
                <Radar name="Performance" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* AI Summary */}
          <div className="bg-blue-50 rounded-xl p-4 mb-4">
            <h3 className="font-bold text-gray-800 mb-2">AI Summary</h3>
            <p className="text-gray-700">{selectedAssessment.aiSummary}</p>
          </div>

          {/* Coach Comments */}
          <div className="bg-gray-50 rounded-xl p-4 mb-4">
            <h3 className="font-bold text-gray-800 mb-2">Coach Comments</h3>
            <p className="text-gray-700">{selectedAssessment.coachComments}</p>
          </div>

          {selectedAssessment.videoUrl && (
            <button className="w-full py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2">
              <Play className="w-5 h-5" />
              Watch Assessment Video
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <h2 className="text-3xl font-bold mb-2">My Assessments</h2>
        <p className="text-white/90">Track your progress and improvements</p>
      </div>

      <div className="space-y-4">
        {assessments.map((assessment) => (
          <div
            key={assessment.id}
            onClick={() => setSelectedAssessment(assessment)}
            className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition cursor-pointer"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-800 text-lg mb-1">{assessment.type} Assessment</h3>
                  <p className="text-sm text-gray-600">{assessment.date}</p>
                  <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-medium ${
                    assessment.status === 'Reviewed by coach' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'
                  }`}>
                    {assessment.status}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-4xl font-bold text-blue-600">{assessment.score}</span>
                  {assessment.score >= 90 ? (
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  ) : assessment.score >= 85 ? (
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                  ) : (
                    <TrendingDown className="w-6 h-6 text-orange-600" />
                  )}
                </div>
                <div className="text-xs text-gray-600">Overall Score</div>
              </div>
            </div>
            <p className="text-sm text-gray-700 line-clamp-2">{assessment.aiSummary}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlayerAssessmentHistory;