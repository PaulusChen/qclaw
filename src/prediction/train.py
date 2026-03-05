"""
模型训练流程

包含:
- 训练循环
- 验证循环
- 早停机制
- 学习率调度
- 训练日志和指标记录
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional, List, Tuple
import time
from pathlib import Path
import json

from .models.lstm import LSTMPredictor
from .models.transformer import TransformerPredictor
from .models.multi_task_head import MultiTaskHead, MultiTaskLoss
from .models.checkpoint import ModelCheckpoint


class Trainer:
    """
    模型训练器
    
    支持:
    - 单任务/多任务训练
    - GPU 加速
    - 早停
    - 学习率调度
    - 检查点保存
    """
    
    def __init__(
        self,
        model: nn.Module,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        device: torch.device,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
        checkpoint_dir: str = "checkpoints",
        early_stopping_patience: int = 10,
        early_stopping_min_delta: float = 0.001,
    ):
        """
        初始化训练器
        
        参数:
            model: 模型
            criterion: 损失函数
            optimizer: 优化器
            device: 计算设备
            scheduler: 学习率调度器 (可选)
            checkpoint_dir: 检查点目录
            early_stopping_patience: 早停耐心值
            early_stopping_min_delta: 早停最小改进值
        """
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.checkpoint_dir = checkpoint_dir
        
        self.early_stopping_patience = early_stopping_patience
        self.early_stopping_min_delta = early_stopping_min_delta
        
        self.checkpoint_mgr = ModelCheckpoint(checkpoint_dir)
        
        self.best_metric = float("-inf")
        self.patience_counter = 0
        self.training_history: List[Dict[str, Any]] = []
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """
        训练一个 epoch
        
        参数:
            train_loader: 训练数据加载器
            
        返回:
            训练指标字典
        """
        self.model.train()
        total_loss = 0.0
        n_batches = 0
        
        for batch in train_loader:
            # 移动数据到设备
            features = batch["features"].to(self.device)
            
            # 前向传播
            self.optimizer.zero_grad()
            
            # 模型输出
            if isinstance(self.criterion, MultiTaskLoss):
                # 多任务模式
                features_out = self.model(features)
                predictions = self.model.head(features_out) if hasattr(self.model, "head") else features_out
                
                # 准备目标
                targets = {
                    "direction": batch["direction"].to(self.device),
                    "return": batch.get("return", torch.zeros_like(batch["direction"])).to(self.device),
                    "confidence": batch.get("confidence", torch.ones_like(batch["direction"])).to(self.device),
                }
                
                loss_dict = self.criterion(predictions, targets)
                loss = loss_dict["total"]
            else:
                # 单任务模式
                outputs = self.model(features)
                targets = batch["direction"].to(self.device)
                loss = self.criterion(outputs, targets)
            
            # 反向传播
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            n_batches += 1
        
        return {
            "train_loss": total_loss / n_batches,
        }
    
    @torch.no_grad()
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """
        验证
        
        参数:
            val_loader: 验证数据加载器
            
        返回:
            验证指标字典
        """
        self.model.eval()
        total_loss = 0.0
        n_batches = 0
        
        all_preds = []
        all_targets = []
        
        for batch in val_loader:
            features = batch["features"].to(self.device)
            
            if isinstance(self.criterion, MultiTaskLoss):
                features_out = self.model(features)
                predictions = self.model.head(features_out) if hasattr(self.model, "head") else features_out
                
                targets = {
                    "direction": batch["direction"].to(self.device),
                    "return": batch.get("return", torch.zeros_like(batch["direction"])).to(self.device),
                    "confidence": batch.get("confidence", torch.ones_like(batch["direction"])).to(self.device),
                }
                
                loss_dict = self.criterion(predictions, targets)
                loss = loss_dict["total"]
                
                # 收集预测
                all_preds.append(predictions["direction"].argmax(dim=1).cpu())
                all_targets.append(batch["direction"])
            else:
                outputs = self.model(features)
                targets = batch["direction"].to(self.device)
                loss = self.criterion(outputs, targets)
                
                all_preds.append(outputs.argmax(dim=1).cpu())
                all_targets.append(batch["direction"].cpu())
            
            total_loss += loss.item()
            n_batches += 1
        
        # 计算准确率
        all_preds = torch.cat(all_preds)
        all_targets = torch.cat(all_targets)
        accuracy = (all_preds == all_targets).float().mean().item()
        
        return {
            "val_loss": total_loss / n_batches,
            "val_accuracy": accuracy,
        }
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 100,
        log_interval: int = 10,
    ) -> Dict[str, Any]:
        """
        完整训练流程
        
        参数:
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            epochs: 训练轮数
            log_interval: 日志间隔
            
        返回:
            训练结果字典
        """
        print(f"Starting training for {epochs} epochs...")
        print(f"Device: {self.device}")
        print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")
        
        start_time = time.time()
        
        for epoch in range(epochs):
            epoch_start = time.time()
            
            # 训练
            train_metrics = self.train_epoch(train_loader)
            
            # 验证
            val_metrics = self.validate(val_loader)
            
            # 学习率调度
            if self.scheduler is not None:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics["val_loss"])
                else:
                    self.scheduler.step()
            
            # 合并指标
            epoch_metrics = {
                "epoch": epoch + 1,
                **train_metrics,
                **val_metrics,
                "lr": self.optimizer.param_groups[0]["lr"],
                "time": time.time() - epoch_start,
            }
            
            self.training_history.append(epoch_metrics)
            
            # 日志
            if (epoch + 1) % log_interval == 0:
                print(f"Epoch {epoch + 1:03d}/{epochs}: "
                      f"train_loss={epoch_metrics['train_loss']:.4f}, "
                      f"val_loss={epoch_metrics['val_loss']:.4f}, "
                      f"val_acc={epoch_metrics['val_accuracy']:.4f}, "
                      f"lr={epoch_metrics['lr']:.6f}, "
                      f"time={epoch_metrics['time']:.1f}s")
            
            # 早停检查
            current_metric = epoch_metrics["val_accuracy"]
            if current_metric > self.best_metric + self.early_stopping_min_delta:
                self.best_metric = current_metric
                self.patience_counter = 0
                
                # 保存最佳检查点
                self.checkpoint_mgr.save(
                    model=self.model,
                    optimizer=self.optimizer,
                    epoch=epoch + 1,
                    metric=current_metric,
                    config=self.model.get_config() if hasattr(self.model, "get_config") else {},
                    is_best=True,
                )
                print(f"  → New best! Saved checkpoint (acc={current_metric:.4f})")
            else:
                self.patience_counter += 1
                
                if self.patience_counter >= self.early_stopping_patience:
                    print(f"Early stopping at epoch {epoch + 1} (no improvement for {self.patience_counter} epochs)")
                    break
        
        total_time = time.time() - start_time
        
        return {
            "best_metric": self.best_metric,
            "total_epochs": len(self.training_history),
            "total_time": total_time,
            "history": self.training_history,
        }
    
    def save_training_log(self, output_path: str):
        """保存训练日志"""
        with open(output_path, "w") as f:
            json.dump({
                "best_metric": self.best_metric,
                "history": self.training_history,
            }, f, indent=2)


def create_trainer(
    model_type: str = "lstm",
    input_size: int = 25,
    hidden_size: int = 128,
    learning_rate: float = 0.001,
    weight_decay: float = 1e-5,
    multi_task: bool = True,
    device: Optional[torch.device] = None,
    checkpoint_dir: str = "checkpoints",
) -> Trainer:
    """
    创建训练器
    
    参数:
        model_type: 模型类型 ("lstm" 或 "transformer")
        input_size: 输入特征数
        hidden_size: 隐藏层维度
        learning_rate: 学习率
        weight_decay: 权重衰减
        multi_task: 是否多任务学习
        device: 计算设备
        checkpoint_dir: 检查点目录
        
    返回:
        Trainer 实例
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 创建模型
    if model_type == "lstm":
        model = LSTMPredictor(input_size=input_size, hidden_size=hidden_size)
    elif model_type == "transformer":
        model = TransformerPredictor(input_size=input_size, d_model=hidden_size)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # 多任务头
    if multi_task:
        model.head = MultiTaskHead(hidden_dim=hidden_size)
        criterion = MultiTaskLoss()
    else:
        criterion = nn.CrossEntropyLoss()
    
    # 优化器
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )
    
    # 学习率调度器
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=5,
        verbose=True,
    )
    
    # 创建训练器
    trainer = Trainer(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        scheduler=scheduler,
        checkpoint_dir=checkpoint_dir,
        early_stopping_patience=10,
    )
    
    return trainer


if __name__ == "__main__":
    # 测试训练器
    from .data.dataset import StockDataset, create_dataloader
    import numpy as np
    
    np.random.seed(42)
    
    # 创建模拟数据
    n_samples = 1000
    seq_len = 60
    n_features = 25
    
    features = np.random.randn(n_samples, seq_len, n_features)
    targets = {"direction": np.random.randint(0, 2, n_samples)}
    
    dataset = StockDataset(features, targets)
    train_loader = create_dataloader(dataset, batch_size=32, shuffle=True, num_workers=0)
    val_loader = create_dataloader(dataset, batch_size=32, shuffle=False, num_workers=0)
    
    # 创建训练器
    trainer = create_trainer(model_type="lstm", input_size=n_features)
    
    print(f"Device: {trainer.device}")
    print(f"Model: {trainer.model.__class__.__name__}")
    
    # 运行少量 epoch 测试
    result = trainer.train(train_loader, val_loader, epochs=3, log_interval=1)
    
    print(f"\nTraining completed!")
    print(f"Best metric: {result['best_metric']:.4f}")
    print(f"Total time: {result['total_time']:.1f}s")
    
    print("\nTrainer test passed!")
