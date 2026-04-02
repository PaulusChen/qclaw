// 深度学习模块布局
import React from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import { Menu } from 'antd';
import {
  PlayCircleOutlined,
  RocketOutlined,
  DatabaseOutlined,
  FolderOutlined,
  ApiOutlined,
} from '@ant-design/icons';

const DeepLearningLayout: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    {
      key: '/deep-learning/training',
      icon: <PlayCircleOutlined />,
      label: '模型训练',
    },
    {
      key: '/deep-learning/inference',
      icon: <RocketOutlined />,
      label: '模型推理',
    },
    {
      key: '/deep-learning/management',
      icon: <FolderOutlined />,
      label: '模型管理',
    },
    {
      key: '/deep-learning/preprocessing',
      icon: <DatabaseOutlined />,
      label: '数据预处理',
    },
  ];

  return (
    <div style={{ display: 'flex' }}>
      {/* 侧边导航菜单 */}
      <div style={{ 
        width: '224px', 
        backgroundColor: '#fff', 
        borderRight: '1px solid #f0f0f0', 
        minHeight: '100vh' 
      }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ApiOutlined style={{ fontSize: 24, color: '#722ed1' }} />
            <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#722ed1' }}>深度学习</span>
          </div>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => {
            window.location.hash = key;
          }}
          style={{ border: 'none' }}
        />
      </div>

      {/* 主内容区域 */}
      <div style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
        <Outlet />
      </div>
    </div>
  );
};

export default DeepLearningLayout;
