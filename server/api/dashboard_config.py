"""
仪表盘配置 API
用户自定义仪表盘布局、组件、主题等
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from database import get_db_context, User, DashboardConfig
from api.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘配置"])


# ============ Pydantic 模型 ============

class WidgetConfig(BaseModel):
    """组件配置"""
    id: str
    type: str
    position: Optional[dict] = None
    props: Optional[dict] = None


class LayoutConfig(BaseModel):
    """布局配置"""
    layout: str = "grid"
    columns: int = 3
    widgets: List[WidgetConfig] = []


class ThemeConfig(BaseModel):
    """主题配置"""
    theme: str = "light"
    color_scheme: str = "red_green"
    font_size: str = "medium"


class DashboardConfigCreate(BaseModel):
    """创建配置请求"""
    name: str = "新配置"
    layout_config: Optional[LayoutConfig] = None
    enabled_widgets: Optional[List[str]] = None
    theme_config: Optional[ThemeConfig] = None
    refresh_interval: int = 30


class DashboardConfigUpdate(BaseModel):
    """更新配置请求"""
    name: Optional[str] = None
    layout_config: Optional[dict] = None
    enabled_widgets: Optional[List[str]] = None
    theme_config: Optional[dict] = None
    refresh_interval: Optional[int] = None
    is_default: Optional[bool] = None


class DashboardConfigResponse(BaseModel):
    """配置响应"""
    id: int
    name: str
    is_default: bool
    layout_config: Optional[dict] = None
    enabled_widgets: Optional[dict] = None
    theme_config: Optional[dict] = None
    refresh_interval: int
    
    class Config:
        from_attributes = True


# ============ API 端点 ============

@router.get("/configs", response_model=List[DashboardConfigResponse])
async def get_configs(current_user: User = Depends(get_current_user)):
    """获取用户的所有仪表盘配置"""
    with get_db_context() as db:
        configs = db.query(DashboardConfig).filter(
            DashboardConfig.user_id == current_user.id
        ).order_by(DashboardConfig.created_at.desc()).all()
        
        return configs


@router.get("/configs/default", response_model=DashboardConfigResponse)
async def get_default_config(current_user: User = Depends(get_current_user)):
    """获取用户的默认仪表盘配置"""
    with get_db_context() as db:
        config = db.query(DashboardConfig).filter(
            DashboardConfig.user_id == current_user.id,
            DashboardConfig.is_default == True
        ).first()
        
        if not config:
            # 如果没有默认配置，返回第一个
            config = db.query(DashboardConfig).filter(
                DashboardConfig.user_id == current_user.id
            ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="未找到仪表盘配置"
            )
        
        return config


@router.post("/configs", response_model=DashboardConfigResponse)
async def create_config(
    config_data: DashboardConfigCreate,
    current_user: User = Depends(get_current_user)
):
    """创建新的仪表盘配置"""
    with get_db_context() as db:
        # 如果是默认配置，先取消其他默认
        if config_data.name == "默认配置":
            db.query(DashboardConfig).filter(
                DashboardConfig.user_id == current_user.id,
                DashboardConfig.is_default == True
            ).update({"is_default": False})
        
        config = DashboardConfig(
            user_id=current_user.id,
            name=config_data.name,
            layout_config=config_data.layout_config.dict() if config_data.layout_config else None,
            enabled_widgets=config_data.enabled_widgets,
            theme_config=config_data.theme_config.dict() if config_data.theme_config else None,
            refresh_interval=config_data.refresh_interval,
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        return config


@router.put("/configs/{config_id}", response_model=DashboardConfigResponse)
async def update_config(
    config_id: int,
    config_data: DashboardConfigUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新仪表盘配置"""
    with get_db_context() as db:
        config = db.query(DashboardConfig).filter(
            DashboardConfig.id == config_id,
            DashboardConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="配置不存在"
            )
        
        # 更新字段
        update_data = config_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        # 如果设置为默认配置，先取消其他默认
        if config_data.is_default:
            db.query(DashboardConfig).filter(
                DashboardConfig.user_id == current_user.id,
                DashboardConfig.id != config_id
            ).update({"is_default": False})
        
        db.commit()
        db.refresh(config)
        
        return config


@router.delete("/configs/{config_id}")
async def delete_config(
    config_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除仪表盘配置"""
    with get_db_context() as db:
        config = db.query(DashboardConfig).filter(
            DashboardConfig.id == config_id,
            DashboardConfig.user_id == current_user.id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="配置不存在"
            )
        
        # 不能删除默认配置
        if config.is_default:
            raise HTTPException(
                status_code=400,
                detail="不能删除默认配置"
            )
        
        db.delete(config)
        db.commit()
        
        return {"message": "删除成功"}


@router.get("/widgets")
async def get_available_widgets():
    """获取可用的组件列表"""
    widgets = [
        {
            "id": "market_indices",
            "name": "大盘指数",
            "type": "market_card",
            "description": "显示 A 股主要指数行情",
            "default_props": {
                "indices": ["shanghai", "shenzhen", "chinext", "csi300"]
            }
        },
        {
            "id": "watchlist",
            "name": "自选股",
            "type": "stock_list",
            "description": "显示用户自选股行情"
        },
        {
            "id": "macd",
            "name": "MACD 指标",
            "type": "indicator_chart",
            "description": "显示 MACD 技术指标"
        },
        {
            "id": "kdj",
            "name": "KDJ 指标",
            "type": "indicator_chart",
            "description": "显示 KDJ 技术指标"
        },
        {
            "id": "news",
            "name": "财经新闻",
            "type": "news_list",
            "description": "显示最新财经新闻"
        },
        {
            "id": "ai_advice",
            "name": "AI 投资建议",
            "type": "ai_advice",
            "description": "显示 AI 分析的投资建议"
        }
    ]
    
    return widgets
