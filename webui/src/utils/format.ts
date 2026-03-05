/**
 * 格式化数字
 * @param num 数字
 * @param precision 小数位数
 */
export const formatNumber = (num: number, precision: number = 2): string => {
  return num.toFixed(precision)
}

/**
 * 格式化百分比
 * @param num 百分比数值
 */
export const formatPercent = (num: number): string => {
  if (num === 0) return '0.00%'
  return `${num > 0 ? '+' : ''}${num.toFixed(2)}%`
}

/**
 * 格式化涨跌
 * @param change 涨跌值
 */
export const formatChange = (change: number): string => {
  return change >= 0 ? `+${change}` : `${change}`
}
