import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Link from 'next/link';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '🚀 Predictator - Sales Forecasting Dashboard',
  description: 'AI-powered sales predictions with XGBoost',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {/* Navigation */}
        <nav className="bg-indigo-600 text-white shadow-lg sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition">
                <span className="text-2xl">🚀</span>
                <span className="text-xl font-bold">Predictator</span>
                <span className="text-xs bg-indigo-500 px-2 py-0.5 rounded-full">v2.0</span>
              </Link>
              <div className="flex items-center gap-6">
                <Link href="/" className="hover:text-indigo-200 transition">Dashboard</Link>
                <Link href="/settings" className="hover:text-indigo-200 transition">⚙️ Settings</Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>

        {/* Footer */}
        <footer className="text-center text-sm text-gray-500 py-4 border-t border-gray-200 bg-white">
          Predictator v2.0 — Built with ❤️, XGBoost, and Next.js
        </footer>
      </body>
    </html>
  );
}
