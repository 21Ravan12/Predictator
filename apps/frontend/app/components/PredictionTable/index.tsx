// app/components/PredictionTable/index.tsx

interface Prediction {
  date: string;
  predicted_sales: number;
  confidence_lower: number;
  confidence_upper: number;
  alert: string | null;
}

interface PredictionTableProps {
  predictions: Prediction[];
}

export default function PredictionTable({ predictions }: PredictionTableProps) {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-sm text-gray-500">
        No predictions available
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">
          Forecast Details
        </h3>
        <p className="text-xs text-gray-500 mt-0.5">
          {predictions.length} day forecast
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-5 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                Date
              </th>
              <th className="px-5 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                Predicted
              </th>
              <th className="px-5 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                Confidence Range
              </th>
              <th className="px-5 py-2.5 text-center text-xs font-medium text-gray-500 uppercase tracking-wide">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {predictions.map((pred, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition">
                <td className="px-5 py-3 font-medium text-gray-900">
                  {new Date(pred.date).toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                  })}
                </td>
                <td className="px-5 py-3 text-right font-semibold text-gray-900">
                  {Math.round(pred.predicted_sales)}
                </td>
                <td className="px-5 py-3 text-right text-gray-600 font-mono text-xs">
                  {Math.round(pred.confidence_lower)} — {Math.round(pred.confidence_upper)}
                </td>
                <td className="px-5 py-3 text-center">
                  {pred.alert ? (
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                      ⚠️ Alert
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-50 px-2 py-0.5 rounded">
                      ● OK
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
