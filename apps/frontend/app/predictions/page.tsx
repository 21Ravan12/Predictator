// app/predictions/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { generatePredictions, getProducts, type Product } from '@/app/services/api';
import Dashboard from '@/app/components/Dashboard';
import PredictionChart from '@/app/components/PredictionChart';
import PredictionTable from '@/app/components/PredictionTable';
import AlertPanel from '@/app/components/AlertPanel';

// ============================================
// 📊 TYPES
// ============================================

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

// ============================================
// 🎨 CATEGORY EMOJI HELPER
// ============================================

const categoryEmoji = (category?: string | null) => {
  switch (category ?? '') {
    case 'Electronics': return '📱';
    case 'Food': return '🍔';
    case 'Clothing': return '👕';
    case 'Home & Garden': return '🏠';
    default: return '📦';
  }
};

// ============================================
// 🏠 MAIN COMPONENT
// ============================================

export default function PredictionsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [productId, setProductId] = useState('');
  const [daysAhead, setDaysAhead] = useState(7);
  const [loading, setLoading] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const loadProducts = async () => {
      try {
        const result = await getProducts();
        if (!active) return;

        setProducts(result);
        if (result.length > 0) {
          setProductId((currentProductId) => currentProductId || result[0].productId);
        }
      } catch (err) {
        if (!active) return;

        console.error('Failed to load products:', err);
        setError('Failed to load products. Is the backend running?');
      } finally {
        if (active) {
          setLoadingProducts(false);
        }
      }
    };

    void loadProducts();
    return () => {
      active = false;
    };
  }, []);

  const handlePredict = async () => {
    if (!productId) {
      setError('Please select a product');
      return;
    }

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

  const selectedProduct = products.find((p) => p.productId === productId);
  const selectedCategory = selectedProduct?.category?.name ?? selectedProduct?.categoryName;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📊 Sales Forecast</h1>
          {selectedProduct && (
            <p className="text-gray-600 mt-1 text-sm">
              {categoryEmoji(selectedCategory)} {selectedProduct.name}
              {selectedProduct.brand && ` • ${selectedProduct.brand}`}
              {selectedProduct.unitPrice != null && ` • $${selectedProduct.unitPrice.toFixed(2)}`}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* 🆕 DYNAMIC PRODUCT DROPDOWN */}
          <select
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            disabled={loadingProducts}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white min-w-70 max-w-md"
          >
            {loadingProducts ? (
              <option>⏳ Loading products...</option>
            ) : products.length === 0 ? (
              <option>❌ No products available</option>
            ) : (
              <>
                {/* Group by category */}
                {['Electronics', 'Food', 'Clothing', 'Home & Garden'].map((cat) => {
                  const catProducts = products.filter(
                    (p) => (p.category?.name ?? p.categoryName) === cat,
                  );
                  if (catProducts.length === 0) return null;

                  return (
                    <optgroup key={cat} label={`${categoryEmoji(cat)} ${cat}`}>
                      {catProducts.map((p) => (
                        <option key={p.productId} value={p.productId}>
                          {p.productId} — {p.name}
                        </option>
                      ))}
                    </optgroup>
                  );
                })}
              </>
            )}
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
            disabled={loading || loadingProducts || !productId}
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
          <PredictionChart predictions={data.predictions} />
          <PredictionTable predictions={data.predictions} />
          {data.dictator_actions && data.dictator_actions.length > 0 && (
            <AlertPanel alerts={data.dictator_actions} />
          )}
        </div>
      )}

      {/* Empty State */}
      {!data && !loading && !error && !loadingProducts && (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center border-2 border-dashed border-gray-200">
          <div className="text-6xl mb-4">📈</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            {products.length} Products Ready
          </h3>
          <p className="text-gray-500">
            Select a product from the dropdown and click `Predict`
          </p>
        </div>
      )}
    </div>
  );
}
