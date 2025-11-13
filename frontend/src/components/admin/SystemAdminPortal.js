import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, Plus, Trash2, Edit, Shield, Search, RefreshCw, 
  BarChart3, Activity, UserPlus, Key, Eye, EyeOff
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const SystemAdminPortal = () => {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    username: '',
    password: '',
    role: 'player',
    age: 18,
    position: ''
  });

  useEffect(() => {
    fetchData();
  }, [filterRole]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch users
      const params = {};
      if (filterRole !== 'all') params.role = filterRole;
      const usersRes = await axios.get(`${BACKEND_URL}/api/admin/users/all`, { headers, params });
      setUsers(usersRes.data.users || []);

      // Fetch stats
      const statsRes = await axios.get(`${BACKEND_URL}/api/admin/stats/overview`, { headers });
      setStats(statsRes.data.stats);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching admin data:', error);
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${BACKEND_URL}/api/admin/users/create`, newUser, { headers });
      alert('User created successfully!');
      setShowCreateModal(false);
      setNewUser({
        name: '',
        email: '',
        username: '',
        password: '',
        role: 'player',
        age: 18,
        position: ''
      });
      fetchData();
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDeleteUser = async (userId, userEmail) => {
    if (!window.confirm(`Are you sure you want to delete ${userEmail}? This will also delete all their data (assessments, programs, etc.)`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      await axios.delete(`${BACKEND_URL}/api/admin/users/${userId}/delete`, { headers });
      alert('User deleted successfully!');
      fetchData();
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleResetPassword = async (userId) => {
    const newPassword = prompt('Enter new password for this user:');
    if (!newPassword) return;

    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      await axios.post(`${BACKEND_URL}/api/admin/users/${userId}/reset-password`, null, {
        headers,
        params: { new_password: newPassword }
      });
      alert('Password reset successfully!');
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-orange-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading System Admin...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-orange-900">
      {/* Header */}
      <div className="bg-gray-900/80 backdrop-blur-lg border-b border-red-400/30 sticky top-0 z-50">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <Shield className="w-10 h-10 text-red-400" />
                System Admin Portal
              </h1>
              <p className="text-sm text-gray-400 mt-1">Complete user and system management</p>
            </div>
            <button
              onClick={fetchData}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Stats Dashboard */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <StatCard icon={Users} label="Total Users" value={stats.users.total} color="blue" />
            <StatCard icon={Activity} label="Players" value={stats.users.players} color="green" />
            <StatCard icon={Shield} label="Coaches" value={stats.users.coaches} color="orange" />
            <StatCard icon={Users} label="Parents" value={stats.users.parents} color="purple" />
            <StatCard icon={Shield} label="Clubs" value={stats.users.clubs} color="red" />
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-700 text-white rounded-xl font-medium hover:shadow-lg transition"
          >
            <Plus className="w-5 h-5" />
            Create User
          </button>

          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-800/60 border border-red-400/20 rounded-xl text-white placeholder-gray-400 focus:border-red-400 focus:outline-none"
            />
          </div>

          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="px-4 py-3 bg-gray-800/60 border border-red-400/20 rounded-xl text-white focus:border-red-400 focus:outline-none"
          >
            <option value="all">All Roles</option>
            <option value="player">Players</option>
            <option value="coach">Coaches</option>
            <option value="parent">Parents</option>
            <option value="club">Clubs</option>
            <option value="admin">Admins</option>
          </select>
        </div>

        {/* Users Table */}
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl border border-red-400/20 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900/80">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">User</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Email</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Role</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Created</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/50">
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-700/30 transition">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center">
                          <span className="text-white font-bold">{(user.name || user.username || 'U')[0].toUpperCase()}</span>
                        </div>
                        <div>
                          <p className="text-white font-medium">{user.name || user.username}</p>
                          <p className="text-xs text-gray-400">@{user.username}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-300">{user.email}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        user.role === 'admin' ? 'bg-red-500/20 text-red-400' :
                        user.role === 'player' ? 'bg-blue-500/20 text-blue-400' :
                        user.role === 'coach' ? 'bg-green-500/20 text-green-400' :
                        user.role === 'parent' ? 'bg-purple-500/20 text-purple-400' :
                        'bg-orange-500/20 text-orange-400'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-sm">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleResetPassword(user.id)}
                          className="p-2 bg-yellow-600/20 text-yellow-400 rounded-lg hover:bg-yellow-600/30 transition"
                          title="Reset Password"
                        >
                          <Key className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id, user.email)}
                          disabled={user.role === 'admin'}
                          className="p-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
                          title={user.role === 'admin' ? 'Cannot delete admin' : 'Delete User'}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No users found</p>
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-2xl p-6 max-w-md w-full border border-red-400/30">
            <h3 className="text-2xl font-bold text-white mb-4">Create New User</h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Full Name"
                value={newUser.name}
                onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-red-400 focus:outline-none"
              />
              <input
                type="email"
                placeholder="Email"
                value={newUser.email}
                onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-red-400 focus:outline-none"
              />
              <input
                type="text"
                placeholder="Username"
                value={newUser.username}
                onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-red-400 focus:outline-none"
              />
              <input
                type="password"
                placeholder="Password"
                value={newUser.password}
                onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-red-400 focus:outline-none"
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-red-400 focus:outline-none"
              >
                <option value="player">Player</option>
                <option value="coach">Coach</option>
                <option value="parent">Parent</option>
                <option value="club">Club Admin</option>
                <option value="admin">System Admin</option>
              </select>
              {newUser.role === 'player' && (
                <>
                  <input
                    type="number"
                    placeholder="Age"
                    value={newUser.age}
                    onChange={(e) => setNewUser({...newUser, age: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-red-400 focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Position"
                    value={newUser.position}
                    onChange={(e) => setNewUser({...newUser, position: e.target.value})}
                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-red-400 focus:outline-none"
                  />
                </>
              )}
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreateUser}
                className="flex-1 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition"
              >
                Create User
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color }) => {
  const colors = {
    blue: 'from-blue-500 to-cyan-500',
    green: 'from-green-500 to-emerald-500',
    orange: 'from-orange-500 to-red-500',
    purple: 'from-purple-500 to-pink-500',
    red: 'from-red-500 to-rose-500'
  };

  return (
    <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-red-400/20">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors[color]} flex items-center justify-center mb-3`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <p className="text-gray-400 text-sm mb-1">{label}</p>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  );
};

export default SystemAdminPortal;