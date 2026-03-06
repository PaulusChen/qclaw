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
from api import market, indicators, advice, news, deep_learning
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
        # 测试连接
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
        logger.warning(f"⚠️ AKShare 服务初始化失败：{e}")
    
    logger.info("🎉 服务启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("👋 正在关闭服务...")
    
    if app.state.redis:
        await app.state.redis.close()
        logger.info("✅ Redis 连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="量化交易平台 API",
    description="提供股票行情、技术指标、AI 建议、财经新闻等数据服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    redis_status = "connected" if app.state.redis else "disconnected"
    return {
        "status": "healthy",
        "version": "1.0.0",
        "redis": redis_status
    }


# 注册路由
app.include_router(market.router, prefix="/api/market", tags=["行情数据"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["技术指标"])
app.include_router(advice.router, prefix="/api/advice", tags=["AI 建议"])
app.include_router(news.router, prefix="/api/news", tags=["财经新闻"])
app.include_router(deep_learning.router, prefix="/api/v1/dl", tags=["深度学习"])


# 根路径
@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "欢迎使用量化交易平台 API",
        "docs": "/docs",
        "health": "/health"
    }


# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常：{exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "path": str(request.url.path)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
