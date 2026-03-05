/**
 * 布局组件
 */

import React from 'react'
import { Link, Outlet } from 'react-router-dom'

const Layout: React.FC = () => {
  return (
    <div className="layout">
      <header className="header">
        <h1>🤖 QCLaw</h1>
        <nav className="nav">
          <Link to="/">大盘指标</Link>
          <Link to="/indicators">量化指标</Link>
          <Link to="/news">新闻资讯</Link>
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
