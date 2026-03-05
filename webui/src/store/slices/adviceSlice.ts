/**
 * AI 投资建议 Redux Slice
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import type { AIAdvice } from '../../types/advice'
import { fetchDailyAdvice } from '../../services/adviceApi'

export interface AdviceState {
  /** 每日建议 */
  daily: AIAdvice | null
  /** 加载状态 */
  loading: boolean
  /** 错误信息 */
  error: string | null
}

const initialState: AdviceState = {
  daily: null,
  loading: false,
  error: null,
}

/**
 * 异步加载每日建议
 */
export const loadDailyAdvice = createAsyncThunk<AIAdvice>(
  'advice/loadDailyAdvice',
  async () => {
    return await fetchDailyAdvice()
  }
)

const adviceSlice = createSlice({
  name: 'advice',
  initialState,
  reducers: {
    /**
     * 清除错误信息
     */
    clearError(state) {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // 加载每日建议
      .addCase(loadDailyAdvice.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loadDailyAdvice.fulfilled, (state, action) => {
        state.loading = false
        state.daily = action.payload
      })
      .addCase(loadDailyAdvice.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to load advice'
      })
  },
})

export const { clearError } = adviceSlice.actions
export default adviceSlice.reducer
