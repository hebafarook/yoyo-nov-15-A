import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Trophy, Star, Award, Target, Zap, Crown, Medal, Shield, Flame } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AchievementsDisplay = ({ user }) => {
  const [achievements, setAchievements] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadAchievements();
    }
  }, [user]);

  const loadAchievements = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      // Load user's benchmarks and assessments
      const benchmarksRes = await axios.get(`${API}/auth/benchmarks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const benchmarks = benchmarksRes.data || [];
      
      // Calculate achievements based on data
      const earnedAchievements = calculateAchievements(benchmarks, user);
      setAchievements(earnedAchievements);

      // Calculate stats
      const userStats = calculateStats(benchmarks);
      setStats(userStats);

    } catch (error) {
      console.error('Error loading achievements:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateAchievements = (benchmarks, userData) => {
    const earned = [];

    // Achievement 1: First Assessment
    if (benchmarks.length >= 1) {
      earned.push({
        id: 'first_assessment',
        name: 'First Steps',
        description: 'Completed your first assessment',
        icon: Star,
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-50',
        earned: true,
        earnedDate: benchmarks[0]?.benchmark_date
      });
    }

    // Achievement 2: Consistent Progress (2+ assessments)
    if (benchmarks.length >= 2) {
      earned.push({
        id: 'consistent_progress',
        name: 'Consistency is Key',
        description: 'Completed 2 or more assessments',
        icon: Target,
        color: 'text-blue-500',
        bgColor: 'bg-blue-50',
        earned: true,
        earnedDate: benchmarks[1]?.benchmark_date
      });
    }

    // Achievement 3: Milestone Master (3+ assessments)
    if (benchmarks.length >= 3) {
      earned.push({
        id: 'milestone_master',
        name: 'Milestone Master',
        description: 'Reached 3 milestone assessments',
        icon: Medal,
        color: 'text-purple-500',
        bgColor: 'bg-purple-50',
        earned: true,
        earnedDate: benchmarks[2]?.benchmark_date
      });
    }

    // Achievement 4: High Performer (Score > 70)
    const hasHighScore = benchmarks.some(b => b.overall_score >= 70);
    if (hasHighScore) {
      earned.push({
        id: 'high_performer',
        name: 'High Performer',
        description: 'Achieved overall score above 70',
        icon: Flame,
        color: 'text-orange-500',
        bgColor: 'bg-orange-50',
        earned: true,
        earnedDate: benchmarks.find(b => b.overall_score >= 70)?.benchmark_date
      });
    }

    // Achievement 5: Elite Status (Score > 80)
    const hasEliteScore = benchmarks.some(b => b.overall_score >= 80);
    if (hasEliteScore) {
      earned.push({
        id: 'elite_status',
        name: 'Elite Status',
        description: 'Reached elite level with score above 80',
        icon: Crown,
        color: 'text-red-500',
        bgColor: 'bg-red-50',
        earned: true,
        earnedDate: benchmarks.find(b => b.overall_score >= 80)?.benchmark_date
      });
    }

    // Achievement 6: Speed Demon (sprint_30m < 4.2)
    const hasGoodSpeed = benchmarks.some(b => b.sprint_30m && b.sprint_30m < 4.2);
    if (hasGoodSpeed) {
      earned.push({
        id: 'speed_demon',
        name: 'Speed Demon',
        description: 'Sprint 30m under 4.2 seconds',
        icon: Zap,
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50',
        earned: true,
        earnedDate: benchmarks.find(b => b.sprint_30m < 4.2)?.benchmark_date
      });
    }

    // Achievement 7: Technical Master (Technical skills > 7)
    const hasTechnicalSkills = benchmarks.some(b => 
      b.ball_control >= 7 && b.passing_accuracy >= 75
    );
    if (hasTechnicalSkills) {
      earned.push({
        id: 'technical_master',
        name: 'Technical Master',
        description: 'Ball control & passing above 7/10 and 75%',
        icon: Award,
        color: 'text-green-500',
        bgColor: 'bg-green-50',
        earned: true,
        earnedDate: benchmarks.find(b => b.ball_control >= 7)?.benchmark_date
      });
    }

    // Achievement 8: Improvement Streak (show improvement between assessments)
    if (benchmarks.length >= 2) {
      const sorted = benchmarks.sort((a, b) => 
        new Date(a.benchmark_date) - new Date(b.benchmark_date)
      );
      const improved = sorted[sorted.length - 1].overall_score > sorted[0].overall_score;
      
      if (improved) {
        earned.push({
          id: 'improvement_streak',
          name: 'On The Rise',
          description: 'Improved your overall score since baseline',
          icon: TrendingUp,
          color: 'text-indigo-500',
          bgColor: 'bg-indigo-50',
          earned: true,
          earnedDate: sorted[sorted.length - 1]?.benchmark_date
        });
      }
    }

    // Achievement 9: Position Specialist
    if (userData?.position) {
      earned.push({
        id: 'position_specialist',
        name: `${userData.position} Specialist`,
        description: `Registered as ${userData.position}`,
        icon: Shield,
        color: 'text-teal-500',
        bgColor: 'bg-teal-50',
        earned: true,
        earnedDate: userData.created_at
      });
    }

    return earned;
  };

  const calculateStats = (benchmarks) => {
    if (benchmarks.length === 0) return null;

    const sorted = benchmarks.sort((a, b) => 
      new Date(a.benchmark_date) - new Date(b.benchmark_date)
    );

    const baseline = sorted[0];
    const latest = sorted[sorted.length - 1];

    return {
      totalAssessments: benchmarks.length,
      currentScore: latest.overall_score,
      improvement: latest.overall_score - baseline.overall_score,
      highestScore: Math.max(...benchmarks.map(b => b.overall_score)),
      totalAchievements: benchmarks.length // This will be replaced with actual earned count
    };
  };

  const TrendingUp = ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Your Achievements</h1>
        <p className="text-gray-600">Track your progress and celebrate your milestones</p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardContent className="p-6 text-center">
              <Trophy className="w-8 h-8 mx-auto mb-2 text-yellow-500" />
              <div className="text-2xl font-bold">{achievements.length}</div>
              <div className="text-sm text-gray-600">Achievements</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <Target className="w-8 h-8 mx-auto mb-2 text-blue-500" />
              <div className="text-2xl font-bold">{stats.totalAssessments}</div>
              <div className="text-sm text-gray-600">Assessments</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <Star className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <div className="text-2xl font-bold">{stats.currentScore}</div>
              <div className="text-sm text-gray-600">Current Score</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <Zap className="w-8 h-8 mx-auto mb-2 text-orange-500" />
              <div className="text-2xl font-bold">{stats.highestScore}</div>
              <div className="text-sm text-gray-600">Best Score</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <TrendingUp className="w-8 h-8 mx-auto mb-2 text-purple-500" />
              <div className="text-2xl font-bold">+{stats.improvement.toFixed(0)}</div>
              <div className="text-sm text-gray-600">Improvement</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Achievements Grid */}
      {achievements.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-xl font-semibold mb-2">No Achievements Yet</h3>
            <p className="text-gray-600">
              Complete assessments and improve your skills to earn achievements!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {achievements.map((achievement) => {
            const Icon = achievement.icon;
            return (
              <Card 
                key={achievement.id}
                className={`hover:shadow-lg transition-shadow ${achievement.bgColor} border-2`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-full ${achievement.bgColor}`}>
                        <Icon className={`w-6 h-6 ${achievement.color}`} />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{achievement.name}</CardTitle>
                        {achievement.earnedDate && (
                          <div className="text-xs text-gray-500 mt-1">
                            {new Date(achievement.earnedDate).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    </div>
                    {achievement.earned && (
                      <Badge className="bg-green-500 text-white">Earned</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{achievement.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Locked Achievements (Coming Soon) */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold mb-6">Upcoming Achievements</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              name: 'Perfect Score',
              description: 'Achieve an overall score of 90 or above',
              icon: Crown,
              color: 'text-gray-400'
            },
            {
              name: 'Year Veteran',
              description: 'Complete assessments for 12 months',
              icon: Medal,
              color: 'text-gray-400'
            },
            {
              name: 'All-Rounder',
              description: 'Score 7+ in all assessment categories',
              icon: Shield,
              color: 'text-gray-400'
            }
          ].map((locked, idx) => {
            const Icon = locked.icon;
            return (
              <Card key={idx} className="opacity-60 border-dashed">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-full bg-gray-100">
                      <Icon className={`w-6 h-6 ${locked.color}`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{locked.name}</CardTitle>
                      <Badge variant="secondary" className="mt-1">Locked</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{locked.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AchievementsDisplay;
