import React, { useState, useCallback } from 'react';
import { Upload, FileText, Check, X, Edit3, Save, AlertCircle, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Valid sections from backend
const VALID_SECTIONS = [
  'technical', 'tactical', 'possession', 'speed_agility',
  'cardio', 'gym', 'mobility', 'recovery', 'prehab'
];

const INTENSITIES = ['low', 'moderate', 'high'];

const CoachDrillUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [parsedDrills, setParsedDrills] = useState([]);
  const [errors, setErrors] = useState([]);
  const [meta, setMeta] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);
  const [confirmResult, setConfirmResult] = useState(null);
  const [expandedIndex, setExpandedIndex] = useState(null);

  // Get auth token from localStorage
  const getAuthToken = () => {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const parsed = JSON.parse(user);
        return parsed.token;
      } catch (e) {
        return null;
      }
    }
    return null;
  };

  // Handle file selection
  const handleFileSelect = useCallback((e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
        setErrors(['Only PDF files are accepted']);
        return;
      }
      setFile(selectedFile);
      setErrors([]);
      setParsedDrills([]);
      setMeta(null);
      setConfirmResult(null);
    }
  }, []);

  // Handle drag and drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      if (!droppedFile.name.toLowerCase().endsWith('.pdf')) {
        setErrors(['Only PDF files are accepted']);
        return;
      }
      setFile(droppedFile);
      setErrors([]);
      setParsedDrills([]);
      setMeta(null);
      setConfirmResult(null);
    }
  }, []);

  // Upload PDF for parsing (preview only - no DB writes)
  const handleUpload = async () => {
    if (!file) return;

    const token = getAuthToken();
    if (!token) {
      setErrors(['Please log in to upload drills']);
      return;
    }

    setUploading(true);
    setErrors([]);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${BACKEND_URL}/api/coach/drills/upload-pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error?.message || 'Upload failed');
      }

      setParsedDrills(data.parsed || []);
      setErrors(data.errors || []);
      setMeta(data.meta || {});

    } catch (error) {
      setErrors([error.message]);
    } finally {
      setUploading(false);
    }
  };

  // Update a drill field
  const updateDrill = (index, field, value) => {
    setParsedDrills(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      // If updating required fields, check if still needs review
      if (['drill_id', 'name', 'section'].includes(field)) {
        const drill = updated[index];
        updated[index].needs_review = !drill.drill_id || !drill.name || !drill.section;
      }
      return updated;
    });
  };

  // Confirm and save drills to database
  const handleConfirm = async () => {
    const token = getAuthToken();
    if (!token) {
      setErrors(['Please log in to confirm drills']);
      return;
    }

    // Validate all drills have required fields
    const invalidDrills = parsedDrills.filter(d => !d.drill_id || !d.name || !d.section);
    if (invalidDrills.length > 0) {
      setErrors(['Please fill in all required fields (ID, Name, Section) for all drills']);
      return;
    }

    setConfirming(true);
    setErrors([]);

    try {
      // Prepare drills for confirmation (remove preview-only fields)
      const drillsToConfirm = parsedDrills.map(d => ({
        drill_id: d.drill_id,
        name: d.name,
        section: d.section,
        tags: d.tags || [],
        duration_min: d.duration_min,
        sets: d.sets,
        reps: d.reps,
        intensity: d.intensity,
        equipment: d.equipment || [],
        coaching_points: d.coaching_points || [],
        contraindications: d.contraindications || []
      }));

      const response = await fetch(`${BACKEND_URL}/api/coach/drills/confirm`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ drills: drillsToConfirm })
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.detail?.errors) {
          throw new Error(data.detail.errors.join('\n'));
        }
        throw new Error(data.detail?.message || data.error?.message || 'Confirmation failed');
      }

      setConfirmResult(data);
      setParsedDrills([]);
      setFile(null);

    } catch (error) {
      setErrors([error.message]);
    } finally {
      setConfirming(false);
    }
  };

  // Reset to start over
  const handleReset = () => {
    setFile(null);
    setParsedDrills([]);
    setErrors([]);
    setMeta(null);
    setConfirmResult(null);
    setEditingIndex(null);
  };

  // Get status badge color
  const getStatusColor = (drill) => {
    if (!drill.drill_id || !drill.name || !drill.section) {
      return 'bg-red-100 text-red-700 border-red-300';
    }
    if (drill.needs_review) {
      return 'bg-yellow-100 text-yellow-700 border-yellow-300';
    }
    return 'bg-green-100 text-green-700 border-green-300';
  };

  // Render success message
  if (confirmResult) {
    return (
      <div className="space-y-6">
        <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-green-800 mb-2">Drills Imported Successfully!</h3>
          <p className="text-green-600 mb-4">
            {confirmResult.inserted} new drills added, {confirmResult.updated} drills updated
          </p>
          <div className="bg-white rounded-lg p-4 max-w-md mx-auto mb-6">
            <p className="text-sm text-gray-600 mb-2">Imported drill IDs:</p>
            <div className="flex flex-wrap gap-2">
              {confirmResult.drill_ids?.map(id => (
                <span key={id} className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">
                  {id}
                </span>
              ))}
            </div>
          </div>
          <button
            onClick={handleReset}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Upload More Drills
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Upload Training Drills</h2>
        <p className="text-gray-600 mt-1">
          Upload a PDF containing training drills. The system will parse and extract drill information.
        </p>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
            <div>
              <h4 className="font-medium text-red-800">Error</h4>
              {errors.map((error, i) => (
                <p key={i} className="text-sm text-red-600">{error}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Step 1: Upload PDF */}
      {parsedDrills.length === 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm">1</span>
            Upload PDF File
          </h3>

          {/* Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className={`border-2 border-dashed rounded-xl p-8 text-center transition ${
              file ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
            }`}
          >
            {file ? (
              <div className="flex items-center justify-center gap-4">
                <FileText className="w-12 h-12 text-green-600" />
                <div className="text-left">
                  <p className="font-medium text-gray-800">{file.name}</p>
                  <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="p-2 hover:bg-red-100 rounded-lg transition"
                >
                  <X className="w-5 h-5 text-red-500" />
                </button>
              </div>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">Drag and drop your PDF here, or</p>
                <label className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition">
                  Browse Files
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
                <p className="text-sm text-gray-400 mt-2">Only PDF files are accepted (max 10MB)</p>
              </>
            )}
          </div>

          {/* Upload Button */}
          {file && (
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="mt-4 w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Parsing PDF...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Parse PDF
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Step 2: Preview and Edit */}
      {parsedDrills.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm">2</span>
              Review & Edit Drills
            </h3>
            {meta && (
              <span className="text-sm text-gray-500">
                {meta.candidates_parsed || parsedDrills.length} drills from {meta.pages} page(s)
              </span>
            )}
          </div>

          <p className="text-gray-600 mb-4">
            Review the parsed drills below. Edit any fields that need correction. All fields marked with * are required.
          </p>

          {/* Drills List */}
          <div className="space-y-4">
            {parsedDrills.map((drill, index) => (
              <div
                key={index}
                className={`border rounded-xl overflow-hidden transition ${
                  drill.needs_review ? 'border-yellow-300 bg-yellow-50/50' : 'border-gray-200'
                }`}
              >
                {/* Drill Header */}
                <div
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
                  onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                >
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(drill)}`}>
                      {!drill.drill_id || !drill.name || !drill.section ? 'Missing Fields' :
                       drill.needs_review ? 'Needs Review' : 'Ready'}
                    </span>
                    <span className="font-medium text-gray-800">
                      {drill.name || `Drill ${index + 1}`}
                    </span>
                    {drill.section && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                        {drill.section}
                      </span>
                    )}
                    {drill.confidence !== undefined && (
                      <span className="text-xs text-gray-400">
                        {Math.round(drill.confidence * 100)}% confidence
                      </span>
                    )}
                  </div>
                  {expandedIndex === index ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>

                {/* Drill Details (Expanded) */}
                {expandedIndex === index && (
                  <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-4">
                    {/* Required Fields */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Drill ID *
                        </label>
                        <input
                          type="text"
                          value={drill.drill_id || ''}
                          onChange={(e) => updateDrill(index, 'drill_id', e.target.value)}
                          placeholder="e.g., TECH01"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Name *
                        </label>
                        <input
                          type="text"
                          value={drill.name || ''}
                          onChange={(e) => updateDrill(index, 'name', e.target.value)}
                          placeholder="e.g., Triangle Passing Drill"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Section *
                        </label>
                        <select
                          value={drill.section || ''}
                          onChange={(e) => updateDrill(index, 'section', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select section...</option>
                          {VALID_SECTIONS.map(s => (
                            <option key={s} value={s}>{s.replace('_', ' ')}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Optional Fields */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Duration (min)
                        </label>
                        <input
                          type="number"
                          value={drill.duration_min || ''}
                          onChange={(e) => updateDrill(index, 'duration_min', parseInt(e.target.value) || null)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Sets
                        </label>
                        <input
                          type="number"
                          value={drill.sets || ''}
                          onChange={(e) => updateDrill(index, 'sets', parseInt(e.target.value) || null)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Reps
                        </label>
                        <input
                          type="number"
                          value={drill.reps || ''}
                          onChange={(e) => updateDrill(index, 'reps', parseInt(e.target.value) || null)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Intensity
                        </label>
                        <select
                          value={drill.intensity || ''}
                          onChange={(e) => updateDrill(index, 'intensity', e.target.value || null)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select...</option>
                          {INTENSITIES.map(i => (
                            <option key={i} value={i}>{i}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Tags */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tags (comma-separated)
                      </label>
                      <input
                        type="text"
                        value={(drill.tags || []).join(', ')}
                        onChange={(e) => updateDrill(index, 'tags', e.target.value.split(',').map(t => t.trim()).filter(Boolean))}
                        placeholder="e.g., passing, accuracy, first_touch"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    {/* Raw Text (Read Only) */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Parsed Text (Reference)
                      </label>
                      <div className="bg-white border border-gray-200 rounded-lg p-3 text-sm text-gray-600 max-h-32 overflow-y-auto">
                        {drill.raw_text || 'No raw text available'}
                      </div>
                    </div>

                    {/* Warnings */}
                    {drill.parse_warnings && drill.parse_warnings.length > 0 && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <p className="text-sm font-medium text-yellow-800 mb-1">Parsing Notes:</p>
                        <ul className="text-sm text-yellow-700 list-disc list-inside">
                          {drill.parse_warnings.map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Remove Button */}
                    <div className="flex justify-end">
                      <button
                        onClick={() => setParsedDrills(prev => prev.filter((_, i) => i !== index))}
                        className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition flex items-center gap-2"
                      >
                        <X className="w-4 h-4" />
                        Remove Drill
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
            >
              Cancel & Start Over
            </button>
            <button
              onClick={handleConfirm}
              disabled={confirming || parsedDrills.some(d => !d.drill_id || !d.name || !d.section)}
              className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition flex items-center gap-2"
            >
              {confirming ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Confirm & Save {parsedDrills.length} Drill{parsedDrills.length !== 1 ? 's' : ''}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <h4 className="font-medium text-blue-800 mb-2">📋 How it works</h4>
        <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
          <li>Upload a PDF containing your training drills</li>
          <li>The system will automatically parse and extract drill information</li>
          <li>Review the parsed drills and edit any fields that need correction</li>
          <li>Click "Confirm & Save" to add the drills to your library</li>
        </ol>
        <p className="text-sm text-blue-600 mt-2 italic">
          Note: All drills are saved by ID. Uploading a drill with the same ID will update the existing drill.
        </p>
      </div>
    </div>
  );
};

export default CoachDrillUpload;
