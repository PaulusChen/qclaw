/**
 * 财经新闻数据类型定义
 */

export interface NewsItem {
  /** 新闻 ID */
  id: string
  /** 新闻标题 */
  title: string
  /** 新闻摘要 */
  summary: string
  /** 新闻内容 */
  content?: string
  /** 新闻来源 */
  source: string
  /** 作者 */
  author?: string
  /** 发布时间 */
  publishedAt: string
  /** 新闻链接 */
  url: string
  /** 封面图片 */
  imageUrl?: string
  /** 相关股票代码 */
  symbols: string[]
  /** 情感分析 */
  sentiment: 'positive' | 'negative' | 'neutral'
  /** 情感得分 (-1 到 1) */
  sentimentScore: number
  /** 标签 */
  tags: string[]
  /** 分类 */
  category: NewsCategory
  /** 重要性 (1-5) */
  importance: number
  /** 阅读量 */
  viewCount?: number
}

export type NewsCategory = 
  | 'market'      // 市场动态
  | 'policy'      // 政策监管
  | 'company'     // 公司动态
  | 'industry'    // 行业分析
  | 'macro'       // 宏观经济
  | 'international' // 国际市场
  | 'crypto'      // 加密货币
  | 'technology'  // 科技金融

export interface NewsFilter {
  /** 分类筛选 */
  category?: NewsCategory
  /** 情感筛选 */
  sentiment?: 'positive' | 'negative' | 'neutral'
  /** 股票代码筛选 */
  symbol?: string
  /** 时间范围 */
  timeRange?: 'today' | 'week' | 'month' | 'quarter'
  /** 最小重要性 */
  minImportance?: number
  /** 搜索关键词 */
  keyword?: string
  /** 分页 */
  page?: number
  /** 每页数量 */
  pageSize?: number
}

export interface NewsListResponse {
  /** 新闻列表 */
  items: NewsItem[]
  /** 总数量 */
  total: number
  /** 当前页 */
  page: number
  /** 每页数量 */
  pageSize: number
  /** 总页数 */
  totalPages: number
}

export interface NewsCategoryInfo {
  /** 分类 ID */
  id: NewsCategory
  /** 分类名称 */
  name: string
  /** 分类图标 */
  icon: string
  /** 新闻数量 */
  count: number
}

export const NEWS_CATEGORY_LABELS: Record<NewsCategory, string> = {
  market: '市场动态',
  policy: '政策监管',
  company: '公司动态',
  industry: '行业分析',
  macro: '宏观经济',
  international: '国际市场',
  crypto: '加密货币',
  technology: '科技金融'
}

export const NEWS_CATEGORY_ICONS: Record<NewsCategory, string> = {
  market: '📈',
  policy: '📋',
  company: '🏢',
  industry: '🏭',
  macro: '🌍',
  international: '🌐',
  crypto: '₿',
  technology: '💻'
}

export const SENTIMENT_LABELS: Record<string, string> = {
  positive: '利好',
  negative: '利空',
  neutral: '中性'
}

export const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#22c55e',
  negative: '#ef4444',
  neutral: '#6b7280'
}
