import React, { useState } from 'react';
import { Heart, Droplet, Moon, AlertCircle, TrendingUp } from 'lucide-react';

const ParentHealth = ({ child }) => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [formData, setFormData] = useState({
    sleepHours: 8,
    hydrationLiters: 2,
    sorenessLevel: 3,
    injuryNotes: '',
    meals: '',
    energyFeeling: 'normal'
  });

  // Mock history data
  const healthHistory = [
    { date: '2024-03-18', sleep: 8, hydration: 2.5, soreness: 2, injury: false, energy: 'high' },
    { date: '2024-03-17', sleep: 7, hydration: 2, soreness: 4, injury: false, energy: 'normal' },
    { date: '2024-03-16', sleep: 6, hydration: 1.5, soreness: 6, injury: true, energy: 'low' },
    { date: '2024-03-15', sleep: 9, hydration: 3, soreness: 1, injury: false, energy: 'high' },
    { date: '2024-03-14', sleep: 7.5, hydration: 2, soreness: 3, injury: false, energy: 'normal' },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Health log saved successfully!');
  };

  const getSorenessColor = (level) => {
    if (level <= 3) return 'text-green-600';
    if (level <= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getEnergyBadgeColor = (energy) => {
    switch (energy) {
      case 'high': return 'bg-green-100 text-green-800';
      case 'normal': return 'bg-blue-100 text-blue-800';
      case 'low': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Health & Nutrition Log</h2>
        <p className="text-gray-600">Track daily wellness factors to optimize training</p>
      </div>

      {/* Log Entry Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-gray-800">Today's Log</h3>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Sleep Hours */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Moon className="w-4 h-4" />
                Sleep Hours
              </label>
              <input
                type="number"
                min="0"
                max="24"
                step="0.5"
                value={formData.sleepHours}
                onChange={(e) => setFormData({...formData, sleepHours: parseFloat(e.target.value)})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Hydration */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Droplet className="w-4 h-4" />
                Hydration (liters)
              </label>
              <input
                type="number"
                min="0"
                max="10"
                step="0.1"
                value={formData.hydrationLiters}
                onChange={(e) => setFormData({...formData, hydrationLiters: parseFloat(e.target.value)})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Soreness Level */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Heart className="w-4 h-4" />
              Soreness Level (0 = None, 10 = Severe)
            </label>
            <input
              type="range"
              min="0"
              max="10"
              value={formData.sorenessLevel}
              onChange={(e) => setFormData({...formData, sorenessLevel: parseInt(e.target.value)})}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600 mt-1">
              <span>None</span>
              <span className={`font-bold ${getSorenessColor(formData.sorenessLevel)}`}>
                {formData.sorenessLevel}
              </span>
              <span>Severe</span>
            </div>
          </div>

          {/* Energy Feeling */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Energy Level</label>
            <div className="flex gap-2">
              {['low', 'normal', 'high'].map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setFormData({...formData, energyFeeling: level})}
                  className={`flex-1 py-2 rounded-lg font-medium transition ${
                    formData.energyFeeling === level
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Injury Notes */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <AlertCircle className="w-4 h-4" />
              Injury / Pain Notes
            </label>
            <textarea
              value={formData.injuryNotes}
              onChange={(e) => setFormData({...formData, injuryNotes: e.target.value})}
              placeholder="Any injuries, pain, or discomfort?"
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Meals */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Meals Summary</label>
            <textarea
              value={formData.meals}
              onChange={(e) => setFormData({...formData, meals: e.target.value})}
              placeholder="What did they eat today? (e.g., Breakfast: oats, lunch: chicken salad...)"
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Save Today's Log
          </button>
        </form>
      </div>

      {/* Health History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Last 7 Days</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Date</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Sleep</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Hydration</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Soreness</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Injury</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Energy</th>
              </tr>
            </thead>
            <tbody>
              {healthHistory.map((day, idx) => (
                <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm text-gray-700">{day.date}</td>
                  <td className="py-3 px-4 text-sm text-gray-700 text-center">{day.sleep}h</td>
                  <td className="py-3 px-4 text-sm text-gray-700 text-center">{day.hydration}L</td>
                  <td className={`py-3 px-4 text-sm text-center font-medium ${getSorenessColor(day.soreness)}`}>
                    {day.soreness}/10
                  </td>
                  <td className="py-3 px-4 text-center">
                    {day.injury ? (
                      <span className="text-red-600">Yes</span>
                    ) : (
                      <span className="text-green-600">No</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEnergyBadgeColor(day.energy)}`}>
                      {day.energy}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Health Insight */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg shadow p-6">
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-orange-600" />
          AI Health Insights
        </h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-orange-600 mt-0.5" />
            <span>Low sleep detected for 2 consecutive days - recommend lighter training intensity</span>
          </li>
          <li className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-orange-600 mt-0.5" />
            <span>Soreness level high after intense sprint day - recovery protocols suggested</span>
          </li>
          <li className="flex items-start gap-2">
            <Heart className="w-4 h-4 text-green-600 mt-0.5" />
            <span>Hydration improving - maintain 2-3L daily for optimal performance</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ParentHealth;