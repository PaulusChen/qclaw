// 深度学习推理 API 服务
import axios from 'axios';
import type {
  PredictionRequest,
  BatchPredictionRequest,
  PredictionResult,
  BatchPredictionResult,
  ModelsListResponse,
  ModelInfo,
  PredictionHistory,
  AccuracyTrend,
} from '../../types/dl';

const API_BASE = '/api/v1/dl';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 单次预测
 */
export const predictSingle = async (request: PredictionRequest): Promise<PredictionResult> => {
  const response = await api.post<PredictionResult>('/predict/single', request);
  return response.data;
};

/**
 * 批量预测
 */
export const predictBatch = async (request: BatchPredictionRequest): Promise<{ task_id: string }> => {
  const response = await api.post<{ task_id: string }>('/predict/batch', request);
  return response.data;
};

/**
 * 获取批量预测任务状态
 */
export const getBatchPredictionStatus = async (taskId: string): Promise<BatchPredictionResult> => {
  const response = await api.get<BatchPredictionResult>(`/predict/batch/${taskId}/status`);
  return response.data;
};

/**
 * 获取模型列表
 */
export const getModels = async (): Promise<ModelsListResponse> => {
  const response = await api.get<ModelsListResponse>('/models');
  return response.data;
};

/**
 * 获取模型详情
 */
export const getModelDetail = async (version: string): Promise<ModelInfo> => {
  const response = await api.get<ModelInfo>(`/models/${version}`);
  return response.data;
};

/**
 * 激活模型
 */
export const activateModel = async (version: string): Promise<void> => {
  await api.post(`/models/${version}/activate`);
};

/**
 * 获取预测历史
 */
export const getPredictionHistory = async (
  stockCode: string,
  limit: number = 30
): Promise<PredictionHistory[]> => {
  const response = await api.get<PredictionHistory[]>(`/predictions/history/${stockCode}`, {
    params: { limit },
  });
  return response.data;
};

/**
 * 获取准确率趋势
 */
export const getAccuracyTrend = async (
  modelVersion: string,
  days: number = 30
): Promise<AccuracyTrend[]> => {
  const response = await api.get<AccuracyTrend[]>(`/models/${modelVersion}/accuracy-trend`, {
    params: { days },
  });
  return response.data;
};

/**
 * 导出预测结果
 */
export const exportPredictions = async (taskIds: string[]): Promise<{ download_url: string }> => {
  const response = await api.post<{ download_url: string }>('/predictions/export', { task_ids: taskIds });
  return response.data;
};

export const inferenceApi = {
  predictSingle,
  predictBatch,
  getBatchPredictionStatus,
  getModels,
  getModelDetail,
  activateModel,
  getPredictionHistory,
  getAccuracyTrend,
  exportPredictions,
};
