import React, { useState } from 'react';
import { Award, Trophy, TrendingUp, Zap, Heart, Star } from 'lucide-react';

const ParentAchievements = ({ child }) => {
  const [filterCategory, setFilterCategory] = useState('all');

  // Mock achievements data
  const achievements = [
    {
      id: '1',
      title: '7-Day Training Streak',
      category: 'Consistency',
      dateEarned: '2024-03-18',
      description: 'Completed 7 consecutive days of training',
      icon: 'fire'
    },
    {
      id: '2',
      title: 'Sprint Personal Best',
      category: 'Speed',
      dateEarned: '2024-03-15',
      description: 'Beat 30m sprint personal record by 0.3 seconds',
      icon: 'zap'
    },
    {
      id: '3',
      title: 'Left Foot Master',
      category: 'Skill',
      dateEarned: '2024-03-10',
      description: 'Achieved 80% accuracy with weak foot in training',
      icon: 'star'
    },
    {
      id: '4',
      title: 'Mental Toughness',
      category: 'Mental',
      dateEarned: '2024-03-05',
      description: 'Completed 5 tough sessions with excellent attitude',
      icon: 'heart'
    },
    {
      id: '5',
      title: 'Assessment Excellence',
      category: 'Speed',
      dateEarned: '2024-02-28',
      description: 'Scored 85+ on physical assessment',
      icon: 'trophy'
    },
    {
      id: '6',
      title: 'Team Player',
      category: 'Skill',
      dateEarned: '2024-02-20',
      description: 'Highest passing accuracy in team training',
      icon: 'star'
    }
  ];

  const stats = {
    total: achievements.length,
    currentStreak: 12,
    recentBadge: achievements[0]
  };

  const categories = ['all', 'Consistency', 'Speed', 'Skill', 'Mental'];

  const filteredAchievements = filterCategory === 'all'
    ? achievements
    : achievements.filter(a => a.category === filterCategory);

  const getIconComponent = (icon) => {
    switch (icon) {
      case 'fire': return <Award className="w-8 h-8" />;
      case 'zap': return <Zap className="w-8 h-8" />;
      case 'star': return <Star className="w-8 h-8" />;
      case 'heart': return <Heart className="w-8 h-8" />;
      case 'trophy': return <Trophy className="w-8 h-8" />;
      default: return <Award className="w-8 h-8" />;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Consistency': return 'bg-orange-100 text-orange-800';
      case 'Speed': return 'bg-blue-100 text-blue-800';
      case 'Skill': return 'bg-purple-100 text-purple-800';
      case 'Mental': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Trophy className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Achievements</p>
              <p className="text-3xl font-bold text-gray-800">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Current Streak</p>
              <p className="text-3xl font-bold text-gray-800">{stats.currentStreak} days</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Most Recent</p>
              <p className="text-sm font-bold text-gray-800">{stats.recentBadge.title}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-gray-800 mb-4">Filter by Category</h3>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                filterCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Achievements Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAchievements.map((achievement) => (
          <div key={achievement.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div className={`w-16 h-16 rounded-lg flex items-center justify-center ${
                getCategoryColor(achievement.category)
              }`}>
                {getIconComponent(achievement.icon)}
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                getCategoryColor(achievement.category)
              }`}>
                {achievement.category}
              </span>
            </div>

            <h3 className="font-bold text-gray-800 text-lg mb-2">{achievement.title}</h3>
            <p className="text-sm text-gray-600 mb-3">{achievement.description}</p>
            
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Award className="w-4 h-4" />
              <span>Earned on {achievement.dateEarned}</span>
            </div>
          </div>
        ))}
      </div>

      {filteredAchievements.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Award className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-800 mb-2">No achievements in this category yet</h3>
          <p className="text-gray-600">Keep training to unlock more badges!</p>
        </div>
      )}
    </div>
  );
};

export default ParentAchievements;