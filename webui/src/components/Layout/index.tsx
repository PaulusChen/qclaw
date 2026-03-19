/**
 * 布局组件
 */

import React from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { Menu } from 'antd'
import {
  DashboardOutlined,
  LineChartOutlined,
  FileTextOutlined,
  RocketOutlined,
  ExperimentOutlined,
  SettingOutlined,
} from '@ant-design/icons'

const Layout: React.FC = () => {
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">大盘指标</Link>,
    },
    {
      key: '/indicators',
      icon: <LineChartOutlined />,
      label: <Link to="/indicators">量化指标</Link>,
    },
    {
      key: '/news',
      icon: <FileTextOutlined />,
      label: <Link to="/news">新闻资讯</Link>,
    },
    {
      key: '/deep-learning',
      icon: <RocketOutlined />,
      label: <Link to="/deep-learning">深度学习</Link>,
    },
    {
      key: '/backtest',
      icon: <ExperimentOutlined />,
      label: <Link to="/backtest">回测中心</Link>,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">系统设置</Link>,
    },
  ]

  return (
    <div className="layout">
      <header className="header">
        <h1>🤖 QCLaw</h1>
        <nav className="nav">
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname.split('/')[1] || '/']}
            items={menuItems}
            style={{ borderBottom: 'none', background: 'transparent' }}
          />
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        <p>QCLaw 投资分析仪表盘</p>
      </footer>
    </div>
  )
}

export default Layout
