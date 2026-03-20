import React, { useState, useEffect, useCallback } from 'react'
import { Card, Button, Space, message, Spin, Alert, Statistic, Row, Col, Tag } from 'antd'
import { ReloadOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons'
import { useMarketStore } from '../../store/marketStore'

interface MarketIndex {
  key: string
  name: string
  symbol: string
  current?: number
  change?: number
  changePercent?: number
  open?: number
  high?: number
  low?: number
  previousClose?: number
}

const DEFAULT_INDICES: Omit<MarketIndex, 'current' | 'change' | 'changePercent'>[] = [
  { key: 'shanghai', name: '上证指数', symbol: '000001.SH', open: 0, high: 0, low: 0, previousClose: 0 },
  { key: 'shenzhen', name: '深证成指', symbol: '399001.SZ', open: 0, high: 0, low: 0, previousClose: 0 },
  { key: 'chinext', name: '创业板指', symbol: '399006.SZ', open: 0, high: 0, low: 0, previousClose: 0 },
  { key: 'csi300', name: '沪深 300', symbol: '000300.SH', open: 0, high: 0, low: 0, previousClose: 0 },
]

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [indices, setIndices] = useState<MarketIndex[]>(DEFAULT_INDICES)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchMarketData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/market/indices')
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      
      // 处理 API 返回的数据格式：{ indices: { shanghai: {...}, shenzhen: {...}, ... } }
      let indicesData: any[] = []
      if (data.indices && typeof data.indices === 'object') {
        // 将对象转换为数组
        indicesData = Object.values(data.indices)
      } else if (Array.isArray(data)) {
        indicesData = data
      } else if (data.data) {
        indicesData = Array.isArray(data.data) ? data.data : Object.values(data.data)
      }
      
      // 更新指数数据
      setIndices(prev => prev.map(index => {
        const marketData = indicesData.find((d: any) => 
          d.code === index.symbol || d.symbol === index.symbol || d.name === index.name
        )
        return marketData ? {
          ...index,
          current: marketData.current || marketData.price || marketData.value || 0,
          change: marketData.change || 0,
          changePercent: marketData.changePercent || 0,
          open: marketData.open || index.open,
          high: marketData.high || index.high,
          low: marketData.low || index.low,
          previousClose: marketData.previousClose || index.previousClose,
        } : index
      }))
      setLastUpdate(new Date())
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '获取数据失败'
      setError(errorMsg)
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }, [])

  // 初始加载和定时刷新
  useEffect(() => {
    fetchMarketData()
    
    // 交易时间自动刷新（9:30-11:30, 13:00-15:00）
    const interval = setInterval(() => {
      const now = new Date()
      const hours = now.getHours()
      const minutes = now.getMinutes()
      const currentTime = hours * 60 + minutes
      
      const isMorningSession = currentTime >= 570 && currentTime < 690
      const isAfternoonSession = currentTime >= 780 && currentTime < 900
      
      if (isMorningSession || isAfternoonSession) {
        fetchMarketData()
      }
    }, 30000)
    
    return () => clearInterval(interval)
  }, [fetchMarketData])

  const formatTime = (date: Date | null) => {
    if (!date) return '-'
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const renderChange = (change?: number, changePercent?: number) => {
    if (change === undefined || changePercent === undefined) return '-'
    const isPositive = change >= 0
    return (
      <span style={{ color: isPositive ? '#cf1322' : '#3f8600', fontWeight: 600 }}>
        {isPositive ? '+' : ''}{change?.toFixed(2)} ({isPositive ? '+' : ''}{changePercent?.toFixed(2)}%)
      </span>
    )
  }

  const renderTrendIcon = (change?: number) => {
    if (change === undefined) return null
    return change >= 0 ? <RiseOutlined /> : <FallOutlined />
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* 头部 */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '24px' 
      }}>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#1f2937' }}>
          🤖 QCLaw - 大盘指数
        </h1>
        <Space>
          <Button 
            type="primary" 
            icon={<ReloadOutlined spin={loading} />}
            onClick={fetchMarketData}
            loading={loading}
          >
            刷新数据
          </Button>
        </Space>
      </div>

      {/* 错误提示 */}
      {error && (
        <Alert
          message="数据加载失败"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: '24px' }}
          action={
            <Button size="small" type="primary" onClick={fetchMarketData}>
              重试
            </Button>
          }
        />
      )}

      {/* 指数卡片 */}
      <div className="market-indices">
        <Row gutter={[24, 24]}>
          {indices.map((index) => (
            <Col xs={24} sm={12} lg={6} key={index.key}>
              <Card 
                className="market-card index"
                hoverable
                style={{ 
                  height: '100%',
                  borderLeft: `4px solid ${
                    (index.change || 0) >= 0 ? '#cf1322' : '#3f8600'
                  }`
                }}
              >
              <Space direction="vertical" style={{ width: '100%' }} size="small">
                <div style={{ fontSize: '16px', fontWeight: 600, color: '#262626' }}>
                  {renderTrendIcon(index.change)} {index.name}
                </div>
                
                <Statistic
                  value={index.current || 0}
                  precision={2}
                  valueStyle={{ 
                    fontSize: '28px', 
                    fontWeight: 700,
                    color: (index.change || 0) >= 0 ? '#cf1322' : '#3f8600'
                  }}
                  suffix={
                    <span style={{ fontSize: '14px', marginLeft: '8px' }}>
                      {renderChange(index.change, index.changePercent)}
                    </span>
                  }
                />
                
                <Space split={<span style={{ color: '#d9d9d9' }}>|</span>} size={12}>
                  <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
                    今开：{index.open?.toFixed(2) || '-'}
                  </span>
                  <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
                    最高：{index.high?.toFixed(2) || '-'}
                  </span>
                  <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
                    最低：{index.low?.toFixed(2) || '-'}
                  </span>
                </Space>
              </Space>
            </Card>
          </Col>
        ))}
        </Row>
      </div>

      {/* 最后更新时间 */}
      <div style={{ 
        marginTop: '24px', 
        padding: '12px 16px', 
        background: '#f5f5f5', 
        borderRadius: '8px',
        textAlign: 'center',
        color: '#8c8c8c',
        fontSize: '13px'
      }}>
        🕐 最后更新：{formatTime(lastUpdate)}
      </div>

      {/* 免责声明 */}
      <div style={{ 
        marginTop: '32px', 
        paddingTop: '16px', 
        borderTop: '1px solid #f0f0f0',
        textAlign: 'center',
        color: '#bfbfbf',
        fontSize: '12px'
      }}>
        数据仅供参考，不构成投资建议。市场有风险，投资需谨慎。
      </div>
    </div>
  )
}

export default Dashboard
