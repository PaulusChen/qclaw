/**
 * 财经新闻 API 服务
 */

import type { NewsItem, NewsFilter, NewsListResponse, NewsCategoryInfo } from '../types/news'

const API_BASE = '/api/news'

/**
 * 获取新闻列表
 * @param filter 筛选条件
 */
export async function fetchNewsList(filter?: NewsFilter): Promise<NewsListResponse> {
  const params = new URLSearchParams()
  
  if (filter?.category) {
    params.append('category', filter.category)
  }
  if (filter?.sentiment) {
    params.append('sentiment', filter.sentiment)
  }
  if (filter?.symbol) {
    params.append('symbol', filter.symbol)
  }
  if (filter?.timeRange) {
    params.append('time_range', filter.timeRange)
  }
  if (filter?.minImportance) {
    params.append('min_importance', filter.minImportance.toString())
  }
  if (filter?.keyword) {
    params.append('keyword', filter.keyword)
  }
  if (filter?.page) {
    params.append('page', filter.page.toString())
  }
  if (filter?.pageSize) {
    params.append('page_size', filter.pageSize.toString())
  }
  
  const queryString = params.toString()
  const url = queryString ? `${API_BASE}?${queryString}` : API_BASE
  
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch news list: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取单条新闻详情
 * @param id 新闻 ID
 */
export async function fetchNewsById(id: string): Promise<NewsItem> {
  const response = await fetch(`${API_BASE}/${id}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch news detail: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取新闻分类统计
 */
export async function fetchNewsCategories(): Promise<NewsCategoryInfo[]> {
  const response = await fetch(`${API_BASE}/categories`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch news categories: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取重要新闻 (重要性 >= 4)
 */
export async function fetchImportantNews(minImportance: number = 4): Promise<NewsItem[]> {
  const params = new URLSearchParams({
    min_importance: minImportance.toString()
  })
  
  const response = await fetch(`${API_BASE}/important?${params}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch important news: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取利好新闻
 */
export async function fetchPositiveNews(): Promise<NewsItem[]> {
  const response = await fetch(`${API_BASE}/sentiment/positive`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch positive news: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取利空新闻
 */
export async function fetchNegativeNews(): Promise<NewsItem[]> {
  const response = await fetch(`${API_BASE}/sentiment/negative`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch negative news: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取指定股票相关新闻
 * @param symbol 股票代码
 */
export async function fetchNewsBySymbol(symbol: string, limit: number = 10): Promise<NewsItem[]> {
  const params = new URLSearchParams({
    symbol,
    limit: limit.toString()
  })
  
  const response = await fetch(`${API_BASE}/symbol/${symbol}?${params}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch news by symbol: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 搜索新闻
 * @param keyword 搜索关键词
 * @param limit 返回数量
 */
export async function searchNews(keyword: string, limit: number = 20): Promise<NewsItem[]> {
  const params = new URLSearchParams({
    q: keyword,
    limit: limit.toString()
  })
  
  const response = await fetch(`${API_BASE}/search?${params}`)
  
  if (!response.ok) {
    throw new Error(`Failed to search news: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 获取最新新闻 (实时推送)
 * @param limit 返回数量
 */
export async function fetchLatestNews(limit: number = 10): Promise<NewsItem[]> {
  const params = new URLSearchParams({
    limit: limit.toString()
  })
  
  const response = await fetch(`${API_BASE}/latest?${params}`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch latest news: ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * 标记新闻已读
 * @param id 新闻 ID
 */
export async function markNewsAsRead(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/${id}/read`, {
    method: 'POST'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to mark news as read: ${response.statusText}`)
  }
}

/**
 * 收藏新闻
 * @param id 新闻 ID
 */
export async function bookmarkNews(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/${id}/bookmark`, {
    method: 'POST'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to bookmark news: ${response.statusText}`)
  }
}

/**
 * 取消收藏新闻
 * @param id 新闻 ID
 */
export async function unbookmarkNews(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/${id}/bookmark`, {
    method: 'DELETE'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to unbookmark news: ${response.statusText}`)
  }
}

/**
 * 获取收藏的新闻列表
 */
export async function fetchBookmarkedNews(): Promise<NewsItem[]> {
  const response = await fetch(`${API_BASE}/bookmarks`)
  
  if (!response.ok) {
    throw new Error(`Failed to fetch bookmarked news: ${response.statusText}`)
  }
  
  return response.json()
}
