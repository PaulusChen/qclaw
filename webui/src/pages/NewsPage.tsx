/**
 * 新闻资讯页面
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Card, List, Space, message, Spin, Tag, Typography, Button } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'

const { Text } = Typography

interface NewsItem {
  id: string
  title: string
  summary: string
  source: string
  publishTime: string
  category: string
  url?: string
}

const NewsPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [news, setNews] = useState<NewsItem[]>([])

  const fetchNews = useCallback(async () => {
    setLoading(true)
    try {
      // TODO: 实现真实的新闻 API
      // 当前使用模拟数据
      const mockData: NewsItem[] = [
        {
          id: '1',
          title: '央行：保持流动性合理充裕，支持实体经济发展',
          summary: '中国人民银行今日召开新闻发布会，表示将继续实施稳健的货币政策，保持流动性合理充裕...',
          source: '新华社',
          publishTime: new Date().toISOString(),
          category: '宏观',
        },
        {
          id: '2',
          title: '证监会：稳步推进全面注册制改革',
          summary: '中国证监会表示，将继续深化资本市场改革，稳步推进全面注册制，提高上市公司质量...',
          source: '证券时报',
          publishTime: new Date().toISOString(),
          category: '政策',
        },
        {
          id: '3',
          title: '多家券商上调 A 股策略：看好二季度行情',
          summary: '近期多家头部券商发布投资策略报告，普遍看好二季度 A 股市场表现，建议关注科技、消费等板块...',
          source: '中国证券报',
          publishTime: new Date().toISOString(),
          category: '策略',
        },
        {
          id: '4',
          title: '北向资金连续 5 日净流入，累计超 200 亿元',
          summary: '沪深股通数据显示，北向资金本周连续 5 个交易日呈现净流入态势，累计净买入金额超过 200 亿元...',
          source: 'Wind',
          publishTime: new Date().toISOString(),
          category: '资金',
        },
        {
          id: '5',
          title: '科技股领涨，半导体板块大涨超 3%',
          summary: '今日科技股表现强势，半导体、芯片等板块集体上涨，多只个股涨停...',
          source: '东方财富',
          publishTime: new Date().toISOString(),
          category: '板块',
        },
      ]
      setNews(mockData)
    } catch (err) {
      message.error('获取新闻失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchNews()
  }, [fetchNews])

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      '宏观': 'blue',
      '政策': 'red',
      '策略': 'green',
      '资金': 'orange',
      '板块': 'purple',
    }
    return colors[category] || 'default'
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between' }}>
        <h1 style={{ margin: 0 }}>📰 财经新闻</h1>
        <Space>
          <button
            className="ant-btn ant-btn-primary"
            onClick={fetchNews}
            disabled={loading}
          >
            <ReloadOutlined spin={loading} /> 刷新
          </button>
        </Space>
      </div>

      <Card>
        <Spin spinning={loading}>
          <List
            itemLayout="vertical"
            dataSource={news}
            renderItem={(item) => (
              <List.Item
                style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong style={{ fontSize: '16px' }}>{item.title}</Text>
                      <Tag color={getCategoryColor(item.category)}>{item.category}</Tag>
                      <Text type="secondary" style={{ fontSize: '12px' }}>{item.source}</Text>
                    </Space>
                  }
                  description={
                    <div>
                      <p style={{ margin: '8px 0', color: '#666' }}>{item.summary}</p>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {new Date(item.publishTime).toLocaleString('zh-CN')}
                      </Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Spin>
      </Card>
    </div>
  )
}

export default NewsPage
