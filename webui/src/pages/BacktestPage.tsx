/**
 * 回测中心页面
 */

import React, { useState } from 'react'
import { Card, Table, Button, Space, Tag, Progress, Statistic, Row, Col } from 'antd'
import { PlayCircleOutlined, StopOutlined, BarChartOutlined } from '@ant-design/icons'

interface BacktestResult {
  id: string
  name: string
  strategy: string
  period: string
  returnRate: number
  sharpeRatio: number
  maxDrawdown: number
  status: 'running' | 'completed' | 'failed'
  progress?: number
}

const BacktestPage: React.FC = () => {
  const [results, setResults] = useState<BacktestResult[]>([
    {
      id: '1',
      name: 'MACD 金叉策略',
      strategy: '趋势跟踪',
      period: '2024-01-01 ~ 2024-12-31',
      returnRate: 25.6,
      sharpeRatio: 1.8,
      maxDrawdown: -12.3,
      status: 'completed',
      progress: 100,
    },
    {
      id: '2',
      name: '双均线策略',
      strategy: '趋势跟踪',
      period: '2024-01-01 ~ 2024-12-31',
      returnRate: 18.2,
      sharpeRatio: 1.5,
      maxDrawdown: -15.8,
      status: 'completed',
      progress: 100,
    },
    {
      id: '3',
      name: 'RSI 超卖策略',
      strategy: '均值回归',
      period: '2024-06-01 ~ 2024-12-31',
      returnRate: 0,
      sharpeRatio: 0,
      maxDrawdown: 0,
      status: 'running',
      progress: 65,
    },
  ])

  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '策略类型',
      dataIndex: 'strategy',
      key: 'strategy',
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '回测区间',
      dataIndex: 'period',
      key: 'period',
    },
    {
      title: '收益率',
      dataIndex: 'returnRate',
      key: 'returnRate',
      render: (value: number, record: BacktestResult) =>
        record.status === 'completed' ? (
          <span style={{ color: value >= 0 ? '#cf1322' : '#3f8600', fontWeight: 600 }}>
            {value >= 0 ? '+' : ''}{value.toFixed(2)}%
          </span>
        ) : (
          '-'
        ),
    },
    {
      title: '夏普比率',
      dataIndex: 'sharpeRatio',
      key: 'sharpeRatio',
      render: (value: number, record: BacktestResult) =>
        record.status === 'completed' ? value.toFixed(2) : '-',
    },
    {
      title: '最大回撤',
      dataIndex: 'maxDrawdown',
      key: 'maxDrawdown',
      render: (value: number, record: BacktestResult) =>
        record.status === 'completed' ? (
          <span style={{ color: '#3f8600' }}>{value.toFixed(2)}%</span>
        ) : (
          '-'
        ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string, record: BacktestResult) => {
        if (status === 'running') {
          return (
            <Space>
              <Tag color="processing">运行中</Tag>
              <Progress percent={record.progress} size="small" style={{ width: '100px' }} />
            </Space>
          )
        }
        return <Tag color={status === 'completed' ? 'success' : 'error'}>
          {status === 'completed' ? '已完成' : '失败'}
        </Tag>
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: BacktestResult) => (
        <Space>
          {record.status !== 'running' && (
            <Button type="link" size="small" icon={<PlayCircleOutlined />}>
              重新运行
            </Button>
          )}
          {record.status === 'running' && (
            <Button type="link" size="small" danger icon={<StopOutlined />}>
              停止
            </Button>
          )}
          {record.status === 'completed' && (
            <Button type="link" size="small" icon={<BarChartOutlined />}>
              查看报告
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ margin: 0 }}>📈 回测中心</h1>
        <p style={{ color: '#666', marginTop: '8px' }}>
          管理和查看策略回测结果
        </p>
      </div>

      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="总策略数"
              value={results.length}
              suffix="个"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="已完成"
              value={results.filter(r => r.status === 'completed').length}
              suffix="个"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="平均收益率"
              value={
                results
                  .filter(r => r.status === 'completed')
                  .reduce((sum, r) => sum + r.returnRate, 0) /
                results.filter(r => r.status === 'completed').length || 0
              }
              precision={2}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={results}
          rowKey="id"
          pagination={false}
        />
      </Card>
    </div>
  )
}

export default BacktestPage
