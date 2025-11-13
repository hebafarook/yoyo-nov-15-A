import React from 'react';
import { Heart, AlertTriangle, TrendingUp, Activity, Droplet, Moon } from 'lucide-react';

const CoachRecovery = () => {
  const players = [
    {
      id: 1,
      name: 'Marcus Silva',
      recoveryScore: 85,
      status: 'Good',
      lastWorkload: 'High',
      sleepHours: 8,
      hydrationLevel: 90,
      sorenessLevel: 3,
      injuryRisk: 'Low',
      recommendation: 'Continue with normal training load',
      assignedRoutine: 'Standard Recovery Protocol'
    },
    {
      id: 2,
      name: 'Alex Johnson',
      recoveryScore: 62,
      status: 'Moderate',
      lastWorkload: 'Very High',
      sleepHours: 6,
      hydrationLevel: 75,
      sorenessLevel: 6,
      injuryRisk: 'Medium',
      recommendation: 'Reduce intensity for 48 hours, focus on mobility work',
      assignedRoutine: 'Active Recovery + Ice Bath'
    },
    {
      id: 3,
      name: 'David Chen',
      recoveryScore: 45,
      status: 'Poor',
      lastWorkload: 'High',
      sleepHours: 5,
      hydrationLevel: 60,
      injuryRisk: 'High',
      sorenessLevel: 8,
      recommendation: 'Immediate rest required. Medical assessment recommended.',
      assignedRoutine: 'Complete Rest + Physiotherapy'
    }
  ];

  const recoveryProtocols = [
    {
      name: 'Ice Bath Protocol',
      duration: '12-15 min',
      temp: '10-15°C',
      frequency: 'Post high-intensity sessions'
    },
    {
      name: 'Heat Therapy',
      duration: '15-20 min',
      temp: '38-40°C',
      frequency: 'For muscle stiffness'
    },
    {
      name: 'Foam Rolling',
      duration: '20 min',
      focus: 'Major muscle groups',
      frequency: 'Daily'
    },
    {
      name: 'Yoga Flow',
      duration: '30 min',
      focus: 'Flexibility & breathing',
      frequency: '3x per week'
    }
  ];

  const getRecoveryColor = (score) => {
    if (score >= 80) return { bg: 'bg-[#4DFF91]/20', text: 'text-[#4DFF91]', border: 'border-[#4DFF91]/30' };
    if (score >= 60) return { bg: 'bg-[#FFD93D]/20', text: 'text-[#FFD93D]', border: 'border-[#FFD93D]/30' };
    return { bg: 'bg-[#FF6B6B]/20', text: 'text-[#FF6B6B]', border: 'border-[#FF6B6B]/30' };
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Low': return 'text-[#4DFF91]';
      case 'Medium': return 'text-[#FFD93D]';
      case 'High': return 'text-[#FF6B6B]';
      default: return 'text-white/60';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-2">
          <Heart className="w-8 h-8 text-[#4DFF91]" />
          <h2 className="text-3xl font-bold">Recovery & Injury Prevention</h2>
        </div>
        <p className="text-white/70">Monitor player recovery status and prevent injuries</p>
      </div>

      {/* Player Recovery Status */}
      <div className="space-y-4">
        {players.map((player) => {
          const colorConfig = getRecoveryColor(player.recoveryScore);
          
          return (
            <div key={player.id} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <div className="flex items-start gap-6">
                {/* Player Avatar */}
                <div className="w-16 h-16 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-2xl flex items-center justify-center text-lg font-bold flex-shrink-0">
                  {player.name.split(' ').map(n => n[0]).join('')}
                </div>

                {/* Player Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold mb-1">{player.name}</h3>
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${colorConfig.bg} ${colorConfig.text} ${colorConfig.border}`}>
                        {player.status}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className={`text-5xl font-bold ${colorConfig.text} mb-1`}>{player.recoveryScore}</div>
                      <div className="text-xs text-white/60">Recovery Score</div>
                    </div>
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="bg-white/5 rounded-xl p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Activity className="w-4 h-4 text-white/60" />
                        <span className="text-xs text-white/60">Workload</span>
                      </div>
                      <div className="text-sm font-medium">{player.lastWorkload}</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Moon className="w-4 h-4 text-white/60" />
                        <span className="text-xs text-white/60">Sleep</span>
                      </div>
                      <div className="text-sm font-medium">{player.sleepHours}h</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Droplet className="w-4 h-4 text-white/60" />
                        <span className="text-xs text-white/60">Hydration</span>
                      </div>
                      <div className="text-sm font-medium">{player.hydrationLevel}%</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <AlertTriangle className="w-4 h-4 text-white/60" />
                        <span className="text-xs text-white/60">Soreness</span>
                      </div>
                      <div className="text-sm font-medium">{player.sorenessLevel}/10</div>
                    </div>
                  </div>

                  {/* Injury Risk */}
                  <div className="bg-gradient-to-r from-white/5 to-white/10 rounded-xl p-4 mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Injury Risk Assessment</span>
                      <span className={`text-sm font-bold ${getRiskColor(player.injuryRisk)}`}>
                        {player.injuryRisk} Risk
                      </span>
                    </div>
                    <p className="text-sm text-white/70">{player.recommendation}</p>
                  </div>

                  {/* Assigned Routine */}
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs text-white/60 mb-1">Assigned Routine</div>
                      <div className="text-sm font-medium">{player.assignedRoutine}</div>
                    </div>
                    <button className="px-4 py-2 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-lg text-sm font-medium text-[#0C1A2A] hover:shadow-lg hover:shadow-[#4DFF91]/30 transition">
                      Update Protocol
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recovery Protocols Reference */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-6">Recovery Protocols Library</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recoveryProtocols.map((protocol, idx) => (
            <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h4 className="font-bold text-lg mb-3">{protocol.name}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-white/60">Duration:</span>
                  <span className="font-medium">{protocol.duration}</span>
                </div>
                {protocol.temp && (
                  <div className="flex justify-between">
                    <span className="text-white/60">Temperature:</span>
                    <span className="font-medium">{protocol.temp}</span>
                  </div>
                )}
                {protocol.focus && (
                  <div className="flex justify-between">
                    <span className="text-white/60">Focus:</span>
                    <span className="font-medium">{protocol.focus}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-white/60">Frequency:</span>
                  <span className="font-medium">{protocol.frequency}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CoachRecovery;