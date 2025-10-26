import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  FileText, Calendar, Trash2, Eye, Download, 
  User, Trophy, BarChart3, RefreshCw, Target
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import AssessmentReport from './AssessmentReport';
import BenchmarkHistory from './BenchmarkHistory';

const SavedReports = () => {
  const [activeTab, setActiveTab] = useState('reports'); // 'reports' or 'benchmarks'
  const [savedReports, setSavedReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const { getSavedReports, deleteSavedReport, user } = useAuth();

  useEffect(() => {
    loadSavedReports();
  }, []);

  const loadSavedReports = async () => {
    setLoading(true);
    const result = await getSavedReports();
    if (result.success) {
      setSavedReports(result.reports);
    } else {
      console.error('Failed to load saved reports:', result.error);
    }
    setLoading(false);
  };

  const handleDeleteReport = async (reportId) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      const result = await deleteSavedReport(reportId);
      if (result.success) {
        setSavedReports(prev => prev.filter(report => report.id !== reportId));
      } else {
        alert('Failed to delete report: ' + result.error);
      }
    }
  };

  const handleViewReport = (report) => {
    setSelectedReport(report);
    setShowReportModal(true);
  };

  const getReportTypeIcon = (type) => {
    switch (type) {
      case 'startup': return <Trophy className="w-4 h-4" />;
      case 'milestone': return <BarChart3 className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getReportTypeColor = (type) => {
    switch (type) {
      case 'startup': return 'bg-purple-100 text-purple-800';
      case 'milestone': return 'bg-green-100 text-green-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  if (loading && activeTab === 'reports') {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-[--text-navy]">Player Performance Center</h2>
          <p className="text-[--text-gray]">Manage saved reports and track assessment benchmarks</p>
        </div>
        {activeTab === 'reports' && (
          <Button onClick={loadSavedReports} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        )}
      </div>

      {/* User Info */}
      <Card className="professional-card">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold">{user?.full_name}</h3>
              <p className="text-sm text-gray-600">
                {user?.is_coach ? 'Coach/Professional' : 'Player/Parent'} • {savedReports.length} saved reports
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-4">
          <button
            onClick={() => setActiveTab('reports')}
            className={`py-2 px-4 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
              activeTab === 'reports'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FileText className="w-4 h-4" />
            Saved Reports
            <Badge variant="secondary">{savedReports.length}</Badge>
          </button>
          <button
            onClick={() => setActiveTab('benchmarks')}
            className={`py-2 px-4 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
              activeTab === 'benchmarks'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Target className="w-4 h-4" />
            Assessment Benchmarks
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'reports' ? (
        // Reports List
        savedReports.length === 0 ? (
          <Card className="professional-card text-center p-12">
            <CardContent>
              <FileText className="w-16 h-16 mx-auto mb-4 text-[--text-muted]" />
              <h3 className="text-2xl font-semibold mb-2">No Saved Reports</h3>
              <p className="text-[--text-muted]">
                Complete player assessments and save reports to see them here.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedReports.map((report) => (
              <Card key={report.id} className="professional-card hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getReportTypeIcon(report.report_type)}
                      <CardTitle className="text-lg">{report.title}</CardTitle>
                    </div>
                    <Badge className={getReportTypeColor(report.report_type)}>
                      {report.report_type.charAt(0).toUpperCase() + report.report_type.slice(1)}
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <User className="w-4 h-4 text-gray-500" />
                      <span className="font-medium">{report.player_name}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(report.saved_at).toLocaleDateString()}</span>
                    </div>
                    {report.notes && (
                      <p className="text-sm text-gray-600 line-clamp-2">{report.notes}</p>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      onClick={() => handleViewReport(report)}
                      size="sm" 
                      className="flex-1"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    <Button 
                      onClick={() => handleDeleteReport(report.id)}
                      size="sm" 
                      variant="outline"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )
      ) : (
        // Benchmarks Tab
        <BenchmarkHistory />
      )}

      {/* Report Viewer Modal */}
      {showReportModal && selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] overflow-y-auto w-full">
            <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">{selectedReport.title}</h2>
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    window.print();
                  }}
                  variant="outline"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Print Report
                </Button>
                <Button
                  onClick={() => {
                    setShowReportModal(false);
                    setSelectedReport(null);
                  }}
                  variant="outline"
                >
                  Close
                </Button>
              </div>
            </div>
            <div className="p-6">
              <AssessmentReport
                playerData={selectedReport.report_data.playerData}
                previousAssessments={selectedReport.report_data.previousAssessments || []}
                showComparison={true}
                isStartupReport={selectedReport.report_type === 'startup'}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedReports;
