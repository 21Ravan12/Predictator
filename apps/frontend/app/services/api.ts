const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface PredictRequest {
  product_id: string;
  days_ahead: number;
  floor_limit?: number;
}

export interface PredictResponse {
  success: boolean;
  product_id: string;
  predictions: Array<{
    date: string;
    predicted_sales: number;
    confidence_lower: number;
    confidence_upper: number;
    alert: string | null;
  }>;
  summary: {
    total_predicted: number;
    average_daily: number;
    peak_day: number;
    floor_violations: number;
  };
  dictator_actions?: Array<{
    day: number;
    message: string;
  }>;
}

export async function generatePredictions(
  productId: string,
  daysAhead: number,
  floorLimit: number = 0
): Promise<PredictResponse> {
  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      product_id: productId,
      days_ahead: daysAhead,
      floor_limit: floorLimit,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate predictions');
  }

  return response.json();
}

export async function trainModel(csvPath?: string, forceRetrain: boolean = true) {
  const response = await fetch(`${API_BASE}/train`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      csv_path: csvPath,
      force_retrain: forceRetrain,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to train model');
  }

  return response.json();
}

export async function getTrainingStatus() {
  const response = await fetch(`${API_BASE}/train/status`);
  if (!response.ok) {
    throw new Error('Failed to get training status');
  }
  return response.json();
}
