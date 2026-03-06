// 深度学习数据预处理 API 服务

import axios from 'axios';
import type {
  GetFeaturesResponse,
  DataStatsResponse,
  DataPreviewResponse,
  PreprocessingConfig,
  SavePreprocessingConfigRequest,
  SavePreprocessingConfigResponse,
  LoadPreprocessingConfigResponse,
  ApplyPreprocessingRequest,
  ApplyPreprocessingResponse,
  GetPreprocessingStatusResponse,
} from '@/types/dl/preprocessing';

const API_BASE = '/api/v1/dl';

/**
 * 获取可用特征列表
 */
export const getFeatures = async (): Promise<GetFeaturesResponse> => {
  const response = await axios.get(`${API_BASE}/features`);
  return response.data;
};

/**
 * 获取数据统计信息
 */
export const getDataStats = async (
  source: string,
  startDate: string,
  endDate: string
): Promise<DataStatsResponse> => {
  const response = await axios.get(`${API_BASE}/data/stats`, {
    params: { source, start: startDate, end: endDate },
  });
  return response.data;
};

/**
 * 预览数据
 */
export const previewData = async (
  source: string,
  limit: number = 100
): Promise<DataPreviewResponse> => {
  const response = await axios.get(`${API_BASE}/data/preview`, {
    params: { source, limit },
  });
  return response.data;
};

/**
 * 保存预处理配置
 */
export const savePreprocessingConfig = async (
  config: PreprocessingConfig
): Promise<SavePreprocessingConfigResponse> => {
  const response = await axios.post<SavePreprocessingConfigResponse>(
    `${API_BASE}/preprocessing/config`,
    { config } as SavePreprocessingConfigRequest
  );
  return response.data;
};

/**
 * 加载预处理配置
 */
export const loadPreprocessingConfig = async (
  configId: string
): Promise<LoadPreprocessingConfigResponse> => {
  const response = await axios.get<LoadPreprocessingConfigResponse>(
    `${API_BASE}/preprocessing/config/${configId}`
  );
  return response.data;
};

/**
 * 获取已保存的配置列表
 */
export const listPreprocessingConfigs = async (): Promise<
  Array<{
    id: string;
    name: string;
    description?: string;
    updated_at: string;
  }>
> => {
  const response = await axios.get(`${API_BASE}/preprocessing/configs`);
  return response.data;
};

/**
 * 应用预处理
 */
export const applyPreprocessing = async (
  config: PreprocessingConfig
): Promise<ApplyPreprocessingResponse> => {
  const response = await axios.post<ApplyPreprocessingResponse>(
    `${API_BASE}/preprocessing/apply`,
    { config } as ApplyPreprocessingRequest
  );
  return response.data;
};

/**
 * 获取预处理任务状态
 */
export const getPreprocessingStatus = async (
  taskId: string
): Promise<GetPreprocessingStatusResponse> => {
  const response = await axios.get<GetPreprocessingStatusResponse>(
    `${API_BASE}/preprocessing/${taskId}/status`
  );
  return response.data;
};

/**
 * 取消预处理任务
 */
export const cancelPreprocessing = async (
  taskId: string
): Promise<{ status: 'cancelled' | 'error'; message?: string }> => {
  const response = await axios.post(`${API_BASE}/preprocessing/${taskId}/cancel`);
  return response.data;
};
