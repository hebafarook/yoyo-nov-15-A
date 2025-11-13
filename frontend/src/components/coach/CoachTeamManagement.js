import React from 'react';
import { Users, TrendingUp, Download, Calendar, AlertTriangle } from 'lucide-react';

const CoachTeamManagement = () => {
  const teams = [
    {
      id: 1,
      name: 'U14 Elite Squad',
      ageGroup: 'U14',
      playerCount: 18,
      attendance: 94,
      avgFitnessLevel: 82,
      needsImprovement: ['Tactical awareness', 'Defensive transitions'],
      nextSession: '2024-03-20 16:00'
    },
    {
      id: 2,
      name: 'U16 Development',
      ageGroup: 'U16',
      playerCount: 20,
      attendance: 88,
      avgFitnessLevel: 78,
      needsImprovement: ['Speed endurance', 'Set piece organization'],
      nextSession: '2024-03-20 18:00'
    },
    {
      id: 3,
      name: 'U18 Premier',
      ageGroup: 'U18',
      playerCount: 22,
      attendance: 91,
      avgFitnessLevel: 85,
      needsImprovement: ['Mental toughness', 'Finishing under pressure'],
      nextSession: '2024-03-21 17:00'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold">Team Management</h2>
        <p className="text-white/60 mt-1">Manage and monitor your team squads</p>
      </div>

      {/* Teams Grid */}
      <div className="space-y-6">
        {teams.map((team) => (
          <div key={team.id} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold mb-2">{team.name}</h3>
                <div className="flex items-center gap-4 text-white/70">
                  <span className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    {team.playerCount} Players
                  </span>
                  <span>•</span>
                  <span>{team.ageGroup}</span>
                </div>
              </div>
              <button className="px-4 py-2 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-medium text-[#0C1A2A] hover:shadow-lg hover:shadow-[#4DFF91]/30 transition flex items-center gap-2">
                <Download className="w-4 h-4" />
                Weekly Report
              </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white/5 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white/60">Attendance</span>
                  <TrendingUp className="w-4 h-4 text-[#4DFF91]" />
                </div>
                <div className="text-3xl font-bold text-[#4DFF91] mb-1">{team.attendance}%</div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-[#4DFF91] to-[#007BFF] h-2 rounded-full"
                    style={{ width: `${team.attendance}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white/5 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white/60">Avg Fitness Level</span>
                  <TrendingUp className="w-4 h-4 text-[#007BFF]" />
                </div>
                <div className="text-3xl font-bold text-[#007BFF] mb-1">{team.avgFitnessLevel}</div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-[#007BFF] to-[#4DFF91] h-2 rounded-full"
                    style={{ width: `${team.avgFitnessLevel}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white/5 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="w-4 h-4 text-white/60" />
                  <span className="text-sm text-white/60">Next Session</span>
                </div>
                <div className="text-sm font-medium">{team.nextSession}</div>
              </div>
            </div>

            {/* Needs Improvement */}
            <div className="bg-gradient-to-r from-[#FFD93D]/10 to-[#FF6B6B]/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4 text-[#FFD93D]" />
                <span className="text-sm font-medium">Needs Improvement</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {team.needsImprovement.map((item, idx) => (
                  <span key={idx} className="px-3 py-1 bg-white/10 border border-[#FFD93D]/30 rounded-lg text-sm">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CoachTeamManagement;