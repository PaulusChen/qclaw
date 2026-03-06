# 多任务学习头详细设计

**文档 ID:** DESIGN-DL-002-MULTITASK  
**创建日期:** 2026-03-06  
**版本:** v1.0  
**状态:** 设计中  
**关联任务:** CODE-DL-002, CODE-DL-003 (模型实现)

---

## 1. 模块概述

### 1.1 职责

多任务学习头模块负责实现共享表示下的多任务预测，包括：

- 三个预测任务头的设计与实现
- 任务间梯度平衡机制
- 损失函数加权策略
- 不确定性加权自动调参

### 1.2 任务定义

| 任务 | 类型 | 输出 | 损失函数 | 业务意义 |
|------|------|------|---------|---------|
| Direction | 二分类 | 涨/跌 | CrossEntropy | 交易方向决策 |
| Return | 回归 | 收益率 | MSE/Huber | 预期收益估计 |
| Confidence | 回归 | 置信度 | MSE | 预测可靠性评估 |

### 1.3 设计原则

- **共享表示**: 底层特征共享，提高数据效率
- **任务平衡**: 避免某任务主导梯度更新
- **不确定性加权**: 自动学习任务权重
- **可解释性**: 各任务输出有明确业务含义

---

## 2. 多任务架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        多任务学习架构                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                          共享编码器 (Shared Encoder)                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  LSTM / Transformer                                             │   │
│  │  输入: (batch, seq_len=60, features=38)                         │   │
│  │  输出: (batch, hidden_dim=256)                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│                                   ▼                                     │
│                    ┌──────────────────────────────┐                     │
│                    │   Shared Representation      │                     │
│                    │   (batch, 256)               │                     │
│                    └──────────────────────────────┘                     │
│                                   │                                     │
│              ┌────────────────────┼────────────────────┐                │
│              │                    │                    │                │
│              ▼                    ▼                    ▼                │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐     │
│  │  Direction Head   │ │   Return Head     │ │ Confidence Head   │     │
│  │  (分类)            │ │   (回归)           │ │   (回归)           │     │
│  │                   │ │                   │ │                   │     │
│  │  Linear(256, 128) │ │  Linear(256, 128) │ │  Linear(256, 128) │     │
│  │  ReLU             │ │  ReLU             │ │  ReLU             │     │
│  │  Dropout(0.3)     │ │  Dropout(0.3)     │ │  Dropout(0.3)     │     │
│  │  Linear(128, 64)  │ │  Linear(128, 64)  │ │  Linear(128, 64)  │     │
│  │  ReLU             │ │  ReLU             │ │  ReLU             │     │
│  │  Dropout(0.3)     │ │  Dropout(0.3)     │ │  Dropout(0.3)     │     │
│  │  Linear(64, 2)    │ │  Linear(64, 1)    │ │  Linear(64, 1)    │     │
│  │  Softmax          │ │  ReLU             │ │  Sigmoid          │     │
│  │                   │ │                   │ │                   │     │
│  │  Output: (B, 2)   │ │  Output: (B, 1)   │ │  Output: (B, 1)   │     │
│  │  [P(down),P(up)]  │ │  [return_pred]    │ │  [confidence]     │     │
│  └───────────────────┘ └───────────────────┘ └───────────────────┘     │
│              │                    │                    │                │
│              ▼                    ▼                    ▼                │
│       CrossEntropy           MSE/Huber              MSE                │
│              │                    │                    │                │
│              └────────────────────┼────────────────────┘                │
│                                   ▼                                     │
│                    ┌──────────────────────────────┐                     │
│                    │   Weighted Sum Loss          │                     │
│                    │   L = Σ λᵢ · Lᵢ              │                     │
│                    └──────────────────────────────┘                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 硬共享 vs 软共享

本设计采用**硬共享 (Hard Parameter Sharing)** 架构：

