'use client';

import { useState, useEffect } from 'react';
import { getTrainingStatus, trainModel } from '@/app/services/api';

type TrainingStatus = {
  is_trained?: boolean;
  metrics?: {
    r2?: number;
  };
  last_training?: string;
};

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState('http://localhost:4000');
  const [floorLimit, setFloorLimit] = useState(0);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadStatus = async () => {
      try {
        const response = await fetch('/api/status');
        const status = await response.json();

        if (!cancelled) {
          setTrainingStatus(status);
        }
      } catch (error) {
        if (!cancelled) {
          setMessage({
            type: 'error',
            text: error instanceof Error ? error.message : 'Failed to load status',
          });
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void loadStatus();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleRetrain = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const result = await trainModel(undefined, true);
      setMessage({ type: 'success', text: `✅ ${result.message}` });
      await fetchStatus();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Training failed',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const status = await getTrainingStatus();
      setTrainingStatus(status);
    } catch (error) {
      console.error('Failed to fetch training status:', error);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">⚙️ Settings</h1>

      {/* Message */}
      {message && (
        <div className={`px-4 py-3 rounded-lg mb-4 ${message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* API Settings */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">🔗 API Connection</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">API URL</label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">Backend API endpoint</p>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className={`w-2 h-2 rounded-full ${trainingStatus ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span className="text-gray-600">Status: {trainingStatus ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
        </div>

        {/* Dictator Settings */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">👑 Dictator Engine</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Default Floor Limit</label>
              <input
                type="number"
                value={floorLimit}
                onChange={(e) => setFloorLimit(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">Minimum sales enforced per day (0 = disabled)</p>
            </div>
            <button className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition">
              💾 Save Settings
            </button>
          </div>
        </div>

        {/* Model Training */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100 md:col-span-2">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">🧠 Model Management</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-500">Status</p>
              <p className="font-semibold text-gray-800">{trainingStatus?.is_trained ? '✅ Trained' : '❌ Not Trained'}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-500">R² Score</p>
              <p className="font-semibold text-gray-800">{trainingStatus?.metrics?.r2 ? trainingStatus.metrics.r2.toFixed(3) : '—'}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-xs text-gray-500">Last Training</p>
              <p className="font-semibold text-gray-800">{trainingStatus?.last_training ? new Date(trainingStatus.last_training).toLocaleDateString() : '—'}</p>
            </div>
          </div>

          <button
            onClick={handleRetrain}
            disabled={loading}
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">⏳</span> Training...
              </>
            ) : (
              '🔄 Retrain Model'
            )}
          </button>
          <p className="text-xs text-gray-500 mt-2">This will retrain the model using the current dataset</p>
        </div>
      </div>
    </div>
  );
}
