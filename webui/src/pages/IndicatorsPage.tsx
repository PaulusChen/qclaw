/**
 * 技术指标页面
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Card, Table, Space, message, Spin, Alert, Tag, Input, Select, Button } from 'antd'
import { ReloadOutlined, SearchOutlined } from '@ant-design/icons'

const { Search } = Input

interface Indicator {
  symbol: string
  name: string
  macd?: { dif: number; dea: number; histogram: number }
  kdj?: { k: number; d: number; j: number }
  rsi?: number
  boll?: { upper: number; middle: number; lower: number }
  updateTime?: string
}

const IndicatorsPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [indicators, setIndicators] = useState<Indicator[]>([])
  const [searchSymbol, setSearchSymbol] = useState('')
  const [period, setPeriod] = useState('daily')

  const fetchIndicators = useCallback(async () => {
    setLoading(true)
    try {
      // TODO: 实现真实的技术指标 API
      // 当前使用模拟数据
      const mockData: Indicator[] = [
        {
          symbol: '600519',
          name: '贵州茅台',
          macd: { dif: 12.5, dea: 10.2, histogram: 2.3 },
          kdj: { k: 75, d: 70, j: 85 },
          rsi: 65,
          boll: { upper: 1850, middle: 1800, lower: 1750 },
          updateTime: new Date().toISOString(),
        },
        {
          symbol: '300750',
          name: '宁德时代',
          macd: { dif: 8.3, dea: 7.1, histogram: 1.2 },
          kdj: { k: 60, d: 55, j: 70 },
          rsi: 58,
          boll: { upper: 220, middle: 210, lower: 200 },
          updateTime: new Date().toISOString(),
        },
        {
          symbol: '601318',
          name: '中国平安',
          macd: { dif: 2.1, dea: 1.8, histogram: 0.3 },
          kdj: { k: 45, d: 50, j: 35 },
          rsi: 48,
          boll: { upper: 52, middle: 50, lower: 48 },
          updateTime: new Date().toISOString(),
        },
      ]
      setIndicators(mockData)
    } catch (err) {
      message.error('获取技术指标失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchIndicators()
  }, [fetchIndicators])

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'MACD',
      key: 'macd',
      render: (_: any, record: Indicator) =>
        record.macd ? (
          <Space>
            <Tag color="red">DIF: {record.macd.dif.toFixed(2)}</Tag>
            <Tag color="green">DEA: {record.macd.dea.toFixed(2)}</Tag>
            <Tag color="orange">HIST: {record.macd.histogram.toFixed(2)}</Tag>
          </Space>
        ) : (
          '-'
        ),
    },
    {
      title: 'KDJ',
      key: 'kdj',
      render: (_: any, record: Indicator) =>
        record.kdj ? (
          <Space>
            <Tag>K: {record.kdj.k}</Tag>
            <Tag>D: {record.kdj.d}</Tag>
            <Tag>J: {record.kdj.j}</Tag>
          </Space>
        ) : (
          '-'
        ),
    },
    {
      title: 'RSI',
      dataIndex: 'rsi',
      key: 'rsi',
      render: (value?: number) => {
        if (value === undefined) return '-'
        const color = value > 70 ? 'red' : value < 30 ? 'green' : 'blue'
        return <Tag color={color}>{value}</Tag>
      },
    },
    {
      title: '布林带',
      key: 'boll',
      render: (_: any, record: Indicator) =>
        record.boll ? (
          <Space>
            <Tag>上轨：{record.boll.upper}</Tag>
            <Tag>中轨：{record.boll.middle}</Tag>
            <Tag>下轨：{record.boll.lower}</Tag>
          </Space>
        ) : (
          '-'
        ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between' }}>
        <h1 style={{ margin: 0 }}>📊 技术指标分析</h1>
        <Space>
          <Select
            value={period}
            onChange={setPeriod}
            options={[
              { value: 'daily', label: '日线' },
              { value: 'weekly', label: '周线' },
              { value: 'monthly', label: '月线' },
            ]}
          />
          <Button
            type="primary"
            icon={<ReloadOutlined spin={loading} />}
            onClick={fetchIndicators}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={indicators}
          rowKey="symbol"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}

export default IndicatorsPage
