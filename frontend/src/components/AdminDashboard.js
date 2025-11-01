import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userAssessments, setUserAssessments] = useState([]);
  const [userPrograms, setUserPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAllUsers();
  }, []);

  const loadAllUsers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setError('Not authenticated. Please log in as admin.');
        setLoading(false);
        return;
      }

      const response = await axios.get(`${API}/auth/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setUsers(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading users:', err);
      setError(err.response?.data?.detail || 'Failed to load users. Admin access required.');
    } finally {
      setLoading(false);
    }
  };

  const loadUserDetails = async (user) => {
    try {
      setSelectedUser(user);
      const token = localStorage.getItem('access_token');

      // Load user's assessments
      const assessmentsRes = await axios.get(
        `${API}/auth/admin/user/${user.id}/assessments`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      setUserAssessments(assessmentsRes.data);

      // Load user's programs
      const programsRes = await axios.get(
        `${API}/auth/admin/user/${user.id}/programs`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      setUserPrograms(programsRes.data);

    } catch (err) {
      console.error('Error loading user details:', err);
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-500';
      case 'coach': return 'bg-blue-500';
      case 'player': return 'bg-green-500';
      case 'parent': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <Card className="border-red-200">
          <CardContent className="p-6">
            <h3 className="text-xl font-bold text-red-600 mb-2">Access Denied</h3>
            <p className="text-gray-600">{error}</p>
            <p className="text-sm text-gray-500 mt-4">
              Please log in with an admin account to access this dashboard.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Admin Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Users List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                All Users
                <Badge variant="secondary">{users.length} total</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {users.map((user) => (
                  <div
                    key={user.id}
                    onClick={() => loadUserDetails(user)}
                    className={`p-3 rounded-lg border cursor-pointer hover:bg-gray-50 transition ${
                      selectedUser?.id === user.id ? 'bg-blue-50 border-blue-500' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-sm">{user.full_name}</div>
                        <div className="text-xs text-gray-500">@{user.username}</div>
                        {user.position && (
                          <div className="text-xs text-gray-600 mt-1">
                            {user.position} • Age {user.age}
                          </div>
                        )}
                      </div>
                      <Badge className={`${getRoleBadgeColor(user.role)} text-white text-xs`}>
                        {user.role}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* User Details */}
        <div className="lg:col-span-2">
          {!selectedUser ? (
            <Card>
              <CardContent className="p-12 text-center">
                <p className="text-gray-500">Select a user to view their details</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {/* User Info Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    {selectedUser.full_name}
                    <Badge className={`${getRoleBadgeColor(selectedUser.role)} text-white`}>
                      {selectedUser.role}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">Username</div>
                      <div className="font-medium">{selectedUser.username}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Email</div>
                      <div className="font-medium">{selectedUser.email}</div>
                    </div>
                    {selectedUser.position && (
                      <>
                        <div>
                          <div className="text-sm text-gray-500">Position</div>
                          <div className="font-medium">{selectedUser.position}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-500">Age</div>
                          <div className="font-medium">{selectedUser.age} years</div>
                        </div>
                      </>
                    )}
                    <div>
                      <div className="text-sm text-gray-500">Created</div>
                      <div className="font-medium">
                        {new Date(selectedUser.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Status</div>
                      <Badge variant={selectedUser.is_active ? "success" : "secondary"}>
                        {selectedUser.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Assessments Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    Assessments
                    <Badge variant="secondary">{userAssessments.length} total</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {userAssessments.length === 0 ? (
                    <p className="text-gray-500 text-sm">No assessments yet</p>
                  ) : (
                    <div className="space-y-3">
                      {userAssessments.slice(0, 5).map((assessment, idx) => (
                        <div key={assessment.id || idx} className="p-3 border rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium text-sm">{assessment.player_name}</div>
                              <div className="text-xs text-gray-500">
                                {assessment.position} • Age {assessment.age}
                              </div>
                            </div>
                            <Badge>Score: {assessment.overall_score || 'N/A'}</Badge>
                          </div>
                          <div className="mt-2 text-xs text-gray-600 grid grid-cols-2 gap-2">
                            <div>Sprint: {assessment.sprint_30m}s</div>
                            <div>Shooting: {assessment.shooting_accuracy}%</div>
                            <div>Passing: {assessment.passing_accuracy}%</div>
                            <div>Ball Control: {assessment.ball_control}/10</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Training Programs Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    Training Programs
                    <Badge variant="secondary">{userPrograms.length} total</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {userPrograms.length === 0 ? (
                    <p className="text-gray-500 text-sm">No training programs yet</p>
                  ) : (
                    <div className="space-y-3">
                      {userPrograms.map((program, idx) => (
                        <div key={program.id || idx} className="p-3 border rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium text-sm">{program.program_name}</div>
                              <div className="text-xs text-gray-500">
                                {program.total_duration_weeks} weeks
                              </div>
                            </div>
                            <Badge variant="success">Active</Badge>
                          </div>
                          <div className="mt-2 text-xs text-gray-600">
                            <div>Phases: {program.macro_cycles?.length || 0}</div>
                            <div className="mt-1">
                              Objectives: {program.program_objectives?.slice(0, 2).join(', ')}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
