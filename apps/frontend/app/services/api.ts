const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';

// ============================================
// 📊 TYPES
// ============================================

export interface Prediction {
  date: string;
  predicted_sales: number;
  confidence_lower: number;
  confidence_upper: number;
  alert: string | null;
}

export interface PredictionSummary {
  total_predicted: number;
  average_daily: number;
  peak_day: number;
  floor_violations: number;
}

export interface DictatorAction {
  day: number;
  message: string;
}

export interface PredictionResponse {
  success: boolean;
  product_id: string;
  predictions: Prediction[];
  summary: PredictionSummary;
  dictator_actions: DictatorAction[];
}

// Wrapper from NestJS TransformInterceptor
interface NestJSResponse<T> {
  success: boolean;
  data: T;
  timestamp: string;
  path: string;
  duration: number;
}

// ============================================
// 🚀 API FUNCTIONS
// ============================================

export async function generatePredictions(
  productId: string,
  daysAhead: number,
  floorLimit: number = 0
): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE}/api/predictions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      productId,      // ← NestJS expects camelCase!
      daysAhead,
      floorLimit,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to generate predictions');
  }

  const json: NestJSResponse<PredictionResponse> = await response.json();
  
  // 🔥 UNWRAP the NestJS wrapper!
  return json.data;
}

export async function trainModel(csvPath?: string, forceRetrain: boolean = true) {
  const response = await fetch(`${API_BASE}/api/predictions/train`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      csvPath,
      forceRetrain,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to train model');
  }

  const json = await response.json();
  return json.data;
}

export async function getTrainingStatus() {
  const response = await fetch(`${API_BASE}/api/predictions/status`);
  if (!response.ok) {
    throw new Error('Failed to get training status');
  }
  const json = await response.json();
  return json.data;
}

export async function getProducts() {
  const response = await fetch(`${API_BASE}/api/predictions/products`);
  if (!response.ok) {
    throw new Error('Failed to get products');
  }
  const json = await response.json();
  return json.data;
}