```
硬共享 (本设计):
┌─────────────┐
│  Shared     │  ← 所有任务共享底层参数
│  Encoder    │
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
 Task1   Task2  ← 仅任务头独立

优点:
- 参数效率高
- 隐式数据增强
- 减少过拟合风险

软共享 (备选):
┌─────────┐ ┌─────────┐
│ Encoder1│ │ Encoder2│  ← 各任务独立编码器
└────┬────┘ └────┬────┘
     │          │
     └────┬─────┘
          │
     Cross-talk  ← 通过正则化共享信息
```

---

## 3. 任务头详细设计

### 3.1 Direction Head (涨跌方向分类)

```python
class DirectionHead(nn.Module):
    """
    涨跌方向二分类头
    
    输入: 共享隐藏表示 (batch, hidden_dim)
    输出:  logits (batch, 2) - [P(跌), P(涨)]
    """
    def __init__(self, hidden_dim=256, num_classes=2, dropout=0.3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
            # 注意：Softmax 在损失函数中处理 (CrossEntropyLoss 包含 softmax)
        )
    
    def forward(self, x):
        logits = self.network(x)  # (batch, 2)
        return logits
    
    def predict(self, x):
        logits = self.forward(x)
        probs = torch.softmax(logits, dim=-1)
        preds = probs.argmax(dim=-1)
        return preds, probs
```

**标签定义:**
```python
# direction = 0: 下跌 (return < 0)
# direction = 1: 上涨 (return >= 0)
direction = (future_return >= 0).long()
```

**损失函数:**
```python
criterion_direction = nn.CrossEntropyLoss(weight=class_weight)
loss_direction = criterion_direction(direction_logits, direction_labels)
```

**类别不平衡处理:**
```python
# 计算类别权重 (逆频率)
class_counts = torch.bincount(direction_labels)
class_weights = len(direction_labels) / (len(class_counts) * class_counts + 1e-6)
# 或使用 Focal Loss
```

### 3.2 Return Head (收益率回归)

```python
class ReturnHead(nn.Module):
    """
    收益率回归头
    
    输入: 共享隐藏表示 (batch, hidden_dim)
    输出:  predicted_return (batch, 1)
    """
    def __init__(self, hidden_dim=256, dropout=0.3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.ReLU()  # 确保非负，或根据数据调整
        )
    
    def forward(self, x):
        return_pred = self.network(x)  # (batch, 1)
        return return_pred
```

**标签定义:**
```python
# 未来 N 日收益率
future_return = (close_future - close_current) / close_current
# 可缩放为百分比: future_return * 100
```

**损失函数选项:**

```python
# 选项 1: MSE (均方误差) - 对异常值敏感
criterion_return = nn.MSELoss()
loss_return = criterion_return(return_pred, return_labels)

# 选项 2: Huber Loss - 对异常值鲁棒
criterion_return = nn.HuberLoss(delta=1.0)
loss_return = criterion_return(return_pred, return_labels)

# 选项 3: Smooth L1 Loss
criterion_return = nn.SmoothL1Loss()
loss_return = criterion_return(return_pred, return_labels)
```

**推荐:** Huber Loss (δ=1.0)，平衡 MSE 的敏感性和 MAE 的鲁棒性

### 3.3 Confidence Head (置信度回归)

```python
class ConfidenceHead(nn.Module):
    """
    预测置信度回归头
    
    输入: 共享隐藏表示 (batch, hidden_dim)
    输出:  confidence (batch, 1), 范围 [0, 1]
    """
    def __init__(self, hidden_dim=256, dropout=0.3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()  # 输出压缩到 [0, 1]
        )
    
    def forward(self, x):
        confidence = self.network(x)  # (batch, 1)
        return confidence
```

**标签定义 (关键):**

置信度标签需要精心设计，有几种方案：

