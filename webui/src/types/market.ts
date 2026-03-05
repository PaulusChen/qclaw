/**
 * 大盘指数数据类型定义
 */

export interface MarketIndex {
  /** 指数代码 */
  symbol: string
  /** 指数名称 */
  name: string
  /** 当前点位 */
  current: number
  /** 涨跌点数 */
  change: number
  /** 涨跌幅 (%) */
  changePercent: number
  /** 开盘价 */
  open: number
  /** 最高价 */
  high: number
  /** 最低价 */
  low: number
  /** 昨收 */
  previousClose: number
  /** 成交量 (手) */
  volume: number
  /** 成交额 (元) */
  turnover: number
  /** 更新时间 */
  updatedAt: string
}

export interface KLineData {
  /** 日期 */
  date: string
  /** 开盘价 */
  open: number
  /** 收盘价 */
  close: number
  /** 最高价 */
  high: number
  /** 最低价 */
  low: number
  /** 成交量 */
  volume: number
  /** 成交额 */
  turnover: number
  /** MA5 */
  ma5?: number
  /** MA10 */
  ma10?: number
  /** MA20 */
  ma20?: number
}

export interface MarketIndexList {
  /** 上证指数 */
  shanghai: MarketIndex
  /** 深证成指 */
  shenzhen: MarketIndex
  /** 创业板指 */
  chinext: MarketIndex
}

export interface MarketIndexConfig {
  /** 指数代码 */
  symbol: string
  /** 指数名称 */
  name: string
  /** 显示名称 */
  displayName: string
}

export const MARKET_INDICES: MarketIndexConfig[] = [
  {
    symbol: '000001',
    name: 'shanghai',
    displayName: '上证指数'
  },
  {
    symbol: '399001',
    name: 'shenzhen',
    displayName: '深证成指'
  },
  {
    symbol: '399006',
    name: 'chinext',
    displayName: '创业板指'
  }
]

export const INDEX_LABELS: Record<string, string> = {
  shanghai: '上证指数',
  shenzhen: '深证成指',
  chinext: '创业板指'
}
