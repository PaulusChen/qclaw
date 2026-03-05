/**
 * AI 投资建议数据类型定义
 */

export interface AIAdvice {
  /** 建议 ID */
  id: string
  /** 股票代码 */
  symbol: string
  /** 股票名称 */
  name: string
  /** 建议类型 */
  type: 'buy' | 'sell' | 'hold' | 'watch'
  /** 建议内容 */
  content: string
  /** 置信度 (0-100) */
  confidence: number
  /** 理由分析 */
  reasons: string[]
  /** 风险提示 */
  risks: string[]
  /** 目标价格 */
  targetPrice?: number
  /** 止损价格 */
  stopLoss?: number
  /** 创建时间 */
  createdAt: string
  /** 更新时间 */
  updatedAt: string
}

export interface AdviceSummary {
  /** 总建议数 */
  total: number
  /** 买入建议数 */
  buyCount: number
  /** 卖出建议数 */
  sellCount: number
  /** 持有建议数 */
  holdCount: number
  /** 观察建议数 */
  watchCount: number
  /** 平均置信度 */
  avgConfidence: number
}

export interface AdviceFilter {
  /** 建议类型筛选 */
  type?: 'buy' | 'sell' | 'hold' | 'watch'
  /** 最小置信度 */
  minConfidence?: number
  /** 股票代码筛选 */
  symbol?: string
  /** 时间范围 */
  timeRange?: 'today' | 'week' | 'month'
}

export const ADVICE_TYPE_LABELS: Record<string, string> = {
  buy: '买入',
  sell: '卖出',
  hold: '持有',
  watch: '观察'
}

export const ADVICE_TYPE_COLORS: Record<string, string> = {
  buy: '#ef4444',
  sell: '#22c55e',
  hold: '#f59e0b',
  watch: '#6b7280'
}
