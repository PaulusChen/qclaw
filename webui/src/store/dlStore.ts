// 深度学习模块统一状态管理 (Zustand)
import { create } from 'zustand';
import { createTrainingSlice, type TrainingSlice } from './slices/dl/trainingSlice';
import { createManagementSlice, type ManagementSlice } from './slices/dl/managementSlice';
import { createPreprocessingSlice, type PreprocessingState } from './slices/dl/preprocessingSlice';

// 合并所有 DL 相关的 slice
interface DLState extends TrainingSlice, ManagementSlice, PreprocessingState {}

export const useDLStore = create<DLState>((...args) => ({
  ...createTrainingSlice(...args),
  ...createManagementSlice(...args),
  ...createPreprocessingSlice(...args),
}));

export type { DLState };
export default useDLStore;
