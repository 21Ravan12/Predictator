'use client';

import { useState } from 'react';
import { generatePredictions } from '@/app/services/api';
import Dashboard from '@/app/components/Dashboard';
import PredictionTable from '@/app/components/PredictionTable';
import AlertPanel from '@/app/components/AlertPanel';

interface Prediction {
  date: string;
  predicted_sales: number;
  confidence_lower: number;
  confidence_upper: number;
  alert: string | null;
}

interface Alert {
  day: number;
  message: string;
}

interface PredictionResponse {
  product_id: string;
  predictions: Prediction[];
  summary: {
    total_predicted: number;
    average_daily: number;
    peak_day: number;
    floor_violations: number;
  };
  dictator_actions?: Alert[];
}

export default function HomePage() {
  const [productId, setProductId] = useState('P001');
  const [daysAhead, setDaysAhead] = useState(7);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await generatePredictions(productId, daysAhead);

      setData({
        product_id: result.product_id ?? productId,
        predictions: result.predictions ?? [],
        summary: result.summary ?? {
          total_predicted: 0,
          average_daily: 0,
          peak_day: 0,
          floor_violations: 0,
        },
        dictator_actions: result.dictator_actions ?? [],
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get predictions');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <h1 className="text-3xl font-bold text-gray-900">📊 Sales Forecast</h1>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
          >
            <option value="P001">📱 P001 - Electronics</option>
            <option value="P002">🍔 P002 - Food</option>
            <option value="P003">👕 P003 - Clothing</option>
          </select>
          <input
            type="number"
            value={daysAhead}
            onChange={(e) => setDaysAhead(Math.min(30, Math.max(1, Number(e.target.value))))}
            className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            min={1}
            max={30}
          />
          <button
            onClick={handlePredict}
            disabled={loading}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">⏳</span> Loading...
              </>
            ) : (
              '🚀 Predict'
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          ❌ {error}
        </div>
      )}

      {/* Results */}
      {data && (
        <div className="space-y-6 animate-fadeIn">
          <Dashboard data={data} />
          <PredictionTable predictions={data.predictions} />
          {data.dictator_actions && data.dictator_actions.length > 0 && (
            <AlertPanel alerts={data.dictator_actions} />
          )}
        </div>
      )}

      {/* Empty State */}
      {!data && !loading && !error && (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center border-2 border-dashed border-gray-200">
          <div className="text-6xl mb-4">📈</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Predictions Yet</h3>
          <p className="text-gray-500">Select a product and click Predict to see the forecast</p>
        </div>
      )}
    </div>
  );
}
