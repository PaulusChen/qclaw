<template>
  <div class="news-list-container">
    <!-- 标题栏 -->
    <div class="news-header">
      <h3 class="news-title">
        <span class="news-icon">📰</span>
        财经资讯
      </h3>
      <div class="header-actions">
        <!-- 分类筛选 -->
        <select 
          v-model="selectedCategory"
          class="category-select"
          @change="loadNews"
        >
          <option value="">全部分类</option>
          <option v-for="(label, key) in categoryLabels" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
        
        <!-- 刷新按钮 -->
        <button 
          class="refresh-btn" 
          @click="loadNews"
          :disabled="loading"
        >
          <span :class="{ 'spinning': loading }">🔄</span>
        </button>
      </div>
    </div>

    <!-- 重要新闻提示 -->
    <div v-if="importantNews.length > 0" class="important-news-banner">
      <div class="banner-icon">🔥</div>
      <div class="banner-content">
        <div class="banner-title">重要新闻</div>
        <div class="banner-summary">{{ importantNews[0].title }}</div>
      </div>
      <button class="banner-btn" @click="viewNews(importantNews[0])">查看</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && newsList.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <span>正在加载新闻...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="retry-btn" @click="loadNews">重试</button>
    </div>

    <!-- 新闻列表 -->
    <div v-else class="news-list">
      <div 
        v-for="news in newsList" 
        :key="news.id"
        class="news-item"
        :class="{ 
          'is-important': news.importance >= 4,
          'is-read': news.id === readNewsId
        }"
        @click="viewNews(news)"
      >
        <!-- 封面图 -->
        <div v-if="news.imageUrl" class="news-image">
          <img :src="news.imageUrl" :alt="news.title" loading="lazy" />
        </div>

        <!-- 新闻内容 -->
        <div class="news-content">
          <!-- 头部信息 -->
          <div class="news-meta">
            <span class="news-category" :class="`cat-${news.category}`">
              {{ getCategoryIcon(news.category) }} {{ getCategoryLabel(news.category) }}
            </span>
            <span class="news-source">{{ news.source }}</span>
            <span class="news-time">{{ formatTime(news.publishedAt) }}</span>
          </div>

          <!-- 标题 -->
          <h4 class="news-headline">
            {{ news.title }}
            <span v-if="news.importance >= 4" class="importance-badge">🔥</span>
          </h4>

          <!-- 摘要 -->
          <p class="news-summary">{{ news.summary }}</p>

          <!-- 底部信息 -->
          <div class="news-footer">
            <!-- 情感标签 -->
            <span 
              class="sentiment-tag" 
              :class="`sentiment-${news.sentiment}`"
              :style="{ backgroundColor: getSentimentColor(news.sentiment) }"
            >
              {{ getSentimentLabel(news.sentiment) }}
            </span>

            <!-- 相关股票 -->
            <div v-if="news.symbols.length > 0" class="news-symbols">
              <span 
                v-for="symbol in news.symbols.slice(0, 3)" 
                :key="symbol"
                class="symbol-tag"
              >
                {{ symbol }}
              </span>
              <span v-if="news.symbols.length > 3" class="more-symbols">
                +{{ news.symbols.length - 3 }}
              </span>
            </div>

            <!-- 标签 -->
            <div v-if="news.tags.length > 0" class="news-tags">
              <span 
                v-for="tag in news.tags.slice(0, 2)" 
                :key="tag"
                class="tag"
              >
                #{{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more">
        <button 
          class="load-more-btn" 
          @click="loadMore"
          :disabled="loadingMore"
        >
          <span v-if="loadingMore" class="loading-spinner small"></span>
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="newsList.length === 0 && !loading" class="empty-state">
        <span class="empty-icon">📭</span>
        <p>暂无新闻</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { NewsItem, NewsCategory } from '../../types/news'
import { 
  fetchNewsList, 
  fetchImportantNews,
  markNewsAsRead
} from '../../services/newsApi'
import { 
  NEWS_CATEGORY_LABELS, 
  NEWS_CATEGORY_ICONS,
  SENTIMENT_LABELS,
  SENTIMENT_COLORS
} from '../../types/news'

// 状态
const loading = ref(false)
const loadingMore = ref(false)
const error = ref<string | null>(null)
const newsList = ref<NewsItem[]>([])
const importantNews = ref<NewsItem[]>([])
const currentPage = ref(1)
const pageSize = 10
const hasMore = ref(true)
const readNewsId = ref<string | null>(null)
const selectedCategory = ref<string>('')

// 分类标签
const categoryLabels = NEWS_CATEGORY_LABELS

