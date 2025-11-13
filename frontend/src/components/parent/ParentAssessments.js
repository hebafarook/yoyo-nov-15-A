import React, { useState } from 'react';
import { FileText, TrendingUp, TrendingDown, Minus, Calendar, User } from 'lucide-react';

const ParentAssessments = ({ child }) => {
  const [filter, setFilter] = useState('all');
  const [selectedAssessment, setSelectedAssessment] = useState(null);

  // Mock assessment data
  const assessments = [
    {
      id: '1',
      date: '2024-03-15',
      assessorType: 'Mixed',
      overallScore: 78,
      strengths: ['Speed', 'First Touch', 'Work Rate'],
      weaknesses: ['Left Foot', '1v1 Defending', 'Heading'],
      summary: 'Showing excellent progress in physical development. Technical skills improving steadily.',
      comparisonPrevious: 'Improved overall score by 5 points since last assessment',
      trend: 'up'
    },
    {
      id: '2',
      date: '2024-02-01',
      assessorType: 'Coach',
      overallScore: 73,
      strengths: ['Stamina', 'Positioning', 'Attitude'],
      weaknesses: ['Shooting Power', 'Weak Foot', 'Defensive Headers'],
      summary: 'Good foundation established. Need to focus on technical refinement.',
      comparisonPrevious: 'Steady progress with 3-point improvement',
      trend: 'up'
    },
    {
      id: '3',
      date: '2024-01-10',
      assessorType: 'AI',
      overallScore: 70,
      strengths: ['Speed', 'Dribbling', 'Mental Toughness'],
      weaknesses: ['Crossing', 'Tackling', 'Game Intelligence'],
      summary: 'Solid baseline established. Clear development pathway identified.',
      comparisonPrevious: 'Initial assessment - no comparison available',
      trend: 'stable'
    }
  ];

  const getAssessorColor = (type) => {
    switch (type) {
      case 'Coach': return 'bg-blue-100 text-blue-800';
      case 'AI': return 'bg-purple-100 text-purple-800';
      case 'Mixed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  if (selectedAssessment) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => setSelectedAssessment(null)}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Back to Assessments
        </button>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Assessment Report</h2>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {selectedAssessment.date}
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getAssessorColor(selectedAssessment.assessorType)}`}>
                  {selectedAssessment.assessorType}
                </span>
              </div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-bold text-blue-600 mb-1">{selectedAssessment.overallScore}</div>
              <div className="text-sm text-gray-600">Overall Score</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                Strengths
              </h3>
              <ul className="space-y-2">
                {selectedAssessment.strengths.map((strength, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-green-600 rounded-full"></span>
                    {strength}
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3">Areas for Development</h3>
              <ul className="space-y-2">
                {selectedAssessment.weaknesses.map((weakness, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                    {weakness}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="font-semibold text-gray-800 mb-2">Summary</h3>
            <p className="text-sm text-gray-700">{selectedAssessment.summary}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2">Progress Comparison</h3>
            <p className="text-sm text-gray-700">{selectedAssessment.comparisonPrevious}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Assessment History</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('3months')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === '3months' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Last 3 Months
          </button>
          <button
            onClick={() => setFilter('6months')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === '6months' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Last 6 Months
          </button>
        </div>
      </div>

      {/* Assessment List */}
      <div className="space-y-4">
        {assessments.map((assessment) => (
          <div key={assessment.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-gray-800">Assessment Report</h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getAssessorColor(assessment.assessorType)}`}>
                      {assessment.assessorType}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    {assessment.date}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-3xl font-bold text-blue-600">{assessment.overallScore}</span>
                  {getTrendIcon(assessment.trend)}
                </div>
                <span className="text-xs text-gray-600">Overall Score</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600 mb-1">Strengths</p>
                <p className="text-sm font-medium text-green-700">
                  {assessment.strengths.join(', ')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Development Areas</p>
                <p className="text-sm font-medium text-blue-700">
                  {assessment.weaknesses.join(', ')}
                </p>
              </div>
            </div>

            <p className="text-sm text-gray-700 mb-4">{assessment.summary}</p>

            <button
              onClick={() => setSelectedAssessment(assessment)}
              className="w-full py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition"
            >
              View Full Report
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ParentAssessments;