// 深度学习训练状态管理 (Zustand)
import { StateCreator } from 'zustand';
import { trainingApi } from '../../../services/dl/trainingApi';
import type {
  TrainingConfig,
  TrainingTask,
  TrainingStatus,
  TrainingLog,
} from '../../../types/dl';

export interface TrainingSlice {
  // 当前训练任务
  currentTask: TrainingTask | null;
  
  // 训练任务历史
  taskHistory: TrainingTask[];
  
  // 操作
  startTraining: (config: TrainingConfig) => Promise<string>;
  stopTraining: () => Promise<void>;
  updateTrainingStatus: (taskId: string) => Promise<void>;
  addLog: (log: TrainingLog) => void;
  clearCurrentTask: () => void;
  loadTaskHistory: () => Promise<void>;
}

export const createTrainingSlice: StateCreator<TrainingSlice, [], [], TrainingSlice> = (set, get) => ({
  currentTask: null,
  taskHistory: [],

  startTraining: async (config: TrainingConfig) => {
    try {
      const response = await trainingApi.startTraining(config);
      const { task_id } = response;
      
      const newTask: TrainingTask = {
        task_id,
        config,
        state: {
          status: 'running',
          progress: null,
          metrics: null,
          learning_rates: [],
          train_loss_history: [],
          val_loss_history: [],
        },
        logs: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      set({ currentTask: newTask });
      return task_id;
    } catch (error) {
      console.error('Failed to start training:', error);
      throw error;
    }
  },

  stopTraining: async () => {
    const { currentTask } = get();
    if (!currentTask) return;
    
    try {
      await trainingApi.stopTraining(currentTask.task_id);
      set((state) => ({
        currentTask: state.currentTask
          ? {
              ...state.currentTask,
              state: {
                ...state.currentTask.state,
                status: 'completed',
              },
              updated_at: new Date().toISOString(),
            }
          : null,
      }));
    } catch (error) {
      console.error('Failed to stop training:', error);
      throw error;
    }
  },

  updateTrainingStatus: async (taskId: string) => {
    try {
      const status = await trainingApi.getTrainingStatus(taskId);
      
      set((state) => ({
        currentTask: state.currentTask
          ? {
              ...state.currentTask,
              state: {
                ...state.currentTask.state,
                status: status.status,
                progress: status.progress,
                metrics: status.metrics,
                train_loss_history: [
                  ...state.currentTask.state.train_loss_history,
                  status.metrics.train_loss,
                ],
                val_loss_history: [
                  ...state.currentTask.state.val_loss_history,
                  status.metrics.val_loss,
                ],
              },
              updated_at: new Date().toISOString(),
            }
          : null,
      }));
    } catch (error) {
      console.error('Failed to update training status:', error);
    }
  },

  addLog: (log: TrainingLog) => {
    set((state) => ({
      currentTask: state.currentTask
        ? {
            ...state.currentTask,
            logs: [...state.currentTask.logs, log],
          }
        : null,
    }));
  },

  clearCurrentTask: () => {
    set({ currentTask: null });
  },

  loadTaskHistory: async () => {
    // TODO: Implement API to load task history
    set({ taskHistory: [] });
  },
});

export default createTrainingSlice;
