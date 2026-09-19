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
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Predicted Sales
              </th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Confidence Range
              </th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Alert
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {predictions.map((pred, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition">
                <td className="px-6 py-3 text-sm font-medium text-gray-900">
                  {new Date(pred.date).toLocaleDateString('en-US', { 
                    weekday: 'short',
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </td>
                <td className="px-6 py-3 text-sm font-bold text-indigo-600">
                  {pred.predicted_sales}
                </td>
                <td className="px-6 py-3 text-sm text-gray-600">
                  {pred.confidence_lower} — {pred.confidence_upper}
                </td>
                <td className="px-6 py-3 text-sm">
                  {pred.alert ? (
                    <span className="inline-flex items-center gap-1 text-amber-600">
                      ⚠️ {pred.alert}
                    </span>
                  ) : (
                    <span className="text-green-600">✅ OK</span>
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
