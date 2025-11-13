import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Filter, AlertTriangle, Activity } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PlayersDirectory = ({ clubId }) => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSafety, setFilterSafety] = useState('all');

  useEffect(() => {
    fetchPlayers();
  }, [clubId, filterSafety]);

  const fetchPlayers = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const params = {};
      if (filterSafety !== 'all') params.safety_status = filterSafety;
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/players`, { headers, params });
      setPlayers(res.data.players || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching players:', error);
      setLoading(false);
    }
  };

  const filteredPlayers = players.filter(p => 
    p.player_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="flex justify-center items-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Players Directory</h2>
        <p className="text-gray-400">Complete player database</p>
      </div>

      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search players..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-gray-800/60 border border-green-400/20 rounded-xl text-white placeholder-gray-400 focus:border-green-400 focus:outline-none"
          />
        </div>
        <select
          value={filterSafety}
          onChange={(e) => setFilterSafety(e.target.value)}
          className="px-4 py-3 bg-gray-800/60 border border-green-400/20 rounded-xl text-white focus:border-green-400 focus:outline-none"
        >
          <option value="all">All Status</option>
          <option value="safe">Safe</option>
          <option value="caution">Caution</option>
          <option value="red_flag">Red Flag</option>
        </select>
      </div>

      <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl border border-green-400/20 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-900/80">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Player</th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Age</th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Position</th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Score</th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Safety</th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Load</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50">
            {filteredPlayers.map((player) => (
              <tr key={player.id} className="hover:bg-gray-700/30 transition">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-sm">{player.player_name[0]}</span>
                    </div>
                    <span className="text-white font-medium">{player.player_name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-300">{player.age}</td>
                <td className="px-6 py-4 text-gray-300">{player.position}</td>
                <td className="px-6 py-4">
                  <span className="text-white font-medium">{player.overall_score.toFixed(1)}</span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    player.safety_status === 'safe' ? 'bg-green-500/20 text-green-400' :
                    player.safety_status === 'caution' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {player.safety_status}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-300">{player.weekly_training_load.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlayersDirectory;