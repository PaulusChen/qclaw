"""
配置模块

提供全局配置和目录管理功能
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """全局配置类"""
    
    def __init__(self):
        # 项目根目录
        self.ROOT_DIR = Path(__file__).parent.parent
        
        # 数据目录
        self.QLIB_DATA_DIR = os.getenv("QLIB_DATA_DIR", str(self.ROOT_DIR / "data" / "qlib"))
        self.DATA_CACHE_DIR = os.getenv("DATA_CACHE_DIR", str(self.ROOT_DIR / "data" / "cache"))
        
        # 结果目录
        self.RESULTS_DIR = os.getenv("RESULTS_DIR", str(self.ROOT_DIR / "results"))
        
        # 模型目录
        self.MODELS_DIR = os.getenv("MODELS_DIR", str(self.ROOT_DIR / "models"))
        
        # 日志目录
        self.LOGS_DIR = os.getenv("LOGS_DIR", str(self.ROOT_DIR / "logs"))
        
        # 确保目录存在
        self.ensure_dirs()
    
    def ensure_dirs(self):
        """确保所有配置目录存在"""
        dirs = [
            self.QLIB_DATA_DIR,
            self.DATA_CACHE_DIR,
            self.RESULTS_DIR,
            self.MODELS_DIR,
            self.LOGS_DIR,
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


# 全局配置实例
config = Config()
