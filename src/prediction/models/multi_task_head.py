"""
多任务学习输出头

支持同时预测：
- 涨跌方向 (分类)
- 收益率 (回归)
- 置信度 (概率)
"""

import torch
import torch.nn as nn
from typing import Dict, Optional


class MultiTaskHead(nn.Module):
    """
    多任务学习头
    
    接收模型的特征表示，输出多个任务的结果
    """
    
    def __init__(self, hidden_dim: int, dropout: float = 0.1):
        """
        初始化多任务头
        
        参数:
            hidden_dim: 输入特征维度
            dropout: Dropout 概率
        """
        super(MultiTaskHead, self).__init__()
        
        # 共享的隐藏层
        self.shared_hidden = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        
        # 涨跌方向头 (二分类：涨/跌)
        self.direction_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 2),  # 2 类：涨/跌
        )
        
        # 收益率头 (回归)
        self.return_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),  # 连续值
        )
        
        # 置信度头 (0-1 概率)
        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),  # 输出 0-1 之间的概率
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        参数:
            x: 输入特征 (batch_size, hidden_dim)
            
        返回:
            包含多个任务输出的字典:
            - direction: (batch_size, 2) 涨跌 logits
            - return: (batch_size, 1) 预测收益率
            - confidence: (batch_size, 1) 置信度 (0-1)
        """
        # 共享隐藏层
        hidden = self.shared_hidden(x)
        
        # 各任务输出
        direction_logits = self.direction_head(hidden)
        return_value = self.return_head(hidden)
        confidence = self.confidence_head(hidden)
        
        return {
            "direction": direction_logits,
            "return": return_value,
            "confidence": confidence,
        }


class MultiTaskLoss(nn.Module):
    """
    多任务损失函数
    
    组合分类损失和回归损失
    """
    
    def __init__(
        self,
        direction_weight: float = 1.0,
        return_weight: float = 0.5,
        confidence_weight: float = 0.1,
    ):
        """
        初始化多任务损失
        
        参数:
            direction_weight: 涨跌分类损失权重
            return_weight: 收益率回归损失权重
            confidence_weight: 置信度损失权重
        """
        super(MultiTaskLoss, self).__init__()
        
        self.direction_weight = direction_weight
        self.return_weight = return_weight
        self.confidence_weight = confidence_weight
        
        # 分类损失 (交叉熵)
        self.direction_loss = nn.CrossEntropyLoss()
        
        # 回归损失 (MSE)
        self.return_loss = nn.MSELoss()
        
        # 置信度损失 (BCE)
        self.confidence_loss = nn.BCELoss()
    
    def forward(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor],
    ) -> Dict[str, torch.Tensor]:
        """
        计算多任务损失
        
        参数:
            predictions: 预测结果字典
            targets: 真实标签字典
                - direction: (batch_size,) 涨跌标签 (0/1)
                - return: (batch_size, 1) 真实收益率
                - confidence: (batch_size, 1) 置信度标签
                
        返回:
            包含各任务损失和总损失的字典
        """
        # 各任务损失
        direction_loss = self.direction_loss(
            predictions["direction"],
            targets["direction"].long(),
        )
        
        return_loss = self.return_loss(
            predictions["return"],
            targets["return"],
        )
        
        confidence_loss = self.confidence_loss(
            predictions["confidence"],
            targets["confidence"],
        )
        
        # 加权总损失
        total_loss = (
            self.direction_weight * direction_loss
            + self.return_weight * return_loss
            + self.confidence_weight * confidence_loss
        )
        
        return {
            "total": total_loss,
            "direction": direction_loss,
            "return": return_loss,
            "confidence": confidence_loss,
        }


if __name__ == "__main__":
    # 测试多任务头
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    batch_size = 32
    hidden_dim = 128
    
    # 创建模型
    head = MultiTaskHead(hidden_dim=hidden_dim).to(device)
    loss_fn = MultiTaskLoss().to(device)
    
    # 测试前向传播
    x = torch.randn(batch_size, hidden_dim).to(device)
    
    with torch.no_grad():
        outputs = head(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Direction output shape: {outputs['direction'].shape}")
    print(f"Return output shape: {outputs['return'].shape}")
    print(f"Confidence output shape: {outputs['confidence'].shape}")
    
    # 测试损失计算
    targets = {
        "direction": torch.randint(0, 2, (batch_size,)).to(device),
        "return": torch.randn(batch_size, 1).to(device),
        "confidence": torch.rand(batch_size, 1).to(device),
    }
    
    losses = loss_fn(outputs, targets)
    print(f"\nLoss values:")
    print(f"  Total: {losses['total'].item():.4f}")
    print(f"  Direction: {losses['direction'].item():.4f}")
    print(f"  Return: {losses['return'].item():.4f}")
    print(f"  Confidence: {losses['confidence'].item():.4f}")
    
    print("\nMultiTaskHead test passed!")
