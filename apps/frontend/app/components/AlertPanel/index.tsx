// app/components/AlertPanel/index.tsx

interface Alert {
  day: number;
  message: string;
}

interface AlertPanelProps {
  alerts: Alert[];
}

export default function AlertPanel({ alerts }: AlertPanelProps) {
  if (!alerts || alerts.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg border border-amber-200 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 bg-amber-50 border-b border-amber-200 flex items-center gap-2">
        <span className="text-base">⚠️</span>
        <h3 className="text-sm font-semibold text-amber-900">
          Dictator Alerts
        </h3>
        <span className="text-xs font-medium bg-amber-200 text-amber-800 px-1.5 py-0.5 rounded">
          {alerts.length}
        </span>
      </div>

      {/* List */}
      <ul className="divide-y divide-gray-100">
        {alerts.map((alert, idx) => (
          <li key={idx} className="px-5 py-3 flex items-start gap-3">
            <span className="text-xs font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded shrink-0">
              Day {alert.day}
            </span>
            <span className="text-sm text-gray-700">
              {alert.message}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
