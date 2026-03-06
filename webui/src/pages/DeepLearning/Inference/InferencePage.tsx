// 模型推理页面 (骨架)
import React from 'react';
import { Typography, Card, Alert } from 'antd';
import { InboxOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const InferencePage: React.FC = () => {
  return (
    <div className="p-6">
      <Title level={2}>模型推理</Title>
      
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <InboxOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
          <Title level={4}>模型推理页面开发中</Title>
          <Text type="secondary">
            该页面将支持单次预测、批量预测、预测结果展示等功能
          </Text>
          <Alert
            message="WEBUI-DL-002"
            description="模型推理页面实现 - 预计工时 6 小时"
            type="info"
            showIcon
            style={{ marginTop: 24, maxWidth: 400, marginLeft: 'auto', marginRight: 'auto' }}
          />
        </div>
      </Card>
    </div>
  );
};

export default InferencePage;
