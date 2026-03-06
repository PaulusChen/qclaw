// 深度学习训练 API 服务
import axios from 'axios';
import type {
  TrainingConfig,
  StartTrainingResponse,
  TrainingStatusResponse,
  TrainingLogsResponse,
  TrainingLog,
} from '../../types/dl';

const API_BASE = '/api/v1/dl';

export const trainingApi = {
  /**
   * 启动训练任务
   */
  async startTraining(config: TrainingConfig): Promise<StartTrainingResponse> {
    const response = await axios.post(`${API_BASE}/training/start`, { config });
    return response.data;
  },

  /**
   * 获取训练状态
   */
  async getTrainingStatus(taskId: string): Promise<TrainingStatusResponse> {
    const response = await axios.get(`${API_BASE}/training/${taskId}/status`);
    return response.data;
  },

  /**
   * 停止训练任务
   */
  async stopTraining(taskId: string): Promise<void> {
    await axios.post(`${API_BASE}/training/${taskId}/stop`);
  },

  /**
   * 获取训练日志
   */
  async getTrainingLogs(taskId: string, lines = 100): Promise<TrainingLogsResponse> {
    const response = await axios.get(`${API_BASE}/training/${taskId}/logs`, {
      params: { lines },
    });
    return response.data;
  },

  /**
   * 创建 WebSocket 连接用于实时训练监控
   */
  createTrainingWebSocket(taskId: string): WebSocket {
    const wsUrl = `ws://${window.location.host}${API_BASE}/training/${taskId}/ws`;
    return new WebSocket(wsUrl);
  },
};

export default trainingApi;
