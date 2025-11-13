import React, { useState } from 'react';
import { Search, Filter, Users } from 'lucide-react';

const CoachPlayerList = ({ onSelectPlayer }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPosition, setFilterPosition] = useState('all');

  // Mock player data
  const players = [
    { id: 1, name: 'Marcus Silva', position: 'Forward', age: 17, height: '5\'10"', weight: '165 lbs', level: 'Elite', lastSeen: '2 hours ago', assessmentScore: 92, photo: null },
    { id: 2, name: 'Alex Johnson', position: 'Midfielder', age: 16, height: '5\'9"', weight: '160 lbs', level: 'Advanced', lastSeen: '1 day ago', assessmentScore: 78, photo: null },
    { id: 3, name: 'David Chen', position: 'Defender', age: 18, height: '6\'1"', weight: '180 lbs', level: 'Intermediate', lastSeen: '3 hours ago', assessmentScore: 65, photo: null },
    { id: 4, name: 'Leo Martinez', position: 'Goalkeeper', age: 17, height: '6\'2"', weight: '185 lbs', level: 'Elite', lastSeen: '4 hours ago', assessmentScore: 88, photo: null },
    { id: 5, name: 'Jake Williams', position: 'Forward', age: 16, height: '5\'11"', weight: '170 lbs', level: 'Advanced', lastSeen: '5 hours ago', assessmentScore: 74, photo: null },
    { id: 6, name: 'Ryan O\'Connor', position: 'Midfielder', age: 17, height: '5\'8"', weight: '155 lbs', level: 'Advanced', lastSeen: '2 days ago', assessmentScore: 76, photo: null },
    { id: 7, name: 'Carlos Rodriguez', position: 'Defender', age: 18, height: '6\'0"', weight: '175 lbs', level: 'Intermediate', lastSeen: '6 hours ago', assessmentScore: 68, photo: null },
    { id: 8, name: 'Tom Baker', position: 'Forward', age: 16, height: '5\'10"', weight: '168 lbs', level: 'Advanced', lastSeen: '1 hour ago', assessmentScore: 79, photo: null },
    { id: 9, name: 'Samuel Lee', position: 'Midfielder', age: 17, height: '5\'9"', weight: '162 lbs', level: 'Elite', lastSeen: '3 days ago', assessmentScore: 90, photo: null },
    { id: 10, name: 'Noah Brown', position: 'Defender', age: 16, height: '6\'0"', weight: '172 lbs', level: 'Intermediate', lastSeen: '1 day ago', assessmentScore: 66, photo: null }
  ];

  const filteredPlayers = players.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPosition = filterPosition === 'all' || player.position === filterPosition;
    return matchesSearch && matchesPosition;
  });

  const getLevelColor = (level) => {
    switch (level) {
      case 'Elite': return 'bg-[#4DFF91]/20 text-[#4DFF91] border-[#4DFF91]/30';
      case 'Advanced': return 'bg-[#007BFF]/20 text-[#007BFF] border-[#007BFF]/30';
      case 'Intermediate': return 'bg-[#FFD93D]/20 text-[#FFD93D] border-[#FFD93D]/30';
      default: return 'bg-white/10 text-white border-white/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Players</h2>
          <p className="text-white/60 mt-1">{filteredPlayers.length} players in your academy</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search players by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
          />
        </div>
        <select
          value={filterPosition}
          onChange={(e) => setFilterPosition(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
        >
          <option value="all">All Positions</option>
          <option value="Forward">Forward</option>
          <option value="Midfielder">Midfielder</option>
          <option value="Defender">Defender</option>
          <option value="Goalkeeper">Goalkeeper</option>
        </select>
      </div>

      {/* Player Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPlayers.map((player) => (
          <div 
            key={player.id}
            onClick={() => onSelectPlayer(player)}
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:scale-105 transition-all cursor-pointer"
          >
            <div className="flex items-start gap-4 mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-2xl flex items-center justify-center text-xl font-bold">
                {player.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-1">{player.name}</h3>
                <p className="text-sm text-white/60">{player.position} • {player.age}y</p>
                <span className={`inline-block mt-2 text-xs px-2 py-1 rounded-full border ${getLevelColor(player.level)}`}>
                  {player.level}
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/60">Assessment</span>
                <span className="font-bold text-[#4DFF91]">{player.assessmentScore}</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-[#4DFF91] to-[#007BFF] h-2 rounded-full"
                  style={{ width: `${player.assessmentScore}%` }}
                ></div>
              </div>
              <p className="text-xs text-white/40">Last seen: {player.lastSeen}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CoachPlayerList;