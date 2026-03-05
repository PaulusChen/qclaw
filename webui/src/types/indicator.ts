/**
 * 技术指标数据类型定义
 */

export interface IndicatorData {
  /** 日期数组 */
  date: string[]
  /** 主指标值 */
  values: number[]
  /** 信号线值 (如 MACD 的 DEA, KDJ 的 D) */
  signal?: number[]
  /** 柱状图值 (如 MACD 柱，KDJ 的 J) */
  histogram?: number[]
}

export interface IndicatorConfig {
  /** 指标名称 */
  name: string
  /** 指标类型 */
  type: 'macd' | 'kdj' | 'rsi' | 'custom'
  /** 显示名称 */
  displayName: string
  /** 参数配置 */
  params?: Record<string, number>
}

export interface ChartOptions {
  /** 图表标题 */
  title?: string
  /** 时间范围 */
  timeRange: '1M' | '3M' | '6M' | '1Y'
  /** 是否显示网格 */
  showGrid?: boolean
  /** 是否显示图例 */
  showLegend?: boolean
}

export const DEFAULT_INDICATORS: IndicatorConfig[] = [
  {
    name: 'MACD',
    type: 'macd',
    displayName: '平滑异同移动平均线',
    params: { fast: 12, slow: 26, signal: 9 }
  },
  {
    name: 'KDJ',
    type: 'kdj',
    displayName: '随机指标',
    params: { n: 9, m1: 3, m2: 3 }
  },
  {
    name: 'RSI',
    type: 'rsi',
    displayName: '相对强弱指标',
    params: { period: 14 }
  }
]
