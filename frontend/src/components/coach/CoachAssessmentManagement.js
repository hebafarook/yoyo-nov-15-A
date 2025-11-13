import React, { useState, useEffect } from 'react';
import { Filter, Play, FileText, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const CoachAssessmentManagement = ({ onSelectAssessment }) => {
  const { user } = useAuth();
  const [filterStatus, setFilterStatus] = useState('all');
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      fetchRealAssessments();
    }
  }, [user]);

  const fetchRealAssessments = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch coach's players
      const playersRes = await axios.get(`${BACKEND_URL}/api/relationships/my-players`, { headers });
      const players = playersRes.data || [];

      // Fetch assessments for all players
      const assessmentsData = [];
      for (const playerRel of players) {
        try {
          const benchmarksRes = await axios.get(`${BACKEND_URL}/api/auth/benchmarks`, { 
            headers,
            params: { user_id: playerRel.child_id }
          });
          
          const benchmarks = benchmarksRes.data || [];
          benchmarks.forEach(benchmark => {
            const daysAgo = Math.floor((Date.now() - new Date(benchmark.saved_at)) / (1000 * 60 * 60 * 24));
            assessmentsData.push({
              id: benchmark.id,
              playerName: benchmark.player_name,
              playerId: playerRel.child_id,
              type: 'Full Performance Assessment',
              status: daysAgo < 7 ? 'Review Needed' : daysAgo < 30 ? 'Completed' : 'Archived',
              score: benchmark.overall_score ? Math.round(benchmark.overall_score) : null,
              date: new Date(benchmark.saved_at).toLocaleDateString(),
              saved_at: benchmark.saved_at,
              assessment_data: benchmark.assessment_data,
              aiSummary: generateAISummary(benchmark.assessment_data)
            });
          });
        } catch (err) {
          console.log(`No benchmarks for player ${playerRel.child_id}`);
        }
      }

      // Sort by date (newest first)
      assessmentsData.sort((a, b) => new Date(b.saved_at) - new Date(a.saved_at));
      setAssessments(assessmentsData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assessments:', error);
      setLoading(false);
    }
  };

  const generateAISummary = (data) => {
    if (!data) return 'Assessment data available';
    
    const strengths = [];
    const improvements = [];
    
    if (data.ball_control >= 4) strengths.push('excellent ball control');
    if (data.passing_accuracy >= 80) strengths.push('high passing accuracy');
    if (data.sprint_30m <= 4.3) strengths.push('good speed');
    if (data.yo_yo_test >= 1700) strengths.push('strong endurance');
    
    if (data.ball_control < 3) improvements.push('ball control');
    if (data.passing_accuracy < 65) improvements.push('passing accuracy');
    if (data.shooting_accuracy < 60) improvements.push('shooting accuracy');
    if (data.mental_toughness < 3) improvements.push('mental strength');
    
    let summary = '';
    if (strengths.length > 0) summary += `Strengths: ${strengths.join(', ')}. `;
    if (improvements.length > 0) summary += `Focus areas: ${improvements.join(', ')}.`;
    
    return summary || 'Balanced performance across all areas';
  };

  // REMOVED MOCK DATA - Now using real data from database
  const mockAssessments_REMOVED = [
    {
      id: 1,
      playerName: 'Marcus Silva',
      type: 'Full Technical Assessment',
      status: 'Review Needed',
      score: 92,
      date: '2024-03-15',
      videoUrl: '#',
      aiSummary: 'Exceptional ball control, needs improvement in weak foot accuracy'
    },
    {
      id: 2,
      playerName: 'Alex Johnson',
      type: 'Physical Fitness Test',
      status: 'In Progress',
      score: null,
      date: '2024-03-18',
      videoUrl: '#',
      aiSummary: 'Assessment currently running...'
    },
    {
      id: 3,
      playerName: 'David Chen',
      type: 'Tactical Assessment',
      status: 'Scheduled',
      score: null,
      date: '2024-03-20',
      videoUrl: null,
      aiSummary: 'Scheduled for tomorrow at 10:00 AM'
    },
    {
      id: 4,
      playerName: 'Leo Martinez',
      type: 'Goalkeeper Specific',
      status: 'Completed',
      score: 88,
      date: '2024-03-10',
      videoUrl: '#',
      aiSummary: 'Strong shot-stopping, positioning needs work'
    },
    {
      id: 5,
      playerName: 'Jake Williams',
      type: 'Speed & Agility',
      status: 'Review Needed',
      score: 74,
      date: '2024-03-14',
      videoUrl: '#',
      aiSummary: 'Good acceleration, needs agility drill focus'
    }
  ];

  const filteredAssessments = filterStatus === 'all' 
    ? assessments 
    : assessments.filter(a => a.status === filterStatus);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto mb-4"></div>
          <p className="text-white">Loading assessments...</p>
        </div>
      </div>
    );
  }

  const getStatusConfig = (status) => {
    switch (status) {
      case 'Review Needed':
        return { icon: AlertCircle, color: 'text-[#FFD93D]', bg: 'bg-[#FFD93D]/20', border: 'border-[#FFD93D]/30' };
      case 'In Progress':
        return { icon: Clock, color: 'text-[#007BFF]', bg: 'bg-[#007BFF]/20', border: 'border-[#007BFF]/30' };
      case 'Scheduled':
        return { icon: FileText, color: 'text-white/60', bg: 'bg-white/10', border: 'border-white/20' };
      case 'Completed':
        return { icon: CheckCircle, color: 'text-[#4DFF91]', bg: 'bg-[#4DFF91]/20', border: 'border-[#4DFF91]/30' };
      default:
        return { icon: FileText, color: 'text-white/60', bg: 'bg-white/10', border: 'border-white/20' };
    }
  };

  const statusCounts = {
    all: assessments.length,
    'Review Needed': assessments.filter(a => a.status === 'Review Needed').length,
    'In Progress': assessments.filter(a => a.status === 'In Progress').length,
    'Scheduled': assessments.filter(a => a.status === 'Scheduled').length,
    'Completed': assessments.filter(a => a.status === 'Completed').length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold">Assessment Management</h2>
        <p className="text-white/60 mt-1">Review and manage player assessments</p>
      </div>

      {/* Status Filters */}
      <div className="flex flex-wrap gap-3">
        {['all', 'Review Needed', 'In Progress', 'Scheduled', 'Completed'].map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={`px-6 py-3 rounded-xl font-medium transition ${
              filterStatus === status
                ? 'bg-gradient-to-r from-[#4DFF91] to-[#007BFF] text-[#0C1A2A]'
                : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
            }`}
          >
            {status === 'all' ? 'All' : status}
            <span className="ml-2 text-xs opacity-70">({statusCounts[status]})</span>
          </button>
        ))}
      </div>

      {/* Assessment Pipeline Funnel */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Scheduled', count: statusCounts['Scheduled'], color: 'from-white/10 to-white/5' },
          { label: 'In Progress', count: statusCounts['In Progress'], color: 'from-[#007BFF]/20 to-[#007BFF]/10' },
          { label: 'Review Needed', count: statusCounts['Review Needed'], color: 'from-[#FFD93D]/20 to-[#FFD93D]/10' },
          { label: 'Completed', count: statusCounts['Completed'], color: 'from-[#4DFF91]/20 to-[#4DFF91]/10' }
        ].map((stage, idx) => (
          <div key={idx} className={`bg-gradient-to-br ${stage.color} backdrop-blur-xl border border-white/10 rounded-2xl p-6 text-center`}>
            <div className="text-4xl font-bold mb-2">{stage.count}</div>
            <div className="text-sm text-white/70">{stage.label}</div>
          </div>
        ))}
      </div>

      {/* Assessment Cards */}
      <div className="space-y-4">
        {filteredAssessments.map((assessment) => {
          const statusConfig = getStatusConfig(assessment.status);
          const StatusIcon = statusConfig.icon;

          return (
            <div
              key={assessment.id}
              onClick={() => assessment.status === 'Review Needed' || assessment.status === 'Completed' ? onSelectAssessment(assessment) : null}
              className={`bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 transition ${
                (assessment.status === 'Review Needed' || assessment.status === 'Completed') ? 'hover:bg-white/10 hover:scale-[1.02] cursor-pointer' : ''
              }`}
            >
              <div className="flex items-start gap-6">
                {/* Player Avatar */}
                <div className="w-16 h-16 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-2xl flex items-center justify-center text-lg font-bold flex-shrink-0">
                  {assessment.playerName.split(' ').map(n => n[0]).join('')}
                </div>

                {/* Assessment Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-xl font-bold mb-1">{assessment.playerName}</h3>
                      <p className="text-sm text-white/60">{assessment.type}</p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${statusConfig.bg} ${statusConfig.color} ${statusConfig.border}`}>
                        <StatusIcon className="w-3 h-3" />
                        {assessment.status}
                      </span>
                      {assessment.score && (
                        <span className="text-2xl font-bold text-[#4DFF91]">{assessment.score}</span>
                      )}
                    </div>
                  </div>

                  {/* AI Summary */}
                  <div className="bg-white/5 rounded-xl p-4 mb-4">
                    <div className="text-xs text-white/60 mb-1">AI Analysis</div>
                    <p className="text-sm text-white/80">{assessment.aiSummary}</p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-white/60">{assessment.date}</span>
                    {assessment.videoUrl && (
                      <button className="flex items-center gap-1 text-xs text-[#4DFF91] hover:text-[#4DFF91]/80">
                        <Play className="w-3 h-3" />
                        Watch Video
                      </button>
                    )}
                    {(assessment.status === 'Review Needed' || assessment.status === 'Completed') && (
                      <button className="ml-auto px-4 py-2 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-lg text-sm font-medium text-[#0C1A2A] hover:shadow-lg hover:shadow-[#4DFF91]/30 transition">
                        {assessment.status === 'Review Needed' ? 'Start Review' : 'View Report'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CoachAssessmentManagement;