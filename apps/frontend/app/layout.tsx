import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navbar from './components/Navbar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '🚀 Predictator - Sales Forecasting',
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
        <Navbar />
        <main className="min-h-screen bg-gray-50">{children}</main>
        <footer className="text-center text-sm text-gray-500 py-4 border-t border-gray-200 bg-white">
          Predictator v2.0 — Built with ❤️, XGBoost, and Next.js
        </footer>
      </body>
    </html>
  );
}
