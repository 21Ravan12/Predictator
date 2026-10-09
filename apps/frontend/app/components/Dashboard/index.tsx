// app/components/Dashboard/index.tsx

interface DashboardProps {
  data: {
    summary: {
      total_predicted: number;
      average_daily: number;
      peak_day: number;
      floor_violations: number;
    };
    product_id: string;
  };
}

export default function Dashboard({ data }: DashboardProps) {
  const metrics = [
    {
      label: 'Total Predicted',
      value: Math.round(data.summary.total_predicted).toLocaleString(),
      subtext: `${data.product_id} • Forecast period`,
      icon: '📊',
    },
    {
      label: 'Average Daily',
      value: Math.round(data.summary.average_daily).toLocaleString(),
      subtext: 'Units per day',
      icon: '📈',
    },
    {
      label: 'Peak Day',
      value: Math.round(data.summary.peak_day).toLocaleString(),
      subtext: 'Highest single-day forecast',
      icon: '🎯',
    },
    {
      label: 'Floor Violations',
      value: data.summary.floor_violations.toString(),
      subtext: data.summary.floor_violations > 0 ? 'Requires attention' : 'All clear',
      icon: '⚠️',
      warning: data.summary.floor_violations > 0,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="bg-white rounded-lg border border-gray-200 p-5"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {metric.label}
            </span>
            <span className="text-base">{metric.icon}</span>
          </div>
          <div
            className={`text-2xl font-semibold ${
              metric.warning ? 'text-amber-600' : 'text-gray-900'
            }`}
          >
            {metric.value}
          </div>
          <div className="text-xs text-gray-500 mt-1 truncate">
            {metric.subtext}
          </div>
        </div>
      ))}
    </div>
  );
}
