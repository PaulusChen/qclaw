<template>
  <!-- AI 建议区域 - E2E 测试选择器 -->
  <div class="ai-advice advice prediction">
    <!-- 标题栏 -->
    <div class="advice-header">
      <h3 class="advice-title">
        <span class="ai-icon">🤖</span>
        AI 投资建议
      </h3>
      <button 
        class="refresh-btn" 
        @click="handleRefresh"
        :disabled="loading"
      >
        <span :class="{ 'spinning': loading }">🔄</span>
        刷新
      </button>
    </div>

    <!-- 统计摘要 -->
    <div v-if="summary" class="advice-summary">
      <!-- 建议类型统计 - E2E 测试选择器 -->
      <div class="advice-type">
        <div class="summary-item">
          <span class="summary-label">总建议</span>
          <span class="summary-value">{{ summary.total }}</span>
        </div>
        <div class="summary-item buy">
          <span class="summary-label">买入</span>
          <span class="summary-value">{{ summary.buyCount }}</span>
        </div>
        <div class="summary-item sell">
          <span class="summary-label">卖出</span>
          <span class="summary-value">{{ summary.sellCount }}</span>
        </div>
        <div class="summary-item hold">
          <span class="summary-label">持有</span>
          <span class="summary-value">{{ summary.holdCount }}</span>
        </div>
        <div class="summary-item watch">
          <span class="summary-label">观察</span>
          <span class="summary-value">{{ summary.watchCount }}</span>
        </div>
      </div>
      <!-- 置信度水平 - E2E 测试选择器 -->
      <div class="confidence-level">
        <div class="summary-item confidence">
          <span class="summary-label">平均置信度</span>
          <span class="summary-value">{{ summary.avgConfidence }}%</span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>正在获取 AI 建议...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="retry-btn" @click="loadAdvice">重试</button>
    </div>

    <!-- 建议列表 -->
    <div v-else-if="adviceList.length > 0" class="advice-list">
      <div 
        v-for="advice in adviceList" 
        :key="advice.id"
        class="advice-card"
        :class="`type-${advice.type}`"
      >
        <!-- 卡片头部 -->
        <div class="advice-card-header">
          <div class="stock-info">
            <span class="stock-symbol">{{ advice.symbol }}</span>
            <span class="stock-name">{{ advice.name }}</span>
          </div>
          <div class="advice-badge" :style="{ backgroundColor: getAdviceColor(advice.type) }">
            {{ getAdviceTypeLabel(advice.type) }}
          </div>
        </div>

        <!-- 置信度 -->
        <div class="confidence-bar">
          <div class="confidence-label">置信度</div>
          <div class="confidence-track">
            <div 
              class="confidence-fill" 
              :style="{ 
                width: `${advice.confidence}%`,
                backgroundColor: getConfidenceColor(advice.confidence)
              }"
            ></div>
          </div>
          <div class="confidence-value">{{ advice.confidence }}%</div>
        </div>

        <!-- 建议内容 -->
        <div class="advice-content">
          <p>{{ advice.content }}</p>
        </div>

        <!-- 理由分析 -->
        <div v-if="advice.reasons.length > 0" class="advice-reasons">
          <div class="reason-title">📊 分析理由</div>
          <ul class="reason-list">
            <li v-for="(reason, index) in advice.reasons" :key="index">
              {{ reason }}
            </li>
          </ul>
        </div>

        <!-- 风险提示 -->
        <div v-if="advice.risks.length > 0" class="advice-risks">
          <div class="risk-title">⚠️ 风险提示</div>
          <ul class="risk-list">
            <li v-for="(risk, index) in advice.risks" :key="index">
              {{ risk }}
            </li>
          </ul>
        </div>

        <!-- 目标价/止损价 -->
        <div v-if="advice.targetPrice || advice.stopLoss" class="price-targets">
          <div v-if="advice.targetPrice" class="target-price">
            <span class="target-label">目标价</span>
            <span class="target-value">¥{{ advice.targetPrice.toFixed(2) }}</span>
          </div>
          <div v-if="advice.stopLoss" class="stop-loss">
            <span class="stop-label">止损价</span>
            <span class="stop-value">¥{{ advice.stopLoss.toFixed(2) }}</span>
          </div>
        </div>

        <!-- 时间戳 -->
        <div class="advice-timestamp">
          更新于 {{ formatTime(advice.updatedAt) }}
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <span class="empty-icon">📭</span>
      <p>暂无 AI 建议</p>
      <button class="refresh-btn primary" @click="handleRefresh">
        获取建议
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { AIAdvice, AdviceSummary } from '../../types/advice'
import { 
  fetchAdviceList, 
  fetchAdviceSummary,
  refreshAdvice as apiRefreshAdvice 
} from '../../services/adviceApi'
import { ADVICE_TYPE_LABELS, ADVICE_TYPE_COLORS } from '../../types/advice'

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const adviceList = ref<AIAdvice[]>([])
const summary = ref<AdviceSummary | null>(null)

