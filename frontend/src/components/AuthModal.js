import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { UserPlus, LogIn, X, Eye, EyeOff, Shield, Users, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const AuthModal = ({ isOpen, onClose, defaultMode = 'login', onForgotPassword }) => {
  const { t } = useTranslation();
  const [mode, setMode] = useState(defaultMode);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('portal'); // 'portal' or 'form'
  const [selectedPortal, setSelectedPortal] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    role: 'parent',
    age: '',
    position: '',
    gender: 'male',
    height: '',
    height_feet: '',
    height_inches: '',
    weight: '',
    height_unit: 'metric',
    weight_unit: 'metric',
    dominant_foot: 'Right',
    current_injuries: '',
    parent_email: '',
    coach_email: '',
    is_coach: false
  });

  const { login, register } = useAuth();
  
  const portals = [
    {
      id: 'player',
      name: 'Player Portal',
      icon: <User className="w-8 h-8" />,
      color: 'blue',
      bgColor: 'bg-blue-500',
      hoverBg: 'hover:bg-blue-50',
      description: 'For players to track their training and performance'
    },
    {
      id: 'coach',
      name: 'Coach Portal',
      icon: <Users className="w-8 h-8" />,
      color: 'green',
      bgColor: 'bg-green-500',
      hoverBg: 'hover:bg-green-50',
      description: 'For coaches to manage teams and assess players'
    },
    {
      id: 'parent',
      name: 'Parent Portal',
      icon: <Shield className="w-8 h-8" />,
      color: 'purple',
      bgColor: 'bg-purple-500',
      hoverBg: 'hover:bg-purple-50',
      description: 'For parents to monitor their child\'s progress'
    },
    {
      id: 'club',
      name: 'Club Portal',
      icon: <Shield className="w-8 h-8" />,
      color: 'orange',
      bgColor: 'bg-orange-500',
      hoverBg: 'hover:bg-orange-50',
      description: 'For club administrators to manage teams, staff, and performance'
    },
    {
      id: 'admin',
      name: 'System Admin',
      icon: <Shield className="w-8 h-8" />,
      color: 'red',
      bgColor: 'bg-red-600',
      hoverBg: 'hover:bg-red-50',
      description: 'For system administrators to manage all users and system'
    }
  ];
  
  const handlePortalSelect = (portalId) => {
    setSelectedPortal(portalId);
    setFormData(prev => ({
      ...prev,
      role: portalId,
      is_coach: portalId === 'coach'
    }));
    setStep('form');
  };

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
          // Check required fields based on unit system
          if (!formData.age || !formData.position || !formData.weight) {
            setError('Age, position, height, and weight are required for player accounts');
            setLoading(false);
            return;
          }
          
          // Validate height based on unit system
          if (formData.height_unit === 'metric') {
            if (!formData.height) {
              setError('Height is required');
              setLoading(false);
              return;
            }
          } else {
            if (!formData.height_feet || !formData.height_inches) {
              setError('Both feet and inches are required for height');
              setLoading(false);
              return;
            }
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
          registrationData.gender = formData.gender;
          
          // Format height based on unit preference
          if (formData.height_unit === 'metric') {
            registrationData.height = `${formData.height}cm`;
          } else {
            registrationData.height = `${formData.height}"`; // Store as inches for imperial
          }
          
          // Format weight based on unit preference
          if (formData.weight_unit === 'metric') {
            registrationData.weight = `${formData.weight}kg`;
          } else {
            registrationData.weight = `${formData.weight}lbs`;
          }
          
          registrationData.dominant_foot = formData.dominant_foot;
          registrationData.current_injuries = formData.current_injuries || 'None';
          registrationData.parent_email = formData.parent_email;
          registrationData.coach_email = formData.coach_email;
          registrationData.height_unit = formData.height_unit;
          registrationData.weight_unit = formData.weight_unit;
        }

        const result = await register(registrationData);

        if (result.success) {
          // Auto-login after successful registration
          const loginResult = await login(formData.email, formData.password);
          
          if (loginResult.success) {
            // Show success message
            alert(`✅ Account created successfully! Welcome, ${formData.full_name}! Redirecting to your dashboard...`);
            onClose();
            // Page will auto-redirect based on user role
          } else {
            // Registration successful but auto-login failed - show login form
            setMode('login');
            setError('Account created! Please log in to continue.');
          }
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

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError('');
    setStep('portal'); // Reset to portal selection
    setSelectedPortal(null);
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
  
  const handleBack = () => {
    setStep('portal');
    setSelectedPortal(null);
    setError('');
  };
  
  const handleClose = () => {
    // Reset to portal selection when closing
    setStep('portal');
    setSelectedPortal(null);
    setError('');
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
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className="min-h-screen flex items-center justify-center py-8">
        <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto my-8">
        <CardHeader className="relative">
          <button
            onClick={handleClose}
            className="absolute right-4 top-4 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
          {step === 'portal' ? (
            <CardTitle className="text-center">
              {mode === 'login' ? 'Login to Your Portal' : 'Choose Your Portal'}
            </CardTitle>
          ) : (
            <CardTitle className="flex items-center gap-2">
              <button
                onClick={handleBack}
                className="text-gray-400 hover:text-gray-600 mr-2"
              >
                ←
              </button>
              {mode === 'login' ? (
                <>
                  <LogIn className="w-5 h-5" />
                  Login to {selectedPortal === 'player' ? 'Player' : selectedPortal === 'coach' ? 'Coach' : 'Parent'} Portal
                </>
              ) : (
                <>
                  <UserPlus className="w-5 h-5" />
                  Register for {selectedPortal === 'player' ? 'Player' : selectedPortal === 'coach' ? 'Coach' : 'Parent'} Portal
                </>
              )}
            </CardTitle>
          )}
        </CardHeader>
        
        <CardContent>
          {step === 'portal' ? (
            /* Portal Selection Step */
            <div className="space-y-4">
              <p className="text-center text-gray-600 mb-6">
                Select your portal to continue
              </p>
              {portals.map((portal) => (
                <button
                  key={portal.id}
                  onClick={() => handlePortalSelect(portal.id)}
                  className={`w-full p-4 border-2 border-gray-200 rounded-lg ${portal.hoverBg} transition-all hover:border-${portal.color}-500 hover:shadow-md text-left`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`${portal.bgColor} text-white p-3 rounded-lg`}>
                      {portal.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-lg">{portal.name}</h3>
                      <p className="text-sm text-gray-600">{portal.description}</p>
                    </div>
                  </div>
                </button>
              ))}
              
              <div className="text-center pt-4 border-t">
                <button
                  onClick={switchMode}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  {mode === 'login' ? "Don't have an account? Register" : "Already have an account? Login"}
                </button>
              </div>
            </div>
          ) : (
            /* Form Step */
          <>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}

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

                {/* Role is pre-selected from portal choice, so hiding this field */}
                <input type="hidden" name="role" value={formData.role} />
                
                {false && (
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
                )}

                {/* Player-specific fields */}
                {formData.role === 'player' && (
                  <>
                    <div className="bg-blue-50 border border-blue-200 p-3 rounded-md text-sm text-blue-800 mb-3">
                      <strong>Complete Your Player Profile</strong> - This information helps us create personalized training programs for you.
                    </div>

                    {/* Basic Info Grid */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="age">Age *</Label>
                        <Input
                          id="age"
                          name="age"
                          type="number"
                          required
                          min="10"
                          max="30"
                          value={formData.age}
                          onChange={handleInputChange}
                          placeholder="Age"
                        />
                      </div>
                      <div>
                        <Label htmlFor="gender">Gender *</Label>
                        <Select value={formData.gender} onValueChange={(value) => setFormData(prev => ({...prev, gender: value}))}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="male">Male</SelectItem>
                            <SelectItem value="female">Female</SelectItem>
                            <SelectItem value="other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Measurement Unit Preference */}
                    <div className="bg-gray-50 border border-gray-300 p-3 rounded-lg">
                      <Label className="text-sm font-semibold text-gray-700 mb-2 block">Measurement Standard *</Label>
                      <p className="text-xs text-gray-600 mb-3">Choose your preferred measurement system</p>
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          type="button"
                          onClick={() => setFormData(prev => ({...prev, height_unit: 'metric', weight_unit: 'metric'}))}
                          className={`p-3 border-2 rounded-lg transition-all text-sm font-medium ${
                            formData.height_unit === 'metric'
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                          }`}
                        >
                          <div className="font-bold">Metric</div>
                          <div className="text-xs">cm • kg</div>
                        </button>
                        <button
                          type="button"
                          onClick={() => setFormData(prev => ({...prev, height_unit: 'imperial', weight_unit: 'imperial'}))}
                          className={`p-3 border-2 rounded-lg transition-all text-sm font-medium ${
                            formData.height_unit === 'imperial'
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                          }`}
                        >
                          <div className="font-bold">Imperial</div>
                          <div className="text-xs">in • lbs</div>
                        </button>
                      </div>
                    </div>

                    {/* Height Input - Different for Metric vs Imperial */}
                    {formData.height_unit === 'metric' ? (
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label htmlFor="height">Height (cm) *</Label>
                          <Input
                            id="height"
                            name="height"
                            type="number"
                            required
                            min="140"
                            max="210"
                            value={formData.height}
                            onChange={handleInputChange}
                            placeholder="e.g., 175"
                          />
                          <p className="text-xs text-gray-500 mt-1">Centimeters</p>
                        </div>
                        <div>
                          <Label htmlFor="weight">Weight (kg) *</Label>
                          <Input
                            id="weight"
                            name="weight"
                            type="number"
                            required
                            min="40"
                            max="120"
                            value={formData.weight}
                            onChange={handleInputChange}
                            placeholder="e.g., 68"
                          />
                          <p className="text-xs text-gray-500 mt-1">Kilograms</p>
                        </div>
                      </div>
                    ) : (
                      <div className="grid grid-cols-2 gap-3">
                        {/* Imperial Height - Feet and Inches */}
                        <div>
                          <Label>Height *</Label>
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <Input
                                id="height_feet"
                                name="height_feet"
                                type="number"
                                required
                                min="4"
                                max="7"
                                value={formData.height_feet}
                                onChange={handleInputChange}
                                placeholder="Feet"
                              />
                              <p className="text-xs text-gray-500 mt-1">Feet</p>
                            </div>
                            <div>
                              <Input
                                id="height_inches"
                                name="height_inches"
                                type="number"
                                required
                                min="0"
                                max="11"
                                value={formData.height_inches}
                                onChange={handleInputChange}
                                placeholder="Inches"
                              />
                              <p className="text-xs text-gray-500 mt-1">Inches</p>
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">e.g., 5 ft 9 in</p>
                        </div>
                        <div>
                          <Label htmlFor="weight">Weight (lbs) *</Label>
                          <Input
                            id="weight"
                            name="weight"
                            type="number"
                            required
                            min="88"
                            max="265"
                            value={formData.weight}
                            onChange={handleInputChange}
                            placeholder="e.g., 150"
                          />
                          <p className="text-xs text-gray-500 mt-1">Pounds</p>
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-3">
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
                      <div>
                        <Label htmlFor="dominant_foot">Dominant Foot *</Label>
                        <Select value={formData.dominant_foot} onValueChange={(value) => setFormData(prev => ({...prev, dominant_foot: value}))}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Right">Right</SelectItem>
                            <SelectItem value="Left">Left</SelectItem>
                            <SelectItem value="Both">Both</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Injury Information */}
                    <div>
                      <Label htmlFor="current_injuries">Current Injuries or Medical Concerns (Optional)</Label>
                      <Input
                        id="current_injuries"
                        name="current_injuries"
                        type="text"
                        value={formData.current_injuries}
                        onChange={handleInputChange}
                        placeholder="e.g., Ankle sprain, knee pain, or None"
                      />
                      <p className="text-xs text-gray-500 mt-1">Help us create a safe training plan for you</p>
                    </div>

                    {/* Parent/Guardian Information */}
                    <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg space-y-3">
                      <h4 className="font-semibold text-purple-900 text-sm">Parent/Guardian Connection</h4>
                      <div>
                        <Label htmlFor="parent_email">Parent/Guardian Email (Optional)</Label>
                        <Input
                          id="parent_email"
                          name="parent_email"
                          type="email"
                          value={formData.parent_email}
                          onChange={handleInputChange}
                          placeholder="parent@email.com"
                        />
                        <p className="text-xs text-gray-600 mt-1">We'll send them an invitation to view your progress</p>
                      </div>
                    </div>

                    {/* Coach Information */}
                    <div className="bg-green-50 border border-green-200 p-4 rounded-lg space-y-3">
                      <h4 className="font-semibold text-green-900 text-sm">Coach Connection</h4>
                      <div>
                        <Label htmlFor="coach_email">Coach Email (Optional)</Label>
                        <Input
                          id="coach_email"
                          name="coach_email"
                          type="email"
                          value={formData.coach_email}
                          onChange={handleInputChange}
                          placeholder="coach@email.com"
                        />
                        <p className="text-xs text-gray-600 mt-1">Connect with your coach for personalized feedback</p>
                      </div>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-md text-xs text-yellow-800">
                      <strong>Next Step:</strong> After registration, you'll complete your first assessment to create your personalized training program!
                    </div>
                  </>
                )}
              </>
            )}

            {mode === 'login' && (
              <div className="text-right">
                <button
                  type="button"
                  onClick={() => {
                    onClose();
                    if (onForgotPassword) onForgotPassword();
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Forgot Password?
                </button>
              </div>
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
          </>
          )}
        </CardContent>
      </Card>
      </div>
    </div>
  );
};

export default AuthModal;
