/**
 * 系统设置页面
 */

import React, { useState } from 'react'
import { Card, Form, Input, InputNumber, Switch, Select, Button, Space, Divider, message, Tag } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'

const { TextArea } = Input

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const handleSave = async (values: any) => {
    setLoading(true)
    try {
      // TODO: 实现保存设置的 API
      console.log('保存设置:', values)
      message.success('设置已保存')
    } catch (err) {
      message.error('保存失败')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    form.resetFields()
    message.info('已重置为默认值')
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ margin: 0 }}>⚙️ 系统设置</h1>
        <p style={{ color: '#666', marginTop: '8px' }}>
          配置系统参数和偏好设置
        </p>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          refreshInterval: 30,
          defaultMarket: 'A 股',
          riskLevel: 'medium',
          enableNotification: true,
          enableAutoTrade: false,
          maxPosition: 80,
          stopLoss: 5,
          takeProfit: 15,
        }}
      >
        <Card title="📊 市场设置" style={{ marginBottom: '16px' }}>
          <Form.Item
            label="默认市场"
            name="defaultMarket"
          >
            <Select>
              <Select.Option value="A 股">A 股</Select.Option>
              <Select.Option value="港股">港股</Select.Option>
              <Select.Option value="美股">美股</Select.Option>
              <Select.Option value="加密货币">加密货币</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="数据刷新间隔（秒）"
            name="refreshInterval"
          >
            <InputNumber min={5} max={300} step={5} addonAfter="秒" style={{ width: '200px' }} />
          </Form.Item>
        </Card>

        <Card title="🎯 交易设置" style={{ marginBottom: '16px' }}>
          <Form.Item
            label="风险等级"
            name="riskLevel"
          >
            <Select>
              <Select.Option value="low">保守型</Select.Option>
              <Select.Option value="medium">稳健型</Select.Option>
              <Select.Option value="high">激进型</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="最大仓位（%）"
            name="maxPosition"
          >
            <InputNumber min={0} max={100} addonAfter="%" style={{ width: '200px' }} />
          </Form.Item>

          <Form.Item
            label="止损线（%）"
            name="stopLoss"
          >
            <InputNumber min={1} max={20} addonAfter="%" style={{ width: '200px' }} />
          </Form.Item>

          <Form.Item
            label="止盈线（%）"
            name="takeProfit"
          >
            <InputNumber min={5} max={50} addonAfter="%" style={{ width: '200px' }} />
          </Form.Item>
        </Card>

        <Card title="🔔 通知设置" style={{ marginBottom: '16px' }}>
          <Form.Item
            label="启用价格提醒"
            name="enableNotification"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="启用自动交易"
            name="enableAutoTrade"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Card>

        <Card title="🔌 API 配置" style={{ marginBottom: '16px' }}>
          <Form.Item
            label="AKShare API Key"
            name="akshareApiKey"
            extra="用于获取实时行情数据"
          >
            <Input.Password placeholder="请输入 API Key" style={{ maxWidth: '400px' }} />
          </Form.Item>

          <Form.Item
            label="备用数据源"
            name="backupDataSource"
          >
            <Select mode="multiple" style={{ maxWidth: '400px' }}>
              <Select.Option value="tencent">腾讯财经</Select.Option>
              <Select.Option value="sina">新浪财经</Select.Option>
              <Select.Option value="eastmoney">东方财富</Select.Option>
            </Select>
          </Form.Item>
        </Card>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={loading}
            >
              保存设置
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleReset}
            >
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>

      <Divider />

      <Card title="ℹ️ 系统信息">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Tag color="blue">QCLaw v1.0.0</Tag>
            <Tag color="green">运行中</Tag>
          </div>
          <p style={{ margin: 0, color: '#666' }}>
            最后更新：{new Date().toLocaleString('zh-CN')}
          </p>
        </Space>
      </Card>
    </div>
  )
}

export default SettingsPage