```python
# 方案 1: 基于预测准确度 (训练后标注)
# 对历史预测，如果方向预测正确，confidence=1，否则=0
# 问题：需要预训练模型

# 方案 2: 基于收益率绝对值 (推荐)
# 收益率绝对值越大，置信度越高
confidence_label = torch.clamp(torch.abs(return_labels) / max_return, 0, 1)
# max_return 可设为历史最大收益率或分位数

# 方案 3: 基于波动率
# 低波动率时期置信度高
confidence_label = 1.0 / (1.0 + volatility)

# 方案 4: 基于预测一致性 (集成方法)
# 多个模型预测一致时置信度高
# 需要集成模型，计算成本高
```

**推荐方案 2 的改进版:**
```python
def compute_confidence_labels(returns, threshold=0.02):
    """
    基于收益率绝对值计算置信度标签
    
    逻辑:
    - |return| > threshold: 高置信度 (接近 1)
    - |return| < threshold: 低置信度 (接近 0)
    - 中间：线性插值
    """
    abs_return = torch.abs(returns)
    confidence = torch.clamp(abs_return / threshold, 0, 1)
    return confidence
```

**损失函数:**
```python
criterion_confidence = nn.MSELoss()
loss_confidence = criterion_confidence(confidence_pred, confidence_labels)
```

---

## 4. 多任务损失设计

### 4.1 固定权重求和

最简单的多任务损失：

```python
class FixedWeightMultiTaskLoss(nn.Module):
    def __init__(self, lambda_direction=1.0, lambda_return=0.5, lambda_confidence=0.3):
        super().__init__()
        self.lambda_direction = lambda_direction
        self.lambda_return = lambda_return
        self.lambda_confidence = lambda_confidence
        
        self.criterion_direction = nn.CrossEntropyLoss()
        self.criterion_return = nn.HuberLoss(delta=1.0)
        self.criterion_confidence = nn.MSELoss()
    
    def forward(self, outputs, targets):
        loss_direction = self.criterion_direction(
            outputs['direction'], 
            targets['direction']
        )
        loss_return = self.criterion_return(
            outputs['return_pred'], 
            targets['return']
        )
        loss_confidence = self.criterion_confidence(
            outputs['confidence'], 
            targets['confidence']
        )
        
        total_loss = (
            self.lambda_direction * loss_direction +
            self.lambda_return * loss_return +
            self.lambda_confidence * loss_confidence
        )
        
        return {
            'total_loss': total_loss,
            'loss_direction': loss_direction,
            'loss_return': loss_return,
            'loss_confidence': loss_confidence
        }
```

**权重调优策略:**
```python
# 网格搜索
lambda_configs = [
    {'d': 1.0, 'r': 0.3, 'c': 0.1},
    {'d': 1.0, 'r': 0.5, 'c': 0.3},
    {'d': 1.0, 'r': 1.0, 'c': 0.5},
    {'d': 0.5, 'r': 1.0, 'c': 0.3},
]

# 基于验证集性能选择最佳配置
```

### 4.2 不确定性加权 (推荐)

基于 Kendall et al. (2018) "Multi-Task Learning Using Uncertainty to Weigh Losses"：

