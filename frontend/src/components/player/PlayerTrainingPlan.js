import React from 'react';
import { Calendar, CheckCircle, Circle, Activity, Zap, Heart } from 'lucide-react';

const PlayerTrainingPlan = () => {
  const weekPlan = {
    weekNumber: 12,
    focus: 'Speed & First Touch',
    coachNotes: 'Important match on Saturday! Focus on quick ball control.',
    days: [
      {
        day: 'Monday',
        date: '2024-03-18',
        type: 'Technical',
        title: 'Ball Control Session',
        duration: '60 min',
        objective: 'Improve first touch and close control',
        completed: true,
        icon: Activity
      },
      {
        day: 'Tuesday',
        date: '2024-03-19',
        type: 'Conditioning',
        title: 'Speed & Agility',
        duration: '50 min',
        objective: 'Develop acceleration and change of direction',
        completed: true,
        icon: Zap
      },
      {
        day: 'Wednesday',
        date: '2024-03-20',
        type: 'Recovery',
        title: 'Active Recovery',
        duration: '30 min',
        objective: 'Light work and stretching',
        completed: false,
        icon: Heart
      },
      {
        day: 'Thursday',
        date: '2024-03-21',
        type: 'Technical',
        title: 'Finishing Practice',
        duration: '60 min',
        objective: 'Shooting accuracy and composure',
        completed: false,
        icon: Activity
      },
      {
        day: 'Friday',
        date: '2024-03-22',
        type: 'Match Prep',
        title: 'Team Tactical',
        duration: '90 min',
        objective: 'Team shape and set pieces',
        completed: false,
        icon: Activity
      },
      {
        day: 'Saturday',
        date: '2024-03-23',
        type: 'Match',
        title: 'League Match',
        duration: '90 min',
        objective: 'Apply training in competition',
        completed: false,
        icon: Zap
      },
      {
        day: 'Sunday',
        date: '2024-03-24',
        type: 'Rest',
        title: 'Complete Rest',
        duration: '0 min',
        objective: 'Recovery and regeneration',
        completed: false,
        icon: Heart
      }
    ]
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'Technical': return 'bg-blue-100 text-blue-600';
      case 'Conditioning': return 'bg-purple-100 text-purple-600';
      case 'Recovery': return 'bg-green-100 text-green-600';
      case 'Match Prep': return 'bg-orange-100 text-orange-600';
      case 'Match': return 'bg-red-100 text-red-600';
      case 'Rest': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Week Summary */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold mb-2">Week {weekPlan.weekNumber} Training Plan</h2>
            <p className="text-lg font-medium mb-1">Focus: {weekPlan.focus}</p>
          </div>
          <Calendar className="w-12 h-12 text-white/80" />
        </div>
        <div className="bg-white/20 rounded-xl p-4">
          <p className="text-sm font-medium mb-1">Coach Notes:</p>
          <p className="text-white/90">{weekPlan.coachNotes}</p>
        </div>
      </div>

      {/* Weekly Calendar */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Your Week</h3>
        <div className="space-y-3">
          {weekPlan.days.map((session, idx) => {
            const Icon = session.icon;
            return (
              <div
                key={idx}
                className="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:bg-gray-100 transition cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getTypeColor(session.type)}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-bold text-gray-800">{session.day}</h4>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getTypeColor(session.type)}`}>
                          {session.type}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-700 mb-1">{session.title}</p>
                      <p className="text-xs text-gray-600 mb-1">{session.objective}</p>
                      <p className="text-xs text-gray-500">⏱️ {session.duration}</p>
                    </div>
                  </div>
                  <div>
                    {session.completed ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <Circle className="w-6 h-6 text-gray-300" />
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Request Change Button */}
      <button className="w-full py-3 bg-white border-2 border-blue-600 text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition shadow-lg">
        Request Plan Change
      </button>
    </div>
  );
};

export default PlayerTrainingPlan;