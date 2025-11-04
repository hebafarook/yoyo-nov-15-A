import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { UserPlus, LogIn, X, Eye, EyeOff, Shield, Users, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const AuthModal = ({ isOpen, onClose, defaultMode = 'login' }) => {
  const [mode, setMode] = useState(defaultMode);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    role: 'parent',
    age: '',
    position: '',
    is_coach: false
  });

  const { login, register } = useAuth();

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setError('');
  };

  const handleRoleChange = (value) => {
    setFormData(prev => ({
      ...prev,
      role: value,
      is_coach: value === 'coach'
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (mode === 'login') {
        const result = await login(formData.username, formData.password);
        if (result.success) {
          onClose();
        } else {
          setError(result.error);
        }
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }
        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          setLoading(false);
          return;
        }

        // Validate player-specific fields
        if (formData.role === 'player') {
          if (!formData.age || !formData.position) {
            setError('Age and position are required for player accounts');
            setLoading(false);
            return;
          }
        }

        const registrationData = {
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          password: formData.password,
          role: formData.role,
          is_coach: formData.is_coach
        };

        // Add player-specific fields if role is player
        if (formData.role === 'player') {
          registrationData.age = parseInt(formData.age);
          registrationData.position = formData.position;
        }

        const result = await register(registrationData);

        if (result.success) {
          onClose();
        } else {
          setError(result.error);
        }
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${BACKEND_URL}/api/auth/forgot-password?email=${encodeURIComponent(formData.email)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (response.ok) {
        setResetToken(data.reset_token || '');
        setSuccess(`Reset token generated! Token: ${data.reset_token} (Valid for ${data.expires_in})`);
        setMode('reset');
      } else {
        setError(data.detail || 'Failed to generate reset token');
      }
    } catch (err) {
      setError('Failed to request password reset');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${BACKEND_URL}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reset_token: resetToken,
          new_password: formData.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Password reset successful! You can now login with your new password.');
        setTimeout(() => {
          setMode('login');
          setSuccess('');
          setResetToken('');
        }, 2000);
      } else {
        setError(data.detail || 'Failed to reset password');
      }
    } catch (err) {
      setError('Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError('');
    setSuccess('');
    setResetToken('');
    setFormData({
      username: '',
      email: '',
      full_name: '',
      password: '',
      confirmPassword: '',
      role: 'parent',
      age: '',
      position: '',
      is_coach: false
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md">
        <CardHeader className="relative">
          <button
            onClick={onClose}
            className="absolute right-4 top-4 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
          <CardTitle className="flex items-center gap-2">
            {mode === 'login' && (
              <>
                <LogIn className="w-5 h-5" />
                Login to Your Account
              </>
            )}
            {mode === 'register' && (
              <>
                <UserPlus className="w-5 h-5" />
                Create New Account
              </>
            )}
            {mode === 'forgot' && (
              <>
                <Shield className="w-5 h-5" />
                Reset Your Password
              </>
            )}
            {mode === 'reset' && (
              <>
                <Shield className="w-5 h-5" />
                Create New Password
              </>
            )}
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={mode === 'forgot' ? handleForgotPassword : mode === 'reset' ? handleResetPassword : handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}

            {success && (
              <div className="p-3 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md">
                {success}
              </div>
            )}

            {/* Forgot Password Mode - Only Email */}
            {mode === 'forgot' && (
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="Enter your email address"
                />
                <p className="text-xs text-gray-600 mt-2">
                  Enter your email to receive a password reset token
                </p>
              </div>
            )}

            {/* Reset Password Mode - Token and New Password */}
            {mode === 'reset' && (
              <>
                <div>
                  <Label htmlFor="resetToken">Reset Token</Label>
                  <Input
                    id="resetToken"
                    type="text"
                    required
                    value={resetToken}
                    onChange={(e) => setResetToken(e.target.value)}
                    placeholder="Enter your reset token"
                  />
                </div>
                <div>
                  <Label htmlFor="password">New Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter new password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm new password"
                  />
                </div>
              </>
            )}

            {/* Login and Register Modes */}
            {(mode === 'login' || mode === 'register') && (
              <>
                <div>
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    name="username"
                    type="text"
                    required
                    value={formData.username}
                    onChange={handleInputChange}
                    placeholder="Enter your username"
                  />
                </div>

                {mode === 'register' && (
              <>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email"
                  />
                </div>

                <div>
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    name="full_name"
                    type="text"
                    required
                    value={formData.full_name}
                    onChange={handleInputChange}
                    placeholder="Enter your full name"
                  />
                </div>
              </>
            )}

            <div>
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {mode === 'register' && (
              <>
                <div>
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm your password"
                  />
                </div>

                <div>
                  <Label htmlFor="role">I am a...</Label>
                  <Select value={formData.role} onValueChange={handleRoleChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select your role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="parent">
                        <div className="flex items-center gap-2">
                          <Users className="w-4 h-4" />
                          Parent/Guardian
                        </div>
                      </SelectItem>
                      <SelectItem value="coach">
                        <div className="flex items-center gap-2">
                          <Shield className="w-4 h-4" />
                          Coach/Professional
                        </div>
                      </SelectItem>
                      <SelectItem value="player">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4" />
                          Player (Self-Assessment)
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-gray-500 mt-1">
                    {formData.role === 'coach' && 'Manage multiple players and create training programs'}
                    {formData.role === 'parent' && 'Track your child\'s performance and progress'}
                    {formData.role === 'player' && 'Create self-assessments and track your own development'}
                  </p>
                </div>

                {/* Player-specific fields */}
                {formData.role === 'player' && (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="age">Age *</Label>
                        <Input
                          id="age"
                          name="age"
                          type="number"
                          required
                          min="12"
                          max="25"
                          value={formData.age}
                          onChange={handleInputChange}
                          placeholder="Age"
                        />
                      </div>
                      <div>
                        <Label htmlFor="position">Position *</Label>
                        <Select value={formData.position} onValueChange={(value) => setFormData(prev => ({...prev, position: value}))}>
                          <SelectTrigger>
                            <SelectValue placeholder="Position" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Goalkeeper">Goalkeeper</SelectItem>
                            <SelectItem value="Defender">Defender</SelectItem>
                            <SelectItem value="Midfielder">Midfielder</SelectItem>
                            <SelectItem value="Forward">Forward</SelectItem>
                            <SelectItem value="Winger">Winger</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 p-3 rounded-md text-sm text-blue-800">
                      As a player, your assessments will be visible to your assigned coaches and parents.
                    </div>
                  </>
                )}
              </>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                'Loading...'
              ) : mode === 'login' ? (
                'Login'
              ) : (
                'Create Account'
              )}
            </Button>
          </form>

          <div className="mt-4 text-center">
            <button
              onClick={switchMode}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              {mode === 'login' ? (
                "Don't have an account? Register here"
              ) : (
                'Already have an account? Login here'
              )}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthModal;
