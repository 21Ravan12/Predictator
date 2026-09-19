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
    { label: 'Total Predicted', value: data.summary.total_predicted, color: 'indigo' },
    { label: 'Average Daily', value: data.summary.average_daily, color: 'green' },
    { label: 'Peak Day', value: data.summary.peak_day, color: 'yellow' },
    { label: 'Floor Violations', value: data.summary.floor_violations, color: 'red' },
  ];

  const colors = {
    indigo: 'border-indigo-500',
    green: 'border-green-500',
    yellow: 'border-yellow-500',
    red: 'border-red-500',
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className={`bg-white p-4 rounded-lg shadow-sm border-l-4 ${colors[metric.color as keyof typeof colors]}`}
        >
          <p className="text-sm text-gray-500">{metric.label}</p>
          <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
        </div>
      ))}
    </div>
  );
}
