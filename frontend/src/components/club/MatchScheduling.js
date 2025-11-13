import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar, Plus, MapPin, Clock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const MatchScheduling = ({ clubId }) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('upcoming'); // upcoming or past

  useEffect(() => {
    fetchMatches();
  }, [clubId, viewMode]);

  const fetchMatches = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/matches?upcoming=${viewMode === 'upcoming'}`, { headers });
      setMatches(res.data.matches || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching matches:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Match & Event Scheduling</h2>
          <p className="text-gray-400">Manage matches and competitions</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg transition">
          <Plus className="w-5 h-5" />
          Schedule Match
        </button>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setViewMode('upcoming')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            viewMode === 'upcoming'
              ? 'bg-green-500/20 text-green-400 border border-green-400/50'
              : 'bg-gray-800/60 text-gray-400 border border-gray-700/50 hover:text-white'
          }`}
        >
          Upcoming
        </button>
        <button
          onClick={() => setViewMode('past')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            viewMode === 'past'
              ? 'bg-green-500/20 text-green-400 border border-green-400/50'
              : 'bg-gray-800/60 text-gray-400 border border-gray-700/50 hover:text-white'
          }`}
        >
          Past Matches
        </button>
      </div>

      <div className="space-y-4">
        {matches.map((match) => (
          <div key={match.id} className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl hover:border-green-400/50 transition">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <h3 className="text-2xl font-bold text-white">vs {match.opponent}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    match.home_away === 'home' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                  }`}>
                    {match.home_away.toUpperCase()}
                  </span>
                  <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-medium">
                    {match.match_type}
                  </span>
                </div>
                <div className="flex flex-wrap gap-4 text-sm text-gray-400">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(match.match_date).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{match.match_time}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    <span>{match.venue}</span>
                  </div>
                </div>
              </div>
              {match.played && match.score_for !== null && (
                <div className="text-right">
                  <p className="text-4xl font-bold text-white">{match.score_for} - {match.score_against}</p>
                  <span className={`text-sm font-medium ${
                    match.result === 'win' ? 'text-green-400' :
                    match.result === 'loss' ? 'text-red-400' : 'text-gray-400'
                  }`}>
                    {match.result?.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {matches.length === 0 && (
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-12 border border-indigo-400/20 text-center">
          <Calendar className="w-16 h-16 text-indigo-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">No {viewMode} matches</h3>
          <p className="text-gray-400">Schedule your first match to get started</p>
        </div>
      )}
    </div>
  );
};

export default MatchScheduling;