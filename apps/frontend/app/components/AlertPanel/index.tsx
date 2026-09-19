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
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <span className="text-xl">⚠️</span>
        <div>
          <h3 className="font-semibold text-amber-800">Dictator Alerts</h3>
          <ul className="mt-2 space-y-1">
            {alerts.map((alert, idx) => (
              <li key={idx} className="text-sm text-amber-700">
                Day {alert.day}: {alert.message}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
