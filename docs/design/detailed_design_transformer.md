# Transformer 模型架构详细设计

**文档 ID:** DESIGN-DL-002-TRANSFORMER  
**创建日期:** 2026-03-06  
**版本:** v1.0  
**状态:** 设计中  
**关联任务:** CODE-DL-003 (实现 Transformer 预测模型)

---

## 1. 模块概述

### 1.1 职责

Transformer 模型模块负责实现基于 Transformer Encoder 的股价预测模型，利用自注意力机制捕捉时间序列中的长期依赖关系，包括：

- Transformer Encoder 架构实现
- 位置编码设计
- 多头注意力机制配置
- 多任务输出头设计
- 模型保存和加载

### 1.2 设计原则

- **注意力优先**: 充分利用自注意力机制捕捉全局依赖
- **残差连接**: 确保梯度流畅传播，支持深层网络
- **层归一化**: 稳定训练过程，加速收敛
- **位置感知**: 精心设计位置编码以保留时间序列顺序信息

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

### 1.4 与 LSTM 对比

| 特性 | LSTM | Transformer |
|------|------|-------------|
| 序列处理 | 顺序处理，难以并行 | 并行处理，效率高 |
| 长期依赖 | 梯度消失问题 | 自注意力直接建模 |
| 位置信息 | 隐式编码 | 显式位置编码 |
| 计算复杂度 | O(n) | O(n²) (注意力) |
| 适用场景 | 短序列、实时性要求高 | 中长序列、精度优先 |

---

## 2. 网络架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Transformer 预测模型架构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  输入层 (Input)                                                          │
│  (batch, seq_len=60, features=38)                                       │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              Input Projection Layer                              │    │
│  │  Linear(38, d_model=256) + LayerNorm + Dropout(0.1)             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          │                                               │
│                          ▼                                               │
│  嵌入表示 (embedded_input): (batch, seq_len=60, d_model=256)            │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              Positional Encoding                                 │    │
│  │  (可学习位置编码 或 正弦位置编码)                                   │    │
│  │  embedded_input + pos_encoding                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │           Transformer Encoder Stack (N=4 layers)                 │    │
│  │  ┌───────────────────────────────────────────────────────────┐  │    │
│  │  │  Encoder Layer 1                                          │  │    │
│  │  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │  │    │
│  │  │  │ Multi-Head  │ →  │ Add & Norm  │ →  │ Feed Forward│   │  │    │
│  │  │  │ Attention   │    │ (残差 + 层归一) │    │ Network     │   │  │    │
│  │  │  │ (8 heads)   │    │             │    │ (ReLU)      │   │  │    │
│  │  │  └─────────────┘    └─────────────┘    └─────────────┘   │  │    │
│  │  │                          │               │                │  │    │
│  │  │                          └──────┬────────┘                │  │    │
│  │  │                                 ▼                         │  │    │
│  │  │                          Add & Norm                       │  │    │
│  │  └───────────────────────────────────────────────────────────┘  │    │
│  │  ┌───────────────────────────────────────────────────────────┐  │    │
│  │  │  Encoder Layer 2 (相同结构)                                │  │    │
│  │  └───────────────────────────────────────────────────────────┘  │    │
│  │  ┌───────────────────────────────────────────────────────────┐  │    │
│  │  │  Encoder Layer 3 (相同结构)                                │  │    │
│  │  └───────────────────────────────────────────────────────────┘  │    │
│  │  ┌───────────────────────────────────────────────────────────┐  │    │
│  │  │  Encoder Layer 4 (相同结构)                                │  │    │
│  │  └───────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          │                                               │
│                          ▼                                               │
│  Encoder 输出: (batch, seq_len=60, d_model=256)                         │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              Global Average Pooling                              │    │
│  │  (对序列维度求平均，或取 [CLS] token)                             │    │
│  │  (batch, d_model=256)                                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          │                                               │
│                          ▼                                               │
│  上下文向量 (context_vector): (batch, 256)                              │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              Prediction Head                                     │    │
│  │  Linear(256, 128) + ReLU + Dropout(0.3)                         │    │
│  │  Linear(128, 64) + ReLU + Dropout(0.3)                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          │                                               │
│          ┌───────────────┼───────────────┐                              │
│          ▼               ▼               ▼                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                    │
│  │ Direction    │ │  Return      │ │ Confidence   │                    │
│  │ Head         │ │  Head        │ │  Head        │                    │
│  │ Linear(64,2) │ │ Linear(64,1) │ │ Linear(64,1) │                    │
│  │ + Softmax    │ │ + ReLU       │ │ + Sigmoid    │                    │
│  └──────────────┘ └──────────────┘ └──────────────┘                    │
│          │               │               │                              │
│          ▼               ▼               ▼                              │
│   direction        return_pred     confidence                           │
│  (涨/跌概率)      (收益率预测)     (0-1 置信度)                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件详解

