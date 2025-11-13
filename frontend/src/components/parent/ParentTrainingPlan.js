import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Play, CheckCircle, Circle, Clock } from 'lucide-react';

const ParentTrainingPlan = ({ child }) => {
  const [expandedDay, setExpandedDay] = useState(null);
  const [currentWeek, setCurrentWeek] = useState(0);

  // Mock training plan data
  const trainingPlan = {
    weekStart: '2024-03-18',
    weekEnd: '2024-03-24',
    focusTheme: 'Speed & First Touch Development',
    days: [
      {
        dayOfWeek: 'Monday',
        focus: 'Speed & Agility',
        status: 'completed',
        drills: [
          {
            name: '30m Sprint Intervals',
            description: 'Maximal effort sprints with full recovery',
            sets: 6,
            reps: 1,
            timeSeconds: 30,
            restSeconds: 120,
            difficultyLevel: 'Intermediate',
            videoUrl: '#',
            completed: true
          },
          {
            name: 'Cone Weave Agility',
            description: 'Quick feet through 10 cones',
            sets: 4,
            reps: 3,
            timeSeconds: 20,
            restSeconds: 60,
            difficultyLevel: 'Beginner',
            videoUrl: '#',
            completed: true
          }
        ]
      },
      {
        dayOfWeek: 'Tuesday',
        focus: 'Ball Control & First Touch',
        status: 'completed',
        drills: [
          {
            name: 'Wall Pass Control',
            description: 'First touch control from wall passes',
            sets: 3,
            reps: 20,
            timeSeconds: 0,
            restSeconds: 90,
            difficultyLevel: 'Intermediate',
            videoUrl: '#',
            completed: true
          },
          {
            name: 'Juggling Progression',
            description: 'Foot juggling with both feet',
            sets: 4,
            reps: 0,
            timeSeconds: 120,
            restSeconds: 60,
            difficultyLevel: 'Beginner',
            videoUrl: '#',
            completed: true
          }
        ]
      },
      {
        dayOfWeek: 'Wednesday',
        focus: 'Rest & Recovery',
        status: 'completed',
        drills: []
      },
      {
        dayOfWeek: 'Thursday',
        focus: 'Shooting & Finishing',
        status: 'in-progress',
        drills: [
          {
            name: 'Left Foot Finishing',
            description: 'Focus on weak foot shooting accuracy',
            sets: 5,
            reps: 10,
            timeSeconds: 0,
            restSeconds: 90,
            difficultyLevel: 'Intermediate',
            videoUrl: '#',
            completed: false
          },
          {
            name: '1v1 Striker Moves',
            description: 'Beat defender and finish',
            sets: 4,
            reps: 5,
            timeSeconds: 0,
            restSeconds: 120,
            difficultyLevel: 'Elite',
            videoUrl: '#',
            completed: false
          }
        ]
      },
      {
        dayOfWeek: 'Friday',
        focus: 'Game Situations',
        status: 'not-started',
        drills: [
          {
            name: 'Small-Sided Game',
            description: '4v4 match simulation',
            sets: 2,
            reps: 0,
            timeSeconds: 900,
            restSeconds: 300,
            difficultyLevel: 'Intermediate',
            videoUrl: '#',
            completed: false
          }
        ]
      }
    ]
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'not-started': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'in-progress': return 'In Progress';
      case 'not-started': return 'Not Started';
      default: return 'Scheduled';
    }
  };

  const getDifficultyColor = (level) => {
    switch (level) {
      case 'Beginner': return 'bg-blue-100 text-blue-800';
      case 'Intermediate': return 'bg-purple-100 text-purple-800';
      case 'Elite': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Training Plan</h2>
            <p className="text-gray-600">{trainingPlan.weekStart} – {trainingPlan.weekEnd}</p>
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 bg-gray-100 rounded-lg text-sm font-medium hover:bg-gray-200">
              Previous Week
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
              Current Week
            </button>
            <button className="px-4 py-2 bg-gray-100 rounded-lg text-sm font-medium hover:bg-gray-200">
              Next Week
            </button>
          </div>
        </div>

        <div className="p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-1">Week Focus</h3>
          <p className="text-sm text-gray-700">{trainingPlan.focusTheme}</p>
        </div>
      </div>

      {/* Daily Sessions */}
      <div className="space-y-3">
        {trainingPlan.days.map((day, dayIdx) => (
          <div key={dayIdx} className="bg-white rounded-lg shadow overflow-hidden">
            <button
              onClick={() => setExpandedDay(expandedDay === dayIdx ? null : dayIdx)}
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition"
            >
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100">
                  {day.status === 'completed' ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : day.status === 'in-progress' ? (
                    <Clock className="w-6 h-6 text-yellow-600" />
                  ) : (
                    <Circle className="w-6 h-6 text-gray-400" />
                  )}
                </div>
                <div className="text-left">
                  <h3 className="font-bold text-gray-800">{day.dayOfWeek}</h3>
                  <p className="text-sm text-gray-600">{day.focus}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(day.status)}`}>
                  {getStatusLabel(day.status)}
                </span>
                {expandedDay === dayIdx ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </button>

            {/* Expanded Drills */}
            {expandedDay === dayIdx && day.drills.length > 0 && (
              <div className="border-t border-gray-200 p-6 bg-gray-50">
                <h4 className="font-semibold text-gray-800 mb-4">Training Drills</h4>
                <div className="space-y-4">
                  {day.drills.map((drill, drillIdx) => (
                    <div key={drillIdx} className="bg-white rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h5 className="font-semibold text-gray-800">{drill.name}</h5>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getDifficultyColor(drill.difficultyLevel)}`}>
                              {drill.difficultyLevel}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-3">{drill.description}</p>
                          
                          <div className="flex flex-wrap gap-4 text-sm text-gray-700">
                            {drill.sets > 0 && (
                              <span><strong>Sets:</strong> {drill.sets}</span>
                            )}
                            {drill.reps > 0 && (
                              <span><strong>Reps:</strong> {drill.reps}</span>
                            )}
                            {drill.timeSeconds > 0 && (
                              <span><strong>Time:</strong> {Math.floor(drill.timeSeconds / 60)}:{(drill.timeSeconds % 60).toString().padStart(2, '0')}</span>
                            )}
                            {drill.restSeconds > 0 && (
                              <span><strong>Rest:</strong> {drill.restSeconds}s</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <button className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200">
                            <Play className="w-5 h-5" />
                          </button>
                          {drill.completed && (
                            <CheckCircle className="w-6 h-6 text-green-600" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {expandedDay === dayIdx && day.drills.length === 0 && (
              <div className="border-t border-gray-200 p-6 bg-gray-50 text-center text-gray-500">
                Rest day - no drills scheduled
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Why This Plan Panel */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow p-6">
        <h3 className="font-bold text-gray-800 mb-3">Why This Plan?</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></span>
            <span><strong>Target:</strong> Last assessment showed left-foot finishing and speed as key development areas</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></span>
            <span><strong>Approach:</strong> Progressive drills building from basic control to game situations</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2"></span>
            <span><strong>Expected Outcome:</strong> 15% improvement in left-foot accuracy and 0.2s faster sprint time by next assessment</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ParentTrainingPlan;