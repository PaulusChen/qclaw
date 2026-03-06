# LSTM 模型架构详细设计

**文档 ID:** DESIGN-DL-002-LSTM  
**创建日期:** 2026-03-06  
**版本:** v1.0  
**状态:** 设计中  
**关联任务:** CODE-DL-002 (实现 LSTM 预测模型)

---

## 1. 模块概述

### 1.1 职责

LSTM (Long Short-Term Memory) 模型模块负责实现基于 LSTM 的股价预测模型，包括：

- LSTM 网络架构实现
- 多任务输出头设计
- 前向传播逻辑
- 模型保存和加载

### 1.2 设计原则

- **简洁性**: 架构清晰，易于理解和调试
- **灵活性**: 支持配置化调整网络参数
- **可扩展性**: 便于添加新特性 (如 Attention 机制)
- **高效性**: 充分利用 GPU 加速

### 1.3 输入输出

```
输入:
  - 特征序列: (batch_size, sequence_length, num_features)
  - 序列长度: 60 (默认)
  - 特征维度: 38 (默认)

输出:
  - direction: (batch_size, 2) - 涨跌方向 logits
  - return_pred: (batch_size, 1) - 收益率预测
  - confidence: (batch_size, 1) - 置信度 (0-1)
```

---

## 2. 网络架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      LSTM 预测模型架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  输入层 (Input)                                                  │
│  (batch, seq_len=60, features=38)                               │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Input Dropout (p=0.2)                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           LSTM Layer 1 (hidden=128, bidirectional)       │    │
│  │  ┌──────────────────┐    ┌──────────────────┐           │    │
│  │  │  Forward LSTM    │    │  Backward LSTM   │           │    │
│  │  │  (128 units)     │    │  (128 units)     │           │    │
│  │  └──────────────────┘    └──────────────────┘           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LSTM Dropout (p=0.2)                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           LSTM Layer 2 (hidden=128, bidirectional)       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Attention Pooling Layer                        │    │
│  │  (对序列所有时刻的 hidden state 加权求和)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  上下文向量 (context_vector): (batch, hidden*2=256)             │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Fully Connected Layer                       │    │
│  │  Linear(256, 64) + ReLU + Dropout(0.3)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  隐藏表示 (hidden_repr): (batch, 64)                            │
│                          │                                       │
│          ┌───────────────┼───────────────┐                      │
│          ▼               ▼               ▼                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ Direction   │ │   Return    │ │ Confidence  │               │
│  │    Head     │ │    Head     │ │    Head     │               │
│  │ Linear(64,2)│ │ Linear(64,1)│ │ Linear(64,1)│               │
│  └─────────────┘ └─────────────┘ └──────┬──────┘               │
│          │               │               │                      │
│          ▼               ▼               ▼                      │
│   (batch, 2)      (batch, 1)      (batch, 1)                   │
│   logits          收益率          sigmoid→[0,1]                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 架构参数配置

```yaml
# config/lstm_model.yaml
lstm_model:
  # 输入配置
  input:
    num_features: 38
    sequence_length: 60
  
  # LSTM 配置
  lstm:
    hidden_size: 128
    num_layers: 2
    bidirectional: true
    dropout: 0.2
    batch_first: true
  
  # Attention 配置
  attention:
    enabled: true
    attention_dim: 64
  
  # FC 层配置
  fc:
    hidden_dim: 64
    dropout: 0.3
    activation: relu
  
  # 输出头配置
  heads:
    direction:
      enabled: true
      num_classes: 2  # 二分类：涨/跌
    
    return:
      enabled: true
      num_outputs: 1  # 回归
    
    confidence:
      enabled: true
      use_sigmoid: true
  
  # 初始化配置
  init:
    method: xavier_uniform
    gain: 1.0
```

---

## 3. 模型实现

### 3.1 LSTM 单元详解

#### LSTM 门控机制

