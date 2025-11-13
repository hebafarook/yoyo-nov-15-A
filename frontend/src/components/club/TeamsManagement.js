import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Plus, Eye, Edit, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const TeamsManagement = ({ clubId }) => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchTeams();
  }, [clubId]);

  const fetchTeams = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/teams`, { headers });
      setTeams(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching teams:', error);
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
          <h2 className="text-3xl font-bold text-white">Teams Management</h2>
          <p className="text-gray-400">Manage all teams and squads</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-medium hover:shadow-lg transition"
        >
          <Plus className="w-5 h-5" />
          Create Team
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {teams.map((team) => (
          <div key={team.id} className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl hover:border-green-400/50 transition">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">{team.name}</h3>
              <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-medium">
                {team.age_group}
              </span>
            </div>
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Players</span>
                <span className="text-white font-medium">{team.player_ids?.length || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Division</span>
                <span className="text-white font-medium">{team.division}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Overall Score</span>
                <span className="text-white font-medium">{team.team_overall_score.toFixed(1)}</span>
              </div>
            </div>
            <button className="w-full py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition flex items-center justify-center gap-2">
              <Eye className="w-4 h-4" />
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TeamsManagement;