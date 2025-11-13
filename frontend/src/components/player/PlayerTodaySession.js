import React, { useState, useEffect } from 'react';
import { CheckCircle, Play, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayerTodaySession = () => {
  const { user } = useAuth();
  const [expandedBlock, setExpandedBlock] = useState(null);
  const [completedDrills, setCompletedDrills] = useState([]);
  const [currentRoutine, setCurrentRoutine] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      fetchTodayRoutine();
    }
  }, [user]);

  const fetchTodayRoutine = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(`${BACKEND_URL}/api/current-routine/${user.id}`, { headers });
      setCurrentRoutine(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching today routine:', error);
      setLoading(false);
    }
  };

  const handleFinishSession = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const progressData = {
        player_id: user.id,
        date: new Date().toISOString().split('T')[0],
        routine_id: currentRoutine?.id || 'daily-routine',
        completed_exercises: completedDrills.map(drillId => ({
          exercise_name: drillId,
          sets_completed: 1,
          reps_completed: 1,
          rating: 5,
          notes: 'Completed',
          player_id: user.id
        })),
        overall_rating: 5,
        feedback: 'Session completed'
      };
      
      await axios.post(`${BACKEND_URL}/api/daily-progress`, progressData, { headers });
      alert('Session completed successfully! Great work!');
      setCompletedDrills([]);
    } catch (error) {
      console.error('Error saving progress:', error);
      alert('Error saving progress. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading today's session...</p>
        </div>
      </div>
    );
  }

  // If no routine, show default mock data
  const session = currentRoutine || {
    title: "Today's Session",
    subtitle: "Built from your latest assessment",
    estimatedTime: "50 min",
    blocks: [
      {
        id: 'warmup',
        title: 'Warm-Up',
        duration: '10 min',
        drills: [
          { id: 'w1', name: 'Dynamic Stretching', time: '3 min', reps: null },
          { id: 'w2', name: 'Light Jogging', time: '3 min', reps: null },
          { id: 'w3', name: 'High Knees', time: '2 min', reps: '30 sec on/off' },
          { id: 'w4', name: 'Butt Kicks', time: '2 min', reps: '30 sec on/off' }
        ]
      },
      {
        id: 'technical',
        title: 'Technical Block',
        duration: '25 min',
        drills: [
          {
            id: 't1',
            name: 'Cone Dribble – Right/Left Foot',
            description: 'Weave through 10 cones focusing on close control',
            skillFocus: 'Dribbling, Weak Foot',
            sets: 4,
            reps: '20m runs',
            time: null,
            requirements: '10 cones, ball, 20m space',
            videoUrl: '#'
          },
          {
            id: 't2',
            name: 'Wall Pass & First Touch',
            description: 'Pass against wall, control with one touch',
            skillFocus: 'Passing, First Touch',
            sets: 3,
            reps: 20,
            time: null,
            requirements: 'Wall, ball',
            videoUrl: '#'
          }
        ]
      },
      {
        id: 'conditioning',
        title: 'Conditioning Block',
        duration: '12 min',
        drills: [
          {
            id: 'c1',
            name: '20m Sprint Intervals',
            description: 'Max effort sprints with recovery',
            skillFocus: 'Speed, Acceleration',
            sets: 6,
            reps: 1,
            time: '20m sprint',
            requirements: '20m marked space',
            videoUrl: '#'
          }
        ]
      },
      {
        id: 'recovery',
        title: 'Recovery',
        duration: '8 min',
        drills: [
          { id: 'r1', name: 'Cool Down Jog', time: '3 min', reps: null },
          { id: 'r2', name: 'Static Stretching', time: '5 min', reps: null }
        ]
      }
    ]
  };

  const toggleDrill = (drillId) => {
    if (completedDrills.includes(drillId)) {
      setCompletedDrills(completedDrills.filter(id => id !== drillId));
    } else {
      setCompletedDrills([...completedDrills, drillId]);
    }
  };

  const totalDrills = session.blocks.reduce((acc, block) => acc + block.drills.length, 0);
  const progressPercent = Math.round((completedDrills.length / totalDrills) * 100);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Session Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <h2 className="text-3xl font-bold mb-2">{session.title}</h2>
        <p className="text-white/90 mb-1">{session.subtitle}</p>
        <p className="text-sm text-white/80">⏱️ Estimated: {session.estimatedTime}</p>
      </div>

      {/* Progress Bar */}
      <div className="bg-white rounded-xl p-4 shadow-lg border border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Session Progress</span>
          <span className="text-sm font-bold text-blue-600">{completedDrills.length}/{totalDrills} drills</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-blue-600 h-3 rounded-full transition-all"
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>
      </div>

      {/* Blocks */}
      {session.blocks.map((block) => (
        <div key={block.id} className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => setExpandedBlock(expandedBlock === block.id ? null : block.id)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition"
          >
            <div className="text-left">
              <h3 className="text-xl font-bold text-gray-800">{block.title}</h3>
              <p className="text-sm text-gray-600">{block.duration}</p>
            </div>
            {expandedBlock === block.id ? (
              <ChevronUp className="w-6 h-6 text-gray-600" />
            ) : (
              <ChevronDown className="w-6 h-6 text-gray-600" />
            )}
          </button>

          {expandedBlock === block.id && (
            <div className="px-6 pb-6 space-y-4">
              {block.drills.map((drill) => (
                <div key={drill.id} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-800 mb-1">{drill.name}</h4>
                      {drill.description && (
                        <p className="text-sm text-gray-600 mb-2">{drill.description}</p>
                      )}
                      {drill.skillFocus && (
                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                          {drill.skillFocus}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => toggleDrill(drill.id)}
                      className={`ml-4 p-2 rounded-lg transition ${
                        completedDrills.includes(drill.id)
                          ? 'bg-green-100'
                          : 'bg-gray-200 hover:bg-gray-300'
                      }`}
                    >
                      <CheckCircle className={`w-6 h-6 ${
                        completedDrills.includes(drill.id) ? 'text-green-600' : 'text-gray-400'
                      }`} />
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-700 mb-3">
                    {drill.sets && <div><strong>Sets:</strong> {drill.sets}</div>}
                    {drill.reps && <div><strong>Reps:</strong> {drill.reps}</div>}
                    {drill.time && <div><strong>Time:</strong> {drill.time}</div>}
                    {drill.requirements && <div className="col-span-2"><strong>Requirements:</strong> {drill.requirements}</div>}
                  </div>

                  {drill.videoUrl && (
                    <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm">
                      <Play className="w-4 h-4" />
                      Watch Video
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}

      {/* Finish Button */}
      <button
        onClick={progressPercent === 100 ? handleFinishSession : null}
        disabled={progressPercent < 100}
        className="w-full py-4 bg-green-600 text-white rounded-xl font-bold text-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-lg"
      >
        {progressPercent === 100 ? 'Finish Session ✓' : `Complete All Drills (${completedDrills.length}/${totalDrills})`}
      </button>
    </div>
  );
};

export default PlayerTodaySession;