// app/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getProducts, type Product } from '@/app/services/api';

export default function DashboardPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data ?? []);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadProducts();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          👋 Welcome to Predictator
        </h1>
        <p className="text-gray-600">
          AI-powered sales forecasting system
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-indigo-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Products</p>
              <p className="text-2xl font-bold text-gray-900">
                {loading ? '...' : products.length}
              </p>
            </div>
            <span className="text-3xl">📦</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Model Status</p>
              <p className="text-2xl font-bold text-green-600">Active</p>
            </div>
            <span className="text-3xl">🧠</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">R² Score</p>
              <p className="text-2xl font-bold text-purple-600">0.961</p>
            </div>
            <span className="text-3xl">🎯</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Link
          href="/predictions"
          className="bg-linear-to-br from-indigo-500 to-indigo-600 text-white p-6 rounded-lg shadow-md hover:shadow-lg transition group"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-2">🔮 Make Predictions</h3>
              <p className="text-indigo-100 text-sm">
                Generate sales forecasts for any product
              </p>
            </div>
            <span className="text-4xl group-hover:translate-x-2 transition">
              →
            </span>
          </div>
        </Link>

        <Link
          href="/products"
          className="bg-linear-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow-md hover:shadow-lg transition group"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-2">📦 Manage Products</h3>
              <p className="text-green-100 text-sm">
                View and manage your product catalog
              </p>
            </div>
            <span className="text-4xl group-hover:translate-x-2 transition">
              →
            </span>
          </div>
        </Link>
      </div>

      {/* Products List */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">
            📦 Your Products
          </h2>
          <Link
            href="/products"
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            View all →
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : products.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No products found
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {products.slice(0, 4).map((product) => {
              const categoryName =
                product.category?.name ?? product.categoryName ?? 'Unknown';
              const categoryIcon =
                product.category?.icon ??
                (categoryName === 'Electronics'
                  ? '📱'
                  : categoryName === 'Food'
                    ? '🍔'
                    : categoryName === 'Clothing'
                      ? '👕'
                      : '📦');

              return (
                <div
                  key={product.productId}
                  className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition"
                >
                  <div className="text-2xl mb-2">{categoryIcon}</div>
                  <p className="font-semibold text-gray-800">{product.name}</p>
                  <p className="text-xs text-gray-500">{categoryName}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