```python
class UncertaintyWeightedLoss(nn.Module):
    """
    基于同方差不确定性的自动损失加权
    
    核心思想:
    - 每个任务学习一个不确定性参数 log(σ²)
    - 高不确定性任务的权重自动降低
    - 公式: L = Σ (1/(2σ²)) * Lᵢ + log(σ)
    """
    def __init__(self, num_tasks=3):
        super().__init__()
        # 可学习的 log 方差参数 (每个任务一个)
        self.log_var_direction = nn.Parameter(torch.zeros(1))
        self.log_var_return = nn.Parameter(torch.zeros(1))
        self.log_var_confidence = nn.Parameter(torch.zeros(1))
        
        self.criterion_direction = nn.CrossEntropyLoss()
        self.criterion_return = nn.HuberLoss(delta=1.0)
        self.criterion_confidence = nn.MSELoss()
    
    def forward(self, outputs, targets):
        # 计算各任务损失
        loss_direction = self.criterion_direction(
            outputs['direction'], 
            targets['direction']
        )
        loss_return = self.criterion_return(
            outputs['return_pred'], 
            targets['return']
        )
        loss_confidence = self.criterion_confidence(
            outputs['confidence'], 
            targets['confidence']
        )
        
        # 提取精度参数 (precision = 1/σ² = exp(-log_var))
        prec_direction = torch.exp(-self.log_var_direction)
        prec_return = torch.exp(-self.log_var_return)
        prec_confidence = torch.exp(-self.log_var_confidence)
        
        # 加权损失 + 正则化项
        loss_direction_weighted = prec_direction * loss_direction + self.log_var_direction
        loss_return_weighted = prec_return * loss_return + self.log_var_return
        loss_confidence_weighted = prec_confidence * loss_confidence + self.log_var_confidence
        
        total_loss = (
            0.5 * loss_direction_weighted +  # 分类任务系数 0.5
            0.5 * loss_return_weighted +
            0.5 * loss_confidence_weighted
        )
        
        return {
            'total_loss': total_loss,
            'loss_direction': loss_direction,
            'loss_return': loss_return,
            'loss_confidence': loss_confidence,
            'weight_direction': prec_direction.item(),
            'weight_return': prec_return.item(),
            'weight_confidence': prec_confidence.item()
        }
```

**优势:**
- 自动平衡任务权重，无需手动调参
- 不确定性参数可解释 (高不确定性 → 低权重)
- 端到端训练

### 4.3 梯度归一化 (GradNorm)

另一种自动平衡方法，通过梯度范数归一化：

```python
class GradNormMultiTaskLoss(nn.Module):
    """
    GradNorm: 基于梯度范数的动态权重调整
    
    核心思想:
    - 监控各任务梯度范数
    - 调整权重使各任务梯度范数相近
    - 避免某任务主导梯度更新
    """
    def __init__(self, alpha=1.5):
        super().__init__()
        self.alpha = alpha  # 平衡强度
        
        self.lambda_direction = nn.Parameter(torch.ones(1))
        self.lambda_return = nn.Parameter(torch.ones(1))
        self.lambda_confidence = nn.Parameter(torch.ones(1))
        
        self.criterion_direction = nn.CrossEntropyLoss()
        self.criterion_return = nn.HuberLoss(delta=1.0)
        self.criterion_confidence = nn.MSELoss()
    
    def compute_grad_norm(self, loss, params):
        grads = torch.autograd.grad(loss, params, retain_graph=True)
        grad_norm = torch.norm(torch.cat([g.view(-1) for g in grads]))
        return grad_norm
    
    def forward(self, outputs, targets, shared_params):
        # 计算各任务损失
        L_direction = self.criterion_direction(outputs['direction'], targets['direction'])
        L_return = self.criterion_return(outputs['return_pred'], targets['return'])
        L_confidence = self.criterion_confidence(outputs['confidence'], targets['confidence'])
        
        # 加权损失
        loss_direction = self.lambda_direction * L_direction
        loss_return = self.lambda_return * L_return
        loss_confidence = self.lambda_confidence * L_confidence
        
        total_loss = loss_direction + loss_return + loss_confidence
        
        # GradNorm 更新逻辑 (在训练循环中调用)
        # 1. 计算各任务梯度范数
        # 2. 计算相对训练速率
        # 3. 更新 lambda 使梯度范数平衡
        
        return {
            'total_loss': total_loss,
            'loss_direction': L_direction,
            'loss_return': L_return,
            'loss_confidence': L_confidence,
            'lambda_direction': self.lambda_direction.item(),
            'lambda_return': self.lambda_return.item(),
            'lambda_confidence': self.lambda_confidence.item()
        }
```

---

