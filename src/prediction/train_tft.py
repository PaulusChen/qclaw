"""
TFT 模型训练脚本

使用 pytorch-forecasting 训练 Temporal Fusion Transformer 模型
"""

import torch
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.metrics import RMSE, MAE
from pytorch_forecasting.data.encoders import GroupNormalizer, NaNLabelEncoder
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger

from .models.tft import TFTModel
from .data.tft_adapter import QclawDataAdapter, load_qclaw_data


class TFTTrainer:
    """
    TFT 模型训练器
    
    基于 pytorch-forecasting 和 pytorch-lightning
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        checkpoint_dir: str = "results/tft_checkpoints",
        log_dir: str = "results/tft_logs",
    ):
        """
        初始化训练器
        
        参数:
            config: 配置字典
            checkpoint_dir: 检查点保存目录
            log_dir: 日志目录
        """
        self.config = config
        self.checkpoint_dir = Path(checkpoint_dir)
        self.log_dir = Path(log_dir)
        
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.training_dataset = None
        self.val_dataset = None
        self.train_dataloader = None
        self.val_dataloader = None
        
    def prepare_data(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
    ):
        """
        准备训练和验证数据集
        
        参数:
            train_df: 训练数据 DataFrame
            val_df: 验证数据 DataFrame
        """
        max_encoder_length = self.config.get("max_encoder_length", 30)
        max_prediction_length = self.config.get("max_prediction_length", 7)
        target = self.config.get("target", "target")
        
        # 创建训练数据集
        self.training_dataset = TimeSeriesDataSet(
            train_df,
            time_idx="time_idx",
            target=target,
            group_ids=["stock_id"],
            max_encoder_length=max_encoder_length,
            max_prediction_length=max_prediction_length,
            static_categoricals=self.config.get("static_categoricals", []),
            static_reals=self.config.get("static_reals", []),
            time_varying_known_categoricals=self.config.get("time_varying_known_categoricals", []),
            time_varying_known_reals=self.config.get("time_varying_known_reals", []),
            time_varying_unknown_categoricals=self.config.get("time_varying_unknown_categoricals", []),
            time_varying_unknown_reals=self.config.get("time_varying_unknown_reals", []),
            target_normalizer=GroupNormalizer(groups=["stock_id"]),
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,
        )
        
        # 创建验证数据集 (使用训练集的编码器)
        self.val_dataset = TimeSeriesDataSet.from_dataset(
            self.training_dataset,
            val_df,
            stop_randomization=True,
        )
        
        # 创建数据加载器
        batch_size = self.config.get("batch_size", 64)
        num_workers = self.config.get("num_workers", 4)
        
        self.train_dataloader = self.training_dataset.to_dataloader(
            train=True,
            batch_size=batch_size,
            num_workers=num_workers,
        )
        
        self.val_dataloader = self.val_dataset.to_dataloader(
            train=False,
            batch_size=batch_size,
            num_workers=num_workers,
        )
        
        print(f"Training dataset: {len(self.training_dataset)} samples")
        print(f"Validation dataset: {len(self.val_dataset)} samples")
        
    def create_model(self):
        """创建 TFT 模型"""
        self.model = TemporalFusionTransformer.from_dataset(
            self.training_dataset,
            hidden_size=self.config.get("hidden_size", 16),
            attention_head_size=self.config.get("attention_head_size", 4),
            dropout=self.config.get("dropout", 0.1),
            hidden_continuous_size=self.config.get("hidden_continuous_size", 8),
            output_size=self.config.get("output_size", 7),
            loss=self.config.get("loss", "MSE"),
            learning_rate=self.config.get("learning_rate", 1e-3),
            log_interval=10,
        )
        
        print(f"Model created with {sum(p.numel() for p in self.model.parameters()):,} parameters")
        
    def train(
        self,
        max_epochs: int = 100,
        early_stopping_patience: int = 10,
        gradient_clip_val: float = 0.1,
        limit_train_batches: int = 30,
        limit_val_batches: int = 30,
    ):
        """
        训练模型
        
        参数:
            max_epochs: 最大训练轮数
            early_stopping_patience: 早停耐心值
            gradient_clip_val: 梯度裁剪值
            limit_train_batches: 训练批次限制
            limit_val_batches: 验证批次限制
        """
        if self.model is None:
            self.create_model()
        
        # 早停回调
        early_stop_callback = EarlyStopping(
            monitor="val_loss",
            min_delta=1e-4,
            patience=early_stopping_patience,
            verbose=False,
            mode="min",
        )
        
        # 检查点回调
        checkpoint_callback = ModelCheckpoint(
            dirpath=self.checkpoint_dir,
            filename="tft-{epoch:02d}-{val_loss:.4f}",
            monitor="val_loss",
            save_top_k=3,
            mode="min",
            save_last=True,
        )
        
        # TensorBoard 日志
        logger = TensorBoardLogger(
            save_dir=self.log_dir,
            name="tft_training",
        )
        
        # 创建 Trainer
        trainer = Trainer(
            max_epochs=max_epochs,
            accelerator="auto",
            devices=1,
            enable_progress_bar=True,
            enable_model_summary=True,
            gradient_clip_val=gradient_clip_val,
            limit_train_batches=limit_train_batches,
            limit_val_batches=limit_val_batches,
            callbacks=[early_stop_callback, checkpoint_callback],
            logger=logger,
        )
        
        # 训练模型
        print("Starting training...")
        trainer.fit(
            self.model,
            train_dataloaders=self.train_dataloader,
            val_dataloaders=self.val_dataloader,
        )
        
        # 加载最佳模型
        best_model_path = checkpoint_callback.best_model_path
        if best_model_path:
            print(f"Loading best model from {best_model_path}")
            self.model = TemporalFusionTransformer.load_from_checkpoint(best_model_path)
        
        return trainer
    
    def evaluate(self, test_df: pd.DataFrame) -> Dict[str, float]:
        """
        在测试集上评估模型
        
        参数:
            test_df: 测试数据 DataFrame
            
        返回:
            评估指标字典
        """
        if self.model is None:
            raise RuntimeError("Model not trained yet")
        
        # 创建测试数据集
        test_dataset = TimeSeriesDataSet.from_dataset(
            self.training_dataset,
            test_df,
        )
        test_dataloader = test_dataset.to_dataloader(
            train=False,
            batch_size=self.config.get("batch_size", 64),
            num_workers=self.config.get("num_workers", 4),
        )
        
        # 进行预测
        predictions = self.model.predict(test_dataloader)
        
        # 计算指标
        actuals = torch.cat([y for x, y in iter(test_dataloader)])
        
        mse = torch.nn.functional.mse_loss(predictions, actuals).item()
        rmse = np.sqrt(mse)
        mae = torch.nn.functional.l1_loss(predictions, actuals).item()
        
        metrics = {
            "MSE": mse,
            "RMSE": rmse,
            "MAE": mae,
        }
        
        print(f"Test Metrics: MSE={mse:.6f}, RMSE={rmse:.6f}, MAE={mae:.6f}")
        
        return metrics
    
    def save_model(self, path: str):
        """保存模型"""
        if self.model is None:
            raise RuntimeError("No model to save")
        
        self.model.save(path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """加载模型"""
        self.model = TemporalFusionTransformer.load_from_checkpoint(path)
        print(f"Model loaded from {path}")


def train_tft(
    data_path: str,
    config: Optional[Dict[str, Any]] = None,
    output_dir: str = "results/tft",
) -> TFTTrainer:
    """
    便捷函数：训练 TFT 模型
    
    参数:
        data_path: 数据文件路径
        config: 配置字典
        output_dir: 输出目录
        
    返回:
        训练好的 TFTTrainer 实例
    """
    # 默认配置
    default_config = {
        "max_encoder_length": 30,
        "max_prediction_length": 7,
        "hidden_size": 16,
        "attention_head_size": 4,
        "dropout": 0.1,
        "hidden_continuous_size": 8,
        "output_size": 7,
        "learning_rate": 1e-3,
        "batch_size": 64,
        "num_workers": 4,
        "target": "target",
        "static_categoricals": [],
        "static_reals": [],
        "time_varying_known_categoricals": [],
        "time_varying_known_reals": [],
        "time_varying_unknown_categoricals": [],
        "time_varying_unknown_reals": [],
    }
    
    if config:
        default_config.update(config)
    
    # 加载数据
    adapter = QclawDataAdapter()
    df = load_qclaw_data(data_path, adapter=adapter)
    
    # 添加技术指标
    df = adapter.add_technical_indicators(df)
    
    # 创建未来目标
    df = adapter.create_future_targets(df)
    
    # 分割数据
    train_df, val_df, test_df = adapter.split_data(df)
    
    # 获取特征配置
    feature_config = adapter.get_feature_config(train_df)
    default_config.update(feature_config)
    
    # 创建训练器
    trainer = TFTTrainer(default_config, checkpoint_dir=f"{output_dir}/checkpoints")
    
    # 准备数据
    trainer.prepare_data(train_df, val_df)
    
    # 创建模型
    trainer.create_model()
    
    # 训练
    trainer.train(max_epochs=100)
    
    # 评估
    trainer.evaluate(test_df)
    
    # 保存模型
    trainer.save_model(f"{output_dir}/tft_model.pt")
    
    # 保存配置
    with open(f"{output_dir}/config.json", "w") as f:
        json.dump(default_config, f, indent=2)
    
    return trainer


if __name__ == "__main__":
    # 示例用法
    config = {
        "max_encoder_length": 30,
        "max_prediction_length": 7,
        "hidden_size": 32,
        "learning_rate": 1e-3,
    }
    
    # 训练模型 (需要提供实际数据路径)
    # trainer = train_tft("data/stock_data.csv", config=config)
