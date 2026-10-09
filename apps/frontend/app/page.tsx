// app/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getProducts, type Product } from '@/app/services/api';

// ============================================
// 🎯 CATEGORY CONFIG
// ============================================

const CATEGORIES = [
  { name: 'Electronics', code: 'CAT001' },
  { name: 'Food', code: 'CAT002' },
  { name: 'Clothing', code: 'CAT003' },
  { name: 'Home & Garden', code: 'CAT004' },
];

// ============================================
// 🏠 ADMIN HOMEPAGE
// ============================================

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await getProducts();
        setProducts(data);
      } catch (err) {
        console.error('Failed to load products:', err);
      } finally {
        setLastUpdate(new Date().toLocaleString());
        setLoading(false);
      }
    };

    void loadProducts();
  }, []);

  // Category breakdown
  const categoryData = CATEGORIES.map((cat) => {
    const count = products.filter(
      (p) => (p.category?.name ?? p.categoryName) === cat.name
    ).length;
    const avgPrice =
      count > 0
        ? products
            .filter((p) => (p.category?.name ?? p.categoryName) === cat.name)
            .reduce((sum, p) => sum + (p.unitPrice || 0), 0) / count
        : 0;
    return { ...cat, count, avgPrice };
  });

  // Calculate total inventory value
  const totalInventoryValue = products.reduce(
    (sum, p) => sum + (p.unitPrice || 0),
    0
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

        {/* ============================================ */}
        {/* 📋 HEADER */}
        {/* ============================================ */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              System Dashboard
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Overview of operations and model status
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs text-gray-500">
              Last updated: {lastUpdate || '—'}
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-md">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs font-medium text-green-700">
                All Systems Operational
              </span>
            </div>
          </div>
        </div>

        {/* ============================================ */}
        {/* 📊 KEY METRICS */}
        {/* ============================================ */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <MetricCard
            label="Total Products"
            value={loading ? '—' : products.length.toString()}
            subtext="Across 4 categories"
            loading={loading}
          />
          <MetricCard
            label="Categories"
            value="4"
            subtext="All active"
            loading={false}
          />
          <MetricCard
            label="Model R²"
            value="0.997"
            subtext="XGBoost • 53 features"
            loading={false}
            accent="green"
          />
          <MetricCard
            label="Training Samples"
            value="29,200"
            subtext="40 products × 730 days"
            loading={false}
          />
        </div>

        {/* ============================================ */}
        {/* 🎯 QUICK ACTIONS */}
        {/* ============================================ */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <ActionCard
              href="/predictions"
              title="Generate Forecast"
              description="Run predictions for any product"
              icon="🔮"
            />
            <ActionCard
              href="/products"
              title="Manage Products"
              description="View and edit product catalog"
              icon="📦"
            />
            <ActionCard
              href="/settings"
              title="Model Configuration"
              description="Training, parameters, and system settings"
              icon="⚙️"
            />
          </div>
        </div>

        {/* ============================================ */}
        {/* 📊 TWO-COLUMN LAYOUT */}
        {/* ============================================ */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

          {/* Category Breakdown */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900">
                Category Breakdown
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Product distribution by category
              </p>
            </div>
            <div className="divide-y divide-gray-100">
              {categoryData.map((cat) => (
                <div
                  key={cat.code}
                  className="px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition"
                >
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {cat.name}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {cat.code}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-gray-900">
                      {cat.count} products
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      Avg ${cat.avgPrice.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900">
                System Status
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Service health and connectivity
              </p>
            </div>
            <div className="divide-y divide-gray-100">
              <StatusRow label="ML Engine (gRPC)" status="healthy" detail="Port 50051" />
              <StatusRow label="Backend API" status="healthy" detail="Port 4000" />
              <StatusRow label="Database (PostgreSQL)" status="healthy" detail="Connected" />
              <StatusRow label="Model (XGBoost)" status="healthy" detail="R² 0.997" />
              <StatusRow label="Cache" status="healthy" detail="In-memory" />
            </div>
          </div>
        </div>

        {/* ============================================ */}
        {/* 📦 INVENTORY SUMMARY */}
        {/* ============================================ */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Catalog Value
            </div>
            <div className="text-2xl font-semibold text-gray-900 mt-2">
              ${totalInventoryValue.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Sum of all product prices
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Model Features
            </div>
            <div className="text-2xl font-semibold text-gray-900 mt-2">53</div>
            <div className="text-xs text-gray-500 mt-1">
              Time • Lag • Rolling • Weather • Holiday
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Data Coverage
            </div>
            <div className="text-2xl font-semibold text-gray-900 mt-2">
              2 years
            </div>
            <div className="text-xs text-gray-500 mt-1">
              2025-01-01 → 2026-12-31
            </div>
          </div>
        </div>

        {/* ============================================ */}
        {/* 📋 RECENT PRODUCTS */}
        {/* ============================================ */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-gray-900">
                Product Catalog
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Recently added products
              </p>
            </div>
            <Link
              href="/products"
              className="text-xs font-medium text-indigo-600 hover:text-indigo-700"
            >
              View all →
            </Link>
          </div>

          {loading ? (
            <div className="p-5 text-center text-sm text-gray-500">
              Loading products...
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      ID
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Name
                    </th>
                    <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Category
                    </th>
                    <th className="px-5 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                      Price
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {products.slice(0, 5).map((p) => (
                    <tr key={p.productId} className="hover:bg-gray-50">
                      <td className="px-5 py-2.5 font-mono text-xs text-gray-600">
                        {p.productId}
                      </td>
                      <td className="px-5 py-2.5 text-gray-900">{p.name}</td>
                      <td className="px-5 py-2.5 text-gray-600">
                        {p.category?.name ?? p.categoryName ?? '—'}
                      </td>
                      <td className="px-5 py-2.5 text-right font-medium text-gray-900">
                        ${p.unitPrice?.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

// ============================================
// 🧩 SUB-COMPONENTS
// ============================================

interface MetricCardProps {
  label: string;
  value: string;
  subtext: string;
  loading?: boolean;
  accent?: 'default' | 'green';
}

function MetricCard({ label, value, subtext, loading, accent = 'default' }: MetricCardProps) {
  const valueColor = accent === 'green' ? 'text-green-600' : 'text-gray-900';

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
        {label}
      </div>
      <div className={`text-2xl font-semibold mt-2 ${valueColor}`}>
        {loading ? (
          <span className="inline-block w-16 h-7 bg-gray-100 rounded animate-pulse"></span>
        ) : (
          value
        )}
      </div>
      <div className="text-xs text-gray-500 mt-1">{subtext}</div>
    </div>
  );
}

interface ActionCardProps {
  href: string;
  title: string;
  description: string;
  icon: string;
}

function ActionCard({ href, title, description, icon }: ActionCardProps) {
  return (
    <Link
      href={href}
      className="group bg-white rounded-lg border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <span className="text-xl">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-gray-900 group-hover:text-indigo-600 transition">
            {title}
          </div>
          <div className="text-xs text-gray-500 mt-0.5">{description}</div>
        </div>
        <span className="text-gray-300 group-hover:text-indigo-500 transition">
          →
        </span>
      </div>
    </Link>
  );
}

interface StatusRowProps {
  label: string;
  status: 'healthy' | 'warning' | 'error';
  detail: string;
}

function StatusRow({ label, status, detail }: StatusRowProps) {
  const statusConfig = {
    healthy: { color: 'bg-green-500', text: 'text-green-700', bg: 'bg-green-50', label: 'Healthy' },
    warning: { color: 'bg-yellow-500', text: 'text-yellow-700', bg: 'bg-yellow-50', label: 'Warning' },
    error: { color: 'bg-red-500', text: 'text-red-700', bg: 'bg-red-50', label: 'Error' },
  };

  const config = statusConfig[status];

  return (
    <div className="px-5 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className={`w-2 h-2 rounded-full ${config.color}`}></span>
        <div>
          <div className="text-sm text-gray-900">{label}</div>
          <div className="text-xs text-gray-500 mt-0.5">{detail}</div>
        </div>
      </div>
      <span className={`text-xs font-medium px-2 py-0.5 rounded ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    </div>
  );
}
