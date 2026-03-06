"""
量化交易平台后端服务
FastAPI + AKShare + Redis
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging

from config.settings import settings
from api import market_router, health_router, advice_router, dl_models_router, dl_predict_router
from api import indicators, news, deep_learning
from services import akshare_service, cache_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 正在启动量化交易平台后端服务...")
    
    # 初始化 Redis 连接
    try:
        app.state.redis = await redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        await app.state.redis.ping()
        logger.info(f"✅ Redis 连接成功：{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    except Exception as e:
        logger.warning(f"⚠️ Redis 连接失败：{e}")
        app.state.redis = None
    
    # 初始化 AKShare 服务
    try:
        await akshare_service.init()
        logger.info("✅ AKShare 服务初始化成功")
    except Exception as e:
        logger.error(f"❌ AKShare 服务初始化失败：{e}")
    
    logger.info("🎉 服务启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 正在关闭服务...")
    if app.state.redis:
        await app.state.redis.close()
        logger.info("✅ Redis 连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="QCLaw 量化交易平台",
    description="基于 AI 的智能量化分析系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - 新增 API
app.include_router(market_router, prefix="/api/market", tags=["市场数据"])
app.include_router(health_router, prefix="/api", tags=["健康检查"])
app.include_router(advice_router, prefix="/api/advice", tags=["AI 建议"])
app.include_router(dl_models_router, tags=["深度学习 - 模型管理"])
app.include_router(dl_predict_router, tags=["深度学习 - 预测"])

# 注册路由 - 原有 API
app.include_router(indicators.router, prefix="/api/indicators", tags=["技术指标"])
app.include_router(news.router, prefix="/api/news", tags=["财经新闻"])
app.include_router(deep_learning.router, prefix="/api/v1/dl", tags=["深度学习"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "QCLaw 量化交易平台",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api")
async def api_info():
    """API 信息"""
    return {
        "name": "QCLaw API",
        "version": "1.0.0",
        "endpoints": [
            "/api/health - 健康检查",
            "/api/market/indices - 大盘指标",
            "/api/advice - AI 建议",
            "/api/v1/dl/models - 模型列表",
            "/api/v1/dl/predict - 模型预测"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
