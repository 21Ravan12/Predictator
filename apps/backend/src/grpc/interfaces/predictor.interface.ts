// TypeScript interfaces for gRPC communication

export interface PredictionRequest {
  product_id: string;
  days_ahead: number;
  floor_limit: number;
}

export interface PredictionResponse {
  success: boolean;
  product_id: string;
  predictions: Prediction[];
  summary: Summary;
  dictator_actions: DictatorAction[];
}

export interface Prediction {
  date: string;
  predicted_sales: number;
  confidence_lower: number;
  confidence_upper: number;
  alert: string;
}

export interface Summary {
  total_predicted: number;
  average_daily: number;
  peak_day: number;
  floor_violations: number;
}

export interface DictatorAction {
  day: number;
  message: string;
}

export interface TrainRequest {
  csv_path: string;
  force_retrain: boolean;
}

export interface TrainResponse {
  success: boolean;
  message: string;
  samples_used: number;
  metrics: {
    r2: number;
    mae: number;
    rmse: number;
    n_features: number;
  };
}

export interface TrainingStatusResponse {
  is_trained: boolean;
  last_training_date: string;
  metrics: {
    r2: number;
    mae: number;
    rmse: number;
    n_features: number;
  };
}

export interface GRPCConnectionStatus {
  connected: boolean;
  error: string | null;
}
