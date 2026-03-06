"""
Temporal Fusion Transformer (TFT) 模型集成

使用 pytorch-forecasting 库实现 TFT 模型
文档：https://pytorch-forecasting.readthedocs.io

核心优势:
- 可解释性：注意力机制可视化
- 多步预测：支持 7/14/30 天预测
- 处理静态和动态特征
- 不确定性量化：分位数预测
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from pathlib import Path

try:
    from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
    from pytorch_forecasting.metrics import QuantileLoss
    PYTORCH_FORECASTING_AVAILABLE = True
except ImportError:
    PYTORCH_FORECASTING_AVAILABLE = False
    print("Warning: pytorch-forecasting not installed. Install with: pip install pytorch-forecasting")


class TFTModel(nn.Module):
    """
    Temporal Fusion Transformer 模型包装器
    
    基于 pytorch-forecasting 的 TFT 实现
    支持多步预测和注意力可视化
    """
    
    def __init__(
        self,
        max_encoder_length: int = 30,
        max_prediction_length: int = 7,
        hidden_size: int = 16,
        attention_head_size: int = 4,
        dropout: float = 0.1,
        hidden_continuous_size: int = 8,
        output_size: int = 7,
        loss: str = "MSE",
        learning_rate: float = 1e-3,
        static_categoricals: Optional[List[str]] = None,
        static_reals: Optional[List[str]] = None,
        time_varying_known_categoricals: Optional[List[str]] = None,
        time_varying_known_reals: Optional[List[str]] = None,
        time_varying_unknown_categoricals: Optional[List[str]] = None,
        time_varying_unknown_reals: Optional[List[str]] = None,
        target: str = "prediction",
        categorical_encoders: Optional[Dict[str, Any]] = None,
        scalers: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化 TFT 模型
        
        参数:
            max_encoder_length: 编码器序列长度 (历史窗口)
            max_prediction_length: 预测长度 (未来窗口)
            hidden_size: 隐藏层大小
            attention_head_size: 注意力头数
            dropout: Dropout 比率
            hidden_continuous_size: 连续特征隐藏维度
            output_size: 输出大小 (分位数数量)
            loss: 损失函数类型 ("MSE" or "Quantile")
            learning_rate: 学习率
            static_categoricals: 静态类别特征列表
            static_reals: 静态连续特征列表
            time_varying_known_categoricals: 时变已知类别特征
            time_varying_known_reals: 时变已知连续特征
            time_varying_unknown_categoricals: 时变未知类别特征
            time_varying_unknown_reals: 时变未知连续特征
            target: 目标变量名称
            categorical_encoders: 类别编码器
            scalers: 标准化器
        """
        super().__init__()
        
        if not PYTORCH_FORECASTING_AVAILABLE:
            raise ImportError("pytorch-forecasting is required for TFTModel")
        
        self.max_encoder_length = max_encoder_length
        self.max_prediction_length = max_prediction_length
        self.hidden_size = hidden_size
        self.attention_head_size = attention_head_size
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.target = target
        
        # 特征配置
        self.static_categoricals = static_categoricals or []
        self.static_reals = static_reals or []
        self.time_varying_known_categoricals = time_varying_known_categoricals or []
        self.time_varying_known_reals = time_varying_known_reals or []
        self.time_varying_unknown_categoricals = time_varying_unknown_categoricals or []
        self.time_varying_unknown_reals = time_varying_unknown_reals or []
        
        # 损失函数
        if loss == "Quantile":
            self.loss = QuantileLoss()
        else:
            self.loss = nn.MSELoss()
        
        # TFT 模型 (延迟初始化，等待数据后)
        self.model = None
        self.training_dataset = None
        
    def create_dataset(
        self,
        data: Any,
        training: bool = True,
        **kwargs
    ) -> TimeSeriesDataSet:
        """
        创建 TimeSeriesDataSet
        
        参数:
            data: pandas DataFrame，包含时间序列数据
            training: 是否为训练集
            **kwargs: 其他参数传递给 TimeSeriesDataSet
            
        返回:
            TimeSeriesDataSet 实例
        """
        if not PYTORCH_FORECASTING_AVAILABLE:
            raise ImportError("pytorch-forecasting is required")
        
        # 构建 dataset 参数
        dataset_params = {
            "data": data,
            "time_idx": "time_idx",
            "target": self.target,
            "group_ids": ["stock_id"],
            "max_encoder_length": self.max_encoder_length,
            "max_prediction_length": self.max_prediction_length,
            "static_categoricals": self.static_categoricals,
            "static_reals": self.static_reals,
            "time_varying_known_categoricals": self.time_varying_known_categoricals,
            "time_varying_known_reals": self.time_varying_known_reals,
            "time_varying_unknown_categoricals": self.time_varying_unknown_categoricals,
            "time_varying_unknown_reals": self.time_varying_unknown_reals,
            "target_normalizer": kwargs.get("target_normalizer", "GroupNormalizer"),
            "categorical_encoders": self.categorical_encoders if hasattr(self, 'categorical_encoders') else None,
        }
        
        # 移除 None 值
        dataset_params = {k: v for k, v in dataset_params.items() if v is not None}
        
        self.training_dataset = TimeSeriesDataSet(**dataset_params)
        return self.training_dataset
    
    def init_model(self, dataset: TimeSeriesDataSet = None):
        """
        初始化 TFT 模型
        
        参数:
            dataset: TimeSeriesDataSet 实例 (可选，如果已创建)
        """
        if not PYTORCH_FORECASTING_AVAILABLE:
            raise ImportError("pytorch-forecasting is required")
        
        if dataset is None and self.training_dataset is None:
            raise ValueError("Dataset must be created before initializing model")
        
        if dataset is not None:
            self.training_dataset = dataset
        
        # 从 dataset 初始化模型
        self.model = TemporalFusionTransformer.from_dataset(
            self.training_dataset,
            hidden_size=self.hidden_size,
            attention_head_size=self.attention_head_size,
            dropout=self.dropout,
            hidden_continuous_size=self.hidden_continuous_size,
            output_size=self.output_size,
            loss=self.loss,
            learning_rate=self.learning_rate,
        )
        
    def forward(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        前向传播
        
        参数:
            x: 输入字典，包含编码器/解码器输入
            
        返回:
            预测输出
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call init_model() first.")
        
        return self.model(x)
    
    def predict(
        self,
        data_loader: torch.utils.data.DataLoader,
        mode: str = "prediction",
        return_x: bool = False,
    ) -> Tuple[torch.Tensor, Optional[Any]]:
        """
        进行预测
        
        参数:
            data_loader: 数据加载器
            mode: 预测模式 ("prediction", "quantiles", "raw")
            return_x: 是否返回输入
            
        返回:
            预测结果和可选的输入
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call init_model() first.")
        
        predictions = self.model.predict(data_loader, mode=mode, return_x=return_x)
        return predictions
    
    def get_attention(self, data_loader: torch.utils.data.DataLoader) -> Dict[str, torch.Tensor]:
        """
        获取注意力权重用于可视化
        
        参数:
            data_loader: 数据加载器
            
        返回:
            注意力权重字典
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call init_model() first.")
        
        # 获取一个批次用于注意力分析
        batch = next(iter(data_loader))
        attention_weights = self.model.attention(batch)
        return attention_weights
    
    def save(self, path: str):
        """保存模型"""
        if self.model is None:
            raise RuntimeError("No model to save")
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "config": {
                "max_encoder_length": self.max_encoder_length,
                "max_prediction_length": self.max_prediction_length,
                "hidden_size": self.hidden_size,
                "attention_head_size": self.attention_head_size,
                "dropout": self.dropout,
                "hidden_continuous_size": self.hidden_continuous_size,
                "output_size": self.output_size,
                "learning_rate": self.learning_rate,
                "static_categoricals": self.static_categoricals,
                "static_reals": self.static_reals,
                "time_varying_known_categoricals": self.time_varying_known_categoricals,
                "time_varying_known_reals": self.time_varying_known_reals,
                "time_varying_unknown_categoricals": self.time_varying_unknown_categoricals,
                "time_varying_unknown_reals": self.time_varying_unknown_reals,
                "target": self.target,
            }
        }, path)
        print(f"Model saved to {path}")
    
    def load(self, path: str, device: str = "cpu"):
        """加载模型"""
        if not PYTORCH_FORECASTING_AVAILABLE:
            raise ImportError("pytorch-forecasting is required")
        
        checkpoint = torch.load(path, map_location=device, weights_only=False)
        
        # 恢复配置
        config = checkpoint["config"]
        self.max_encoder_length = config["max_encoder_length"]
        self.max_prediction_length = config["max_prediction_length"]
        self.hidden_size = config["hidden_size"]
        self.attention_head_size = config["attention_head_size"]
        self.dropout = config["dropout"]
        self.hidden_continuous_size = config["hidden_continuous_size"]
        self.output_size = config["output_size"]
        self.learning_rate = config["learning_rate"]
        self.static_categoricals = config["static_categoricals"]
        self.static_reals = config["static_reals"]
        self.time_varying_known_categoricals = config["time_varying_known_categoricals"]
        self.time_varying_known_reals = config["time_varying_known_reals"]
        self.time_varying_unknown_categoricals = config["time_varying_unknown_categoricals"]
        self.time_varying_unknown_reals = config["time_varying_unknown_reals"]
        self.target = config["target"]
        
        # 需要 dataset 来初始化模型
        print(f"Model config loaded from {path}. Call init_model() with dataset to complete loading.")
        return checkpoint["model_state_dict"]


def create_tft_model(
    max_encoder_length: int = 30,
    max_prediction_length: int = 7,
    **kwargs
) -> TFTModel:
    """
    创建 TFT 模型的便捷函数
    
    参数:
        max_encoder_length: 编码器序列长度
        max_prediction_length: 预测长度
        **kwargs: 其他参数传递给 TFTModel
        
    返回:
        TFTModel 实例
    """
    return TFTModel(
        max_encoder_length=max_encoder_length,
        max_prediction_length=max_prediction_length,
        **kwargs
    )
