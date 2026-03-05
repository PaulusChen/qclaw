import { describe, it, expect } from 'vitest'

// 测试用的格式化函数
const formatNumber = (num: number, precision: number = 2): string => {
  return num.toFixed(precision)
}

const formatPercent = (num: number): string => {
  return `${num > 0 ? '+' : ''}${num.toFixed(2)}%`
}

const formatChange = (change: number): string => {
  return change > 0 ? `+${change}` : `${change}`
}

describe('format utilities', () => {
  describe('formatNumber', () => {
    it('formats number with default precision', () => {
      expect(formatNumber(3000.567)).toBe('3000.57')
    })

    it('formats number with custom precision', () => {
      expect(formatNumber(3000.567, 3)).toBe('3000.567')
    })

    it('handles negative numbers', () => {
      expect(formatNumber(-3000.567)).toBe('-3000.57')
    })
  })

  describe('formatPercent', () => {
    it('formats positive percent', () => {
      expect(formatPercent(1.23)).toBe('+1.23%')
    })

    it('formats negative percent', () => {
      expect(formatPercent(-1.23)).toBe('-1.23%')
    })

    it('formats zero', () => {
      expect(formatPercent(0)).toBe('0.00%')
    })
  })

  describe('formatChange', () => {
    it('formats positive change', () => {
      expect(formatChange(10)).toBe('+10')
    })

    it('formats negative change', () => {
      expect(formatChange(-10)).toBe('-10')
    })
  })
})
