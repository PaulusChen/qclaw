/**
 * 大盘指数数据 Composable
 */

import { ref, reactive, readonly } from 'vue'
import type { MarketIndex, MarketIndexList } from '../types/market'
import { fetchMarketIndices } from '../services/marketApi'

interface MarketState {
  indices: Record<string, MarketIndex>
  loading: boolean
  error: string | null
  lastUpdate: number
}

const state = reactive<MarketState>({
  indices: {},
  loading: false,
  error: null,
  lastUpdate: 0,
})

/**
 * 加载大盘指数数据
 */
export async function loadMarketData(): Promise<void> {
  state.loading = true
  state.error = null
  
  try {
    const data = await fetchMarketIndices()
    state.indices = data
    state.lastUpdate = Date.now()
  } catch (err) {
    state.error = err instanceof Error ? err.message : 'Failed to load market data'
  } finally {
    state.loading = false
  }
}

/**
 * 获取大盘指数状态
 */
export function useMarket() {
  return {
    indices: readonly(state.indices),
    loading: readonly(ref(state.loading)),
    error: readonly(ref(state.error)),
    lastUpdate: readonly(ref(state.lastUpdate)),
    loadMarketData,
  }
}

/**
 * 获取单个指数数据
 */
export function getMarketIndex(indexKey: string): MarketIndex | undefined {
  return state.indices[indexKey]
}

export default useMarket
