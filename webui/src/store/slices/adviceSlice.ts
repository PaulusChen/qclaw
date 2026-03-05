import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

interface AdviceState {
  daily: {
    advice: 'BUY' | 'SELL' | 'HOLD' | 'WAIT'
    confidence: 'HIGH' | 'MEDIUM' | 'LOW'
    reasons: string[]
    risks: string[]
    updatedAt: string
  } | null
  loading: boolean
  error: string | null
}

const initialState: AdviceState = {
  daily: null,
  loading: false,
  error: null,
}

export const loadDailyAdvice = createAsyncThunk(
  'advice/loadDaily',
  async (date: string) => {
    const response = await fetch(`/api/advice/daily?date=${date}`)
    if (!response.ok) throw new Error('Failed to fetch advice')
    return response.json()
  }
)

const adviceSlice = createSlice({
  name: 'advice',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(loadDailyAdvice.pending, (state) => {
        state.loading = true
      })
      .addCase(loadDailyAdvice.fulfilled, (state, action) => {
        state.loading = false
        state.daily = action.payload
      })
      .addCase(loadDailyAdvice.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '加载失败'
      })
  },
})

export default adviceSlice.reducer
