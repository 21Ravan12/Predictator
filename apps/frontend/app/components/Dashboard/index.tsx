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
      color: 'indigo',
      icon: '📊',
    },
    {
      label: 'Average Daily',
      value: Math.round(data.summary.average_daily).toLocaleString(),
      color: 'green',
      icon: '📈',
    },
    {
      label: 'Peak Day',
      value: Math.round(data.summary.peak_day).toLocaleString(),
      color: 'yellow',
      icon: '🎯',
    },
    {
      label: 'Floor Violations',
      value: data.summary.floor_violations,
      color: 'red',
      icon: '⚠️',
    },
  ];

  const colors = {
    indigo: 'border-indigo-500 text-indigo-600',
    green: 'border-green-500 text-green-600',
    yellow: 'border-yellow-500 text-yellow-600',
    red: 'border-red-500 text-red-600',
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className={`bg-white p-4 rounded-lg shadow-sm border-l-4 ${colors[metric.color as keyof typeof colors]}`}
        >
          <div className="flex items-center gap-2">
            <span>{metric.icon}</span>
            <p className="text-sm text-gray-500">{metric.label}</p>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {metric.value}
          </p>
        </div>
      ))}
    </div>
  );
}