// 深度学习模块布局
import React from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import { Menu } from 'antd';
import {
  BrainOutlined,
  PlayCircleOutlined,
  RocketOutlined,
  DatabaseOutlined,
  FolderOutlined,
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
    <div className="flex">
      {/* 侧边导航菜单 */}
      <div className="w-56 bg-white border-r border-gray-200 min-h-screen">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <BrainOutlined style={{ fontSize: 24, color: '#722ed1' }} />
            <span className="text-lg font-bold" style={{ color: '#722ed1' }}>深度学习</span>
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
      <div className="flex-1 bg-gray-50">
        <Outlet />
      </div>
    </div>
  );
};

export default DeepLearningLayout;
