"""
数据库初始化和管理
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from .schema import Base, User, DashboardConfig, WatchlistStock, AlertRule, UserPreference


# 数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app/data/qclaw.db"
)


def get_engine():
    """获取数据库引擎"""
    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite 需要
    )


def init_db():
    """初始化数据库，创建所有表"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库初始化完成：{DATABASE_URL}")


def get_session() -> Session:
    """获取数据库会话"""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


@contextmanager
def get_db_context():
    """数据库会话上下文管理器"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()


# 导出所有模型
__all__ = [
    'Base',
    'User',
    'DashboardConfig',
    'WatchlistStock',
    'AlertRule',
    'UserPreference',
    'init_db',
    'get_session',
    'get_db_context',
]
