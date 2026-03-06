// 数据预处理配置页面 (骨架)
import React from 'react';
import { Typography, Card, Alert } from 'antd';
import { InboxOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const PreprocessingPage: React.FC = () => {
  return (
    <div className="p-6">
      <Title level={2}>数据预处理配置</Title>
      
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <InboxOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
          <Title level={4}>数据预处理页面开发中</Title>
          <Text type="secondary">
            该页面将支持数据源配置、特征选择、标准化方法配置等功能
          </Text>
          <Alert
            message="WEBUI-DL-004"
            description="数据预处理页面实现 - 预计工时 6 小时"
            type="info"
            showIcon
            style={{ marginTop: 24, maxWidth: 400, marginLeft: 'auto', marginRight: 'auto' }}
          />
        </div>
      </Card>
    </div>
  );
};

export default PreprocessingPage;
