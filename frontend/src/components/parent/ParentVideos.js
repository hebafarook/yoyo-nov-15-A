import React, { useState } from 'react';
import { Upload, Video, TrendingUp, AlertCircle } from 'lucide-react';

const ParentVideos = ({ child }) => {
  const [uploading, setUploading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('dribbling');

  // Mock video analysis data
  const videoAnalyses = [
    {
      id: '1',
      uploadDate: '2024-03-12',
      category: 'Shooting',
      videoUrl: '#',
      aiTechniqueScore: 72,
      keyMistakes: [
        'Plant foot positioning too far from ball',
        'Follow-through lacks power',
        'Body weight not fully transferred'
      ],
      improvementTips: [
        'Practice planting foot 6-8 inches from ball',
        'Focus on complete follow-through motion',
        'Work on weight transfer drills'
      ],
      recommendedDrills: ['Shooting Technique Breakdown', 'Power Shot Training', 'Plant Foot Positioning']
    },
    {
      id: '2',
      uploadDate: '2024-03-05',
      category: 'Dribbling',
      videoUrl: '#',
      aiTechniqueScore: 85,
      keyMistakes: [
        'Touches occasionally too heavy in tight spaces',
        'Head down too much when dribbling'
      ],
      improvementTips: [
        'Practice lighter touches in cone drills',
        'Work on peripheral vision awareness'
      ],
      recommendedDrills: ['Close Control Cones', 'Head-Up Dribbling', 'Quick Touch Practice']
    }
  ];

  const [selectedVideo, setSelectedVideo] = useState(null);

  const categories = ['Dribbling', 'Shooting', 'Passing', 'Speed Test', 'General'];

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    // Simulate upload and AI analysis
    setTimeout(() => {
      setUploading(false);
      alert('Video uploaded successfully! AI analysis will be available in 2-3 minutes.');
    }, 2000);
  };

  if (selectedVideo) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => setSelectedVideo(null)}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Back to Videos
        </button>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Video Analysis</h2>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>{selectedVideo.uploadDate}</span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {selectedVideo.category}
                </span>
              </div>
            </div>
            <div className="text-center">
              <div className={`text-5xl font-bold ${getScoreColor(selectedVideo.aiTechniqueScore)} mb-1`}>
                {selectedVideo.aiTechniqueScore}
              </div>
              <div className="text-sm text-gray-600">Technique Score</div>
            </div>
          </div>

          {/* Video Player Placeholder */}
          <div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center mb-6">
            <Video className="w-16 h-16 text-gray-600" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="p-4 bg-red-50 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                Key Mistakes Identified
              </h3>
              <ul className="space-y-2">
                {selectedVideo.keyMistakes.map((mistake, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-red-600 font-bold mt-0.5">•</span>
                    <span>{mistake}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                Improvement Tips
              </h3>
              <ul className="space-y-2">
                {selectedVideo.improvementTips.map((tip, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-green-600 font-bold mt-0.5">✓</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-3">Recommended Training Drills</h3>
            <div className="flex flex-wrap gap-2">
              {selectedVideo.recommendedDrills.map((drill, idx) => (
                <span key={idx} className="px-3 py-1 bg-white text-blue-700 rounded-full text-sm font-medium">
                  {drill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Upload Training Video for AI Feedback</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {categories.map((cat) => (
                <option key={cat} value={cat.toLowerCase()}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
            <input
              type="file"
              accept="video/*"
              onChange={handleFileUpload}
              className="hidden"
              id="video-upload"
            />
            <label htmlFor="video-upload" className="cursor-pointer">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">Click to upload or drag and drop</p>
              <p className="text-sm text-gray-500">MP4, MOV, AVI (max 100MB)</p>
            </label>
          </div>

          {uploading && (
            <div className="p-4 bg-blue-50 rounded-lg text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-700">Uploading and analyzing...</p>
            </div>
          )}

          <button
            disabled={uploading}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            Upload & Analyze
          </button>
        </div>
      </div>

      {/* Previous Analyses */}
      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-4">Previous Analyses</h3>
        <div className="space-y-4">
          {videoAnalyses.map((video) => (
            <div key={video.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer"
              onClick={() => setSelectedVideo(video)}
            >
              <div className="flex items-start gap-4">
                <div className="w-24 h-16 bg-gray-900 rounded flex items-center justify-center flex-shrink-0">
                  <Video className="w-8 h-8 text-gray-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                        {video.category}
                      </span>
                      <p className="text-sm text-gray-600 mt-1">{video.uploadDate}</p>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(video.aiTechniqueScore)}`}>
                        {video.aiTechniqueScore}
                      </div>
                      <div className="text-xs text-gray-600">Technique</div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">
                    <strong>{video.keyMistakes.length}</strong> key mistakes identified, 
                    <strong> {video.improvementTips.length}</strong> improvement tips provided
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ParentVideos;