import { describe, it, expect } from 'vitest'
import adviceReducer, { loadDailyAdvice } from './adviceSlice'

describe('adviceSlice', () => {
  const initialState = {
    daily: null,
    loading: false,
    error: null,
  }

  it('returns initial state', () => {
    expect(adviceReducer(undefined, { type: 'unknown' })).toEqual(initialState)
  })

  it('handles loadDailyAdvice.pending', () => {
    const state = adviceReducer(initialState, { type: 'advice/loadDailyAdvice/pending' })
    expect(state.loading).toBe(true)
  })

  it('handles loadDailyAdvice.fulfilled', () => {
    const mockAdvice = {
      advice: 'HOLD' as const,
      confidence: 'MEDIUM' as const,
      reasons: ['Reason 1', 'Reason 2'],
      risks: ['Risk 1'],
      updatedAt: '2026-03-05T10:00:00Z',
    }
    const state = adviceReducer(initialState, {
      type: 'advice/loadDailyAdvice/fulfilled',
      payload: mockAdvice,
    })
    expect(state.loading).toBe(false)
    expect(state.daily).toEqual(mockAdvice)
  })

  it('handles loadDailyAdvice.rejected', () => {
    const state = adviceReducer(initialState, {
      type: 'advice/loadDailyAdvice/rejected',
      error: { message: 'Failed to fetch advice' },
    })
    expect(state.loading).toBe(false)
    expect(state.error).toBe('Failed to fetch advice')
  })
})
