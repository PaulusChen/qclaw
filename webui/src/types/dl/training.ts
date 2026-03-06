// 深度学习训练相关类型定义

export type ModelType = 'lstm' | 'transformer';
export type OptimizerType = 'adam' | 'adamw' | 'sgd';
export type LRSchedulerType = 'cosine' | 'plateau' | 'step' | 'one_cycle';
export type TrainingStatus = 'idle' | 'running' | 'paused' | 'completed' | 'error';

export interface ModelPreset {
  name: string;
  description: string;
  params: {
    hidden_size?: number;
    d_model?: number;
    num_heads?: number;
    num_layers: number;
    dropout: number;
    bidirectional?: boolean;
  };
}

export interface TrainingConfig {
  // 模型参数
  model_type: ModelType;
  hidden_size?: number;
  d_model?: number;
  num_heads?: number;
  num_layers: number;
  dropout: number;
  bidirectional?: boolean;
  
  // 训练参数
  batch_size: number;
  learning_rate: number;
  epochs: number;
  optimizer: OptimizerType;
  lr_scheduler: LRSchedulerType;
  
  // 高级选项
  mixed_precision: boolean;
  gradient_clip: number;
  early_stopping_patience: number;
  use_pretrained: boolean;
  pretrained_model_path?: string;
  
  // 数据配置
  data_source: string;
  start_date: string;
  end_date: string;
  train_ratio: number;
  val_ratio: number;
  test_ratio: number;
}

export interface TrainingProgress {
  current_epoch: number;
  total_epochs: number;
  eta_seconds: number;
}

export interface TrainingMetrics {
  train_loss: number;
  val_loss: number;
  val_accuracy?: number;
  train_accuracy?: number;
}

export interface TrainingState {
  status: TrainingStatus;
  progress: TrainingProgress | null;
  metrics: TrainingMetrics | null;
  learning_rates: number[];
  train_loss_history: number[];
  val_loss_history: number[];
}

export interface TrainingLog {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
}

export interface TrainingTask {
  task_id: string;
  config: TrainingConfig;
  state: TrainingState;
  logs: TrainingLog[];
  created_at: string;
  updated_at: string;
}

export interface StartTrainingResponse {
  task_id: string;
  status: string;
}

export interface TrainingStatusResponse {
  status: TrainingStatus;
  progress: TrainingProgress;
  metrics: TrainingMetrics;
}

export interface TrainingLogsResponse {
  logs: TrainingLog[];
  total: number;
}
