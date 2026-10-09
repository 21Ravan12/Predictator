'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/', label: 'Dashboard', icon: '📊' },
  { href: '/predictions', label: 'Predictions', icon: '🔮' },
  { href: '/products', label: 'Products', icon: '📦' },
  { href: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14 items-center">

          {/* ============================================ */}
          {/* 🚀 LOGO */}
          {/* ============================================ */}
          <Link
            href="/"
            className="flex items-center gap-2 hover:opacity-80 transition"
          >
            <span className="text-xl">🚀</span>
            <span className="text-base font-semibold text-gray-900">
              Predictator
            </span>
            <span className="text-[10px] font-medium bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
              v2.0
            </span>
          </Link>

          {/* ============================================ */}
          {/* 📍 NAV LINKS */}
          {/* ============================================ */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const isActive =
                item.href === '/'
                  ? pathname === '/'
                  : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-1.5 rounded-md text-sm transition flex items-center gap-2 ${
                    isActive
                      ? 'bg-gray-100 text-gray-900 font-medium'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <span className="text-base">{item.icon}</span>
                  <span className="hidden md:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* ============================================ */}
          {/* 👤 ADMIN AVATAR */}
          {/* ============================================ */}
          <div className="hidden md:flex items-center gap-3">
            <div className="w-px h-6 bg-gray-200"></div>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center">
                <span className="text-xs font-semibold text-indigo-700">
                  AD
                </span>
              </div>
              <span className="text-sm text-gray-700 hidden lg:inline">
                Admin
              </span>
            </div>
          </div>

        </div>
      </div>
    </nav>
  );
}