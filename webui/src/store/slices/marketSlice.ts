/**
 * 大盘指数 Redux Slice
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { MarketIndex, MarketIndexList, KLineData } from '../../types/market'
import { fetchMarketIndices, fetchKLineData } from '../../services/marketApi'

export interface MarketState {
  /** 指数数据 */
  indices: Record<string, MarketIndex>
  /** K 线数据缓存 */
  klineData: Record<string, KLineData[]>
  /** 加载状态 */
  loading: boolean
  /** 错误信息 */
  error: string | null
  /** 最后更新时间 */
  lastUpdate: number
}

const initialState: MarketState = {
  indices: {},
  klineData: {},
  loading: false,
  error: null,
  lastUpdate: 0,
}

/**
 * 异步加载大盘指数数据
 */
export const loadMarketData = createAsyncThunk<MarketIndexList>(
  'market/loadMarketData',
  async () => {
    return await fetchMarketIndices()
  }
)

/**
 * 异步加载 K 线数据
 */
export const loadKLineData = createAsyncThunk<KLineData[], { indexKey: string; timeRange: string }>(
  'market/loadKLineData',
  async ({ indexKey, timeRange }) => {
    return await fetchKLineData(indexKey, timeRange)
  }
)

const marketSlice = createSlice({
  name: 'market',
  initialState,
  reducers: {
    /**
     * 清除错误信息
     */
    clearError(state) {
      state.error = null
    },
    
    /**
     * 设置 K 线数据
     */
    setKLineData(state, action: PayloadAction<{ indexKey: string; data: KLineData[] }>) {
      const { indexKey, data } = action.payload
      state.klineData[indexKey] = data
    },
    
    /**
     * 清除 K 线数据缓存
     */
    clearKLineData(state, action: PayloadAction<string>) {
      delete state.klineData[action.payload]
    },
  },
  extraReducers: (builder) => {
    builder
      // 加载大盘指数数据
      .addCase(loadMarketData.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loadMarketData.fulfilled, (state, action) => {
        state.loading = false
        state.indices = action.payload
        state.lastUpdate = Date.now()
      })
      .addCase(loadMarketData.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to load market data'
      })
      
      // 加载 K 线数据
      .addCase(loadKLineData.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loadKLineData.fulfilled, (state, action) => {
        state.loading = false
        const { indexKey } = action.meta.arg
        state.klineData[indexKey] = action.payload
      })
      .addCase(loadKLineData.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to load K-line data'
      })
  },
})

export const { clearError, setKLineData, clearKLineData } = marketSlice.actions
export default marketSlice.reducer
