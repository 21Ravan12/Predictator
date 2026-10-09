// app/components/PredictionChart/index.tsx
'use client';

import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';

interface Prediction {
  date: string;
  predicted_sales: number;
  confidence_lower: number;
  confidence_upper: number;
}

interface PredictionChartProps {
  predictions: Prediction[];
}

export default function PredictionChart({ predictions }: PredictionChartProps) {
  const data = predictions.map((p) => ({
    date: new Date(p.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    sales: Math.round(p.predicted_sales),
    lower: Math.round(p.confidence_lower),
    upper: Math.round(p.confidence_upper),
  }));

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">
          Forecast Trend
        </h3>
        <p className="text-xs text-gray-500 mt-0.5">
          Predicted sales over the forecast period
        </p>
      </div>

      {/* Chart */}
      <div className="p-5">
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="date"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '12px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}
            />
            <Area
              type="monotone"
              dataKey="sales"
              stroke="#6366f1"
              strokeWidth={2}
              fill="url(#colorSales)"
              name="Predicted Sales"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
