import React from 'react';
import { Play, Globe } from 'lucide-react';

const CoachIntro = ({ onComplete }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center relative overflow-hidden">
      <div className="relative z-10 text-center max-w-2xl px-6">
        {/* Logo Animation */}
        <div className="mb-8">
          <div className="w-32 h-32 mx-auto bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl animate-bounce">
            <Play className="w-16 h-16 text-white" fill="white" />
          </div>
        </div>

        {/* Welcome Text */}
        <h1 className="text-6xl font-bold mb-4 text-gray-800">
          Welcome Coach
        </h1>
        <p className="text-xl text-gray-600 mb-12">
          Elite AI-Powered Training Platform for Professional Soccer Development
        </p>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-semibold text-gray-800 mb-2">AI Assessments</h3>
            <p className="text-sm text-gray-600">Computer vision analysis & performance tracking</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="font-semibold text-gray-800 mb-2">Smart Planning</h3>
            <p className="text-sm text-gray-600">Auto-generated training programs</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="text-4xl mb-3">📊</div>
            <h3 className="font-semibold text-gray-800 mb-2">Analytics</h3>
            <p className="text-sm text-gray-600">Real-time player progress insights</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center mb-8">
          <button
            onClick={onComplete}
            className="px-8 py-4 bg-blue-600 rounded-xl font-semibold text-white hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg"
          >
            Enter Coach Portal
          </button>
          <button className="px-8 py-4 bg-white border border-gray-300 rounded-xl font-semibold text-gray-700 hover:bg-gray-50 transition shadow-lg">
            Sign Up
          </button>
        </div>

        {/* Language Selector */}
        <button className="flex items-center gap-2 mx-auto text-gray-600 hover:text-gray-800 transition">
          <Globe className="w-4 h-4" />
          <span className="text-sm">English</span>
        </button>
      </div>
    </div>
  );
};

export default CoachIntro;