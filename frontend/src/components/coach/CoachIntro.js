import React from 'react';
import { Play, Globe } from 'lucide-react';

const CoachIntro = ({ onComplete }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0C1A2A] via-[#1a2332] to-[#0C1A2A] flex items-center justify-center relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#4DFF91]/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#007BFF]/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="relative z-10 text-center max-w-2xl px-6">
        {/* Logo Animation */}
        <div className="mb-8">
          <div className="w-32 h-32 mx-auto bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-3xl flex items-center justify-center shadow-2xl shadow-[#4DFF91]/30 animate-bounce">
            <Play className="w-16 h-16 text-[#0C1A2A]" fill="#0C1A2A" />
          </div>
        </div>

        {/* Welcome Text */}
        <h1 className="text-6xl font-bold mb-4">
          <span className="bg-gradient-to-r from-[#4DFF91] to-[#007BFF] bg-clip-text text-transparent">
            Welcome Coach
          </span>
        </h1>
        <p className="text-xl text-white/80 mb-12">
          Elite AI-Powered Training Platform for Professional Soccer Development
        </p>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-semibold text-white mb-2">AI Assessments</h3>
            <p className="text-sm text-white/60">Computer vision analysis & performance tracking</p>
          </div>
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="font-semibold text-white mb-2">Smart Planning</h3>
            <p className="text-sm text-white/60">Auto-generated training programs</p>
          </div>
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="text-4xl mb-3">📊</div>
            <h3 className="font-semibold text-white mb-2">Analytics</h3>
            <p className="text-sm text-white/60">Real-time player progress insights</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center mb-8">
          <button
            onClick={onComplete}
            className="px-8 py-4 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition-all transform hover:scale-105"
          >
            Enter Coach Portal
          </button>
          <button className="px-8 py-4 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl font-semibold text-white hover:bg-white/20 transition">
            Sign Up
          </button>
        </div>

        {/* Language Selector */}
        <button className="flex items-center gap-2 mx-auto text-white/60 hover:text-white transition">
          <Globe className="w-4 h-4" />
          <span className="text-sm">English</span>
        </button>
      </div>
    </div>
  );
};

export default CoachIntro;