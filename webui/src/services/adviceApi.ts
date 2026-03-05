/**
 * AI 投资建议 API 服务
 */

import type { AIAdvice, AdviceSummary, AdviceFilter } from '../types/advice'

const API_BASE = '/api/advice'

/**
 * 获取 AI 建议列表
 * @param filter 筛选条件
 */
export async function fetchAdviceList(filter?: AdviceFilter): Promise<AIAdvice[]> {
  const params = new URLSearchParams()
  
  if (filter?.type) {
    params.append('type', filter.type)
  }
  if (filter?.minConfidence) {
    params.append('min_confidence', filter.minConfidence.toString())
  }
  if (filter?.symbol) {
    params.append('symbol', filter.symbol)
  }
  if (filter?.timeRange) {
    params.append('time_range', filter.timeRange)
  }
  
  const queryString = params.toString()
  const url = queryString ? `${API_BASE}?${queryString}` : API_BASE
  
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch advice list: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取单条 AI 建议
 * @param id 建议 ID
 */
export async function fetchAdviceById(id: string): Promise<AIAdvice> {
  const response = await fetch(`${API_BASE}/${id}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch advice: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取建议统计摘要
 */
export async function fetchAdviceSummary(): Promise<AdviceSummary> {
  const response = await fetch(`${API_BASE}/summary`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch advice summary: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取指定股票的 AI 建议
 * @param symbol 股票代码
 */
export async function fetchAdviceBySymbol(symbol: string): Promise<AIAdvice[]> {
  const response = await fetch(`${API_BASE}/symbol/${symbol}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch advice by symbol: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取高置信度建议 (置信度 >= 80)
 */
export async function fetchHighConfidenceAdvice(minConfidence: number = 80): Promise<AIAdvice[]> {
  return fetchAdviceList({ minConfidence })
}

/**
 * 获取买入建议
 */
export async function fetchBuyAdvice(): Promise<AIAdvice[]> {
  return fetchAdviceList({ type: 'buy' })
}

/**
 * 获取卖出建议
 */
export async function fetchSellAdvice(): Promise<AIAdvice[]> {
  return fetchAdviceList({ type: 'sell' })
}

/**
 * 刷新 AI 建议 (触发 OpenClaw 重新分析)
 */
export async function refreshAdvice(): Promise<void> {
  const response = await fetch(`${API_BASE}/refresh`, {
    method: 'POST'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to refresh advice: ${response.statusText}`)
  }
}
