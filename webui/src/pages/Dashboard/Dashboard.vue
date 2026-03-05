<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1 class="dashboard-title">大盘指数</h1>
      <div class="dashboard-actions">
        <button 
          class="refresh-btn" 
          @click="refreshAll" 
          :disabled="loading"
        >
          <span :class="{ 'spinning': loading }">🔄</span>
          刷新
        </button>
      </div>
    </div>
    
    <div class="market-grid">
      <MarketCard
        v-for="index in marketIndices"
        :key="index.name"
        :index-key="index.name"
        :symbol="index.symbol"
        :current-price="getMarketData(index.name)?.current"
        :change="getMarketData(index.name)?.change"
        :change-percent="getMarketData(index.name)?.changePercent"
        :open="getMarketData(index.name)?.open"
        :high="getMarketData(index.name)?.high"
        :low="getMarketData(index.name)?.low"
        :previous-close="getMarketData(index.name)?.previousClose"
        :last-update="lastUpdate"
      />
    </div>
    
    <div v-if="error" class="error-message">
      <span>⚠️</span>
      {{ error }}
      <button @click="refreshAll" class="retry-btn">重试</button>
    </div>
    
    <div class="dashboard-footer">
      <p class="disclaimer">
        数据仅供参考，不构成投资建议。市场有风险，投资需谨慎。
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useMarket, loadMarketData, getMarketIndex } from '../../composables/useMarket'
import MarketCard from '../../components/MarketCard/MarketCard.vue'
import { MARKET_INDICES, type MarketIndex } from '../../types/market'

const { indices, loading, error, lastUpdate } = useMarket()

const marketIndices = MARKET_INDICES

// 获取单个指数数据
const getMarketData = (indexKey: string): MarketIndex | undefined => {
  return getMarketIndex(indexKey)
}

// 刷新所有数据
const refreshAll = async () => {
  await loadMarketData()
}

// 自动刷新定时器
let refreshTimer: number | null = null

const startAutoRefresh = () => {
  // 每 30 秒自动刷新一次
  refreshTimer = window.setInterval(() => {
    // 只在交易时间自动刷新 (9:30-11:30, 13:00-15:00)
    const now = new Date()
    const hours = now.getHours()
    const minutes = now.getMinutes()
    const currentTime = hours * 60 + minutes
    
    const isMorningSession = currentTime >= 570 && currentTime < 690 // 9:30-11:30
    const isAfternoonSession = currentTime >= 780 && currentTime < 900 // 13:00-15:00
    
    if (isMorningSession || isAfternoonSession) {
      refreshAll()
    }
  }, 30000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  refreshAll()
  startAutoRefresh()
})

onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.dashboard-actions {
  display: flex;
  gap: 12px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #4338ca;
}

.refresh-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.refresh-btn .spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.market-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .market-grid {
    grid-template-columns: 1fr;
  }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  margin-bottom: 24px;
}

.retry-btn {
  margin-left: auto;
  padding: 6px 12px;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #b91c1c;
}

.dashboard-footer {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.disclaimer {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
}
</style>