// 获取分类标签
const getCategoryLabel = (category: string): string => {
  return NEWS_CATEGORY_LABELS[category as NewsCategory] || category
}

// 获取分类图标
const getCategoryIcon = (category: string): string => {
  return NEWS_CATEGORY_ICONS[category as NewsCategory] || '📄'
}

// 获取情感标签
const getSentimentLabel = (sentiment: string): string => {
  return SENTIMENT_LABELS[sentiment] || sentiment
}

// 获取情感颜色
const getSentimentColor = (sentiment: string): string => {
  return SENTIMENT_COLORS[sentiment] || '#6b7280'
}

// 格式化时间
const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 1 小时内
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000))
    return `${minutes}分钟前`
  }
  
  // 今天
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours}小时前`
  }
  
  // 本周
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000))
    return `${days}天前`
  }
  
  // 其他
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 加载新闻
const loadNews = async (page: number = 1) => {
  if (page === 1) {
    loading.value = true
  } else {
    loadingMore.value = true
  }
  error.value = null
  
  try {
    const filter: any = {
      page,
      pageSize
    }
    
    if (selectedCategory.value) {
      filter.category = selectedCategory.value
    }
    
    const response = await fetchNewsList(filter)
    
    if (page === 1) {
      newsList.value = response.items
    } else {
      newsList.value = [...newsList.value, ...response.items]
    }
    
    currentPage.value = page
    hasMore.value = page < response.totalPages
    
    // 加载重要新闻
    if (page === 1) {
      importantNews.value = await fetchImportantNews(4)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    console.error('Failed to load news:', err)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 加载更多
const loadMore = () => {
  if (!loadingMore.value && hasMore.value) {
    loadNews(currentPage.value + 1)
  }
}

// 查看新闻
const viewNews = async (news: NewsItem) => {
  // 标记为已读
  readNewsId.value = news.id
  try {
    await markNewsAsRead(news.id)
  } catch (err) {
    console.error('Failed to mark news as read:', err)
  }
  
  // 打开新闻链接
  window.open(news.url, '_blank')
}

// 组件挂载时加载数据
onMounted(() => {
  loadNews()
})
</script>

<style scoped>
.news-list-container {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 标题栏 */
.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.news-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.news-icon {
  font-size: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-select {
  padding: 6px 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  outline: none;
}

.category-select:hover {
  border-color: #d1d5db;
}

.refresh-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  font-size: 16px;
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

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 重要新闻横幅 */
.important-news-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.important-news-banner:hover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.banner-icon {
  font-size: 24px;
}

.banner-content {
  flex: 1;
  min-width: 0;
}

.banner-title {
  font-size: 12px;
  font-weight: 600;
  color: #991b1b;
  margin-bottom: 2px;
}

.banner-summary {
  font-size: 14px;
  color: #7f1d1d;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.banner-btn {
  padding: 6px 12px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.banner-btn:hover {
  background: #dc2626;
}

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

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
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

/* 新闻列表 */
.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.news-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.news-item.is-important {
  border-left: 3px solid #ef4444;
  background: #fef2f2;
}

.news-item.is-read {
  opacity: 0.7;
}

/* 新闻图片 */
.news-image {
  flex-shrink: 0;
  width: 120px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  background: #f3f4f6;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 新闻内容 */
.news-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 新闻元数据 */
.news-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.news-category {
  padding: 2px 8px;
  background: #f3f4f6;
  border-radius: 4px;
  color: #4b5563;
  font-size: 11px;
}

.news-source {
  color: #6b7280;
}

.news-time {
  color: #9ca3af;
  margin-left: auto;
}

/* 新闻标题 */
.news-headline {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.4;
}

.importance-badge {
  font-size: 14px;
}

/* 新闻摘要 */
.news-summary {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 新闻底部 */
.news-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: auto;
}

/* 情感标签 */
.sentiment-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: white;
}

.sentiment-positive { background: #22c55e; }
.sentiment-negative { background: #ef4444; }
.sentiment-neutral { background: #6b7280; }

/* 股票标签 */
.news-symbols {
  display: flex;
  align-items: center;
  gap: 4px;
}

.symbol-tag {
  padding: 2px 6px;
  background: #eff6ff;
  border-radius: 4px;
  font-size: 11px;
  color: #2563eb;
  font-weight: 500;
}

.more-symbols {
  font-size: 11px;
  color: #6b7280;
}

/* 标签 */
.news-tags {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.tag {
  font-size: 11px;
  color: #9ca3af;
}

/* 加载更多 */
.load-more {
  padding: 16px 0;
  text-align: center;
}

.load-more-btn {
  padding: 10px 24px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
