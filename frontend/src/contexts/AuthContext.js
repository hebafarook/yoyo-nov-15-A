import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Set up axios interceptor for authentication
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.request.eject(interceptor);
    };
  }, [token]);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/profile`);
          setUser(response.data.user);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Token verification failed:', error);
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password
      });

      const { access_token, user } = response.data;
      
      setToken(access_token);
      setUser(user);
      setIsAuthenticated(true);
      localStorage.setItem('auth_token', access_token);
      
      return { success: true, user };
    } catch (error) {
      console.error('Login failed:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      
      const { access_token, user } = response.data;
      
      setToken(access_token);
      setUser(user);
      setIsAuthenticated(true);
      localStorage.setItem('auth_token', access_token);
      
      return { success: true, user };
    } catch (error) {
      console.error('Registration failed:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      };
    }
  };

  const logout = () => {
    console.log('AuthContext logout called');
    try {
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('token');
      console.log('Tokens cleared, redirecting to homepage');
      // Reload to clear all state
      window.location.href = '/';
    } catch (error) {
      console.error('Error in logout function:', error);
    }
  };

  const saveReport = async (reportData) => {
    try {
      const response = await axios.post(`${API}/auth/save-report`, reportData);
      return { success: true, report: response.data };
    } catch (error) {
      console.error('Failed to save report:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to save report'
      };
    }
  };

  const getSavedReports = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/auth/saved-reports`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return { success: true, reports: response.data };
    } catch (error) {
      console.error('Failed to fetch saved reports:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch saved reports'
      };
    }
  };

  const deleteSavedReport = async (reportId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/auth/saved-reports/${reportId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return { success: true };
    } catch (error) {
      console.error('Failed to delete report:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to delete report'
      };
    }
  };

  const saveBenchmark = async (benchmarkData) => {
    try {
      const response = await axios.post(`${API}/auth/save-benchmark`, benchmarkData);
      return { success: true, benchmark: response.data };
    } catch (error) {
      console.error('Failed to save benchmark:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to save benchmark'
      };
    }
  };

  const getBenchmarks = async (playerName = null) => {
    try {
      const params = playerName ? { player_name: playerName } : {};
      const response = await axios.get(`${API}/auth/benchmarks`, { params });
      return { success: true, benchmarks: response.data };
    } catch (error) {
      console.error('Failed to fetch benchmarks:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch benchmarks'
      };
    }
  };

  const getPlayerProgress = async (playerName) => {
    try {
      const response = await axios.get(`${API}/auth/benchmarks/progress/${playerName}`);
      return { success: true, progress: response.data };
    } catch (error) {
      console.error('Failed to fetch player progress:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to fetch player progress'
      };
    }
  };

  const deleteBenchmark = async (benchmarkId) => {
    try {
      await axios.delete(`${API}/auth/benchmarks/${benchmarkId}`);
      return { success: true };
    } catch (error) {
      console.error('Failed to delete benchmark:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to delete benchmark'
      };
    }
  };

  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    saveReport,
    getSavedReports,
    deleteSavedReport,
    saveBenchmark,
    getBenchmarks,
    getPlayerProgress,
    deleteBenchmark
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};