// 深度学习模型管理相关类型定义

export type ModelType = 'lstm' | 'transformer';
export type ModelStatus = 'active' | 'archived' | 'deleted';

export interface ModelMetrics {
  val_accuracy: number;
  val_loss: number;
  test_accuracy?: number;
  test_loss?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_return?: number;
  win_rate?: number;
}

export interface ModelParams {
  // Transformer 参数
  d_model?: number;
  num_heads?: number;
  num_layers?: number;
  d_ff?: number;
  dropout?: number;
  activation?: string;
  
  // LSTM 参数
  hidden_size?: number;
  num_lstm_layers?: number;
  bidirectional?: boolean;
  
  // 通用参数
  input_size?: number;
  output_size?: number;
}

export interface TrainingConfig {
  data_source: string;
  start_date: string;
  end_date: string;
  batch_size: number;
  learning_rate: number;
  epochs: number;
  optimizer: string;
  lr_scheduler: string;
  early_stopping_patience: number;
  train_samples: number;
  val_samples: number;
  test_samples: number;
}

export interface ModelInfo {
  version: string;
  name?: string;
  description?: string;
  type: ModelType;
  status: ModelStatus;
  created_at: string;
  updated_at: string;
  file_path: string;
  file_size_mb: number;
  metrics: ModelMetrics;
  params: ModelParams;
  training_config: TrainingConfig;
  tags?: string[];
}

export interface ModelComparison {
  versions: string[];
  metrics_comparison: Record<string, Record<string, number>>;
  params_comparison: Record<string, Record<string, number | string>>;
  ranking: Array<{
    version: string;
    rank: number;
    score: number;
  }>;
}

export interface ModelsListResponse {
  models: ModelInfo[];
  total: number;
  active_count: number;
  archived_count: number;
}

export interface ModelDetailResponse extends ModelInfo {
  training_history?: {
    epoch: number;
    train_loss: number;
    val_loss: number;
    train_accuracy?: number;
    val_accuracy?: number;
    learning_rate: number;
  }[];
  feature_importance?: Array<{
    feature_name: string;
    importance: number;
  }>;
}

export interface ActivateModelRequest {
  version: string;
}

export interface ArchiveModelRequest {
  version: string;
}

export interface DeleteModelRequest {
  version: string;
  confirm: boolean;
}

export interface ExportModelRequest {
  version: string;
  format?: 'onnx' | 'torchscript' | 'safetensors';
}

export interface ExportModelResponse {
  download_url: string;
  expires_at: string;
  file_size_mb: number;
}

export interface ImportModelRequest {
  file: File;
  metadata?: {
    name?: string;
    description?: string;
    tags?: string[];
  };
}

export interface ImportModelResponse {
  version: string;
  status: 'success' | 'error';
  message?: string;
}

export interface CompareModelsRequest {
  versions: string[];
}

export interface CompareModelsResponse extends ModelComparison {}
