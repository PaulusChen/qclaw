<template>
  <!-- 技术指标区域 - E2E 测试选择器 -->
  <div 
    class="technical-indicators indicator chart"
    :class="[
      `indicator-${selectedIndicator}`,
      selectedIndicator,  // 添加 macd/kdj/rsi 类名
      { 'chart-rendered': !loading && chartInstance !== null }
    ]"
  >
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <select v-model="selectedIndicator" @change="updateChart">
          <option value="macd">MACD</option>
          <option value="kdj">KDJ</option>
          <option value="rsi">RSI</option>
        </select>
        <select v-model="timeRange" @change="updateChart">
          <option value="1M">1 个月</option>
          <option value="3M">3 个月</option>
          <option value="6M">6 个月</option>
          <option value="1Y">1 年</option>
        </select>
      </div>
    </div>
    
    <!-- 图表容器 - 根据指标类型添加特定类名 -->
    <div 
      ref="chartContainer" 
      class="chart-container"
      :class="`chart-${selectedIndicator}`"
    ></div>
    
    <div v-if="loading" class="loading-overlay">
      <span>加载数据中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { fetchIndicatorData } from '../../services/indicatorApi'

interface IndicatorData {
  date: string[]
  values: number[]
  signal?: number[]
  histogram?: number[]
}

const props = defineProps<{
  symbol: string
  title?: string
}>()

const title = props.title || '技术指标'
const chartContainer = ref<HTMLElement | null>(null)
const chartInstance = ref<echarts.ECharts | null>(null)

const selectedIndicator = ref<string>('macd')
const timeRange = ref<string>('3M')
const loading = ref<boolean>(false)

const initChart = () => {
  if (!chartContainer.value) return
  
  chartInstance.value = echarts.init(chartContainer.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    series: []
  }
  
  chartInstance.setOption(option)
  updateChart()
}

const updateChart = async () => {
  if (!chartInstance.value) return
  
  loading.value = true
  
  try {
    const data = await fetchIndicatorData(
      props.symbol,
      selectedIndicator.value,
      timeRange.value
    )
    
    renderChart(data)
  } catch (error) {
    console.error('Failed to fetch indicator data:', error)
  } finally {
    loading.value = false
  }
}

const renderChart = (data: IndicatorData) => {
  if (!chartInstance.value) return
  
  const option: echarts.EChartsOption = {
    xAxis: {
      data: data.date
    },
    series: getSeriesConfig(data)
  }
  
  chartInstance.setOption(option, true)
}

const getSeriesConfig = (data: IndicatorData): echarts.SeriesOption[] => {
  switch (selectedIndicator.value) {
    case 'macd':
      return [
        {
          name: 'DIF',
          type: 'line',
          data: data.values,
          smooth: true,
          itemStyle: { color: '#ff6b6b' }
        },
        {
          name: 'DEA',
          type: 'line',
          data: data.signal || [],
          smooth: true,
          itemStyle: { color: '#4ecdc4' }
        },
        {
          name: 'MACD',
          type: 'bar',
          data: data.histogram || [],
          itemStyle: {
            color: (params: any) => {
              return params.value >= 0 ? '#ff6b6b' : '#4ecdc4'
            }
          }
        }
      ]
    
    case 'kdj':
      return [
        {
          name: 'K',
          type: 'line',
          data: data.values,
          smooth: true,
          itemStyle: { color: '#ff6b6b' }
        },
        {
          name: 'D',
          type: 'line',
          data: data.signal || [],
          smooth: true,
          itemStyle: { color: '#4ecdc4' }
        },
        {
          name: 'J',
          type: 'line',
          data: data.histogram || [],
          smooth: true,
          itemStyle: { color: '#ffe66d' }
        }
      ]
    
    case 'rsi':
      return [
        {
          name: 'RSI',
          type: 'line',
          data: data.values,
          smooth: true,
          itemStyle: { color: '#ff6b6b' },
          markLine: {
            data: [
              { yAxis: 70, name: '超买' },
              { yAxis: 30, name: '超卖' }
            ],
            lineStyle: {
              type: 'dashed',
              color: '#999'
            }
          }
        }
      ]
    
    default:
      return []
  }
}

const handleResize = () => {
  chartInstance.value?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance.value?.dispose()
})

watch(() => props.symbol, () => {
  updateChart()
})
</script>

<style scoped>
.indicator-chart {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.chart-controls select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  color: #666;
}
</style>
