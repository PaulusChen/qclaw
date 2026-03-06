// 深度学习数据预处理状态管理 (Zustand)

import { StateCreator } from 'zustand';
import * as api from '@/services/dl/preprocessingApi';
import type {
  FeatureGroup,
  PreprocessingConfig,
  PreprocessingTask,
  PreprocessingStatus,
  DataStatsResponse,
  DataPreviewResponse,
} from '@/types/dl/preprocessing';

// 状态接口
export interface PreprocessingState {
  // 可用特征
  availableFeatures: FeatureGroup[];
  featuresLoaded: boolean;
  
  // 当前配置
  currentConfig: PreprocessingConfig | null;
  
  // 数据统计
  dataStats: DataStatsResponse | null;
  dataPreview: DataPreviewResponse | null;
  
  // 预处理任务
  currentTask: PreprocessingTask | null;
  taskStatus: PreprocessingStatus;
  
  // 已保存的配置列表
  savedConfigs: Array<{
    id: string;
    name: string;
    description?: string;
    updated_at: string;
  }>;
  
  // Actions
  loadFeatures: () => Promise<void>;
  updateConfig: (updates: Partial<PreprocessingConfig>) => void;
  setConfig: (config: PreprocessingConfig) => void;
  resetConfig: () => void;
  
  loadDataStats: (source: string, startDate: string, endDate: string) => Promise<void>;
  loadDataPreview: (source: string, limit?: number) => Promise<void>;
  
  saveConfig: (name: string, description?: string) => Promise<void>;
  loadSavedConfig: (configId: string) => Promise<void>;
  listSavedConfigs: () => Promise<void>;
  
  applyPreprocessing: () => Promise<string>;
  checkTaskStatus: () => Promise<void>;
  cancelTask: () => Promise<void>;
}

// 创建默认配置
const createDefaultConfig = (): PreprocessingConfig => ({
  name: '新预处理配置',
  data_source: {
    type: 'parquet',
    file_path: '/home/qclaw/data/processed/stock_features.parquet',
    start_date: '2020-01-01',
    end_date: '2024-12-31',
  },
  selected_features: [], // 默认不选任何特征
  normalization: {
    method: 'zscore',
  },
  handle_missing: 'fill_mean',
  handle_outliers: 'clip',
  outlier_threshold: 3,
});

// 状态切片
export const createPreprocessingSlice: StateCreator<
  PreprocessingState,
  [],
  [],
  PreprocessingState
> = (set, get) => ({
  // 初始状态
  availableFeatures: [],
  featuresLoaded: false,
  currentConfig: null,
  dataStats: null,
  dataPreview: null,
  currentTask: null,
  taskStatus: 'idle',
  savedConfigs: [],
  
  // 加载可用特征
  loadFeatures: async () => {
    try {
      const response = await api.getFeatures();
      set({ 
        availableFeatures: response.features,
        featuresLoaded: true,
      });
    } catch (error) {
      console.error('Failed to load features:', error);
      // 使用内置的特征列表作为 fallback
      set({ featuresLoaded: true });
    }
  },
  
  // 更新配置
  updateConfig: (updates) => {
    const current = get().currentConfig || createDefaultConfig();
    set({
      currentConfig: { ...current, ...updates },
    });
  },
  
  // 设置完整配置
  setConfig: (config) => {
    set({ currentConfig: config });
  },
  
  // 重置配置
  resetConfig: () => {
    set({ currentConfig: createDefaultConfig() });
  },
  
  // 加载数据统计
  loadDataStats: async (source, startDate, endDate) => {
    try {
      const stats = await api.getDataStats(source, startDate, endDate);
      set({ dataStats: stats });
    } catch (error) {
      console.error('Failed to load data stats:', error);
      set({ dataStats: null });
    }
  },
  
  // 加载数据预览
  loadDataPreview: async (source, limit = 100) => {
    try {
      const preview = await api.previewData(source, limit);
      set({ dataPreview: preview });
    } catch (error) {
      console.error('Failed to load data preview:', error);
      set({ dataPreview: null });
    }
  },
  
  // 保存配置
  saveConfig: async (name, description) => {
    const current = get().currentConfig;
    if (!current) throw new Error('No config to save');
    
    const configToSave: PreprocessingConfig = {
      ...current,
      name,
      description,
    };
    
    const response = await api.savePreprocessingConfig(configToSave);
    if (response.status === 'success') {
      await get().listSavedConfigs();
    }
  },
  
  // 加载已保存的配置
  loadSavedConfig: async (configId) => {
    try {
      const config = await api.loadPreprocessingConfig(configId);
      set({ currentConfig: config });
    } catch (error) {
      console.error('Failed to load saved config:', error);
    }
  },
  
  // 列出已保存的配置
  listSavedConfigs: async () => {
    try {
      const configs = await api.listPreprocessingConfigs();
      set({ savedConfigs: configs });
    } catch (error) {
      console.error('Failed to list saved configs:', error);
    }
  },
  
  // 应用预处理
  applyPreprocessing: async () => {
    const current = get().currentConfig;
    if (!current) throw new Error('No config to apply');
    
    set({ taskStatus: 'running' });
    
    try {
      const response = await api.applyPreprocessing(current);
      if (response.status === 'started') {
        set({
          currentTask: {
            task_id: response.task_id,
            config: current,
            status: 'running',
            progress: {
              current_step: 0,
              total_steps: 5,
              current_action: '初始化...',
              eta_seconds: 0,
            },
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        });
        return response.task_id;
      }
      throw new Error(response.message || 'Failed to start preprocessing');
    } catch (error) {
      set({ taskStatus: 'error' });
      throw error;
    }
  },
  
  // 检查任务状态
  checkTaskStatus: async () => {
    const task = get().currentTask;
    if (!task) return;
    
    try {
      const status = await api.getPreprocessingStatus(task.task_id);
      set({
        taskStatus: status.status,
        currentTask: task.currentTask ? {
          ...task.currentTask,
          status: status.status,
          progress: status.progress,
          result: status.result,
          error: status.error,
          updated_at: new Date().toISOString(),
        } : null,
      });
    } catch (error) {
      console.error('Failed to check task status:', error);
    }
  },
  
  // 取消任务
  cancelTask: async () => {
    const task = get().currentTask;
    if (!task) return;
    
    try {
      await api.cancelPreprocessing(task.task_id);
      set({
        taskStatus: 'idle',
        currentTask: null,
      });
    } catch (error) {
      console.error('Failed to cancel task:', error);
    }
  },
});
