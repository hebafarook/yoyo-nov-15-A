import React, { useState } from 'react';
import { Heart, Moon, Droplet, AlertCircle } from 'lucide-react';

const PlayerRecovery = () => {
  const [checkIn, setCheckIn] = useState({
    energy: 7,
    soreness: 3,
    mood: 8,
    pain: false,
    sleep: 8,
    water: 6
  });

  const [submitted, setSubmitted] = useState(false);

  const recoveryProtocol = [
    { title: 'Light Stretching', duration: '10 min', description: 'Focus on legs and back' },
    { title: 'Foam Rolling', duration: '5 min', description: 'Target sore muscle groups' },
    { title: 'Breathing Exercise', duration: '5 min', description: 'Deep breathing for relaxation' }
  ];

  const handleSubmit = () => {
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 2000);
  };

  const getSuggestion = () => {
    if (checkIn.energy < 5 || checkIn.soreness > 6) {
      return {
        type: 'warning',
        message: 'Light day recommended. Focus on recovery activities.',
        icon: AlertCircle,
        color: 'text-orange-600'
      };
    }
    return {
      type: 'success',
      message: 'You\'re ready for a good training session!',
      icon: Heart,
      color: 'text-green-600'
    };
  };

  const suggestion = getSuggestion();
  const SuggestionIcon = suggestion.icon;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-6 text-white shadow-lg border-2 border-yellow-400">
        <div className="flex items-center gap-3 mb-2">
          <Heart className="w-8 h-8" />
          <h2 className="text-3xl font-bold">Recovery & Well-Being</h2>
        </div>
        <p className="text-white/90">Track how you feel and optimize your training</p>
      </div>

      {/* Daily Check-In */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-6">Today's Check-In</h3>
        
        <div className="space-y-6">
          {/* Energy Level */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Energy Level</label>
              <span className="text-2xl font-bold text-blue-600">{checkIn.energy}/10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={checkIn.energy}
              onChange={(e) => setCheckIn({...checkIn, energy: parseInt(e.target.value)})}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>

          {/* Muscle Soreness */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Muscle Soreness</label>
              <span className={`text-2xl font-bold ${
                checkIn.soreness <= 3 ? 'text-green-600' :
                checkIn.soreness <= 6 ? 'text-yellow-600' : 'text-red-600'
              }`}>{checkIn.soreness}/10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={checkIn.soreness}
              onChange={(e) => setCheckIn({...checkIn, soreness: parseInt(e.target.value)})}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>None</span>
              <span>Severe</span>
            </div>
          </div>

          {/* Mood */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Mood</label>
              <span className="text-2xl font-bold text-purple-600">{checkIn.mood}/10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={checkIn.mood}
              onChange={(e) => setCheckIn({...checkIn, mood: parseInt(e.target.value)})}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Pain Check */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <label className="text-sm font-medium text-gray-700">Any pain or discomfort?</label>
            <button
              onClick={() => setCheckIn({...checkIn, pain: !checkIn.pain})}
              className={`px-6 py-2 rounded-lg font-medium transition ${
                checkIn.pain ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              {checkIn.pain ? 'Yes' : 'No'}
            </button>
          </div>

          {/* Sleep & Hydration */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Moon className="w-5 h-5 text-gray-600" />
                <label className="text-sm font-medium text-gray-700">Sleep (hours)</label>
              </div>
              <input
                type="number"
                min="0"
                max="12"
                value={checkIn.sleep}
                onChange={(e) => setCheckIn({...checkIn, sleep: parseInt(e.target.value)})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Droplet className="w-5 h-5 text-gray-600" />
                <label className="text-sm font-medium text-gray-700">Water (glasses)</label>
              </div>
              <input
                type="number"
                min="0"
                max="15"
                value={checkIn.water}
                onChange={(e) => setCheckIn({...checkIn, water: parseInt(e.target.value)})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          className={`w-full mt-6 py-3 rounded-xl font-semibold transition ${
            submitted ? 'bg-green-600 text-white' : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {submitted ? '✓ Saved!' : 'Save Check-In'}
        </button>
      </div>

      {/* AI Suggestion */}
      <div className={`bg-white rounded-2xl p-6 shadow-lg border-2 ${
        suggestion.type === 'warning' ? 'border-orange-200' : 'border-green-200'
      }`}>
        <div className="flex items-start gap-3">
          <SuggestionIcon className={`w-6 h-6 ${suggestion.color} mt-1`} />
          <div>
            <h3 className="font-bold text-gray-800 mb-1">AI Recommendation</h3>
            <p className="text-gray-700">{suggestion.message}</p>
          </div>
        </div>
      </div>

      {/* Recovery Protocol */}
      {suggestion.type === 'warning' && (
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Recommended Recovery</h3>
          <div className="space-y-3">
            {recoveryProtocol.map((activity, idx) => (
              <div key={idx} className="bg-gray-50 rounded-xl p-4">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-bold text-gray-800">{activity.title}</h4>
                  <span className="text-sm text-gray-600">{activity.duration}</span>
                </div>
                <p className="text-sm text-gray-600">{activity.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerRecovery;