import React, { useState } from 'react';
import { Zap, Calendar, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

const CoachAITrainingGenerator = () => {
  const [formData, setFormData] = useState({
    playerName: '',
    position: 'Forward',
    weakness: '',
    strength: '',
    matchDate: ''
  });
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    
    // Simulate AI generation
    setTimeout(() => {
      setGeneratedPlan({
        playerName: formData.playerName,
        position: formData.position,
        focus: `${formData.weakness} Development & ${formData.strength} Maintenance`,
        matchDate: formData.matchDate,
        weeklyMicrocycle: [
          {
            day: 'Monday',
            phase: 'Development',
            focus: `${formData.weakness} Focused Training`,
            intensity: 'High',
            duration: '90 min',
            drills: [
              { name: 'Weakness-specific drill 1', sets: 4, reps: 10, rest: '2 min' },
              { name: 'Technical progression', sets: 3, reps: 15, rest: '90 sec' }
            ]
          },
          {
            day: 'Tuesday',
            phase: 'Maintenance',
            focus: `${formData.strength} Maintenance`,
            intensity: 'Medium',
            duration: '60 min',
            drills: [
              { name: 'Strength maintenance drill', sets: 3, reps: 12, rest: '2 min' }
            ]
          },
          {
            day: 'Wednesday',
            phase: 'Recovery',
            focus: 'Active Recovery & Mobility',
            intensity: 'Low',
            duration: '45 min',
            drills: [
              { name: 'Yoga flow', sets: 1, reps: 0, rest: 'N/A' },
              { name: 'Foam rolling', sets: 1, reps: 0, rest: 'N/A' }
            ]
          },
          {
            day: 'Thursday',
            phase: 'Integration',
            focus: 'Game-like scenarios',
            intensity: 'High',
            duration: '75 min',
            drills: [
              { name: 'Small-sided games', sets: 2, reps: 0, rest: '5 min' },
              { name: 'Position-specific work', sets: 3, reps: 8, rest: '2 min' }
            ]
          },
          {
            day: 'Friday',
            phase: 'Pre-Match',
            focus: 'Tactical & Light Technical',
            intensity: 'Medium',
            duration: '60 min',
            drills: [
              { name: 'Team shape drills', sets: 2, reps: 0, rest: '3 min' },
              { name: 'Set piece practice', sets: 3, reps: 5, rest: '2 min' }
            ]
          },
          {
            day: 'Saturday',
            phase: 'Match Day',
            focus: 'Competition',
            intensity: 'Match',
            duration: '90 min',
            drills: []
          },
          {
            day: 'Sunday',
            phase: 'Recovery',
            focus: 'Complete Rest',
            intensity: 'Rest',
            duration: '0 min',
            drills: []
          }
        ],
        progressionLogic: [
          'Week 1-2: Foundation building with emphasis on technique',
          'Week 3-4: Increase intensity and game-like scenarios',
          'Week 5-6: Peak performance and match readiness',
          'Auto-adjust based on assessment scores every 2 weeks'
        ]
      });
      setGenerating(false);
    }, 2000);
  };

  const getIntensityColor = (intensity) => {
    switch (intensity) {
      case 'High': return 'bg-[#FF6B6B]/20 text-[#FF6B6B] border-[#FF6B6B]/30';
      case 'Medium': return 'bg-[#FFD93D]/20 text-[#FFD93D] border-[#FFD93D]/30';
      case 'Low': return 'bg-[#4DFF91]/20 text-[#4DFF91] border-[#4DFF91]/30';
      case 'Match': return 'bg-[#007BFF]/20 text-[#007BFF] border-[#007BFF]/30';
      case 'Rest': return 'bg-white/10 text-white/60 border-white/20';
      default: return 'bg-white/10 text-white border-white/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-2">
          <Zap className="w-8 h-8 text-[#4DFF91]" />
          <h2 className="text-3xl font-bold">AI Training Plan Generator</h2>
        </div>
        <p className="text-white/70">Generate personalized training programs based on player data and goals</p>
      </div>

      {/* Input Form */}
      {!generatedPlan && (
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
          <form onSubmit={handleGenerate} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Player Name</label>
                <input
                  type="text"
                  value={formData.playerName}
                  onChange={(e) => setFormData({...formData, playerName: e.target.value})}
                  required
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
                  placeholder="Enter player name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Position</label>
                <select
                  value={formData.position}
                  onChange={(e) => setFormData({...formData, position: e.target.value})}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
                >
                  <option value="Forward">Forward</option>
                  <option value="Midfielder">Midfielder</option>
                  <option value="Defender">Defender</option>
                  <option value="Goalkeeper">Goalkeeper</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Primary Weakness to Address</label>
              <input
                type="text"
                value={formData.weakness}
                onChange={(e) => setFormData({...formData, weakness: e.target.value})}
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
                placeholder="e.g., Left foot finishing, Tactical positioning"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Key Strength to Maintain</label>
              <input
                type="text"
                value={formData.strength}
                onChange={(e) => setFormData({...formData, strength: e.target.value})}
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
                placeholder="e.g., Speed, Ball control"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Upcoming Match Date</label>
              <input
                type="date"
                value={formData.matchDate}
                onChange={(e) => setFormData({...formData, matchDate: e.target.value})}
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
              />
            </div>

            <button
              type="submit"
              disabled={generating}
              className="w-full py-4 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <div className="w-5 h-5 border-2 border-[#0C1A2A]/30 border-t-[#0C1A2A] rounded-full animate-spin"></div>
                  Generating...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Generate AI Training Plan
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* Generated Plan */}
      {generatedPlan && (
        <div className="space-y-6">
          {/* Plan Header */}
          <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold mb-1">{generatedPlan.playerName}'s Training Plan</h3>
                <p className="text-white/70">{generatedPlan.position} • Match: {generatedPlan.matchDate}</p>
              </div>
              <button
                onClick={() => setGeneratedPlan(null)}
                className="px-4 py-2 bg-white/10 rounded-lg text-sm hover:bg-white/20 transition"
              >
                Generate New Plan
              </button>
            </div>
            <div className="bg-white/5 rounded-xl p-4">
              <div className="text-sm text-white/60 mb-1">Plan Focus</div>
              <div className="font-medium">{generatedPlan.focus}</div>
            </div>
          </div>

          {/* Weekly Microcycle */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h4 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-[#4DFF91]" />
              Weekly Microcycle
            </h4>
            <div className="space-y-4">
              {generatedPlan.weeklyMicrocycle.map((session, idx) => (
                <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-12 h-12 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-lg flex items-center justify-center font-bold">
                          {session.day.slice(0, 3)}
                        </div>
                        <div>
                          <h5 className="font-bold text-lg">{session.day}</h5>
                          <p className="text-sm text-white/60">{session.phase}</p>
                        </div>
                      </div>
                      <p className="text-white/80">{session.focus}</p>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getIntensityColor(session.intensity)}`}>
                        {session.intensity}
                      </span>
                      <p className="text-sm text-white/60 mt-2">{session.duration}</p>
                    </div>
                  </div>

                  {session.drills.length > 0 && (
                    <div className="space-y-2 mt-4">
                      <div className="text-sm font-medium text-white/70">Drills:</div>
                      {session.drills.map((drill, dIdx) => (
                        <div key={dIdx} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                          <span className="text-sm">{drill.name}</span>
                          <span className="text-xs text-white/60">
                            {drill.sets > 0 && `${drill.sets} sets`}
                            {drill.reps > 0 && ` x ${drill.reps} reps`}
                            {drill.rest !== 'N/A' && ` • ${drill.rest} rest`}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Progression Logic */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h4 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-[#4DFF91]" />
              Progression Logic
            </h4>
            <ul className="space-y-3">
              {generatedPlan.progressionLogic.map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#4DFF91] mt-0.5 flex-shrink-0" />
                  <span className="text-white/80">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button className="flex-1 py-3 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition">
              Apply to {generatedPlan.playerName}
            </button>
            <button className="px-6 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl font-semibold text-white hover:bg-white/20 transition">
              Save as Template
            </button>
            <button className="px-6 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl font-semibold text-white hover:bg-white/20 transition">
              Export PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CoachAITrainingGenerator;