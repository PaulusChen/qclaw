/**
 * 技术指标数据 API 服务
 */

import type { IndicatorData } from '../types/indicator'

const API_BASE = '/api/indicators'

/**
 * 获取技术指标数据
 * @param symbol 股票代码
 * @param indicator 指标类型 (macd|kdj|rsi)
 * @param timeRange 时间范围 (1M|3M|6M|1Y)
 */
export async function fetchIndicatorData(
  symbol: string,
  indicator: string,
  timeRange: string
): Promise<IndicatorData> {
  const params = new URLSearchParams({
    symbol,
    indicator,
    time_range: timeRange
  })
  
  const response = await fetch(`${API_BASE}?${params}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch indicator data: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取 MACD 数据
 */
export async function fetchMACD(symbol: string, timeRange: string = '3M'): Promise<IndicatorData> {
  return fetchIndicatorData(symbol, 'macd', timeRange)
}

/**
 * 获取 KDJ 数据
 */
export async function fetchKDJ(symbol: string, timeRange: string = '3M'): Promise<IndicatorData> {
  return fetchIndicatorData(symbol, 'kdj', timeRange)
}

/**
 * 获取 RSI 数据
 */
export async function fetchRSI(symbol: string, timeRange: string = '3M'): Promise<IndicatorData> {
  return fetchIndicatorData(symbol, 'rsi', timeRange)
}

/**
 * 批量获取多个指标数据
 */
export async function fetchIndicatorsBatch(
  symbol: string,
  indicators: string[],
  timeRange: string = '3M'
): Promise<Record<string, IndicatorData>> {
  const results: Record<string, IndicatorData> = {}
  
  await Promise.all(
    indicators.map(async (indicator) => {
      try {
        results[indicator] = await fetchIndicatorData(symbol, indicator, timeRange)
      } catch (error) {
        console.error(`Failed to fetch ${indicator}:`, error)
      }
    })
  )
  
  return results
}
