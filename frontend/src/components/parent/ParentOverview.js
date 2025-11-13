import React from 'react';
import { TrendingUp, TrendingDown, Minus, Calendar, Award } from 'lucide-react';

const ParentOverview = ({ child }) => {
  // Mock data - will connect to API
  const weeklyProgress = {
    completed: 4,
    total: 5,
    percentage: 80,
    nextAssessment: '2024-03-25',
    lastAssessmentScore: 78,
    trend: 'up'
  };

  const strengths = ['Speed & Acceleration', 'First Touch Control', 'Work Rate & Stamina'];
  const weaknesses = ['Left-foot finishing', '1v1 Defending', 'Heading accuracy'];

  const aiInsights = [
    'Showing consistent improvement in sprint times - down 0.3s this month',
    'Left-foot control needs extra focus - recommend 10 min daily juggling',
    'Excellent attendance and attitude in training sessions'
  ];

  const getTrendIcon = () => {
    if (weeklyProgress.trend === 'up') return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (weeklyProgress.trend === 'down') return <TrendingDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  return (
    <div className="space-y-6">
      {/* Top Section - Two Column */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Player Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-start gap-4">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {child.first_name[0]}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-800">
                {child.first_name} {child.last_name}
              </h2>
              <p className="text-gray-600">{child.age_group} • {child.primary_position}</p>
              
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">AI Rating</span>
                  <span className="text-2xl font-bold text-blue-600">{child.current_ai_rating}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${child.current_ai_rating}%` }}
                  ></div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-1">Current Focus</p>
                <p className="text-sm text-gray-600">Improving left-foot finishing and acceleration</p>
              </div>
            </div>
          </div>
        </div>

        {/* Weekly Progress Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">This Week's Progress</h3>
          
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Training Completion</span>
              <span className="text-sm font-bold text-gray-900">{weeklyProgress.percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-green-500 h-3 rounded-full transition-all"
                style={{ width: `${weeklyProgress.percentage}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Sessions Completed</p>
              <p className="text-2xl font-bold text-green-600">{weeklyProgress.completed}</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Sessions Missed</p>
              <p className="text-2xl font-bold text-red-600">{weeklyProgress.total - weeklyProgress.completed}</p>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <span className="text-sm text-gray-600">Next Assessment</span>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium">{weeklyProgress.nextAssessment}</span>
              </div>
            </div>
            <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <span className="text-sm text-gray-600">Last Assessment</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{weeklyProgress.lastAssessmentScore}</span>
                {getTrendIcon()}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-green-600" />
            Top 3 Strengths
          </h3>
          <div className="space-y-2">
            {strengths.map((strength, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-700">{strength}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Areas for Development</h3>
          <div className="space-y-2">
            {weaknesses.map((weakness, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-gray-700">{weakness}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Insights */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">AI Insights for Parents</h3>
        <div className="space-y-3">
          {aiInsights.map((insight, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold mt-0.5">
                {idx + 1}
              </div>
              <p className="text-sm text-gray-700 flex-1">{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ParentOverview;