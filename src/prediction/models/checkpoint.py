"""
模型检查点管理

支持模型保存、加载、版本控制
"""

import torch
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class ModelCheckpoint:
    """
    模型检查点管理器
    
    功能:
    - 保存模型状态
    - 加载模型
    - 管理最佳模型和最新模型
    - 版本控制
    """
    
    def __init__(self, checkpoint_dir: str, keep_max: int = 5):
        """
        初始化检查点管理器
        
        参数:
            checkpoint_dir: 检查点保存目录
            keep_max: 保留的最大检查点数量
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.keep_max = keep_max
        
        self.best_metric = float("-inf")
        self.best_epoch = 0
    
    def save(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        metric: float,
        config: Dict[str, Any],
        is_best: bool = False,
    ) -> str:
        """
        保存检查点
        
        参数:
            model: 模型
            optimizer: 优化器
            epoch: 当前 epoch
            metric: 评估指标
            config: 模型配置
            is_best: 是否为最佳模型
            
        返回:
            保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 检查点数据
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "metric": metric,
            "config": config,
            "timestamp": timestamp,
        }
        
        # 文件名
        filename = f"checkpoint_epoch{epoch:04d}_{metric:.4f}_{timestamp}.pt"
        filepath = self.checkpoint_dir / filename
        
        # 保存
        torch.save(checkpoint, filepath)
        
        # 保存最佳模型
        if is_best or metric > self.best_metric:
            self.best_metric = metric
            self.best_epoch = epoch
            best_path = self.checkpoint_dir / "best_model.pt"
            torch.save(checkpoint, best_path)
            
            # 保存配置到单独文件
            config_path = self.checkpoint_dir / "best_config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
        
        # 保存最新模型
        latest_path = self.checkpoint_dir / "latest_model.pt"
        torch.save(checkpoint, latest_path)
        
        # 清理旧检查点
        self._cleanup_old_checkpoints()
        
        return str(filepath)
    
    def load(
        self,
        model: torch.nn.Module,
        optimizer: Optional[torch.optim.Optimizer] = None,
        checkpoint_path: Optional[str] = None,
        device: Optional[torch.device] = None,
    ) -> Dict[str, Any]:
        """
        加载检查点
        
        参数:
            model: 模型
            optimizer: 优化器 (可选)
            checkpoint_path: 检查点路径 (默认加载最新)
            device: 计算设备
            
        返回:
            检查点信息字典
        """
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 确定加载路径
        if checkpoint_path is None:
            checkpoint_path = self.checkpoint_dir / "latest_model.pt"
            if not checkpoint_path.exists():
                raise FileNotFoundError("No checkpoint found")
        else:
            checkpoint_path = Path(checkpoint_path)
        
        # 加载检查点
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # 恢复模型状态
        model.load_state_dict(checkpoint["model_state_dict"])
        
        # 恢复优化器状态
        if optimizer is not None:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        return {
            "epoch": checkpoint["epoch"],
            "metric": checkpoint["metric"],
            "config": checkpoint["config"],
            "timestamp": checkpoint["timestamp"],
        }
    
    def load_best(
        self,
        model: torch.nn.Module,
        device: Optional[torch.device] = None,
    ) -> Dict[str, Any]:
        """
        加载最佳模型
        
        参数:
            model: 模型
            device: 计算设备
            
        返回:
            检查点信息字典
        """
        best_path = self.checkpoint_dir / "best_model.pt"
        if not best_path.exists():
            raise FileNotFoundError("No best model found")
        
        return self.load(model, checkpoint_path=str(best_path), device=device)
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        列出所有检查点
        
        返回:
            检查点信息列表
        """
        checkpoints = []
        
        for filepath in self.checkpoint_dir.glob("checkpoint_*.pt"):
            checkpoint = torch.load(filepath, map_location="cpu")
            checkpoints.append({
                "path": str(filepath),
                "epoch": checkpoint["epoch"],
                "metric": checkpoint["metric"],
                "timestamp": checkpoint["timestamp"],
            })
        
        # 按指标排序
        checkpoints.sort(key=lambda x: x["metric"], reverse=True)
        
        return checkpoints
    
    def _cleanup_old_checkpoints(self):
        """清理旧检查点，保留最近的 keep_max 个"""
        checkpoints = list(self.checkpoint_dir.glob("checkpoint_*.pt"))
        
        if len(checkpoints) > self.keep_max:
            # 按修改时间排序
            checkpoints.sort(key=lambda x: x.stat().st_mtime)
            
            # 删除最旧的
            for checkpoint in checkpoints[:-self.keep_max]:
                checkpoint.unlink()
    
    def get_checkpoint_info(self) -> Dict[str, Any]:
        """获取检查点目录信息"""
        checkpoints = self.list_checkpoints()
        
        return {
            "checkpoint_dir": str(self.checkpoint_dir),
            "num_checkpoints": len(checkpoints),
            "best_metric": self.best_metric,
            "best_epoch": self.best_epoch,
            "checkpoints": checkpoints[:5],  # 返回前 5 个
        }


if __name__ == "__main__":
    # 测试检查点管理
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_mgr = ModelCheckpoint(tmpdir, keep_max=3)
        
        # 创建简单模型
        model = torch.nn.Linear(10, 2)
        optimizer = torch.optim.Adam(model.parameters())
        
        # 保存多个检查点
        for epoch in range(5):
            metric = 0.5 + epoch * 0.1
            filepath = checkpoint_mgr.save(
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                metric=metric,
                config={"test": True},
            )
            print(f"Saved: {filepath}")
        
        # 列出检查点
        info = checkpoint_mgr.get_checkpoint_info()
        print(f"\nCheckpoint info: {json.dumps(info, indent=2)}")
        
        print("\nModelCheckpoint test passed!")