## 5. 任务间梯度平衡

### 5.1 梯度冲突问题

多任务学习中，不同任务的梯度可能冲突：

```
共享参数 θ
    │
    ├─> 任务 1 梯度：∇L₁/∂θ = [1, -1, 0.5]
    ├─> 任务 2 梯度：∇L₂/∂θ = [-1, 1, -0.5]
    │
    └─> 简单求和：∇L/∂θ = [0, 0, 0]  ← 梯度抵消！
```

### 5.2 解决方案

#### 方案 1: 梯度裁剪

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

#### 方案 2: 梯度投影 (PCGrad)

```python
def pc_grad_update(params, task_grads):
    """
    PCGrad: 将冲突梯度投影到彼此的法平面
    
    对每对任务梯度 (gᵢ, gⱼ):
    如果 gᵢ · gⱼ < 0 (冲突):
        gᵢ ← gᵢ - (gᵢ · gⱼ / ||gⱼ||²) * gⱼ
    """
    for i, grad_i in enumerate(task_grads):
        for j, grad_j in enumerate(task_grads):
            if i != j:
                dot_product = torch.sum(grad_i * grad_j)
                if dot_product < 0:
                    # 投影
                    proj = grad_i - (dot_product / (torch.norm(grad_j)**2 + 1e-8)) * grad_j
                    task_grads[i] = proj
    
    # 求和更新
    total_grad = sum(task_grads)
    # 应用到参数...
```

#### 方案 3: 任务分组训练

```python
# 交替训练不同任务
for epoch in range(num_epochs):
    if epoch % 3 == 0:
        # 主要训练 Direction 任务
        loss = loss_direction
    elif epoch % 3 == 1:
        # 主要训练 Return 任务
        loss = loss_return
    else:
        # 主要训练 Confidence 任务
        loss = loss_confidence
    
    # 加上其他任务的辅助损失 (小权重)
    loss += 0.1 * (loss_direction + loss_return + loss_confidence)
```

---

## 6. 完整多任务模型实现

```python
class MultiTaskPredictor(nn.Module):
    """
    完整的多任务预测模型
    
    支持 LSTM 或 Transformer 作为共享编码器
    """
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # 共享编码器 (LSTM 或 Transformer)
        if config.encoder_type == 'lstm':
            self.encoder = LSTMEncoder(config)
        elif config.encoder_type == 'transformer':
            self.encoder = TransformerEncoder(config)
        else:
            raise ValueError(f"Unknown encoder type: {config.encoder_type}")
        
        # 任务头
        self.direction_head = DirectionHead(
            hidden_dim=config.hidden_dim,
            dropout=config.dropout
        )
        self.return_head = ReturnHead(
            hidden_dim=config.hidden_dim,
            dropout=config.dropout
        )
        self.confidence_head = ConfidenceHead(
            hidden_dim=config.hidden_dim,
            dropout=config.dropout
        )
        
        # 损失函数 (不确定性加权)
        self.loss_fn = UncertaintyWeightedLoss(num_tasks=3)
    
    def forward(self, x):
        # 共享编码
        hidden = self.encoder(x)  # (batch, hidden_dim)
        
        # 多任务预测
        direction_logits = self.direction_head(hidden)
        return_pred = self.return_head(hidden)
        confidence = self.confidence_head(hidden)
        
        return {
            'direction': direction_logits,
            'return_pred': return_pred,
            'confidence': confidence,
            'hidden': hidden
        }
    
    def compute_loss(self, outputs, targets):
        return self.loss_fn(outputs, targets)
    
    @torch.no_grad()
    def predict(self, x):
        self.eval()
        outputs = self.forward(x)
        
        # 解析方向预测
        direction_probs = torch.softmax(outputs['direction'], dim=-1)
        direction_pred = direction_probs.argmax(dim=-1)
        
        return {
            'direction': direction_pred,
            'direction_probs': direction_probs,
            'return_pred': outputs['return_pred'],
            'confidence': outputs['confidence']
        }
```

