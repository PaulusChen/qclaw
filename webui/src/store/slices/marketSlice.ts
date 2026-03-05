import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'

interface IndexData {
  name: string
  code: string
  current: number
  change: number
  changePercent: number
  volume: number
  amount: number
  high: number
  low: number
  open: number
  prevClose: number
  kline: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>
}

interface MarketState {
  indices: Record<string, IndexData>
  klineData: Record<string, any>
  loading: boolean
  error: string | null
  lastUpdate: number
}

const initialState: MarketState = {
  indices: {},
  klineData: {},
  loading: false,
  error: null,
  lastUpdate: 0,
}

export const loadMarketData = createAsyncThunk(
  'market/loadIndices',
  async () => {
    const response = await fetch('/api/market/indices')
    if (!response.ok) throw new Error('Failed to fetch market data')
    return response.json()
  }
)

const marketSlice = createSlice({
  name: 'market',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadMarketData.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loadMarketData.fulfilled, (state, action: PayloadAction<any>) => {
        state.loading = false
        state.indices = action.payload
        state.lastUpdate = Date.now()
      })
      .addCase(loadMarketData.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '加载失败'
      })
  },
})

export const { clearError } = marketSlice.actions
export default marketSlice.reducer