#### 2.2.1 输入投影层 (Input Projection)

将原始特征映射到 Transformer 的 d_model 维度：

```python
class InputProjection(nn.Module):
    def __init__(self, input_dim=38, d_model=256, dropout=0.1):
        super().__init__()
        self.projection = nn.Linear(input_dim, d_model)
        self.layer_norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # x: (batch, seq_len, input_dim)
        x = self.projection(x)  # (batch, seq_len, d_model)
        x = self.layer_norm(x)
        x = self.dropout(x)
        return x
```

**参数配置:**
- `input_dim`: 38 (特征数量)
- `d_model`: 256 (模型维度)
- `dropout`: 0.1

#### 2.2.2 位置编码 (Positional Encoding)

采用**可学习位置编码**，相比正弦编码更能适应金融时间序列特性：

```python
class LearnablePositionalEncoding(nn.Module):
    def __init__(self, d_model=256, max_len=60, dropout=0.1):
        super().__init__()
        self.pos_encoding = nn.Parameter(
            torch.randn(1, max_len, d_model) * 0.02
        )
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # x: (batch, seq_len, d_model)
        x = x + self.pos_encoding[:, :x.size(1), :]
        x = self.dropout(x)
        return x
```

**设计理由:**
- 可学习参数能更好地适应数据分布
- 初始化方差较小 (0.02) 避免破坏原始嵌入
- 支持可变长度序列 (通过切片)

**备选方案:** 正弦位置编码 (用于消融实验)

```python
class SinusoidalPositionalEncoding(nn.Module):
    def __init__(self, d_model=256, max_len=5000, dropout=0.1):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * 
                            -(math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        x = self.dropout(x)
        return x
```