---

## 7. 训练流程

### 7.1 训练循环

```python
def train_multi_task(model, train_loader, val_loader, config, device):
    model = model.to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config.epochs
    )
    
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(config.epochs):
        # 训练阶段
        model.train()
        train_losses = {'total': 0, 'direction': 0, 'return': 0, 'confidence': 0}
        
        for batch in train_loader:
            features = batch['features'].to(device)
            targets = {
                'direction': batch['direction'].to(device),
                'return': batch['return'].to(device),
                'confidence': batch['confidence'].to(device)
            }
            
            optimizer.zero_grad()
            
            # 前向传播
            outputs = model(features)
            
            # 计算多任务损失
            loss_dict = model.compute_loss(outputs, targets)
            loss = loss_dict['total_loss']
            
            # 反向传播
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            # 记录损失
            train_losses['total'] += loss.item()
            train_losses['direction'] += loss_dict['loss_direction'].item()
            train_losses['return'] += loss_dict['loss_return'].item()
            train_losses['confidence'] += loss_dict['loss_confidence'].item()
        
        # 验证阶段
        val_losses = validate_multi_task(model, val_loader, device)
        
        # 学习率调度
        scheduler.step()
        
        # 早停检查
        if val_losses['total'] < best_val_loss:
            best_val_loss = val_losses['total']
            patience_counter = 0
            # 保存最佳模型
            torch.save(model.state_dict(), 'best_multi_task.pth')
        else:
            patience_counter += 1
            if patience_counter >= config.patience:
                print(f"Early stopping at epoch {epoch}")
                break
        
        # 打印进度
        print(f"Epoch {epoch}: "
              f"train_loss={train_losses['total']:.4f}, "
              f"val_loss={val_losses['total']:.4f}, "
              f"λ_dir={loss_dict.get('weight_direction', 'N/A'):.3f}, "
              f"λ_ret={loss_dict.get('weight_return', 'N/A'):.3f}")
```

### 7.2 验证函数

```python
@torch.no_grad()
def validate_multi_task(model, val_loader, device):
    model.eval()
    val_losses = {'total': 0, 'direction': 0, 'return': 0, 'confidence': 0}
    num_batches = 0
    
    all_direction_preds = []
    all_direction_labels = []
    all_return_preds = []
    all_return_labels = []
    
    for batch in val_loader:
        features = batch['features'].to(device)
        targets = {
            'direction': batch['direction'].to(device),
            'return': batch['return'].to(device),
            'confidence': batch['confidence'].to(device)
        }
        
        outputs = model(features)
        loss_dict = model.compute_loss(outputs, targets)
        
        val_losses['total'] += loss_dict['total_loss'].item()
        val_losses['direction'] += loss_dict['loss_direction'].item()
        val_losses['return'] += loss_dict['loss_return'].item()
        val_losses['confidence'] += loss_dict['loss_confidence'].item()
        num_batches += 1
        
        # 收集预测用于指标计算
        direction_probs = torch.softmax(outputs['direction'], dim=-1)
        direction_pred = direction_probs.argmax(dim=-1)
        all_direction_preds.extend(direction_pred.cpu().numpy())
        all_direction_labels.extend(targets['direction'].cpu().numpy())
        all_return_preds.extend(outputs['return_pred'].cpu().numpy())
        all_return_labels.extend(targets['return'].cpu().numpy())
    
    # 计算平均损失
    for key in val_losses:
        val_losses[key] /= num_batches
    
    # 计算评估指标
    direction_accuracy = accuracy_score(all_direction_labels, all_direction_preds)
    direction_f1 = f1_score(all_direction_labels, all_direction_preds)
    return_mae = mean_absolute_error(all_return_labels, all_return_preds)
    return_mse = mean_squared_error(all_return_labels, all_return_preds)
    
    val_losses['metrics'] = {
        'direction_accuracy': direction_accuracy,
        'direction_f1': direction_f1,
        'return_mae': return_mae,
        'return_mse': return_mse
    }
    
    return val_losses
```

