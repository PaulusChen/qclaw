"""
数据库模型定义
用户配置系统 Schema
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 用户信息
    nickname = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # 关联
    dashboard_configs = relationship("DashboardConfig", back_populates="user", cascade="all, delete-orphan")
    watchlist_stocks = relationship("WatchlistStock", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class DashboardConfig(Base):
    """用户仪表盘配置表"""
    __tablename__ = 'dashboard_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 配置名称
    name = Column(String(100), default='默认配置', nullable=False)
    
    # 是否为默认配置
    is_default = Column(Boolean, default=False)
    
    # 布局配置 (JSON)
    # 示例结构：
    # {
    #   "layout": "grid",  // grid, list, custom
    #   "columns": 3,      // 列数
    #   "widgets": [       // 组件列表
    #     {
    #       "id": "market_indices",
    #       "type": "market_card",
    #       "position": {"x": 0, "y": 0, "w": 2, "h": 1},
    #       "props": {"indices": ["shanghai", "shenzhen"]}
    #     }
    #   ]
    # }
    layout_config = Column(JSON, nullable=True)
    
    # 显示的指标组件 (JSON)
    # 示例：["market_indices", "macd", "kdj", "news", "ai_advice"]
    enabled_widgets = Column(JSON, nullable=True)
    
    # 主题配置
    # 示例：{"theme": "light", "color_scheme": "red_green", "font_size": "medium"}
    theme_config = Column(JSON, nullable=True)
    
    # 刷新间隔（秒）
    refresh_interval = Column(Integer, default=30)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联
    user = relationship("User", back_populates="dashboard_configs")
    
    def __repr__(self):
        return f"<DashboardConfig(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class WatchlistStock(Base):
    """用户自选股表"""
    __tablename__ = 'watchlist_stocks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 股票代码
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(50), nullable=True)
    market = Column(String(20), nullable=True)  # SH, SZ, HK, US
    
    # 分组/标签
    group_name = Column(String(50), default='默认', nullable=True)
    
    # 排序
    sort_order = Column(Integer, default=0)
    
    # 备注
    note = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联
    user = relationship("User", back_populates="watchlist_stocks")
    
    # 唯一约束（同一用户不能重复添加同一股票）
    __table_args__ = (
        # 这里需要在创建表时添加唯一约束
        # UniqueConstraint('user_id', 'stock_code', name='uq_user_stock')
    )
    
    def __repr__(self):
        return f"<WatchlistStock(id={self.id}, user_id={self.user_id}, stock='{self.stock_code}')>"


class AlertRule(Base):
    """用户预警规则表"""
    __tablename__ = 'alert_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 规则名称
    name = Column(String(100), nullable=False)
    
    # 股票代码
    stock_code = Column(String(20), nullable=False)
    
    # 预警类型
    # price_above: 价格高于
    # price_below: 价格低于
    # change_above: 涨幅高于
    # change_below: 跌幅低于
    # volume_above: 成交量高于
    alert_type = Column(String(20), nullable=False)
    
    # 阈值
    threshold = Column(Float, nullable=False)
    
    # 是否启用
    is_active = Column(Boolean, default=True)
    
    # 通知方式
    # email, sms, push, wechat
    notification_methods = Column(JSON, nullable=True)
    
    # 触发次数
    triggered_count = Column(Integer, default=0)
    
    # 最后触发时间
    last_triggered_at = Column(DateTime, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class UserPreference(Base):
    """用户偏好设置表"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # 偏好设置 (JSON)
    # 示例：
    # {
    #   "language": "zh-CN",
    #   "timezone": "Asia/Shanghai",
    #   "default_market": "A",  # A 股/港股/美股
    #   "show_help_tips": true,
    #   "auto_refresh": true,
    #   "sound_alerts": false,
    #   "compact_mode": false
    # }
    preferences = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UserPreference(id={self.id}, user_id={self.user_id})>"