#### 2.2.3 多头自注意力 (Multi-Head Self-Attention)

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model=256, num_heads=8, dropout=0.1):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads  # 32
        
        self.q_linear = nn.Linear(d_model, d_model)
        self.k_linear = nn.Linear(d_model, d_model)
        self.v_linear = nn.Linear(d_model, d_model)
        self.out_linear = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.d_k)
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        # 线性投影并分割多头
        q = self.q_linear(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        k = self.k_linear(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        v = self.v_linear(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # 计算注意力分数
        scores = torch.matmul(q, k.transpose(-2, -1)) / self.scale  # (batch, heads, seq, seq)
        
        # 因果掩码 (防止看到未来信息)
        if mask is None:
            mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
            mask = mask.unsqueeze(0).unsqueeze(0).to(x.device)
        
        scores.masked_fill_(mask, -1e9)
        
        # Softmax 和 Dropout
        attn = torch.softmax(scores, dim=-1)
        attn = self.dropout(attn)
        
        # 加权求和
        out = torch.matmul(attn, v)  # (batch, heads, seq, d_k)
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        
        # 输出投影
        out = self.out_linear(out)
        return out
```

**关键设计:**
- **因果掩码**: 防止模型看到未来时间步的信息
- 缩放点积注意力: 除以 √d_k 稳定梯度
- 8 个注意力头: 每个头学习不同的表示子空间

#### 2.2.4 前馈网络 (Feed-Forward Network)

```python
class PositionwiseFeedForward(nn.Module):
    def __init__(self, d_model=256, d_ff=1024, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.ReLU()
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        return x
```

**参数配置:**
- `d_ff`: 1024 (4 倍 d_model，标准配置)
- ReLU 激活函数

#### 2.2.5 Encoder 层

```python
class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model=256, num_heads=8, d_ff=1024, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = PositionwiseFeedForward(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # 自注意力 + 残差连接 + 层归一化
        attn_out = self.self_attn(x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # 前馈网络 + 残差连接 + 层归一化
        ff_out = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_out))
        
        return x
```

#### 2.2.6 完整 Transformer 模型

```python
class TransformerPredictor(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # 输入投影
        self.input_projection = InputProjection(
            input_dim=config.num_features,
            d_model=config.d_model,
            dropout=config.dropout
        )
        
        # 位置编码
        self.pos_encoding = LearnablePositionalEncoding(
            d_model=config.d_model,
            max_len=config.seq_length,
            dropout=config.dropout
        )
        
        # Transformer Encoder 堆叠
        encoder_layer = TransformerEncoderLayer(
            d_model=config.d_model,
            num_heads=config.num_heads,
            d_ff=config.d_ff,
            dropout=config.dropout
        )
        self.encoder_layers = nn.ModuleList([
            deepcopy(encoder_layer) for _ in range(config.num_layers)
        ])
        
        # 全局池化
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        
        # 预测头
        self.prediction_head = nn.Sequential(
            nn.Linear(config.d_model, 128),
            nn.ReLU(),
            nn.Dropout(config.dropout * 2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(config.dropout * 2)
        )
        
        # 多任务输出
        self.direction_head = nn.Linear(64, 2)
        self.return_head = nn.Sequential(
            nn.Linear(64, 1),
            nn.ReLU()
        )
        self.confidence_head = nn.Sequential(
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # x: (batch, seq_len, num_features)
        x = self.input_projection(x)
        x = self.pos_encoding(x)
        
        # 通过所有 Encoder 层
        for layer in self.encoder_layers:
            x = layer(x)
        
        # 全局池化: (batch, seq_len, d_model) → (batch, d_model)
        x = x.transpose(1, 2)  # (batch, d_model, seq_len)
        x = self.global_pool(x).squeeze(-1)  # (batch, d_model)
        
        # 预测头
        hidden = self.prediction_head(x)
        
        # 多任务输出
        direction_logits = self.direction_head(hidden)
        return_pred = self.return_head(hidden)
        confidence = self.confidence_head(hidden)
        
        return {
            'direction': direction_logits,
            'return_pred': return_pred,
            'confidence': confidence,
            'hidden': hidden
        }
```

---

## 3. 参数配置

### 3.1 默认配置

```python
@dataclass
class TransformerConfig:
    # 输入配置
    num_features: int = 38
    seq_length: int = 60
    
    # 模型配置
    d_model: int = 256          # 模型维度
    num_heads: int = 8          # 注意力头数
    num_layers: int = 4         # Encoder 层数
    d_ff: int = 1024           # 前馈网络维度
    
    # 正则化
    dropout: float = 0.1
    attention_dropout: float = 0.1
    
    # 训练配置
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    warmup_steps: int = 1000
    
    # 优化器
    optimizer: str = 'adamw'
    scheduler: str = 'cosine'
```

### 3.2 配置建议

| 场景 | d_model | num_heads | num_layers | d_ff |
|------|---------|-----------|------------|------|
| 小型 (快速实验) | 128 | 4 | 2 | 512 |
| 中型 (默认) | 256 | 8 | 4 | 1024 |
| 大型 (高精度) | 512 | 16 | 6 | 2048 |

---

## 4. 前向传播流程

### 4.1 详细流程

```
1. 输入接收
   └─> x: (batch=32, seq_len=60, features=38)

2. 输入投影
   └─> Linear(38→256) + LayerNorm + Dropout
   └─> x: (32, 60, 256)

3. 位置编码
   └─> 加上可学习位置编码
   └─> x: (32, 60, 256)

4. Transformer Encoder (重复 4 次)
   ├─> 多头自注意力 (因果掩码)
   │   └─> Q, K, V 投影 → 注意力分数 → 加权求和
   │   └─> 输出：(32, 60, 256)
   ├─> 残差连接 + LayerNorm
   ├─> 前馈网络 (Linear + ReLU + Linear)
   └─> 残差连接 + LayerNorm

5. 全局池化
   └─> 对序列维度求平均
   └─> x: (32, 256)

6. 预测头
   ├─> Linear(256→128) + ReLU + Dropout
   ├─> Linear(128→64) + ReLU + Dropout
   └─> hidden: (32, 64)

7. 多任务输出
   ├─> direction: Linear(64→2) → Softmax → (32, 2)
   ├─> return_pred: Linear(64→1) + ReLU → (32, 1)
   └─> confidence: Linear(64→1) + Sigmoid → (32, 1)
```

### 4.2 计算复杂度分析

对于序列长度 n=60，特征维度 d=38，模型维度 d_model=256：

| 组件 | 计算复杂度 | 参数量 |
|------|-----------|--------|
| 输入投影 | O(n·d·d_model) | 38×256 + 256 = 10K |
| 自注意力 (单层) | O(n²·d_model) | 256×256×4 = 262K |
| 前馈网络 (单层) | O(n·d_model·d_ff) | 256×1024×2 = 524K |
| 预测头 | O(d_model·64) | 256×128 + 128×64 = 41K |
| **总计 (4 层)** | - | **~3.5M** |

---

## 5. 梯度流分析

### 5.1 残差连接的梯度传播

```
损失函数 L
    │
    ▼
输出头梯度 ∂L/∂output
    │
    ▼
预测头梯度 ∂L/∂hidden
    │
    ▼
池化层梯度 ∂L/∂encoder_output
    │
    ▼
┌─────────────────────────────────────┐
│  Encoder Layer N                     │
│  ┌───────────────────────────────┐   │
│  │  梯度通过 LayerNorm            │   │
│  │  ∂L/∂x = ∂L/∂norm_out · ∂norm/∂x │
│  └───────────────────────────────┘   │
│  │                                   │
│  ▼                                   │
│  残差梯度: ∂L/∂x + ∂L/∂ff_out        │
│  (直接相加，避免梯度消失)              │
└─────────────────────────────────────┘
    │
    ▼
... (逐层反向传播)
    │
    ▼
输入嵌入梯度 ∂L/∂embedding
```

### 5.2 注意力梯度

注意力机制的梯度可以直接从任意位置传播到任意位置，不受序列长度限制：

```
∂L/∂Q = (∂L/∂attn_out) · V^T · softmax'(scores) / √d_k
∂L/∂K = (∂L/∂attn_out) · Q^T · softmax'(scores) / √d_k
∂L/∂V = (∂L/∂attn_out) · attn_weights

关键：梯度可以直接从输出传播到任意输入位置
     没有 RNN 的连乘问题，梯度不会指数衰减
```

---

## 6. 模型初始化策略

### 6.1 权重初始化

```python
def init_weights(module):
    if isinstance(module, nn.Linear):
        # Xavier 均匀初始化
        nn.init.xavier_uniform_(module.weight)
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    
    elif isinstance(module, nn.LayerNorm):
        nn.init.ones_(module.weight)
        nn.init.zeros_(module.bias)
    
    elif isinstance(module, nn.Embedding):
        nn.init.normal_(module.weight, mean=0, std=0.02)
    
    elif isinstance(module, LearnablePositionalEncoding):
        nn.init.normal_(module.pos_encoding, mean=0, std=0.02)
```

### 6.2 初始化理由

- **Xavier 初始化**: 保持各层输出方差一致
- **位置编码小方差**: 避免初始阶段破坏输入信息
- **LayerNorm 标准初始化**: γ=1, β=0

---

## 7. 伪代码示例

### 7.1 训练循环

```python
def train_transformer(model, train_loader, val_loader, config, device):
    model = model.to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=config.warmup_steps,
        num_training_steps=len(train_loader) * config.epochs
    )
    
    # 多任务损失权重
    lambda_direction = 1.0
    lambda_return = 0.5
    lambda_confidence = 0.3
    
    best_val_loss = float('inf')
    
    for epoch in range(config.epochs):
        model.train()
        train_loss = 0.0
        
        for batch in train_loader:
            features = batch['features'].to(device)  # (B, 60, 38)
            direction_label = batch['direction'].to(device)  # (B,)
            return_label = batch['return'].to(device)  # (B, 1)
            confidence_label = batch['confidence'].to(device)  # (B, 1)
            
            optimizer.zero_grad()
            
            # 前向传播
            outputs = model(features)
            
            # 计算多任务损失
            loss_direction = F.cross_entropy(
                outputs['direction'], 
                direction_label
            )
            loss_return = F.mse_loss(
                outputs['return_pred'], 
                return_label
            )
            loss_confidence = F.mse_loss(
                outputs['confidence'], 
                confidence_label
            )
            
            loss = (lambda_direction * loss_direction +
                   lambda_return * loss_return +
                   lambda_confidence * loss_confidence)
            
            # 反向传播
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            
            train_loss += loss.item()
        
        # 验证
        val_loss = validate(model, val_loader, device)
        
        # 保存最佳模型
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'config': config
            }, 'best_transformer.pth')
        
        print(f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")
```

### 7.2 推理示例

```python
@torch.no_grad()
def predict(model, features, device='cuda'):
    model.eval()
    features = features.to(device)  # (1, 60, 38)
    
    outputs = model(features)
    
    # 解析输出
    direction_probs = torch.softmax(outputs['direction'], dim=-1)
    direction_pred = direction_probs.argmax(dim=-1).item()
    up_prob = direction_probs[0, 1].item()
    
    return_pred = outputs['return_pred'][0, 0].item()
    confidence = outputs['confidence'][0, 0].item()
    
    return {
        'direction': 'up' if direction_pred == 1 else 'down',
        'up_probability': up_prob,
        'predicted_return': return_pred,
        'confidence': confidence
    }
```

---

## 8. 优化技巧

### 8.1 训练优化

1. **梯度裁剪**: `clip_grad_norm_(parameters, max_norm=1.0)`
2. **学习率预热**: 前 1000 步线性 warmup
3. **余弦退火**: warmup 后余弦衰减学习率
4. **混合精度训练**: `torch.cuda.amp.autocast()` + GradScaler

### 8.2 推理优化

1. **模型量化**: INT8 量化减少内存占用
2. **批处理**: 多股票批量推理提高吞吐
3. **缓存**: 缓存特征计算结果
4. **ONNX 导出**: 使用 ONNX Runtime 加速推理

---

## 9. 常见问题与解决方案

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 训练不收敛 | 学习率过大 | 降低学习率，增加 warmup |
| 过拟合 | 模型容量过大 | 增加 dropout，添加正则化 |
| 注意力分散 | 序列太长 | 使用局部注意力或稀疏注意力 |
| 推理延迟高 | 序列长度大 | 缩短序列或使用蒸馏 |

---

## 10. 验收标准

- [ ] Transformer 模型实现完成
- [ ] 支持因果掩码自注意力
- [ ] 多任务输出头正常工作
- [ ] 训练收敛且验证集表现良好
- [ ] 推理延迟 < 100ms (单样本)
- [ ] 模型文件可保存和加载
- [ ] 与 LSTM 模型接口一致，可互换使用

---

**下一步:** 
- 实现 CODE-DL-003 (Transformer 模型代码)
- 进行 LSTM vs Transformer 对比实验
- 根据实验结果调整模型配置
