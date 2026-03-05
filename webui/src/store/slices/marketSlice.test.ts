import { describe, it, expect, vi, beforeEach } from 'vitest'
import marketReducer, { clearError, loadMarketData } from './marketSlice'

// Mock fetch
global.fetch = vi.fn()

describe('marketSlice', () => {
  const initialState = {
    indices: {},
    klineData: {},
    loading: false,
    error: null,
    lastUpdate: 0,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns initial state', () => {
    expect(marketReducer(undefined, { type: 'unknown' })).toEqual(initialState)
  })

  it('handles clearError', () => {
    const state = { ...initialState, error: 'Some error' }
    const newState = marketReducer(state, clearError())
    expect(newState.error).toBeNull()
  })

  it('handles loadMarketData.pending', () => {
    const state = marketReducer(initialState, { type: 'market/loadMarketData/pending' })
    expect(state.loading).toBe(true)
    expect(state.error).toBeNull()
  })

  it('handles loadMarketData.fulfilled', () => {
    const mockData = {
      shanghai: { name: '上证指数', current: 3000 },
      shenzhen: { name: '深证成指', current: 9000 },
      chinext: { name: '创业板指', current: 2000 },
    }
    const state = marketReducer(initialState, {
      type: 'market/loadMarketData/fulfilled',
      payload: mockData,
    })
    expect(state.loading).toBe(false)
    expect(state.indices).toEqual(mockData)
    expect(state.lastUpdate).toBeGreaterThan(0)
  })

  it('handles loadMarketData.rejected', () => {
    const state = marketReducer(initialState, {
      type: 'market/loadMarketData/rejected',
      error: { message: 'Failed to fetch market data' },
    })
    expect(state.loading).toBe(false)
    expect(state.error).toBe('Failed to fetch market data')
  })
})
