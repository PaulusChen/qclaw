// 深度学习模型管理状态管理 (Zustand)
import { StateCreator } from 'zustand';
import { managementApi } from '../../../services/dl/managementApi';
import type {
  ModelInfo,
  ModelDetailResponse,
  ModelComparison,
  ModelsListResponse,
} from '../../../types/dl';

export interface ManagementSlice {
  // 模型列表
  models: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  
  // 当前选中的模型
  selectedModel: ModelInfo | null;
  selectedModelLoading: boolean;
  
  // 模型对比
  comparingModels: string[];
  comparisonResult: ModelComparison | null;
  comparisonLoading: boolean;
  
  // 操作
  loadModels: () => Promise<void>;
  selectModel: (version: string) => Promise<void>;
  clearSelectedModel: () => void;
  activateModel: (version: string) => Promise<void>;
  archiveModel: (version: string) => Promise<void>;
  deleteModel: (version: string) => Promise<void>;
  addToComparison: (version: string) => void;
  removeFromComparison: (version: string) => void;
  clearComparison: () => void;
  compareSelected: () => Promise<void>;
}

export const createManagementSlice: StateCreator<ManagementSlice, [], [], ManagementSlice> = (set, get) => ({
  models: [],
  modelsLoading: false,
  modelsError: null,
  
  selectedModel: null,
  selectedModelLoading: false,
  
  comparingModels: [],
  comparisonResult: null,
  comparisonLoading: false,
  
  loadModels: async () => {
    set({ modelsLoading: true, modelsError: null });
    try {
      const response: ModelsListResponse = await managementApi.getModels();
      set({ 
        models: response.models, 
        modelsLoading: false 
      });
    } catch (error) {
      console.error('Failed to load models:', error);
      set({ 
        modelsError: '加载模型列表失败', 
        modelsLoading: false 
      });
    }
  },

  selectModel: async (version: string) => {
    set({ selectedModelLoading: true });
    try {
      const detail: ModelDetailResponse = await managementApi.getModelDetail(version);
      set({ 
        selectedModel: detail, 
        selectedModelLoading: false 
      });
    } catch (error) {
      console.error('Failed to load model detail:', error);
      set({ selectedModelLoading: false });
    }
  },

  clearSelectedModel: () => {
    set({ selectedModel: null });
  },

  activateModel: async (version: string) => {
    try {
      await managementApi.activateModel(version);
      // 刷新模型列表
      await get().loadModels();
    } catch (error) {
      console.error('Failed to activate model:', error);
      throw error;
    }
  },

  archiveModel: async (version: string) => {
    try {
      await managementApi.archiveModel(version);
      // 刷新模型列表
      await get().loadModels();
      // 如果归档的是当前选中的模型，清除选择
      if (get().selectedModel?.version === version) {
        get().clearSelectedModel();
      }
    } catch (error) {
      console.error('Failed to archive model:', error);
      throw error;
    }
  },

  deleteModel: async (version: string) => {
    try {
      await managementApi.deleteModel(version);
      // 刷新模型列表
      await get().loadModels();
      // 如果删除的是当前选中的模型，清除选择
      if (get().selectedModel?.version === version) {
        get().clearSelectedModel();
      }
      // 从对比列表中移除
      get().removeFromComparison(version);
    } catch (error) {
      console.error('Failed to delete model:', error);
      throw error;
    }
  },

  addToComparison: (version: string) => {
    const { comparingModels } = get();
    if (!comparingModels.includes(version) && comparingModels.length < 5) {
      set({ comparingModels: [...comparingModels, version] });
    }
  },

  removeFromComparison: (version: string) => {
    const { comparingModels } = get();
    set({ 
      comparingModels: comparingModels.filter(v => v !== version) 
    });
  },

  clearComparison: () => {
    set({ 
      comparingModels: [], 
      comparisonResult: null 
    });
  },

  compareSelected: async () => {
    const { comparingModels } = get();
    if (comparingModels.length < 2) {
      return;
    }
    
    set({ comparisonLoading: true });
    try {
      const result = await managementApi.compareModels(comparingModels);
      set({ 
        comparisonResult: result, 
        comparisonLoading: false 
      });
    } catch (error) {
      console.error('Failed to compare models:', error);
      set({ comparisonLoading: false });
    }
  },
});

export default createManagementSlice;
