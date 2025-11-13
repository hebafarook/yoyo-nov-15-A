import React, { useState } from 'react';
import { Search, Filter, Play, Plus, Clock, TrendingUp } from 'lucide-react';

const CoachDrillLibrary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [selectedDrill, setSelectedDrill] = useState(null);

  // 20 Sample drills
  const drills = [
    { id: 1, title: 'Sprint Intervals', category: 'Speed', difficulty: 'Beginner', duration: '20 min', sets: 6, reps: 1, rest: '2 min', focus: 'Acceleration', videoUrl: '#' },
    { id: 2, title: 'Cone Weave Dribbling', category: 'Technical', difficulty: 'Intermediate', duration: '15 min', sets: 4, reps: 5, rest: '1 min', focus: 'Ball Control', videoUrl: '#' },
    { id: 3, title: 'Box Jumping', category: 'Strength', difficulty: 'Intermediate', duration: '12 min', sets: 3, reps: 10, rest: '90 sec', focus: 'Explosive Power', videoUrl: '#' },
    { id: 4, title: 'Tactical Positioning Game', category: 'Tactical', difficulty: 'Advanced', duration: '30 min', sets: 1, reps: 0, rest: 'N/A', focus: 'Awareness', videoUrl: '#' },
    { id: 5, title: 'YoYo Intermittent Test', category: 'Conditioning', difficulty: 'Elite', duration: '25 min', sets: 1, reps: 0, rest: 'N/A', focus: 'Endurance', videoUrl: '#' },
    { id: 6, title: 'Foam Rolling Recovery', category: 'Recovery', difficulty: 'Beginner', duration: '15 min', sets: 1, reps: 0, rest: 'N/A', focus: 'Mobility', videoUrl: '#' },
    { id: 7, title: 'GK Reaction Saves', category: 'Goalkeeper', difficulty: 'Intermediate', duration: '20 min', sets: 5, reps: 8, rest: '2 min', focus: 'Reflexes', videoUrl: '#' },
    { id: 8, title: 'Weak Foot Shooting', category: 'Technical', difficulty: 'Intermediate', duration: '25 min', sets: 4, reps: 10, rest: '90 sec', focus: 'Finishing', videoUrl: '#' },
    { id: 9, title: 'Ladder Agility Drills', category: 'Speed', difficulty: 'Beginner', duration: '15 min', sets: 4, reps: 6, rest: '60 sec', focus: 'Footwork', videoUrl: '#' },
    { id: 10, title: 'Small-Sided Game 4v4', category: 'Tactical', difficulty: 'Intermediate', duration: '30 min', sets: 2, reps: 0, rest: '5 min', focus: 'Game Sense', videoUrl: '#' },
    { id: 11, title: 'Passing Circuit', category: 'Technical', difficulty: 'Beginner', duration: '20 min', sets: 3, reps: 15, rest: '2 min', focus: 'Accuracy', videoUrl: '#' },
    { id: 12, title: 'Hill Sprints', category: 'Speed', difficulty: 'Advanced', duration: '18 min', sets: 8, reps: 1, rest: '3 min', focus: 'Power', videoUrl: '#' },
    { id: 13, title: 'Yoga Flow', category: 'Recovery', difficulty: 'Beginner', duration: '30 min', sets: 1, reps: 0, rest: 'N/A', focus: 'Flexibility', videoUrl: '#' },
    { id: 14, title: 'Deadlift Progression', category: 'Strength', difficulty: 'Advanced', duration: '35 min', sets: 4, reps: 6, rest: '3 min', focus: 'Lower Body', videoUrl: '#' },
    { id: 15, title: 'Pressing Triggers', category: 'Tactical', difficulty: 'Elite', duration: '40 min', sets: 1, reps: 0, rest: 'N/A', focus: 'Defensive Shape', videoUrl: '#' },
    { id: 16, title: '1v1 Finishing', category: 'Technical', difficulty: 'Intermediate', duration: '20 min', sets: 5, reps: 4, rest: '2 min', focus: 'Composure', videoUrl: '#' },
    { id: 17, title: 'Plyometric Circuit', category: 'Strength', difficulty: 'Advanced', duration: '25 min', sets: 3, reps: 12, rest: '2 min', focus: 'Explosiveness', videoUrl: '#' },
    { id: 18, title: 'GK Distribution Practice', category: 'Goalkeeper', difficulty: 'Intermediate', duration: '25 min', sets: 4, reps: 10, rest: '90 sec', focus: 'Throwing/Kicking', videoUrl: '#' },
    { id: 19, title: 'Fartlek Running', category: 'Conditioning', difficulty: 'Intermediate', duration: '35 min', sets: 1, reps: 0, rest: 'N/A', focus: 'Aerobic Base', videoUrl: '#' },
    { id: 20, title: 'Set Piece Routines', category: 'Tactical', difficulty: 'Advanced', duration: '30 min', sets: 1, reps: 0, rest: 'N/A', focus: 'Organization', videoUrl: '#' }
  ];

  const categories = ['all', 'Technical', 'Tactical', 'Conditioning', 'Strength', 'Speed', 'Recovery', 'Goalkeeper'];

  const filteredDrills = drills.filter(drill => {
    const matchesSearch = drill.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         drill.focus.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || drill.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'bg-[#4DFF91]/20 text-[#4DFF91] border-[#4DFF91]/30';
      case 'Intermediate': return 'bg-[#007BFF]/20 text-[#007BFF] border-[#007BFF]/30';
      case 'Advanced': return 'bg-[#FFD93D]/20 text-[#FFD93D] border-[#FFD93D]/30';
      case 'Elite': return 'bg-[#FF6B6B]/20 text-[#FF6B6B] border-[#FF6B6B]/30';
      default: return 'bg-white/10 text-white border-white/20';
    }
  };

  if (selectedDrill) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => setSelectedDrill(null)}
          className="text-white/70 hover:text-white transition"
        >
          ← Back to Library
        </button>
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold mb-2">{selectedDrill.title}</h2>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-[#4DFF91]/20 text-[#4DFF91] rounded-lg text-sm border border-[#4DFF91]/30">
                  {selectedDrill.category}
                </span>
                <span className={`px-3 py-1 rounded-lg text-sm border ${getDifficultyColor(selectedDrill.difficulty)}`}>
                  {selectedDrill.difficulty}
                </span>
              </div>
            </div>
            <button className="px-6 py-3 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Assign to Player
            </button>
          </div>

          {/* Video Placeholder */}
          <div className="bg-black/50 rounded-xl aspect-video flex items-center justify-center mb-6">
            <Play className="w-16 h-16 text-[#4DFF91]" />
          </div>

          {/* Drill Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white/5 rounded-xl p-4">
              <div className="text-sm text-white/60 mb-1">Duration</div>
              <div className="text-xl font-bold">{selectedDrill.duration}</div>
            </div>
            <div className="bg-white/5 rounded-xl p-4">
              <div className="text-sm text-white/60 mb-1">Sets</div>
              <div className="text-xl font-bold">{selectedDrill.sets}</div>
            </div>
            <div className="bg-white/5 rounded-xl p-4">
              <div className="text-sm text-white/60 mb-1">Reps</div>
              <div className="text-xl font-bold">{selectedDrill.reps || 'N/A'}</div>
            </div>
            <div className="bg-white/5 rounded-xl p-4">
              <div className="text-sm text-white/60 mb-1">Rest</div>
              <div className="text-xl font-bold">{selectedDrill.rest}</div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 rounded-xl p-6">
            <h3 className="font-bold mb-2">Primary Focus</h3>
            <p className="text-white/80">{selectedDrill.focus}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold">Training Drill Library</h2>
        <p className="text-white/60 mt-1">{filteredDrills.length} drills available</p>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-wrap gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search drills by name or focus..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
          />
        </div>
      </div>

      {/* Category Filters */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`px-4 py-2 rounded-xl font-medium transition ${
              filterCategory === cat
                ? 'bg-gradient-to-r from-[#4DFF91] to-[#007BFF] text-[#0C1A2A]'
                : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
            }`}
          >
            {cat === 'all' ? 'All' : cat}
          </button>
        ))}
      </div>

      {/* Drills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDrills.map((drill) => (
          <div
            key={drill.id}
            onClick={() => setSelectedDrill(drill)}
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:scale-105 transition-all cursor-pointer"
          >
            {/* Video Thumbnail */}
            <div className="bg-black/50 rounded-xl aspect-video flex items-center justify-center mb-4">
              <Play className="w-12 h-12 text-[#4DFF91]" />
            </div>

            {/* Drill Info */}
            <h3 className="font-bold text-lg mb-2">{drill.title}</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="px-2 py-1 bg-[#4DFF91]/20 text-[#4DFF91] rounded-lg text-xs border border-[#4DFF91]/30">
                {drill.category}
              </span>
              <span className={`px-2 py-1 rounded-lg text-xs border ${getDifficultyColor(drill.difficulty)}`}>
                {drill.difficulty}
              </span>
            </div>

            <div className="space-y-2 text-sm text-white/70">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {drill.duration}
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Focus: {drill.focus}
              </div>
            </div>

            <button className="w-full mt-4 py-2 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-lg font-medium text-[#0C1A2A] hover:shadow-lg hover:shadow-[#4DFF91]/30 transition">
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CoachDrillLibrary;