```
LSTM Cell 内部结构:

输入: x_t (输入), h_{t-1} (前时刻隐藏状态), c_{t-1} (前时刻细胞状态)

遗忘门 (Forget Gate):
  f_t = σ(W_f · [h_{t-1}, x_t] + b_f)
  决定丢弃多少旧信息

输入门 (Input Gate):
  i_t = σ(W_i · [h_{t-1}, x_t] + b_i)
  决定更新多少新信息
  
  c̃_t = tanh(W_c · [h_{t-1}, x_t] + b_c)
  候选细胞状态

细胞状态更新:
  c_t = f_t ⊙ c_{t-1} + i_t ⊙ c̃_t

输出门 (Output Gate):
  o_t = σ(W_o · [h_{t-1}, x_t] + b_o)
  决定输出多少信息
  
  h_t = o_t ⊙ tanh(c_t)

输出: h_t (当前隐藏状态), c_t (当前细胞状态)

其中:
  σ = sigmoid 激活函数
  ⊙ = 逐元素乘法
  W_* = 权重矩阵
  b_* = 偏置向量
```

### 3.2 PyTorch 实现

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
import math


class AttentionLayer(nn.Module):
    """
    注意力池化层
    
    对 LSTM 输出的序列进行加权求和，得到上下文向量
    """
    def __init__(self, hidden_dim: int, attention_dim: int = 64):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, attention_dim),
            nn.Tanh(),
            nn.Linear(attention_dim, 1, bias=False)
        )
    
    def forward(self, lstm_output: torch.Tensor, 
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        参数:
            lstm_output: (batch, seq_len, hidden_dim)
            mask: (batch, seq_len) - padding mask
        
        返回:
            context_vector: (batch, hidden_dim)
        """
        # 计算注意力分数
        attention_scores = self.attention(lstm_output).squeeze(-1)  # (batch, seq_len)
        
        # 应用 mask (如果有)
        if mask is not None:
            attention_scores = attention_scores.masked_fill(mask == 0, -1e9)
        
        # Softmax 归一化
        attention_weights = F.softmax(attention_scores, dim=1)  # (batch, seq_len)
        
        # 加权求和
        context_vector = torch.sum(
            lstm_output * attention_weights.unsqueeze(-1), 
            dim=1
        )  # (batch, hidden_dim)
        
        return context_vector


class MultiTaskHead(nn.Module):
    """
    多任务输出头
    
    同时输出:
    - 涨跌方向 (分类)
    - 收益率预测 (回归)
    - 置信度 (0-1)
    """
    def __init__(self, hidden_dim: int = 64):
        super().__init__()
        
        # 方向预测头 (二分类)
        self.direction_head = nn.Linear(hidden_dim, 2)
        
        # 收益率预测头 (回归)
        self.return_head = nn.Linear(hidden_dim, 1)
        
        # 置信度预测头 (0-1)
        self.confidence_head = nn.Linear(hidden_dim, 1)
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        参数:
            x: (batch, hidden_dim)
        
        返回:
            outputs: {
                'direction': (batch, 2) - logits
                'return': (batch, 1) - 收益率预测
                'confidence': (batch, 1) - 置信度 (sigmoid 后)
            }
        """
        direction_logits = self.direction_head(x)
        return_pred = self.return_head(x)
        confidence = torch.sigmoid(self.confidence_head(x))
        
        return {
            'direction': direction_logits,
            'return': return_pred,
            'confidence': confidence
        }


class LSTMPredictor(nn.Module):
    """
    LSTM 股价预测模型
    
    架构:
        Input → Dropout → BiLSTM(×2) → Attention → FC → MultiTask Heads
    """
    def __init__(
        self,
        num_features: int = 38,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = True,
        attention_dim: int = 64,
        fc_hidden_dim: int = 64,
        **kwargs
    ):
        """
        参数:
            num_features: 输入特征维度
            hidden_size: LSTM 隐藏层维度
            num_layers: LSTM 层数
            dropout: Dropout 比例
            bidirectional: 是否双向 LSTM
            attention_dim: Attention 层维度
            fc_hidden_dim: FC 层隐藏维度
        """
        super().__init__()
        
        self.num_features = num_features
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        # 输入 Dropout
        self.input_dropout = nn.Dropout(dropout)
        
        # LSTM 层
        self.lstm = nn.LSTM(
            input_size=num_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )
        
        # LSTM 输出 Dropout
        self.lstm_dropout = nn.Dropout(dropout)
        
        # Attention 层
        lstm_output_dim = hidden_size * self.num_directions
        self.attention = AttentionLayer(lstm_output_dim, attention_dim)
        
        # 全连接层
        self.fc = nn.Sequential(
            nn.Linear(lstm_output_dim, fc_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout + 0.1)  # FC 层用稍高的 dropout
        )
        
        # 多任务输出头
        self.head = MultiTaskHead(fc_hidden_dim)
        
        # 权重初始化
        self._init_weights()
    
    def _init_weights(self):
        """Xavier 均匀初始化"""
        for name, param in self.named_parameters():
            if 'weight_ih' in name:  # 输入到隐藏
                nn.init.xavier_uniform_(param.data, gain=1.0)
            elif 'weight_hh' in name:  # 隐藏到隐藏
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                # 遗忘门偏置初始化为 1 (有助于长序列学习)
                if 'lstm' in name and 'bias_ih' in name:
                    n = param.size(0)
                    param.data[n//4:n//2].fill_(1.0)
    
    def forward(
        self, 
        x: torch.Tensor,
        lengths: Optional[torch.Tensor] = None,
        return_attention: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        前向传播
        
        参数:
            x: 输入特征 (batch, seq_len, num_features)
            lengths: 序列实际长度 (batch,) - 用于 padding
            return_attention: 是否返回注意力权重
        
        返回:
            outputs: {
                'direction': (batch, 2)
                'return': (batch, 1)
                'confidence': (batch, 1)
            }
            (可选) attention_weights: (batch, seq_len)
        """
        batch_size = x.size(0)
        
        # 输入 Dropout
        x = self.input_dropout(x)
        
        # Pack padded sequence (如果有 padding)
        if lengths is not None:
            # 按长度降序排序
            lengths, perm_idx = lengths.sort(descending=True)
            x = x[perm_idx]
            
            # Pack sequence
            packed = nn.utils.rnn.pack_padded_sequence(
                x, lengths.cpu(), batch_first=True, enforce_sorted=True
            )
            
            # LSTM
            packed_output, (h_n, c_n) = self.lstm(packed)
            
            # Unpack
            lstm_output, _ = nn.utils.rnn.pad_packed_sequence(
                packed_output, batch_first=True
            )
            
            # 恢复原始顺序
            _, unperm_idx = perm_idx.sort()
            lstm_output = lstm_output[unperm_idx]
            h_n = h_n[:, unperm_idx]
        else:
            # 标准 LSTM 前向
            lstm_output, (h_n, c_n) = self.lstm(x)
        
        # LSTM Dropout
        lstm_output = self.lstm_dropout(lstm_output)
        
        # Attention 池化
        if lengths is not None:
            # 创建 mask
            mask = torch.arange(lstm_output.size(1), device=x.device)[None, :] < lengths[:, None]
            mask = mask.float()
        else:
            mask = None
        
        context_vector = self.attention(lstm_output, mask)
        
        # 全连接层
        hidden_repr = self.fc(context_vector)
        
        # 多任务输出
        outputs = self.head(hidden_repr)
        
        if return_attention:
            # 重新计算注意力权重用于可视化
            with torch.no_grad():
                attention_weights = self.attention.attention(lstm_output).squeeze(-1)
                attention_weights = F.softmax(attention_weights, dim=1)
                if lengths is not None:
                    attention_weights = attention_weights * mask
                outputs['attention_weights'] = attention_weights
        
        return outputs
    
    def predict(
        self, 
        x: torch.Tensor,
        threshold: float = 0.5
    ) -> Dict[str, torch.Tensor]:
        """
        预测接口 (自动处理设备转移和 eval 模式)
        
        参数:
            x: 输入特征 (batch, seq_len, num_features)
            threshold: 分类阈值
        
        返回:
            predictions: {
                'direction': (batch,) - 0 或 1
                'direction_prob': (batch,) - 上涨概率
                'return': (batch,) - 收益率预测
                'confidence': (batch,) - 置信度
                'signal': (batch,) - -1(卖), 0(持), 1(买)
            }
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            
            # 方向预测
            direction_probs = F.softmax(outputs['direction'], dim=1)[:, 1]
            direction_pred = (direction_probs > threshold).long()
            
            # 买卖信号
            # 结合方向和置信度生成信号
            confidence = outputs['confidence'].squeeze(-1)
            signal = torch.zeros_like(direction_pred)
            signal[direction_pred == 1] = 1  # 涨→买
            signal[direction_pred == 0] = -1  # 跌→卖
            
            # 低置信度时改为持有
            signal[confidence < 0.5] = 0
            
            return {
                'direction': direction_pred,
                'direction_prob': direction_probs,
                'return': outputs['return'].squeeze(-1),
                'confidence': confidence,
                'signal': signal
            }
    
    def get_num_params(self) -> int:
        """获取模型参数量"""
        return sum(p.numel() for p in self.parameters())
    
    def get_model_size_mb(self) -> float:
        """获取模型大小 (MB)"""
        return sum(p.numel() * p.element_size() for p in self.parameters()) / (1024 * 1024)
```

---

## 4. 梯度流分析

### 4.1 前向传播梯度路径

```
输入 x
  │
  ├─→ Input Dropout (梯度：mask)
  │
  ├─→ LSTM Layer 1
  │     │
  │     ├─→ 遗忘门 f_t (梯度：σ'(·) · ∂L/∂c_t)
  │     ├─→ 输入门 i_t (梯度：σ'(·) · ∂L/∂c_t)
  │     ├─→ 候选状态 c̃_t (梯度：tanh'(·) · i_t · ∂L/∂c_t)
  │     └─→ 输出门 o_t (梯度：σ'(·) · tanh(c_t) · ∂L/∂h_t)
  │
  ├─→ LSTM Layer 2 (同上)
  │
  ├─→ Attention
  │     │
  │     ├─→ 注意力分数 (梯度：softmax 反向)
  │     └─→ 加权求和 (梯度：分配至各时刻)
  │
  ├─→ FC Layer
  │     │
  │     └─→ ReLU (梯度：max(0, x) 的导数)
  │
  └─→ MultiTask Heads
        │
        ├─→ Direction Head → BCE Loss
        ├─→ Return Head → MSE Loss
        └─→ Confidence Head → BCE Loss
```

### 4.2 梯度消失/爆炸缓解

| 技术 | 实现 | 效果 |
|------|------|------|
| **门控机制** | LSTM 原生设计 | 长期依赖梯度流动 |
| **遗忘门偏置** | 初始化为 1 | 鼓励信息保留 |
| **正交初始化** | 隐藏权重正交初始化 | 稳定梯度传播 |
| **梯度裁剪** | torch.nn.utils.clip_grad_norm_ | 防止梯度爆炸 |
| **LayerNorm** | 可选添加 | 稳定训练 |

### 4.3 梯度裁剪实现

```python
def clip_gradients(model: nn.Module, max_norm: float = 1.0):
    """梯度裁剪"""
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_norm)


# 训练循环中使用
for batch in train_loader:
    optimizer.zero_grad()
    outputs = model(batch['features'])
    loss = compute_loss(outputs, batch['target'])
    loss.backward()
    
    # 梯度裁剪
    clip_gradients(model, max_norm=1.0)
    
    optimizer.step()
```

---

## 5. 参数配置和初始化

### 5.1 默认参数

```python
# 推荐配置 (RTX 2070 8GB)
DEFAULT_CONFIG = {
    'num_features': 38,
    'sequence_length': 60,
    'hidden_size': 128,      # 双向→256 输出
    'num_layers': 2,
    'dropout': 0.2,
    'bidirectional': True,
    'attention_dim': 64,
    'fc_hidden_dim': 64,
}

# 参数量估算:
# - LSTM: 4 × [(38+128+1)×128] × 2 (双向) × 2 (层) ≈ 270K
# - Attention: (256+1)×64 + (64+1)×1 ≈ 17K
# - FC: (256+1)×64 ≈ 17K
# - Heads: 64×2 + 64×1 + 64×1 + 4 ≈ 324
# 总计: ≈ 304K 参数 (~1.2MB FP32)
```

### 5.2 权重初始化策略

```python
def init_weights(module: nn.Module, init_method: str = 'xavier'):
    """
    权重初始化
    
    方法:
    - xavier: Xavier 均匀初始化 (推荐)
    - xavier_normal: Xavier 正态初始化
    - kaiming: Kaiming 初始化 (ReLU 适用)
    - orthogonal: 正交初始化 (RNN 推荐)
    """
    if init_method == 'xavier':
        gain = nn.init.calculate_gain('tanh')
        for name, param in module.named_parameters():
            if 'weight' in name and len(param.shape) > 1:
                nn.init.xavier_uniform_(param, gain=gain)
            elif 'bias' in name:
                nn.init.constant_(param, 0)
    
    elif init_method == 'orthogonal':
        for name, param in module.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param)
            elif 'bias' in name:
                nn.init.constant_(param, 0)
                # 遗忘门偏置
                if 'lstm' in name:
                    n = param.size(0)
                    param.data[n//4:n//2].fill_(1.0)
```

---

## 6. 模型变体

### 6.1 基础版 (快速原型)

```python
class LSTMPredictorBasic(nn.Module):
    """简化版 LSTM，用于快速原型验证"""
    def __init__(self, num_features=38, hidden_size=64, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(num_features, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 2)  # 仅方向分类
    
    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        return self.fc(h_n[-1])
```

### 6.2 增强版 (带 LayerNorm)

```python
class LSTMPredictorLN(nn.Module):
    """带 LayerNorm 的 LSTM，训练更稳定"""
    def __init__(self, **kwargs):
        super().__init__()
        self.lstm = nn.LSTM(**kwargs)
        self.layer_norm = nn.LayerNorm(kwargs['hidden_size'] * 2)
        # ... 其他层
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        lstm_out = self.layer_norm(lstm_out)
        # ... 继续
```

### 6.3 带外部注意力的记忆增强版

```python
class LSTMPredictorExternalAttention(nn.Module):
    """带外部记忆的 LSTM"""
    def __init__(self, memory_size=10, **kwargs):
        super().__init__()
        self.lstm = LSTMPredictor(**kwargs)
        self.external_memory = nn.Parameter(torch.randn(memory_size, kwargs['hidden_size']*2))
        self.memory_attention = nn.Linear(kwargs['hidden_size']*2, memory_size)
    
    def forward(self, x):
        # 标准 LSTM 输出
        context = self.lstm.encode(x)
        
        # 外部记忆注意力
        memory_weights = F.softmax(self.memory_attention(context), dim=1)
        memory_context = torch.matmul(memory_weights, self.external_memory)
        
        # 融合
        fused = context + memory_context
        return self.lstm.decode(fused)
```

---

## 7. 模型保存和加载

### 7.1 保存策略

```python
import torch
from pathlib import Path
from datetime import datetime
import json


class ModelCheckpoint:
    """模型检查点管理"""
    def __init__(self, save_dir: str, max_keep: int = 3):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.max_keep = max_keep
        self.checkpoints = []
    
    def save(
        self,
        model: nn.Module,
        optimizer: Optional[torch.optim.Optimizer],
        epoch: int,
        metrics: dict,
        is_best: bool = False
    ) -> str:
        """
        保存检查点
        
        返回:
            保存路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict() if optimizer else None,
            'metrics': metrics,
            'config': {
                'num_features': model.num_features,
                'hidden_size': model.hidden_size,
                'num_layers': model.num_layers,
                'bidirectional': model.bidirectional,
            },
            'timestamp': timestamp,
        }
        
        # 保存文件
        if is_best:
            filename = self.save_dir / 'model_best.pt'
        else:
            filename = self.save_dir / f'model_epoch{epoch:03d}_{timestamp}.pt'
        
        torch.save(checkpoint, filename)
        self.checkpoints.append(filename)
        
        # 清理旧检查点
        if len(self.checkpoints) > self.max_keep:
            old_checkpoint = self.checkpoints.pop(0)
            if old_checkpoint.exists() and not old_checkpoint.name.endswith('best.pt'):
                old_checkpoint.unlink()
        
        return str(filename)
    
    def load(
        self,
        model: nn.Module,
        checkpoint_path: str,
        optimizer: Optional[torch.optim.Optimizer] = None,
        load_optimizer: bool = False
    ) -> dict:
        """
        加载检查点
        
        返回:
            检查点信息
        """
        checkpoint = torch.load(checkpoint_path, map_location=model.device)
        
        model.load_state_dict(checkpoint['model_state_dict'])
        
        if optimizer and load_optimizer and checkpoint['optimizer_state_dict']:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        return {
            'epoch': checkpoint['epoch'],
            'metrics': checkpoint['metrics'],
            'timestamp': checkpoint['timestamp'],
        }
```

### 7.2 导出为 ONNX

```python
def export_to_onnx(
    model: nn.Module,
    output_path: str,
    sequence_length: int = 60,
    num_features: int = 38,
    opset_version: int = 14
):
    """导出为 ONNX 格式 (用于推理优化)"""
    model.eval()
    
    # 创建示例输入
    dummy_input = torch.randn(1, sequence_length, num_features)
    
    # 导出
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['direction', 'return', 'confidence'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'direction': {0: 'batch_size'},
            'return': {0: 'batch_size'},
            'confidence': {0: 'batch_size'},
        }
    )
    
    print(f"✅ 模型已导出至：{output_path}")
```

---

## 8. 验收标准

### 8.1 功能验收

- [ ] 模型可正常实例化
- [ ] 前向传播输出正确 shape
- [ ] 多任务输出头工作正常
- [ ] 模型可保存和加载
- [ ] 支持 GPU 训练
- [ ] 参数量符合预期 (~300K)

### 8.2 性能验收

- [ ] 单样本推理时间 < 10ms (GPU)
- [ ] 批量推理 (batch=64) < 50ms (GPU)
- [ ] 训练速度 > 1000 样本/秒 (GPU)
- [ ] 显存占用 < 2GB (batch=64)

### 8.3 质量验收

- [ ] 单元测试覆盖率 > 90%
- [ ] 梯度检查通过 (torch.autograd.gradcheck)
- [ ] 代码通过 type checking
- [ ] 代码通过 linting

---

## 9. 单元测试示例

```python
import pytest
import torch
from src.prediction.models.lstm import LSTMPredictor


class TestLSTMPredictor:
    @pytest.fixture
    def model(self):
        return LSTMPredictor(
            num_features=38,
            hidden_size=128,
            num_layers=2,
            dropout=0.2
        )
    
    def test_forward_shape(self, model):
        """测试前向传播输出 shape"""
        batch_size = 32
        seq_len = 60
        x = torch.randn(batch_size, seq_len, 38)
        
        outputs = model(x)
        
        assert outputs['direction'].shape == (batch_size, 2)
        assert outputs['return'].shape == (batch_size, 1)
        assert outputs['confidence'].shape == (batch_size, 1)
    
    def test_predict_interface(self, model):
        """测试预测接口"""
        batch_size = 1
        x = torch.randn(batch_size, 60, 38)
        
        preds = model.predict(x)
        
        assert 'direction' in preds
        assert 'direction_prob' in preds
        assert 'return' in preds
        assert 'confidence' in preds
        assert 'signal' in preds
        assert preds['signal'].unique().tolist() ⊆ [-1, 0, 1]
    
    def test_parameter_count(self, model):
        """测试参数量"""
        num_params = model.get_num_params()
        assert 250000 <= num_params <= 350000  # ~300K
    
    def test_save_load(self, model, tmp_path):
        """测试保存加载"""
        save_path = tmp_path / 'model.pt'
        
        # 保存
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': {'num_features': 38}
        }, save_path)
        
        # 加载
        new_model = LSTMPredictor(num_features=38)
        checkpoint = torch.load(save_path)
        new_model.load_state_dict(checkpoint['model_state_dict'])
        
        # 验证输出一致
        x = torch.randn(1, 60, 38)
        with torch.no_grad():
            out1 = model(x)
            out2 = new_model(x)
        
        assert torch.allclose(out1['direction'], out2['direction'])
```

---

## 10. 依赖和接口

### 10.1 上游依赖

- `src/prediction/data/` - 数据预处理模块
- `src/prediction/features/` - 特征工程

### 10.2 下游接口

- `src/prediction/train/` - 训练流程
- `src/prediction/inference/` - 推理服务

### 10.3 外部依赖

```requirements.txt
torch>=2.0.0
numpy>=1.24.0
```

---

## 11. 风险与注意事项

| 风险 | 说明 | 缓解措施 |
|------|------|---------|
| 梯度爆炸 | 长序列训练时 | 梯度裁剪 + 正交初始化 |
| 过拟合 | 小数据集 | Dropout + 早停 + 数据增强 |
| 显存不足 | 大 batch_size | 梯度累积 + 混合精度训练 |
| 训练不稳定 | 学习率过高 | Warmup + 学习率调度 |

---

**文档结束**
