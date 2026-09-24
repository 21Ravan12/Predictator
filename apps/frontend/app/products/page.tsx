// app/products/page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getProducts, type Product } from '@/app/services/api';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await getProducts();
        setProducts(data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load products');
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  const filteredProducts = products.filter((product) => {
    if (filter === 'all') return true;

    const categoryName = product.category?.name ?? product.categoryName ?? '';
    return categoryName.toLowerCase() === filter.toLowerCase();
  });

  const categories = ['all', 'Electronics', 'Food', 'Clothing'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📦 Products
        </h1>
        <p className="text-gray-600">
          Manage your product catalog ({products.length} total)
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filter === cat
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 border border-gray-200 hover:border-indigo-300'
            }`}
          >
            {cat === 'all' ? '🌐 All' : ''}
            {cat === 'Electronics' ? '📱 Electronics' : ''}
            {cat === 'Food' ? '🍔 Food' : ''}
            {cat === 'Clothing' ? '👕 Clothing' : ''}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          ❌ {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-12 text-gray-500">
          Loading products...
        </div>
      )}

      {/* Products Grid */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => {
            const categoryName = product.category?.name ?? product.categoryName ?? 'Uncategorized';
            const categoryIcon = product.category?.icon ??
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
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl">{categoryIcon}</div>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      product.isActive !== false
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {product.isActive !== false ? '✅ Active' : '⏸️ Inactive'}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-gray-900 mb-1">
                  {product.name}
                </h3>
                <p className="text-sm text-gray-600 mb-3">{categoryName}</p>

                {product.unitPrice != null && (
                  <p className="text-sm text-gray-500 mb-4">
                    💰 ${product.unitPrice.toFixed(2)}
                  </p>
                )}

                <Link
                  href={`/predictions?product=${product.productId}`}
                  className="block w-full text-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm"
                >
                  🔮 Predict Sales
                </Link>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredProducts.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            No products found
          </h3>
          <p className="text-gray-500">
            {filter === 'all'
              ? 'Start by training your model with product data'
              : `No products in "${filter}" category`}
          </p>
        </div>
      )}
    </div>
  );
}
