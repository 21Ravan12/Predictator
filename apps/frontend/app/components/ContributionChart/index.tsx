'use client';

interface ContributionChartProps {
  features?: Array<{ name: string; importance: number }>;
}

export default function ContributionChart({ features = [] }: ContributionChartProps) {
  if (!features || features.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <h3 className="font-semibold text-gray-800 mb-3">📊 Feature Importance</h3>
        <p className="text-sm text-gray-500">No feature data available</p>
      </div>
    );
  }

  const maxImportance = Math.max(...features.map(f => f.importance));

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
      <h3 className="font-semibold text-gray-800 mb-3">📊 Feature Importance</h3>
      <div className="space-y-2">
        {features.slice(0, 8).map((feature, idx) => (
          <div key={idx}>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">{feature.name}</span>
              <span className="text-gray-500">{(feature.importance * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 rounded-full h-2 transition-all"
                style={{ width: `${(feature.importance / maxImportance) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
