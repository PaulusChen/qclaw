<template>
  <div class="market-card" :class="indexClass">
    <div class="card-header">
      <div class="index-info">
        <h3 class="index-name">{{ indexName }}</h3>
        <span class="index-symbol">{{ symbol }}</span>
      </div>
      <div class="index-controls">
        <select v-model="timeRange" @change="updateChart">
          <option value="1M">1 个月</option>
          <option value="3M">3 个月</option>
          <option value="6M">6 个月</option>
          <option value="1Y">1 年</option>
        </select>
      </div>
    </div>
    
    <div class="index-summary">
      <div class="current-price" :class="priceClass">
        <span class="price-value">{{ formatNumber(currentPrice) }}</span>
        <span class="price-change">{{ formatChange(change) }}</span>
        <span class="price-change-percent">{{ formatPercent(changePercent) }}</span>
      </div>
      <div class="price-details">
        <span class="detail-item">开：{{ formatNumber(open) }}</span>
        <span class="detail-item">高：{{ formatNumber(high) }}</span>
        <span class="detail-item">低：{{ formatNumber(low) }}</span>
        <span class="detail-item">昨收：{{ formatNumber(previousClose) }}</span>
      </div>
    </div>
    
    <div ref="chartContainer" class="chart-container"></div>
    
    <div class="chart-legend">
      <span class="legend-item" style="color: #666;">
        <span class="legend-dot" style="background: #666;"></span>
        K 线
      </span>
      <span class="legend-item" style="color: #e6a23c;">
        <span class="legend-dot" style="background: #e6a23c;"></span>
        MA5
      </span>
      <span class="legend-item" style="color: #409eff;">
        <span class="legend-dot" style="background: #409eff;"></span>
        MA10
      </span>
      <span class="legend-item" style="color: #909399;">
        <span class="legend-dot" style="background: #909399;"></span>
        MA20
      </span>
    </div>
    
    <div v-if="loading" class="loading-overlay">
      <span>加载数据中...</span>
    </div>
    
    <div class="update-time" v-if="lastUpdate">
      更新于：{{ formatTime(lastUpdate) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import type { KLineData } from '../../types/market'
import { fetchKLineData, addMovingAverages } from '../../services/marketApi'
import { INDEX_LABELS } from '../../types/market'

interface MarketCardProps {
  /** 指数键名 (shanghai|shenzhen|chinext) */
  indexKey: string
  /** 指数代码 */
  symbol?: string
  /** 当前价格 */
  currentPrice?: number
  /** 涨跌点数 */
  change?: number
  /** 涨跌幅 */
  changePercent?: number
  /** 开盘价 */
  open?: number
  /** 最高价 */
  high?: number
  /** 最低价 */
  low?: number
  /** 昨收 */
  previousClose?: number
  /** 最后更新时间 */
  lastUpdate?: number
  /** 指数 CSS 类 */
  indexClass?: string
}

const props = withDefaults(defineProps<MarketCardProps>(), {
  symbol: '',
  currentPrice: 0,
  change: 0,
  changePercent: 0,
  open: 0,
  high: 0,
  low: 0,
  previousClose: 0,
  lastUpdate: 0,
  indexClass: '',
})

const indexName = computed(() => INDEX_LABELS[props.indexKey] || props.indexKey)

const chartContainer = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const timeRange = ref<string>('3M')
const loading = ref<boolean>(false)
const klineData = ref<KLineData[]>([])

// 价格样式类
const priceClass = computed(() => {
  if (props.change > 0) return 'price-up'
  if (props.change < 0) return 'price-down'
  return 'price-flat'
})

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return
  
  chartInstance = echarts.init(chartContainer.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params: any) => {
        const data = params[0].axisValueLabel
        let html = `<div style="font-weight:bold">${data}</div>`
        params.forEach((p: any) => {
          if (p.seriesName === 'K 线') {
            html += `<div>开：${p.data[1]} 收：${p.data[2]} 高：${p.data[3]} 低：${p.data[4]}</div>`
          } else {
            html += `<div>${p.seriesName}: ${p.value}</div>`
          }
        })
        return html
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '3%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        rotate: 45,
        formatter: (value: string) => {
          return value.slice(5) // 只显示 MM-DD
        }
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: {
        formatter: (value: number) => {
          return value.toFixed(0)
        }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100
      },
      {
        show: true,
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100
      }
    ],
    series: []
  }
  
  chartInstance.setOption(option)
  updateChart()
}

// 更新图表数据
const updateChart = async () => {
  if (!chartInstance) return
  
  loading.value = true
  
  try {
    const rawData = await fetchKLineData(props.indexKey, timeRange.value)
    klineData.value = addMovingAverages(rawData, [5, 10, 20])
    renderChart()
  } catch (error) {
    console.error('Failed to fetch K-line data:', error)
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartInstance || klineData.value.length === 0) return
  
  const dates = klineData.value.map(d => d.date)
  const klineValues = klineData.value.map(d => [d.open, d.close, d.high, d.low])
  const ma5Values = klineData.value.map(d => d.ma5 || '-')
  const ma10Values = klineData.value.map(d => d.ma10 || '-')
  const ma20Values = klineData.value.map(d => d.ma20 || '-')
  
  const option: echarts.EChartsOption = {
    xAxis: {
      data: dates
    },
    series: [
      {
        name: 'K 线',
        type: 'candlestick',
        data: klineValues,
        itemStyle: {
          color: '#ef4444',
          color0: '#22c55e',
          borderColor: '#ef4444',
          borderColor0: '#22c55e'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5Values,
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#e6a23c'
        },
        showSymbol: false
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10Values,
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#409eff'
        },
        showSymbol: false
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma20Values,
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#909399'
        },
        showSymbol: false
      }
    ]
  }
  
  chartInstance.setOption(option, true)
}

// 格式化数字
const formatNumber = (num: number): string => {
  return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 格式化涨跌
const formatChange = (change: number): string => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}`
}

// 格式化涨跌幅
const formatPercent = (percent: number): string => {
  const sign = percent > 0 ? '+' : ''
  return `${sign}${percent.toFixed(2)}%`
}

// 格式化时间
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 处理窗口大小变化
const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

watch(() => props.indexKey, () => {
  updateChart()
})
</script>

<style scoped>
.market-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.index-info {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.index-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.index-symbol {
  font-size: 12px;
  color: #6b7280;
}

.index-controls select {
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  background: #fff;
}

.index-summary {
  margin-bottom: 16px;
}

.current-price {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 8px;
}

.price-value {
  font-size: 28px;
  font-weight: 700;
}

.price-change {
  font-size: 16px;
  font-weight: 500;
}

.price-change-percent {
  font-size: 14px;
  font-weight: 500;
}

.price-up .price-value,
.price-up .price-change,
.price-up .price-change-percent {
  color: #ef4444;
}

.price-down .price-value,
.price-down .price-change,
.price-down .price-change-percent {
  color: #22c55e;
}

.price-flat .price-value,
.price-flat .price-change,
.price-flat .price-change-percent {
  color: #6b7280;
}

.price-details {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.detail-item {
  font-size: 13px;
  color: #6b7280;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-legend {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  color: #6b7280;
  font-size: 14px;
  border-radius: 12px;
}

.update-time {
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
}
</style>
