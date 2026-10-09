// app/settings/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { getTrainingStatus, trainModel } from '@/app/services/api';

// ============================================
// 📊 TYPES
// ============================================

type TrainingStatus = {
  is_trained?: boolean;
  metrics?: {
    r2?: number;
    mae?: number;
    rmse?: number;
    n_features?: number;
  };
  last_training?: string;
  n_features?: number;
};

// ============================================
// ⚙️ SETTINGS PAGE
// ============================================

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState('http://localhost:4000');
  const [floorLimit, setFloorLimit] = useState(0);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    setLoadingStatus(true);
    try {
      const status = await getTrainingStatus();
      setTrainingStatus(status);
    } catch (error) {
      console.error('Failed to fetch training status:', error);
    } finally {
      setLoadingStatus(false);
    }
  };

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

  const handleSaveSettings = () => {
    // TODO: persist settings
    setMessage({ type: 'success', text: '✅ Settings saved (not yet persisted)' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

        {/* ============================================ */}
        {/* 📋 HEADER */}
        {/* ============================================ */}
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">
            Settings
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Configure connections, model parameters, and system preferences
          </p>
        </div>

        {/* ============================================ */}
        {/* 💬 MESSAGE */}
        {/* ============================================ */}
        {message && (
          <div
            className={`px-4 py-3 rounded-md mb-5 text-sm border ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700 border-green-200'
                : 'bg-red-50 text-red-700 border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* ============================================ */}
        {/* 📊 GRID */}
        {/* ============================================ */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* -------------------------------------------- */}
          {/* 🔗 API CONNECTION */}
          {/* -------------------------------------------- */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900">
                API Connection
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Backend service endpoint configuration
              </p>
            </div>

            <div className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide mb-1.5">
                  API URL
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Backend API endpoint (e.g., http://localhost:4000)
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      trainingStatus ? 'bg-green-500' : 'bg-red-500'
                    }`}
                  ></span>
                  <span className="text-sm text-gray-700">
                    {trainingStatus ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {trainingStatus ? 'All systems operational' : 'Check backend'}
                </span>
              </div>
            </div>
          </div>

          {/* -------------------------------------------- */}
          {/* 👑 DICTATOR ENGINE */}
          {/* -------------------------------------------- */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900">
                Dictator Engine
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Business rule enforcement configuration
              </p>
            </div>

            <div className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 uppercase tracking-wide mb-1.5">
                  Default Floor Limit
                </label>
                <input
                  type="number"
                  value={floorLimit}
                  onChange={(e) => setFloorLimit(Number(e.target.value))}
                  min={0}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Minimum sales enforced per day (0 = disabled)
                </p>
              </div>

              <div className="pt-2 border-t border-gray-100">
                <button
                  onClick={handleSaveSettings}
                  className="w-full px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-md hover:bg-gray-800 transition"
                >
                  Save Settings
                </button>
              </div>
            </div>
          </div>

          {/* -------------------------------------------- */}
          {/* 🧠 MODEL MANAGEMENT (FULL WIDTH) */}
          {/* -------------------------------------------- */}
          <div className="bg-white rounded-lg border border-gray-200 lg:col-span-2">
            <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-gray-900">
                  Model Management
                </h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  Current model status and retraining controls
                </p>
              </div>
              <button
                onClick={fetchStatus}
                disabled={loadingStatus}
                className="text-xs text-gray-500 hover:text-gray-700 transition"
              >
                {loadingStatus ? '⏳ Refreshing...' : '🔄 Refresh'}
              </button>
            </div>

            <div className="p-5">
              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
                <MetricBox
                  label="Status"
                  value={
                    trainingStatus?.is_trained ? 'Trained' : 'Not Trained'
                  }
                  subtext={trainingStatus?.is_trained ? 'Ready for predictions' : 'Requires training'}
                  variant={trainingStatus?.is_trained ? 'success' : 'warning'}
                />

                <MetricBox
                  label="R² Score"
                  value={
                    trainingStatus?.metrics?.r2
                      ? trainingStatus.metrics.r2.toFixed(3)
                      : '—'
                  }
                  subtext="Model accuracy"
                  variant="default"
                />

                <MetricBox
                  label="Features"
                  value={
                    trainingStatus?.metrics?.n_features?.toString() ??
                    trainingStatus?.n_features?.toString() ??
                    '—'
                  }
                  subtext="Engineered features"
                  variant="default"
                />

                <MetricBox
                  label="Last Training"
                  value={
                    trainingStatus?.last_training
                      ? new Date(trainingStatus.last_training).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })
                      : '—'
                  }
                  subtext={
                    trainingStatus?.last_training
                      ? new Date(trainingStatus.last_training).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })
                      : 'Never trained'
                  }
                  variant="default"
                />
              </div>

              {/* Additional Metrics */}
              {(trainingStatus?.metrics?.mae != null || trainingStatus?.metrics?.rmse != null) && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-5">
                  {trainingStatus?.metrics?.mae != null && (
                    <MetricBox
                      label="MAE"
                      value={trainingStatus.metrics.mae.toFixed(2)}
                      subtext="Mean absolute error"
                      variant="default"
                    />
                  )}
                  {trainingStatus?.metrics?.rmse != null && (
                    <MetricBox
                      label="RMSE"
                      value={trainingStatus.metrics.rmse.toFixed(2)}
                      subtext="Root mean squared error"
                      variant="default"
                    />
                  )}
                </div>
              )}

              {/* Retrain Button */}
              <div className="pt-4 border-t border-gray-100">
                <button
                  onClick={handleRetrain}
                  disabled={loading}
                  className="w-full md:w-auto px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin">⏳</span> Training...
                    </>
                  ) : (
                    '🔄 Retrain Model'
                  )}
                </button>
                <p className="text-xs text-gray-500 mt-2">
                  Retrains the XGBoost model using the current dataset (~29,200 rows)
                </p>
              </div>
            </div>
          </div>

          {/* -------------------------------------------- */}
          {/* ℹ️ ABOUT (FULL WIDTH) */}
          {/* -------------------------------------------- */}
          <div className="bg-white rounded-lg border border-gray-200 lg:col-span-2">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900">
                System Information
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Runtime and environment details
              </p>
            </div>

            <div className="divide-y divide-gray-100">
              <InfoRow label="Version" value="Predictator v2.0" />
              <InfoRow label="Model" value="XGBoost Regressor" />
              <InfoRow label="Dataset" value="29,200 rows · 40 products · 730 days" />
              <InfoRow label="Categories" value="4 (Electronics, Food, Clothing, Home & Garden)" />
              <InfoRow label="Communication" value="gRPC (internal) · REST (external)" />
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

// ============================================
// 🧩 SUB-COMPONENTS
// ============================================

interface MetricBoxProps {
  label: string;
  value: string;
  subtext: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
}

function MetricBox({ label, value, subtext, variant = 'default' }: MetricBoxProps) {
  const valueColor = {
    default: 'text-gray-900',
    success: 'text-green-600',
    warning: 'text-amber-600',
    error: 'text-red-600',
  }[variant];

  return (
    <div className="bg-gray-50 rounded-md p-3 border border-gray-100">
      <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
        {label}
      </div>
      <div className={`text-lg font-semibold mt-1.5 ${valueColor}`}>
        {value}
      </div>
      <div className="text-xs text-gray-500 mt-0.5">
        {subtext}
      </div>
    </div>
  );
}

interface InfoRowProps {
  label: string;
  value: string;
}

function InfoRow({ label, value }: InfoRowProps) {
  return (
    <div className="px-5 py-3 flex items-center justify-between">
      <span className="text-sm text-gray-600">{label}</span>
      <span className="text-sm font-medium text-gray-900">{value}</span>
    </div>
  );
}