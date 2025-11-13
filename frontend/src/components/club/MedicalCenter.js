import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Heart, Plus, AlertCircle, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const MedicalCenter = ({ clubId }) => {
  const [injuries, setInjuries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInjuries();
  }, [clubId]);

  const fetchInjuries = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const res = await axios.get(`${BACKEND_URL}/api/club/${clubId}/injuries`, { headers });
      setInjuries(res.data.injuries || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching injuries:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-96">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400"></div>
    </div>;
  }

  const activeInjuries = injuries.filter(i => i.status === 'active');
  const recoveringInjuries = injuries.filter(i => i.status === 'recovering');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Medical & Injury Center</h2>
          <p className="text-gray-400">Track injuries and recovery protocols</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-rose-500 to-pink-600 text-white rounded-xl font-medium hover:shadow-lg transition">
          <Plus className="w-5 h-5" />
          Report Injury
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-red-400/20 shadow-2xl">
          <AlertCircle className="w-12 h-12 text-red-400 mb-3" />
          <p className="text-gray-400 text-sm">Active Injuries</p>
          <p className="text-4xl font-bold text-white">{activeInjuries.length}</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-yellow-400/20 shadow-2xl">
          <TrendingUp className="w-12 h-12 text-yellow-400 mb-3" />
          <p className="text-gray-400 text-sm">Recovering</p>
          <p className="text-4xl font-bold text-white">{recoveringInjuries.length}</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <Heart className="w-12 h-12 text-green-400 mb-3" />
          <p className="text-gray-400 text-sm">Total Records</p>
          <p className="text-4xl font-bold text-white">{injuries.length}</p>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-bold text-white">Recent Injuries</h3>
        {injuries.slice(0, 10).map((injury) => (
          <div key={injury.id} className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-rose-400/20 shadow-2xl">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h4 className="text-white font-bold text-lg mb-2">Player ID: {injury.player_id}</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-400">Type</p>
                    <p className="text-white font-medium">{injury.injury_type}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Location</p>
                    <p className="text-white font-medium">{injury.injury_location}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Severity</p>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      injury.severity === 'severe' ? 'bg-red-500/20 text-red-400' :
                      injury.severity === 'moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {injury.severity}
                    </span>
                  </div>
                  <div>
                    <p className="text-gray-400">Days Out</p>
                    <p className="text-white font-medium">{injury.days_out}</p>
                  </div>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                injury.status === 'active' ? 'bg-red-500/20 text-red-400' :
                injury.status === 'recovering' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-green-500/20 text-green-400'
              }`}>
                {injury.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {injuries.length === 0 && (
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-12 border border-green-400/20 text-center">
          <Heart className="w-16 h-16 text-green-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">No Injuries Recorded</h3>
          <p className="text-gray-400">Great! Keep up the injury prevention work</p>
        </div>
      )}
    </div>
  );
};

export default MedicalCenter;