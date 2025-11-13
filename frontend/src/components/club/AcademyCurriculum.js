import React from 'react';
import { BookOpen, Video, FileText, Plus } from 'lucide-react';

const AcademyCurriculum = ({ clubId }) => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Academy Curriculum & Training Library</h2>
          <p className="text-gray-400">Club philosophy, drills, and methodology</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl font-medium hover:shadow-lg transition">
          <Plus className="w-5 h-5" />
          Add Drill
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-amber-400/20 shadow-2xl">
          <BookOpen className="w-12 h-12 text-amber-400 mb-3" />
          <p className="text-gray-400 text-sm">Total Drills</p>
          <p className="text-4xl font-bold text-white">0</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-orange-400/20 shadow-2xl">
          <Video className="w-12 h-12 text-orange-400 mb-3" />
          <p className="text-gray-400 text-sm">Video Library</p>
          <p className="text-4xl font-bold text-white">0</p>
        </div>
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-red-400/20 shadow-2xl">
          <FileText className="w-12 h-12 text-red-400 mb-3" />
          <p className="text-gray-400 text-sm">Curricula</p>
          <p className="text-4xl font-bold text-white">0</p>
        </div>
      </div>

      <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-12 border border-amber-400/20 text-center">
        <BookOpen className="w-16 h-16 text-amber-400 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">Build Your Training Library</h3>
        <p className="text-gray-400 mb-6">Add drills, videos, and curriculum to create your club's methodology</p>
        <button className="px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl font-medium hover:shadow-lg transition">
          Get Started
        </button>
      </div>
    </div>
  );
};

export default AcademyCurriculum;