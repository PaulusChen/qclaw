/**
 * 大盘指数数据 API 服务
 */

import type { MarketIndex, MarketIndexList, KLineData } from '../types/market'

const API_BASE = '/api/market'

/**
 * 获取大盘指数实时数据
 */
export async function fetchMarketIndices(): Promise<MarketIndexList> {
  const response = await fetch(`${API_BASE}/indices`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch market indices: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取单个指数实时数据
 * @param indexKey 指数键名 (shanghai|shenzhen|chinext)
 */
export async function fetchMarketIndex(indexKey: string): Promise<MarketIndex> {
  const response = await fetch(`${API_BASE}/indices/${indexKey}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch market index ${indexKey}: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取 K 线数据
 * @param indexKey 指数键名 (shanghai|shenzhen|chinext)
 * @param timeRange 时间范围 (1M|3M|6M|1Y)
 */
export async function fetchKLineData(
  indexKey: string,
  timeRange: string = '3M'
): Promise<KLineData[]> {
  const params = new URLSearchParams({ time_range: timeRange })
  const response = await fetch(`${API_BASE}/kline/${indexKey}?${params}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch K-line data for ${indexKey}: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取上证指数 K 线数据
 */
export async function fetchShanghaiKLine(timeRange: string = '3M'): Promise<KLineData[]> {
  return fetchKLineData('shanghai', timeRange)
}

/**
 * 获取深证成指 K 线数据
 */
export async function fetchShenzhenKLine(timeRange: string = '3M'): Promise<KLineData[]> {
  return fetchKLineData('shenzhen', timeRange)
}

/**
 * 获取创业板指 K 线数据
 */
export async function fetchChinextKLine(timeRange: string = '3M'): Promise<KLineData[]> {
  return fetchKLineData('chinext', timeRange)
}

/**
 * 计算移动平均线
 * @param data K 线数据数组
 * @param period 周期 (5, 10, 20)
 */
export function calculateMA(data: KLineData[], period: number): (number | null)[] {
  const result: (number | null)[] = []
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null)
      continue
    }
    
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close
    }
    
    result.push(Number((sum / period).toFixed(2)))
  }
  
  return result
}

/**
 * 为 K 线数据添加移动平均线
 * @param data K 线数据数组
 * @param periods 周期数组 [5, 10, 20]
 */
export function addMovingAverages(data: KLineData[], periods: number[] = [5, 10, 20]): KLineData[] {
  return data.map((item, index) => {
    const newItem = { ...item }
    
    periods.forEach(period => {
      if (index >= period - 1) {
        let sum = 0
        for (let j = 0; j < period; j++) {
          sum += data[index - j].close
        }
        const maKey = `ma${period}` as keyof KLineData
        newItem[maKey] = Number((sum / period).toFixed(2))
      }
    })
    
    return newItem
  })
}