---

## 8. 评估指标

### 8.1 Direction 任务指标

| 指标 | 公式 | 说明 |
|------|------|------|
| Accuracy | (TP+TN)/N | 方向预测准确率 |
| Precision | TP/(TP+FP) | 预测上涨的准确率 |
| Recall | TP/(TP+FN) | 实际上涨的召回率 |
| F1 Score | 2·P·R/(P+R) | 精确率和召回率的调和平均 |
| AUC-ROC | - | 分类器整体性能 |

### 8.2 Return 任务指标

| 指标 | 公式 | 说明 |
|------|------|------|
| MAE | mean\|y-ŷ\| | 平均绝对误差 |
| MSE | mean((y-ŷ)²) | 均方误差 |
| RMSE | √MSE | 均方根误差 |
| MAPE | mean\|(y-ŷ)/y\| | 平均绝对百分比误差 |
| IC | corr(y, ŷ) | 信息系数 (预测与实际的相关性) |

### 8.3 Confidence 任务指标

| 指标 | 说明 |
|------|------|
| Calibration | 置信度与准确率的匹配程度 |
| Brier Score | 概率预测的校准度 |

### 8.4 综合评估

```python
def compute_comprehensive_metrics(model, test_loader, device):
    model.eval()
    all_preds = []
    all_labels = []
    all_confidences = []
    
    with torch.no_grad():
        for batch in test_loader:
            features = batch['features'].to(device)
            outputs = model.predict(features)
            
            all_preds.extend(outputs['direction'].cpu().numpy())
            all_labels.extend(batch['direction'].numpy())
            all_confidences.extend(outputs['confidence'].cpu().numpy())
    
    # 按置信度分组评估
    confidence_bins = [0.0, 0.3, 0.5, 0.7, 1.0]
    bin_accuracies = []
    
    for i in range(len(confidence_bins)-1):
        mask = (np.array(all_confidences) >= confidence_bins[i]) & \
               (np.array(all_confidences) < confidence_bins[i+1])
        if mask.sum() > 0:
            bin_acc = accuracy_score(
                np.array(all_labels)[mask],
                np.array(all_preds)[mask]
            )
            bin_accuracies.append({
                'bin': f'{confidence_bins[i]:.1f}-{confidence_bins[i+1]:.1f}',
                'accuracy': bin_acc,
                'count': mask.sum()
            })
    
    return {
        'overall_accuracy': accuracy_score(all_labels, all_preds),
        'overall_f1': f1_score(all_labels, all_preds),
        'confidence_calibration': bin_accuracies
    }
```

---

## 9. 常见问题与解决方案

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 某任务损失不下降 | 权重过小 | 增大该任务权重或使用不确定性加权 |
| 任务间互相干扰 | 梯度冲突 | 使用 PCGrad 或梯度裁剪 |
| Confidence 任务无意义 | 标签定义不合理 | 重新设计置信度标签计算方式 |
| 过拟合 | 模型容量过大 | 增加 dropout，添加 L2 正则化 |
| 训练不稳定 | 学习率过大 | 降低学习率，添加 warmup |

---

## 10. 验收标准

- [ ] 三个任务头实现完成
- [ ] 不确定性加权损失正常工作
- [ ] 各任务损失均衡下降
- [ ] Direction 准确率 > 55% (验证集)
- [ ] Return 预测 IC > 0.05
- [ ] Confidence 与准确率正相关
- [ ] 支持 LSTM 和 Transformer 编码器

---

**下一步:**
- 实现 CODE-DL-002/CODE-DL-003 中的多任务头代码
- 进行消融实验验证各任务贡献
- 调优损失权重或不确定性参数
