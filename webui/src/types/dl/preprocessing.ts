// 深度学习数据预处理相关类型定义

export type DataSourceType = 'database' | 'parquet' | 'csv';
export type NormalizationMethod = 'zscore' | 'minmax' | 'robust' | 'rankgauss';

// 特征分组定义
export interface FeatureItem {
  id: string;
  name: string;
  description: string;
}

export interface FeatureGroup {
  name: string;
  features: FeatureItem[];
}

// 所有可用特征列表 (38 个特征)
export const AVAILABLE_FEATURES: FeatureGroup[] = [
  {
    name: '价格类特征',
    features: [
      { id: 'open', name: 'open', description: '开盘价' },
      { id: 'high', name: 'high', description: '最高价' },
      { id: 'low', name: 'low', description: '最低价' },
      { id: 'close', name: 'close', description: '收盘价' },
      { id: 'volume', name: 'volume', description: '成交量' },
      { id: 'price_change', name: 'price_change', description: '价格变化' },
      { id: 'price_change_pct', name: 'price_change_pct', description: '价格变化率' },
      { id: 'high_low_range', name: 'high_low_range', description: '高低点范围' },
      { id: 'open_close_diff', name: 'open_close_diff', description: '开盘收盘差' },
    ],
  },
  {
    name: '移动平均线',
    features: [
      { id: 'ma5', name: 'ma5', description: '5 日均线' },
      { id: 'ma10', name: 'ma10', description: '10 日均线' },
      { id: 'ma20', name: 'ma20', description: '20 日均线' },
      { id: 'ma60', name: 'ma60', description: '60 日均线' },
    ],
  },
  {
    name: '趋势指标',
    features: [
      { id: 'macd', name: 'macd', description: 'MACD 指标' },
      { id: 'macd_signal', name: 'macd_signal', description: 'MACD 信号线' },
      { id: 'macd_histogram', name: 'macd_histogram', description: 'MACD 柱状图' },
      { id: 'adx14', name: 'adx14', description: 'ADX 趋势强度' },
      { id: 'sar', name: 'sar', description: '抛物线 SAR' },
    ],
  },
  {
    name: '动量指标',
    features: [
      { id: 'rsi14', name: 'rsi14', description: 'RSI 相对强弱指标' },
      { id: 'roc12', name: 'roc12', description: 'ROC 变化率' },
      { id: 'cci20', name: 'cci20', description: 'CCI 商品通道指标' },
      { id: 'stoch_k', name: 'stoch_k', description: 'KDJ 的 K 值' },
      { id: 'stoch_d', name: 'stoch_d', description: 'KDJ 的 D 值' },
      { id: 'stoch_j', name: 'stoch_j', description: 'KDJ 的 J 值' },
    ],
  },
  {
    name: '波动率指标',
    features: [
      { id: 'atr14', name: 'atr14', description: 'ATR 平均真实波幅' },
      { id: 'volatility_20', name: 'volatility_20', description: '20 日波动率' },
    ],
  },
  {
    name: '成交量指标',
    features: [
      { id: 'volume_ratio', name: 'volume_ratio', description: '成交量比率' },
    ],
  },
  {
    name: '布林带指标',
    features: [
      { id: 'boll_width', name: 'boll_width', description: '布林带宽度' },
      { id: 'close_vs_boll', name: 'close_vs_boll', description: '收盘价相对布林带位置' },
    ],
  },
  {
    name: '位置特征',
    features: [
      { id: 'close_vs_ma20', name: 'close_vs_ma20', description: '收盘价相对 MA20 位置' },
      { id: 'close_vs_ma60', name: 'close_vs_ma60', description: '收盘价相对 MA60 位置' },
    ],
  },
  {
    name: '滞后特征',
    features: [
      { id: 'close_lag_1', name: 'close_lag_1', description: '收盘价滞后 1 期' },
      { id: 'close_lag_5', name: 'close_lag_5', description: '收盘价滞后 5 期' },
      { id: 'close_lag_10', name: 'close_lag_10', description: '收盘价滞后 10 期' },
      { id: 'return_lag_1', name: 'return_lag_1', description: '收益率滞后 1 期' },
      { id: 'return_lag_5', name: 'return_lag_5', description: '收益率滞后 5 期' },
      { id: 'return_lag_10', name: 'return_lag_10', description: '收益率滞后 10 期' },
    ],
  },
];

// 标准化方法配置
export interface NormalizationConfig {
  method: NormalizationMethod;
  params?: {
    // Min-Max 特定参数
    min?: number;
    max?: number;
    // Robust 特定参数
    median?: number;
    iqr?: number;
  };
}

// 数据源配置
export interface DataSourceConfig {
  type: DataSourceType;
  // 数据库连接配置
  db_host?: string;
  db_port?: number;
  db_name?: string;
  db_user?: string;
  db_password?: string;
  db_table?: string;
  // 文件路径配置
  file_path?: string;
  // 时间范围
  start_date: string;
  end_date: string;
}

// 预处理配置
export interface PreprocessingConfig {
  id?: string;
  name: string;
  description?: string;
  data_source: DataSourceConfig;
  selected_features: string[];
  normalization: NormalizationConfig;
  // 高级选项
  handle_missing: 'drop' | 'fill_mean' | 'fill_median' | 'fill_zero';
  handle_outliers: 'none' | 'clip' | 'remove';
  outlier_threshold?: number; // 标准差倍数
  created_at?: string;
  updated_at?: string;
}

// 特征统计信息
export interface FeatureStatistics {
  feature_name: string;
  mean: number;
  std: number;
  min: number;
  max: number;
  missing_rate: number;
  outlier_rate?: number;
}

// 数据预览响应
export interface DataPreviewResponse {
  total_rows: number;
  columns: string[];
  data: Record<string, any>[];
  statistics: FeatureStatistics[];
}

// 数据统计响应
export interface DataStatsResponse {
  total_rows: number;
  date_range: {
    start: string;
    end: string;
  };
  feature_count: number;
  missing_rate: number;
  statistics: FeatureStatistics[];
}

// 预处理任务状态
export type PreprocessingStatus = 'idle' | 'running' | 'completed' | 'error';

export interface PreprocessingProgress {
  current_step: number;
  total_steps: number;
  current_action: string;
  eta_seconds: number;
}

export interface PreprocessingTask {
  task_id: string;
  config: PreprocessingConfig;
  status: PreprocessingStatus;
  progress: PreprocessingProgress | null;
  result?: {
    output_path: string;
    processed_rows: number;
    feature_count: number;
    processing_time_seconds: number;
  };
  error?: string;
  created_at: string;
  updated_at: string;
}

// API 请求/响应类型
export interface GetFeaturesResponse {
  features: FeatureGroup[];
  total_count: number;
}

export interface SavePreprocessingConfigRequest {
  config: PreprocessingConfig;
}

export interface SavePreprocessingConfigResponse {
  config_id: string;
  status: 'success' | 'error';
  message?: string;
}

export interface LoadPreprocessingConfigRequest {
  config_id: string;
}

export interface LoadPreprocessingConfigResponse extends PreprocessingConfig {}

export interface ApplyPreprocessingRequest {
  config: PreprocessingConfig;
}

export interface ApplyPreprocessingResponse {
  task_id: string;
  status: 'started' | 'error';
  message?: string;
}

export interface GetPreprocessingStatusResponse {
  task_id: string;
  status: PreprocessingStatus;
  progress: PreprocessingProgress | null;
  result?: PreprocessingTask['result'];
  error?: string;
}
