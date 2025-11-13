import React from 'react';
import { ArrowLeft, CheckCircle, TrendingUp, AlertTriangle, Target } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CoachAssessmentReport = ({ assessment, onBack }) => {
  // Technical metrics
  const technicalData = [
    { metric: 'Ball Control', score: 95, benchmark: 85 },
    { metric: 'First Touch', score: 92, benchmark: 82 },
    { metric: 'Passing', score: 88, benchmark: 80 },
    { metric: 'Dribbling', score: 90, benchmark: 83 },
    { metric: 'Shooting', score: 85, benchmark: 78 },
    { metric: 'Weak Foot', score: 62, benchmark: 75 }
  ];

  // Physical metrics
  const physicalData = [
    { metric: 'Sprint 30m', score: 4.2, benchmark: 4.5, unit: 's', inverse: true },
    { metric: 'Agility', score: 15.8, benchmark: 16.2, unit: 's', inverse: true },
    { metric: 'Vertical Jump', score: 65, benchmark: 58, unit: 'cm' },
    { metric: 'YoYo Test', score: 1850, benchmark: 1600, unit: 'm' },
    { metric: 'VO2 Max', score: 58, benchmark: 52, unit: 'ml/kg/min' }
  ];

  // Tactical awareness
  const tacticalData = [
    { area: 'Positioning', value: 82 },
    { area: 'Decision Making', value: 88 },
    { area: 'Pressing', value: 75 },
    { area: 'Support Play', value: 90 },
    { area: 'Defensive Work', value: 70 },
    { area: 'Vision', value: 85 }
  ];

  // AI Recommendations
  const aiRecommendations = [
    {
      priority: 'High',
      area: 'Weak Foot Training',
      details: 'Focus on left foot finishing drills. Current accuracy 62% vs benchmark 75%',
      drills: ['Left foot shooting progression', 'Weak foot passing circuits', '1v1 finishing with weak foot']
    },
    {
      priority: 'Medium',
      area: 'Defensive Positioning',
      details: 'Improve tactical awareness in defensive transitions',
      drills: ['Shadow defending', 'Positional awareness games', 'Defensive shape drills']
    },
    {
      priority: 'Low',
      area: 'Aerial Ability',
      details: 'Maintain current level with periodic practice',
      drills: ['Heading technique', 'Jump timing exercises']
    }
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return 'bg-[#FF6B6B]/20 text-[#FF6B6B] border-[#FF6B6B]/30';
      case 'Medium': return 'bg-[#FFD93D]/20 text-[#FFD93D] border-[#FFD93D]/30';
      case 'Low': return 'bg-[#4DFF91]/20 text-[#4DFF91] border-[#4DFF91]/30';
      default: return 'bg-white/10 text-white border-white/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-white/70 hover:text-white transition"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Assessments
        </button>
        <button className="px-6 py-3 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          Approve & Apply to Training Plan
        </button>
      </div>

      {/* Report Header */}
      <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">{assessment.playerName}</h1>
            <p className="text-xl text-white/80 mb-4">{assessment.type}</p>
            <p className="text-sm text-white/60">Assessment Date: {assessment.date}</p>
          </div>
          <div className="text-center">
            <div className="text-6xl font-bold text-[#4DFF91] mb-2">{assessment.score}</div>
            <div className="text-sm text-white/60">Overall Score</div>
          </div>
        </div>
      </div>

      {/* Technical Assessment */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <Target className="w-6 h-6 text-[#4DFF91]" />
          Technical Assessment
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={technicalData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="metric" stroke="rgba(255,255,255,0.6)" />
            <YAxis stroke="rgba(255,255,255,0.6)" />
            <Tooltip contentStyle={{ backgroundColor: '#0C1A2A', border: '1px solid rgba(77, 255, 145, 0.3)', borderRadius: '12px' }} />
            <Legend />
            <Bar dataKey="score" fill="#4DFF91" radius={[8, 8, 0, 0]} />
            <Bar dataKey="benchmark" fill="#007BFF" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
          {technicalData.map((item, idx) => (
            <div key={idx} className="bg-white/5 rounded-xl p-4">
              <div className="text-xs text-white/60 mb-1">{item.metric}</div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-[#4DFF91]">{item.score}</span>
                <span className="text-sm text-white/60">/ {item.benchmark}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Physical Assessment */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-[#4DFF91]" />
          Physical Assessment
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {physicalData.map((item, idx) => {
            const isAbove = item.inverse 
              ? item.score < item.benchmark 
              : item.score > item.benchmark;
            
            return (
              <div key={idx} className="bg-white/5 rounded-xl p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="text-sm font-medium">{item.metric}</div>
                  {isAbove ? (
                    <TrendingUp className="w-4 h-4 text-[#4DFF91]" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-[#FFD93D]" />
                  )}
                </div>
                <div className="flex items-baseline gap-2 mb-2">
                  <span className={`text-3xl font-bold ${
                    isAbove ? 'text-[#4DFF91]' : 'text-[#FFD93D]'
                  }`}>
                    {item.score}
                  </span>
                  <span className="text-sm text-white/60">{item.unit}</span>
                </div>
                <div className="text-xs text-white/60">
                  Benchmark: {item.benchmark} {item.unit}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tactical Awareness */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-2xl font-bold mb-6">Tactical Awareness</h3>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={tacticalData}>
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis dataKey="area" stroke="rgba(255,255,255,0.6)" />
            <PolarRadiusAxis stroke="rgba(255,255,255,0.3)" />
            <Radar name="Performance" dataKey="value" stroke="#4DFF91" fill="#4DFF91" fillOpacity={0.3} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <Target className="w-6 h-6 text-[#4DFF91]" />
          AI-Generated Recommendations
        </h3>
        <div className="space-y-6">
          {aiRecommendations.map((rec, idx) => (
            <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-xl font-bold mb-2">{rec.area}</h4>
                  <p className="text-sm text-white/70">{rec.details}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(rec.priority)}`}>
                  {rec.priority} Priority
                </span>
              </div>
              <div className="mt-4">
                <div className="text-sm font-medium text-white/80 mb-2">Recommended Drills:</div>
                <div className="flex flex-wrap gap-2">
                  {rec.drills.map((drill, dIdx) => (
                    <span key={dIdx} className="px-3 py-1 bg-gradient-to-r from-[#4DFF91]/20 to-[#007BFF]/20 rounded-lg text-xs border border-[#4DFF91]/30">
                      {drill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <button className="px-6 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl font-semibold text-white hover:bg-white/20 transition">
          Save as PDF
        </button>
        <button className="px-6 py-3 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          Approve & Apply to Training Plan
        </button>
      </div>
    </div>
  );
};

export default CoachAssessmentReport;