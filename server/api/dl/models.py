"""
深度学习模型管理 API
模型列表、模型详情、模型训练等
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any, List
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """
    获取可用模型列表
    """
    try:
        # 扫描 checkpoints 目录
        checkpoint_dir = "checkpoints/"
        models = []
        
        if os.path.exists(checkpoint_dir):
            for file in os.listdir(checkpoint_dir):
                if file.endswith('.pth'):
                    model_name = file.replace('.pth', '')
                    models.append({
                        "id": model_name,
                        "name": model_name.replace('_', ' ').title(),
                        "type": "LSTM" if "lstm" in model_name else "TFT",
                        "status": "active",
                        "accuracy": 0.85,  # TODO: 从训练记录读取
                        "last_trained": datetime.now().isoformat(),
                        "path": os.path.join(checkpoint_dir, file)
                    })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"获取模型列表失败：{e}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败：{str(e)}")

@router.get("/models/{model_id}")
async def get_model_detail(model_id: str) -> Dict[str, Any]:
    """
    获取模型详情
    """
    checkpoint_path = f"checkpoints/{model_id}.pth"
    
    if not os.path.exists(checkpoint_path):
        raise HTTPException(status_code=404, detail=f"模型 {model_id} 不存在")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "model": {
            "id": model_id,
            "name": model_id.replace('_', ' ').title(),
            "type": "LSTM" if "lstm" in model_id else "TFT",
            "status": "active",
            "path": checkpoint_path,
            "size": os.path.getsize(checkpoint_path),
            "last_trained": datetime.now().isoformat()
        }
    }
