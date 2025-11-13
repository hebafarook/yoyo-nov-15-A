import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { Calendar, Activity, CheckCircle, Clock, Target, Zap, TrendingUp, Award } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayerTrainingPrograms = ({ onNavigateToAssessment }) => {
  const { user } = useAuth();
  const [programs, setPrograms] = useState({ ai: null, coach: null });
  const [loading, setLoading] = useState(true);
  const [activeProgram, setActiveProgram] = useState('coach'); // 'coach' or 'ai'

  useEffect(() => {
    if (user?.id) {
      fetchTrainingPrograms();
    }
  }, [user]);

  const fetchTrainingPrograms = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch AI-powered program
      const aiResponse = await axios.get(
        `${BACKEND_URL}/api/training/my-ai-program`,
        { headers }
      );

      // Fetch coach-guided program
      const coachResponse = await axios.get(
        `${BACKEND_URL}/api/training/my-coach-program`,
        { headers }
      );

      setPrograms({
        ai: aiResponse.data?.program || null,
        coach: coachResponse.data?.program || null
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching training programs:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your training programs...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!programs.ai && !programs.coach) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-12 shadow-xl border-2 border-blue-300">
          <div className="text-center mb-8">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
              <Calendar className="w-12 h-12 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">🎯 Your Training Programs Await!</h2>
            <p className="text-lg text-gray-700 mb-2">
              You haven't generated your training programs yet.
            </p>
            <p className="text-gray-600 mb-8">
              Complete your assessment first to unlock your personalized training programs!
            </p>
          </div>

          {/* Steps to Generate */}
          <div className="bg-white rounded-xl p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">📋 How to Get Your Programs</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Complete Your Assessment</h4>
                  <p className="text-sm text-gray-600">Fill in all your physical, technical, tactical, and mental metrics</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Review Your Professional Report</h4>
                  <p className="text-sm text-gray-600">Get AI analysis, coach recommendations, and development roadmap</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Generate Your Programs</h4>
                  <p className="text-sm text-gray-600">Get both Coach-Guided and AI-Powered training programs</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-orange-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                  4
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Start Training!</h4>
                  <p className="text-sm text-gray-600">Access your programs here and begin your development journey</p>
                </div>
              </div>
            </div>
          </div>

          {/* What You'll Get */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                  <Award className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-bold text-gray-900">Coach-Guided Program</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>✓ Professional coaching methodology</li>
                <li>✓ Position-specific training</li>
                <li>✓ Structured weekly progression</li>
                <li>✓ Based on coach recommendations</li>
              </ul>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <h4 className="font-bold text-gray-900">AI-Powered Model</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>✓ Machine learning optimization</li>
                <li>✓ Dynamic difficulty adjustment</li>
                <li>✓ Performance prediction</li>
                <li>✓ Personalized exercise selection</li>
              </ul>
            </div>
          </div>

          {/* CTA Button */}
          <div className="text-center">
            <button 
              onClick={() => {
                if (onNavigateToAssessment) {
                  onNavigateToAssessment();
                } else {
                  // Fallback if callback not provided
                  window.location.reload();
                }
              }}
              className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 transition shadow-lg transform hover:scale-105"
            >
              <ClipboardCheck className="w-6 h-6" />
              Take Assessment Now
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <p className="text-sm text-gray-500 mt-4">
              ⏱️ Takes about 10-15 minutes to complete
            </p>
          </div>
        </div>
      </div>
    );
  }

  const currentProgram = activeProgram === 'ai' ? programs.ai : programs.coach;

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-6 text-white shadow-lg">
        <h2 className="text-3xl font-bold mb-2">📋 My Training Programs</h2>
        <p className="text-blue-100">Personalized programs designed for your development</p>
      </div>

      {/* Program Selector */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Coach-Guided Program Card */}
        {programs.coach && (
          <button
            onClick={() => setActiveProgram('coach')}
            className={`text-left p-6 rounded-2xl border-2 transition transform hover:scale-105 ${
              activeProgram === 'coach'
                ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-500 shadow-lg'
                : 'bg-white border-gray-200 hover:border-green-300'
            }`}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                <Award className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">🏆 Coach-Guided Program</h3>
                <p className="text-sm text-gray-600">Professional methodology</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div className="bg-white/50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-600">Duration</p>
                <p className="font-bold text-gray-900">{programs.coach.duration_weeks}w</p>
              </div>
              <div className="bg-white/50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-600">Per Week</p>
                <p className="font-bold text-gray-900">{programs.coach.training_days_per_week}x</p>
              </div>
              <div className="bg-white/50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-600">Progress</p>
                <p className="font-bold text-gray-900">
                  {Math.round((programs.coach.completed_sessions / programs.coach.total_sessions) * 100)}%
                </p>
              </div>
            </div>
          </button>
        )}

        {/* AI-Powered Program Card */}
        {programs.ai && (
          <button
            onClick={() => setActiveProgram('ai')}
            className={`text-left p-6 rounded-2xl border-2 transition transform hover:scale-105 ${
              activeProgram === 'ai'
                ? 'bg-gradient-to-br from-purple-50 to-pink-50 border-purple-500 shadow-lg'
                : 'bg-white border-gray-200 hover:border-purple-300'
            }`}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">🤖 AI-Powered Model</h3>
                <p className="text-sm text-gray-600">Machine learning optimized</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div className="bg-white/50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-600">Duration</p>
                <p className="font-bold text-gray-900">{programs.ai.duration_weeks}w</p>
              </div>
              <div className="bg-white/50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-600">Per Week</p>
                <p className="font-bold text-gray-900">{programs.ai.training_days_per_week}x</p>
              </div>
              <div className="bg-white/50 rounded-lg p-2 text-center">
                <p className="text-xs text-gray-600">Progress</p>
                <p className="font-bold text-gray-900">
                  {Math.round((programs.ai.completed_sessions / programs.ai.total_sessions) * 100)}%
                </p>
              </div>
            </div>
          </button>
        )}
      </div>

      {/* Program Details */}
      {currentProgram && (
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
          {/* Program Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                {activeProgram === 'ai' ? '🤖 AI-Powered Training Model' : '🏆 Coach-Guided Program'}
              </h3>
              <p className="text-gray-600">
                {currentProgram.training_days_per_week} sessions per week • {currentProgram.session_duration_minutes} min each
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Status</p>
              <span className="inline-block px-4 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                {currentProgram.status || 'Active'}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Progress</span>
              <span className="text-sm font-bold text-blue-600">
                {currentProgram.completed_sessions} / {currentProgram.total_sessions} sessions
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all"
                style={{ width: `${(currentProgram.completed_sessions / currentProgram.total_sessions) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Program Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-50 rounded-xl p-4 text-center">
              <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600 mb-1">Duration</p>
              <p className="text-xl font-bold text-gray-900">{currentProgram.duration_weeks}</p>
              <p className="text-xs text-gray-500">weeks</p>
            </div>
            <div className="bg-purple-50 rounded-xl p-4 text-center">
              <Activity className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600 mb-1">Frequency</p>
              <p className="text-xl font-bold text-gray-900">{currentProgram.training_days_per_week}x</p>
              <p className="text-xs text-gray-500">per week</p>
            </div>
            <div className="bg-green-50 rounded-xl p-4 text-center">
              <Target className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600 mb-1">Completed</p>
              <p className="text-xl font-bold text-gray-900">{currentProgram.completed_sessions}</p>
              <p className="text-xs text-gray-500">sessions</p>
            </div>
            <div className="bg-orange-50 rounded-xl p-4 text-center">
              <TrendingUp className="w-8 h-8 text-orange-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600 mb-1">Remaining</p>
              <p className="text-xl font-bold text-gray-900">
                {currentProgram.total_sessions - currentProgram.completed_sessions}
              </p>
              <p className="text-xs text-gray-500">sessions</p>
            </div>
          </div>

          {/* Program Description */}
          <div className="bg-gray-50 rounded-xl p-6 mb-6">
            <h4 className="font-bold text-gray-900 mb-3">Program Overview</h4>
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
              {currentProgram.description || currentProgram.program_content || 'Program details loading...'}
            </div>
          </div>

          {/* Focus Areas */}
          {currentProgram.focus_areas && currentProgram.focus_areas.length > 0 && (
            <div className="bg-blue-50 rounded-xl p-6">
              <h4 className="font-bold text-gray-900 mb-3">🎯 Focus Areas</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentProgram.focus_areas.map((area, idx) => (
                  <div key={idx} className="flex items-start gap-2 bg-white rounded-lg p-3">
                    <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-700">{area}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 mt-8">
            <button className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-blue-900 transition">
              View Full Program
            </button>
            <button className="flex-1 px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition">
              Start Today's Session
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerTrainingPrograms;
