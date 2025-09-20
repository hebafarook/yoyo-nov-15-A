import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { 
  Activity, Heart, Ruler, Scale, Target, 
  TrendingUp, Calendar, Clock, Droplets,
  Apple, Moon, Zap, AlertCircle, CheckCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

const PhysicalPerformanceMonitor = ({ playerData }) => {
  const [bodyMetrics, setBodyMetrics] = useState({
    weight: playerData?.weight || 70,
    height: playerData?.height || 175,
    body_fat: playerData?.body_fat || 12,
    muscle_mass: 0,
    bmi: 0,
    body_water: 0,
    metabolic_age: 0
  });

  const [fitnessGoals, setFitnessGoals] = useState([
    { id: 1, category: 'Speed', target: 'Sub 4.0s 30m Sprint', current: '4.2s', progress: 85, deadline: '2024-03-01' },
    { id: 2, category: 'Endurance', target: '2000m Yo-Yo Test', current: '1800m', progress: 90, deadline: '2024-02-15' },
    { id: 3, category: 'Strength', target: '65cm Vertical Jump', current: '58cm', progress: 75, deadline: '2024-03-15' },
    { id: 4, category: 'Body Comp', target: '10% Body Fat', current: '12%', progress: 60, deadline: '2024-04-01' }
  ]);

  const [recoveryData, setRecoveryData] = useState({
    sleep_hours: 8.5,
    resting_heart_rate: 52,
    hrv_score: 45,
    stress_level: 3,
    hydration_level: 85,
    nutrition_score: 78
  });

  const [performanceHistory, setPerformanceHistory] = useState([]);

  useEffect(() => {
    if (playerData) {
      calculateDerivedMetrics();
      generatePerformanceHistory();
    }
  }, [bodyMetrics, playerData]);

  const calculateDerivedMetrics = () => {
    const height_m = bodyMetrics.height / 100;
    const bmi = bodyMetrics.weight / (height_m * height_m);
    const muscle_mass = bodyMetrics.weight * (1 - bodyMetrics.body_fat / 100) * 0.7; // Rough estimation
    const body_water = bodyMetrics.weight * 0.65; // Average body water percentage
    const metabolic_age = Math.max(15, Math.min(50, 20 + (bodyMetrics.body_fat - 10) * 2)); // Simplified calculation

    setBodyMetrics(prev => ({
      ...prev,
      bmi: Math.round(bmi * 10) / 10,
      muscle_mass: Math.round(muscle_mass * 10) / 10,
      body_water: Math.round(body_water * 10) / 10,
      metabolic_age: Math.round(metabolic_age)
    }));
  };

  const generatePerformanceHistory = () => {
    const history = [
      { date: '2024-01-01', weight: 72, body_fat: 14, vo2_max: 55, rhr: 55 },
      { date: '2024-01-08', weight: 71.5, body_fat: 13.5, vo2_max: 56, rhr: 54 },
      { date: '2024-01-15', weight: 71, body_fat: 13, vo2_max: 57, rhr: 53 },
      { date: '2024-01-22', weight: 70.5, body_fat: 12.5, vo2_max: 58, rhr: 52 },
      { date: '2024-01-29', weight: 70, body_fat: 12, vo2_max: 58.5, rhr: 52 }
    ];
    setPerformanceHistory(history);
  };

  const updateBodyMetric = (metric, value) => {
    setBodyMetrics(prev => ({
      ...prev,
      [metric]: parseFloat(value) || 0
    }));
  };

  const getBMICategory = (bmi) => {
    if (bmi < 18.5) return { category: 'Underweight', color: 'text-blue-600' };
    if (bmi < 25) return { category: 'Normal', color: 'text-green-600' };
    if (bmi < 30) return { category: 'Overweight', color: 'text-yellow-600' };
    return { category: 'Obese', color: 'text-red-600' };
  };

  const getProgressColor = (progress) => {
    if (progress >= 90) return 'bg-green-500';
    if (progress >= 70) return 'bg-yellow-500';
    if (progress >= 50) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getRecoveryStatus = (score) => {
    if (score >= 80) return { status: 'Excellent', color: 'text-green-600', icon: CheckCircle };
    if (score >= 60) return { status: 'Good', color: 'text-yellow-600', icon: CheckCircle };
    return { status: 'Needs Attention', color: 'text-red-600', icon: AlertCircle };
  };

  if (!playerData) {
    return (
      <Card className="professional-card text-center p-12">
        <CardContent>
          <Activity className="w-16 h-16 mx-auto mb-4 text-[--text-muted]" />
          <h3 className="text-2xl font-semibold mb-2">Physical Performance Monitor</h3>
          <p className="text-[--text-muted]">Complete an assessment to access comprehensive fitness tracking and body composition analysis.</p>
        </CardContent>
      </Card>
    );
  }

  const bmiInfo = getBMICategory(bodyMetrics.bmi);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-[--text-navy]">Physical Performance Monitor</h2>
        <p className="text-[--text-gray]">Comprehensive fitness tracking and body composition analysis</p>
      </div>

      {/* Body Composition Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="professional-card">
          <CardContent className="p-4 text-center">
            <Scale className="w-8 h-8 mx-auto text-blue-600 mb-2" />
            <div className="text-2xl font-bold text-[--text-navy]">{bodyMetrics.weight} kg</div>
            <div className="text-sm text-[--text-gray]">Weight</div>
            <Input
              type="number"
              step="0.1"
              value={bodyMetrics.weight}
              onChange={(e) => updateBodyMetric('weight', e.target.value)}
              className="mt-2 text-center"
            />
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardContent className="p-4 text-center">
            <Ruler className="w-8 h-8 mx-auto text-green-600 mb-2" />
            <div className="text-2xl font-bold text-[--text-navy]">{bodyMetrics.height} cm</div>
            <div className="text-sm text-[--text-gray]">Height</div>
            <Input
              type="number"
              value={bodyMetrics.height}
              onChange={(e) => updateBodyMetric('height', e.target.value)}
              className="mt-2 text-center"
            />
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardContent className="p-4 text-center">
            <Target className="w-8 h-8 mx-auto text-orange-600 mb-2" />
            <div className="text-2xl font-bold text-[--text-navy]">{bodyMetrics.body_fat}%</div>
            <div className="text-sm text-[--text-gray]">Body Fat</div>
            <Input
              type="number"
              step="0.1"
              value={bodyMetrics.body_fat}
              onChange={(e) => updateBodyMetric('body_fat', e.target.value)}
              className="mt-2 text-center"
            />
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardContent className="p-4 text-center">
            <Activity className="w-8 h-8 mx-auto text-purple-600 mb-2" />
            <div className="text-2xl font-bold text-[--text-navy]">{bodyMetrics.bmi}</div>
            <div className={`text-sm ${bmiInfo.color}`}>{bmiInfo.category}</div>
            <div className="text-xs text-[--text-gray] mt-1">BMI</div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="professional-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Body Composition
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Muscle Mass</span>
              <span className="font-semibold">{bodyMetrics.muscle_mass} kg</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Body Water</span>
              <span className="font-semibold">{bodyMetrics.body_water} kg</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Metabolic Age</span>
              <span className="font-semibold">{bodyMetrics.metabolic_age} years</span>
            </div>
            <div className="pt-2">
              <Label>Fat Distribution:</Label>
              <Progress value={75} className="mt-2" />
              <div className="text-xs text-[--text-gray] mt-1">Optimal for athletic performance</div>
            </div>
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="w-5 h-5" />
              Recovery Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Sleep Quality</span>
              <div className="flex items-center gap-2">
                <Moon className="w-4 h-4" />
                <span className="font-semibold">{recoveryData.sleep_hours}h</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Resting HR</span>
              <span className="font-semibold">{recoveryData.resting_heart_rate} bpm</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">HRV Score</span>
              <span className="font-semibold">{recoveryData.hrv_score}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Hydration</span>
              <div className="flex items-center gap-2">
                <Droplets className="w-4 h-4" />
                <span className="font-semibold">{recoveryData.hydration_level}%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Apple className="w-5 h-5" />
              Nutrition & Wellness
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Nutrition Score</span>
              <span className="font-semibold">{recoveryData.nutrition_score}/100</span>
            </div>
            <Progress value={recoveryData.nutrition_score} className="mt-2" />
            
            <div className="flex justify-between items-center">
              <span className="text-[--text-gray]">Stress Level</span>
              <Badge className={recoveryData.stress_level <= 3 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                {recoveryData.stress_level}/10
              </Badge>
            </div>
            
            <div className="pt-2">
              <Button variant="outline" size="sm" className="w-full">
                <Apple className="w-4 h-4 mr-2" />
                Update Nutrition Plan
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fitness Goals */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Fitness Goals Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {fitnessGoals.map((goal) => (
              <div key={goal.id} className="border border-[--border-elegant] rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-semibold">{goal.category}: {goal.target}</h4>
                    <p className="text-sm text-[--text-gray]">Current: {goal.current}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-[--text-gray]">
                      Due: {new Date(goal.deadline).toLocaleDateString()}
                    </div>
                    <Badge className="mt-1">
                      {goal.progress}%
                    </Badge>
                  </div>
                </div>
                <Progress value={goal.progress} className={`h-2 ${getProgressColor(goal.progress)}`} />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance History Chart */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Physical Performance Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <Legend />
                <Line 
                  yAxisId="left" 
                  type="monotone" 
                  dataKey="weight" 
                  stroke="#3B82F6" 
                  strokeWidth={2} 
                  name="Weight (kg)" 
                />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="body_fat" 
                  stroke="#F59E0B" 
                  strokeWidth={2} 
                  name="Body Fat %" 
                />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="vo2_max" 
                  stroke="#10B981" 
                  strokeWidth={2} 
                  name="VO2 Max" 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Recovery Analysis */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Recovery Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold">Sleep Quality Insights</h4>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <Moon className="w-5 h-5 text-blue-600" />
                  <span className="font-medium">Sleep Score: 85/100</span>
                </div>
                <p className="text-sm text-[--text-gray]">
                  Excellent sleep duration. Consider maintaining consistent sleep schedule for optimal recovery.
                </p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <Heart className="w-5 h-5 text-green-600" />
                  <span className="font-medium">Heart Rate Variability: Good</span>
                </div>
                <p className="text-sm text-[--text-gray]">
                  HRV indicates good recovery capacity. Ready for high-intensity training.
                </p>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold">Recommendations</h4>
              <div className="space-y-2">
                <div className="flex items-start gap-3 p-3 bg-[--light-bg] rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <div className="font-medium text-sm">Maintain current nutrition plan</div>
                    <div className="text-xs text-[--text-gray]">78% nutrition score is excellent</div>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 bg-[--light-bg] rounded-lg">
                  <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                  <div>
                    <div className="font-medium text-sm">Increase hydration</div>
                    <div className="text-xs text-[--text-gray]">Aim for 2.5L daily water intake</div>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 bg-[--light-bg] rounded-lg">
                  <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-medium text-sm">Continue current training load</div>
                    <div className="text-xs text-[--text-gray]">Recovery metrics support current intensity</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PhysicalPerformanceMonitor;