// 获取建议类型标签
const getAdviceTypeLabel = (type: string): string => {
  return ADVICE_TYPE_LABELS[type] || type
}

// 获取建议类型颜色
const getAdviceColor = (type: string): string => {
  return ADVICE_TYPE_COLORS[type] || '#6b7280'
}

// 获取置信度颜色
const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 80) return '#22c55e'  // 绿色 - 高
  if (confidence >= 60) return '#f59e0b'  // 黄色 - 中
  return '#ef4444'  // 红色 - 低
}

// 格式化时间
const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 今天
  if (diff < 24 * 60 * 60 * 1000) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  
  // 本周
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return days[date.getDay()]
  }
  
  // 其他
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 加载建议
const loadAdvice = async () => {
  loading.value = true
  error.value = null
  
  try {
    const [list, summaryData] = await Promise.all([
      fetchAdviceList(),
      fetchAdviceSummary()
    ])
    
    adviceList.value = list
    summary.value = summaryData
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    console.error('Failed to load advice:', err)
  } finally {
    loading.value = false
  }
}

// 刷新建议
const handleRefresh = async () => {
  loading.value = true
  error.value = null
  
  try {
    await apiRefreshAdvice()
    await loadAdvice()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '刷新失败'
    console.error('Failed to refresh advice:', err)
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadAdvice()
})
</script>

<style scoped>
.ai-advice {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 标题栏 */
.advice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.advice-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.ai-icon {
  font-size: 20px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn.primary {
  background: #3b82f6;
  color: white;
}

.refresh-btn.primary:hover {
  background: #2563eb;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 统计摘要 */
.advice-summary {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.summary-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.summary-item.buy .summary-value { color: #ef4444; }
.summary-item.sell .summary-value { color: #22c55e; }
.summary-item.hold .summary-value { color: #f59e0b; }
.summary-item.watch .summary-value { color: #6b7280; }
.summary-item.confidence .summary-value { color: #3b82f6; }

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #6b7280;
  gap: 12px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #ef4444;
  gap: 12px;
}

.error-icon {
  font-size: 32px;
}

.retry-btn {
  padding: 8px 16px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* 建议列表 */
.advice-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.advice-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
  transition: all 0.2s;
}

.advice-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.advice-card.type-buy {
  border-left: 4px solid #ef4444;
}

.advice-card.type-sell {
  border-left: 4px solid #22c55e;
}

.advice-card.type-hold {
  border-left: 4px solid #f59e0b;
}

.advice-card.type-watch {
  border-left: 4px solid #6b7280;
}

/* 卡片头部 */
.advice-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stock-info {
  display: flex;
  flex-direction: column;
}

.stock-symbol {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.stock-name {
  font-size: 13px;
  color: #6b7280;
}

.advice-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

/* 置信度 */
.confidence-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.confidence-label {
  font-size: 12px;
  color: #6b7280;
  min-width: 50px;
}

.confidence-track {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.confidence-value {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  min-width: 40px;
  text-align: right;
}

/* 建议内容 */
.advice-content {
  margin-bottom: 12px;
}

.advice-content p {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
}

/* 理由分析 */
.advice-reasons {
  background: #f0fdf4;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.reason-title {
  font-size: 13px;
  font-weight: 600;
  color: #166534;
  margin-bottom: 8px;
}

.reason-list {
  margin: 0;
  padding-left: 20px;
}

.reason-list li {
  font-size: 13px;
  color: #15803d;
  line-height: 1.5;
  margin-bottom: 4px;
}

/* 风险提示 */
.advice-risks {
  background: #fef2f2;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.risk-title {
  font-size: 13px;
  font-weight: 600;
  color: #991b1b;
  margin-bottom: 8px;
}

.risk-list {
  margin: 0;
  padding-left: 20px;
}

.risk-list li {
  font-size: 13px;
  color: #b91c1c;
  line-height: 1.5;
  margin-bottom: 4px;
}

/* 目标价/止损价 */
.price-targets {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 12px;
}

.target-price,
.stop-loss {
  display: flex;
  flex-direction: column;
}

.target-label,
.stop-label {
  font-size: 12px;
  color: #6b7280;
}

.target-value,
.stop-value {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

/* 时间戳 */
.advice-timestamp {
  font-size: 12px;
  color: #9ca3af;
  text-align: right;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #6b7280;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}
</style>
