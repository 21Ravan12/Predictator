// app/products/page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getProducts, type Product } from '@/app/services/api';

// ============================================
// 🎯 CATEGORY CONFIG
// ============================================

const CATEGORY_FILTERS = [
  { value: 'all', label: 'All Products', icon: '🌐' },
  { value: 'Electronics', label: 'Electronics', icon: '📱' },
  { value: 'Food', label: 'Food', icon: '🍔' },
  { value: 'Clothing', label: 'Clothing', icon: '👕' },
  { value: 'Home & Garden', label: 'Home & Garden', icon: '🏠' },
];

const categoryIcon = (categoryName: string) => {
  switch (categoryName) {
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

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

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

  const getCategoryName = (product: Product) =>
    product.category?.name ?? product.categoryName ?? 'Uncategorized';

  const filteredProducts = products.filter((product) => {
    // Category filter
    if (filter !== 'all') {
      const categoryName = getCategoryName(product);
      if (categoryName.toLowerCase() !== filter.toLowerCase()) return false;
    }

    // Search filter
    if (search.trim()) {
      const q = search.toLowerCase();
      const name = product.name?.toLowerCase() ?? '';
      const id = product.productId?.toLowerCase() ?? '';
      const brand = product.brand?.toLowerCase() ?? '';
      if (!name.includes(q) && !id.includes(q) && !brand.includes(q)) {
        return false;
      }
    }

    return true;
  });

  // Category counts
  const categoryCounts = CATEGORY_FILTERS.reduce((acc, cat) => {
    if (cat.value === 'all') {
      acc[cat.value] = products.length;
    } else {
      acc[cat.value] = products.filter(
        (p) => getCategoryName(p).toLowerCase() === cat.value.toLowerCase()
      ).length;
    }
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

        {/* ============================================ */}
        {/* 📋 HEADER */}
        {/* ============================================ */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              Product Catalog
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {products.length} products across 4 categories
            </p>
          </div>

          {/* Search */}
          <div className="relative w-full md:w-72">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search products..."
              className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
              🔍
            </span>
          </div>
        </div>

        {/* ============================================ */}
        {/* 🎯 FILTER TABS */}
        {/* ============================================ */}
        <div className="flex flex-wrap gap-2 mb-5">
          {CATEGORY_FILTERS.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setFilter(cat.value)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition flex items-center gap-2 ${
                filter === cat.value
                  ? 'bg-gray-900 text-white'
                  : 'bg-white text-gray-700 border border-gray-200 hover:border-gray-300'
              }`}
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
              <span
                className={`text-xs px-1.5 py-0.5 rounded ${
                  filter === cat.value
                    ? 'bg-white/20 text-white'
                    : 'bg-gray-100 text-gray-500'
                }`}
              >
                {categoryCounts[cat.value] ?? 0}
              </span>
            </button>
          ))}
        </div>

        {/* ============================================ */}
        {/* ⚠️ ERROR */}
        {/* ============================================ */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4 text-sm">
            ❌ {error}
          </div>
        )}

        {/* ============================================ */}
        {/* ⏳ LOADING */}
        {/* ============================================ */}
        {loading && (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center text-sm text-gray-500">
            Loading products...
          </div>
        )}

        {/* ============================================ */}
        {/* 📦 PRODUCTS TABLE */}
        {/* ============================================ */}
        {!loading && filteredProducts.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Table Header */}
            <div className="px-5 py-3 border-b border-gray-200 flex items-center justify-between">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                {filteredProducts.length} of {products.length} products
              </div>
              {search && (
                <button
                  onClick={() => setSearch('')}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  Clear search
                </button>
              )}
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      ID
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Product
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Category
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Brand
                    </th>
                    <th className="px-5 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Price
                    </th>
                    <th className="px-5 py-2.5 text-center text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Status
                    </th>
                    <th className="px-5 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredProducts.map((product) => {
                    const catName = getCategoryName(product);
                    const isActive = product.isActive !== false;

                    return (
                      <tr
                        key={product.productId}
                        className="hover:bg-gray-50 transition"
                      >
                        {/* ID */}
                        <td className="px-5 py-3 font-mono text-xs text-gray-600">
                          {product.productId}
                        </td>

                        {/* Product Name */}
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-2">
                            <span className="text-base">
                              {categoryIcon(catName)}
                            </span>
                            <span className="font-medium text-gray-900">
                              {product.name}
                            </span>
                          </div>
                        </td>

                        {/* Category */}
                        <td className="px-5 py-3 text-gray-600">
                          {catName}
                        </td>

                        {/* Brand */}
                        <td className="px-5 py-3 text-gray-600">
                          {product.brand || '—'}
                        </td>

                        {/* Price */}
                        <td className="px-5 py-3 text-right font-medium text-gray-900">
                          {product.unitPrice != null
                            ? `$${product.unitPrice.toFixed(2)}`
                            : '—'}
                        </td>

                        {/* Status */}
                        <td className="px-5 py-3 text-center">
                          <span
                            className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded ${
                              isActive
                                ? 'bg-green-50 text-green-700'
                                : 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            <span
                              className={`w-1.5 h-1.5 rounded-full ${
                                isActive ? 'bg-green-500' : 'bg-gray-400'
                              }`}
                            ></span>
                            {isActive ? 'Active' : 'Inactive'}
                          </span>
                        </td>

                        {/* Action */}
                        <td className="px-5 py-3 text-right">
                          <Link
                            href={`/predictions?product=${product.productId}`}
                            className="text-xs font-medium text-indigo-600 hover:text-indigo-700"
                          >
                            Predict →
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ============================================ */}
        {/* 📭 EMPTY STATE */}
        {/* ============================================ */}
        {!loading && filteredProducts.length === 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <div className="text-4xl mb-3">📭</div>
            <h3 className="text-base font-semibold text-gray-900 mb-1">
              No products found
            </h3>
            <p className="text-sm text-gray-500">
              {search
                ? `No products matching "${search}"`
                : filter === 'all'
                  ? 'No products in catalog'
                  : `No products in "${filter}" category`}
            </p>
            {(search || filter !== 'all') && (
              <button
                onClick={() => {
                  setSearch('');
                  setFilter('all');
                }}
                className="mt-4 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
              >
                Clear filters
              </button>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
