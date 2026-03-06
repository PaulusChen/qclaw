// 深度学习推理相关类型定义

export type PredictionDirection = 'up' | 'down';
export type PredictionSignal = 'buy' | 'hold' | 'sell';
export type PredictionHorizon = 1 | 3 | 5 | 7 | 14 | 30;

export interface PredictionRequest {
  stock_code: string;
  date: string;
  model_version: string;
  horizons: PredictionHorizon[];
}

export interface BatchPredictionRequest {
  stock_codes: string[];
  date: string;
  model_version: string;
  horizons?: PredictionHorizon[];
}

export interface SinglePrediction {
  direction: PredictionDirection;
  direction_prob: number;
  return_pred: number;
  return_ci: [number, number]; // 置信区间
  signal: PredictionSignal;
  confidence: number;
}

export interface MultiHorizonPrediction {
  horizon: PredictionHorizon;
  direction: PredictionDirection;
  direction_prob: number;
  return_pred: number;
  signal: PredictionSignal;
  confidence: number;
}

export interface FeatureImportance {
  name: string;
  importance: number;
  contribution: 'positive' | 'negative';
}

export interface PredictionResult {
  stock_code: string;
  stock_name: string;
  predict_date: string;
  model_version: string;
  inference_time_ms: number;
  prediction: SinglePrediction;
  multi_horizon: MultiHorizonPrediction[];
  feature_importance: FeatureImportance[];
  key_insights: string[];
}

export interface BatchPredictionResult {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  total: number;
  completed: number;
  results: PredictionResult[];
  created_at: string;
  completed_at?: string;
}

export interface ModelInfo {
  version: string;
  type: 'lstm' | 'transformer';
  created_at: string;
  is_active: boolean;
  metrics: {
    val_accuracy: number;
    val_loss: number;
    test_accuracy?: number;
    sharpe_ratio?: number;
    max_drawdown?: number;
  };
  params: {
    d_model?: number;
    num_heads?: number;
    num_layers: number;
    hidden_size?: number;
  };
}

export interface ModelsListResponse {
  models: ModelInfo[];
  total: number;
}

export interface PredictionHistory {
  date: string;
  stock_code: string;
  predicted_direction: PredictionDirection;
  actual_direction?: PredictionDirection;
  predicted_return: number;
  actual_return?: number;
  is_correct?: boolean;
}

export interface AccuracyTrend {
  date: string;
  accuracy: number;
  cumulative_accuracy: number;
  total_predictions: number;
}
