# 训练流程详细设计

**文档版本:** v1.0  
**创建日期:** 2026-03-06  
**作者:** qclaw-designer  
**状态:** ✅ 已完成  
**关联任务:** DESIGN-DL-002

---

## 📋 目录

1. [训练流程概述](#1-训练流程概述)
2. [训练循环设计](#2-训练循环设计)
3. [验证策略](#3-验证策略)
4. [早停机制](#4-早停机制)
5. [学习率调度](#5-学习率调度)
6. [GPU 优化技术](#6-gpu-优化技术)
7. [多任务学习训练](#7-多任务学习训练)
8. [训练监控与日志](#8-训练监控与日志)
9. [检查点管理](#9-检查点管理)
10. [伪代码与示例](#10-伪代码与示例)

---

## 1. 训练流程概述

### 1.1 训练流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        训练初始化                                │
│  - 加载配置 (config.yaml)                                        │
│  - 准备数据集 (train/val/test)                                   │
│  - 初始化模型 (LSTM/Transformer)                                 │
│  - 初始化优化器 (AdamW)                                          │
│  - 初始化学习率调度器                                            │
│  - 加载检查点 (可选)                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      训练循环 (Epoch Loop)                       │
│  for epoch in range(1, num_epochs + 1):                          │
│    ├── train_one_epoch()                                        │
│    ├── validate()                                               │
│    ├── 记录指标 (loss, metrics)                                  │
│    ├── 学习率调度 (step)                                         │
│    ├── 检查早停条件                                              │
│    └── 保存检查点 (最优/最新)                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        训练完成                                  │
│  - 加载最优检查点                                                │
│  - 测试集评估                                                    │
│  - 导出模型 (ONNX/PyTorch)                                       │
│  - 生成训练报告                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 训练配置参数

```yaml
# config/training.yaml
training:
  # 基础参数
  num_epochs: 100
  batch_size: 64
  sequence_length: 60
  
  # 优化器
  optimizer: adamw
  learning_rate: 0.001
  weight_decay: 0.01
  betas: [0.9, 0.999]
  
  # 学习率调度
  lr_scheduler: cosine_annealing
  lr_min: 0.00001
  warmup_epochs: 5
  
  # 早停
  early_stopping:
    enabled: true
    patience: 10
    min_delta: 0.0001
    mode: min  # min for loss, max for accuracy
  
  # GPU 优化
  gpu:
    enabled: true
    mixed_precision: true  # AMP
    gradient_accumulation_steps: 4
    gradient_clip_val: 1.0
  
  # 检查点
  checkpoint:
    save_every: 5  # 每 N 个 epoch 保存
    save_best_only: true
    monitor: val_loss
  
  # 多任务学习
  multi_task:
    enabled: true
    loss_weights:
      direction: 1.0
      return: 0.5
      confidence: 0.3
```

---

## 2. 训练循环设计

### 2.1 单 epoch 训练流程

```python
def train_one_epoch(model, train_loader, optimizer, criterion, device, config):
    """
    执行一个 epoch 的训练
    
    Args:
        model: 预测模型 (LSTM/Transformer)
        train_loader: 训练数据 DataLoader
        optimizer: 优化器
        criterion: 损失函数字典
        device: 计算设备 (cuda/cpu)
        config: 训练配置
    
    Returns:
        dict: 训练指标 (loss, metrics)
    """
    model.train()
    total_loss = 0.0
    total_samples = 0
    batch_losses = []
    
    # 梯度累积
    accumulation_steps = config.gpu.gradient_accumulation_steps
    optimizer.zero_grad()
    
    # 混合精度训练
    scaler = torch.cuda.amp.GradScaler() if config.gpu.mixed_precision else None
    
    for batch_idx, batch in enumerate(train_loader):
        # 数据准备
        X, y_direction, y_return, y_confidence = prepare_batch(batch, device)
        batch_size = X.size(0)
        
        # 自动混合精度前向传播
        with torch.cuda.amp.autocast(enabled=config.gpu.mixed_precision):
            # 模型前向传播
            outputs = model(X)
            
            # 多任务损失计算
            loss_direction = criterion['direction'](outputs['direction'], y_direction)
            loss_return = criterion['return'](outputs['return'], y_return)
            loss_confidence = criterion['confidence'](outputs['confidence'], y_confidence)
            
            # 加权总损失
            total_batch_loss = (
                config.multi_task.loss_weights.direction * loss_direction +
                config.multi_task.loss_weights.return * loss_return +
                config.multi_task.loss_weights.confidence * loss_confidence
            )
        
        # 梯度累积 + 混合精度反向传播
        total_batch_loss = total_batch_loss / accumulation_steps
        
        if scaler:
            scaler.scale(total_batch_loss).backward()
        else:
            total_batch_loss.backward()
        
        # 梯度裁剪
        if config.gpu.gradient_clip_val > 0:
            if scaler:
                scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.gpu.gradient_clip_val)
        
        # 优化器步长 (累积完成后)
        if (batch_idx + 1) % accumulation_steps == 0:
            if scaler:
                scaler.step(optimizer)
                scaler.update()
            else:
                optimizer.step()
            optimizer.zero_grad()
        
        # 统计指标
        total_loss += total_batch_loss.item() * batch_size * accumulation_steps
        total_samples += batch_size
        batch_losses.append(total_batch_loss.item() * accumulation_steps)
    
    # 计算平均损失
    avg_loss = total_loss / total_samples
    
    return {
        'loss': avg_loss,
        'batch_losses': batch_losses,
        'num_samples': total_samples,
        'num_batches': len(train_loader)
    }
```

### 2.2 完整训练循环

```python
def train_model(model, train_loader, val_loader, config, checkpoint_dir='checkpoints'):
    """
    完整训练循环
    
    Args:
        model: 预测模型
        train_loader: 训练数据加载器
        val_loader: 验证数据加载器
        config: 训练配置
        checkpoint_dir: 检查点保存目录
    
    Returns:
        dict: 训练历史记录
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # 初始化优化器
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
        betas=config.betas
    )
    
    # 初始化学习率调度器
    scheduler = get_scheduler(optimizer, config)
    
    # 初始化损失函数
    criterion = {
        'direction': nn.BCEWithLogitsLoss(),
        'return': nn.MSELoss(),
        'confidence': nn.BCELoss()
    }
    
    # 早停器
    early_stopper = EarlyStopping(
        patience=config.early_stopping.patience,
        min_delta=config.early_stopping.min_delta,
        mode=config.early_stopping.mode
    )
    
    # 训练历史
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_metrics': [],
        'learning_rates': []
    }
    
    best_val_loss = float('inf')
    best_epoch = 0
    
    print(f"🚀 开始训练 | Epochs: {config.num_epochs} | Batch Size: {config.batch_size}")
    print(f"📦 设备：{device} | 混合精度：{config.gpu.mixed_precision}")
    
    for epoch in range(1, config.num_epochs + 1):
        # ========== 训练阶段 ==========
        train_start = time.time()
        train_results = train_one_epoch(model, train_loader, optimizer, criterion, device, config)
        train_time = time.time() - train_start
        
        # ========== 验证阶段 ==========
        val_start = time.time()
        val_results = validate(model, val_loader, criterion, device, config)
        val_time = time.time() - val_start
        
        # ========== 学习率调度 ==========
        if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
            scheduler.step(val_results['loss'])
        else:
            scheduler.step()
        
        current_lr = optimizer.param_groups[0]['lr']
        
        # ========== 记录历史 ==========
        history['train_loss'].append(train_results['loss'])
        history['val_loss'].append(val_results['loss'])
        history['val_metrics'].append(val_results['metrics'])
        history['learning_rates'].append(current_lr)
        
        # ========== 日志输出 ==========
        print(f"\n📊 Epoch {epoch}/{config.num_epochs}")
        print(f"   训练损失：{train_results['loss']:.6f} | 时间：{train_time:.1f}s")
        print(f"   验证损失：{val_results['loss']:.6f} | 时间：{val_time:.1f}s")
        print(f"   验证准确率：{val_results['metrics']['direction_accuracy']:.4f}")
        print(f"   学习率：{current_lr:.6f}")
        
        # ========== 检查点保存 ==========
        if val_results['loss'] < best_val_loss:
            best_val_loss = val_results['loss']
            best_epoch = epoch
            save_checkpoint(model, optimizer, scheduler, epoch, val_results, 
                          f"{checkpoint_dir}/best_model.pth")
            print(f"   ✨ 保存最优模型 (val_loss: {best_val_loss:.6f})")
        
        if epoch % config.checkpoint.save_every == 0:
            save_checkpoint(model, optimizer, scheduler, epoch, val_results,
                          f"{checkpoint_dir}/checkpoint_epoch_{epoch}.pth")
        
        # ========== 早停检查 ==========
        if config.early_stopping.enabled:
            if early_stopper(val_results['loss']):
                print(f"\n⏹️  早停触发 @ Epoch {epoch}")
                print(f"   最优 Epoch: {best_epoch} | 最优验证损失：{best_val_loss:.6f}")
                break
    
    # ========== 训练完成 ==========
    print(f"\n✅ 训练完成!")
    print(f"   总 Epochs: {len(history['train_loss'])}")
    print(f"   最优 Epoch: {best_epoch}")
    print(f"   最优验证损失：{best_val_loss:.6f}")
    
    # 加载最优模型
    model = load_checkpoint(model, f"{checkpoint_dir}/best_model.pth")
    
    return history, model
```

---

## 3. 验证策略

### 3.1 验证流程

```python
@torch.no_grad()
def validate(model, val_loader, criterion, device, config):
    """
    验证阶段评估
    
    Returns:
        dict: 验证指标
    """
    model.eval()
    total_loss = 0.0
    total_samples = 0
    
    # 预测结果收集 (用于计算额外指标)
    all_directions_pred = []
    all_directions_true = []
    all_returns_pred = []
    all_returns_true = []
    
    for batch in val_loader:
        X, y_direction, y_return, y_confidence = prepare_batch(batch, device)
        batch_size = X.size(0)
        
        # 前向传播 (无梯度)
        with torch.cuda.amp.autocast(enabled=config.gpu.mixed_precision):
            outputs = model(X)
            
            # 损失计算
            loss_direction = criterion['direction'](outputs['direction'], y_direction)
            loss_return = criterion['return'](outputs['return'], y_return)
            loss_confidence = criterion['confidence'](outputs['confidence'], y_confidence)
            
            total_batch_loss = (
                config.multi_task.loss_weights.direction * loss_direction +
                config.multi_task.loss_weights.return * loss_return +
                config.multi_task.loss_weights.confidence * loss_confidence
            )
        
        total_loss += total_batch_loss.item() * batch_size
        total_samples += batch_size
        
        # 收集预测结果
        all_directions_pred.append(torch.sigmoid(outputs['direction']).cpu())
        all_directions_true.append(y_direction.cpu())
        all_returns_pred.append(outputs['return'].cpu())
        all_returns_true.append(y_return.cpu())
    
    # 计算综合指标
    all_directions_pred = torch.cat(all_directions_pred, dim=0)
    all_directions_true = torch.cat(all_directions_true, dim=0)
    all_returns_pred = torch.cat(all_returns_pred, dim=0)
    all_returns_true = torch.cat(all_returns_true, dim=0)
    
    # 方向准确率
    direction_preds = (all_directions_pred > 0.5).float()
    direction_accuracy = (direction_preds == all_directions_true).float().mean().item()
    
    # 收益率 MAE/MSE
    return_mae = torch.abs(all_returns_pred - all_returns_true).mean().item()
    return_mse = torch.mean((all_returns_pred - all_returns_true) ** 2).item()
    
    # 置信度校准 (Brier Score)
    confidence_brier = torch.mean((all_directions_pred - all_directions_true) ** 2).item()
    
    return {
        'loss': total_loss / total_samples,
        'metrics': {
            'direction_accuracy': direction_accuracy,
            'return_mae': return_mae,
            'return_mse': return_mse,
            'confidence_brier': confidence_brier
        },
        'num_samples': total_samples
    }
```

### 3.2 验证指标说明

| 指标 | 说明 | 目标值 |
|------|------|--------|
| val_loss | 加权验证损失 | 最小化 |
| direction_accuracy | 涨跌方向预测准确率 | > 55% |
| return_mae | 收益率预测平均绝对误差 | 最小化 |
| return_mse | 收益率预测均方误差 | 最小化 |
| confidence_brier | 置信度校准分数 | < 0.25 |

---

## 4. 早停机制

### 4.1 早停器实现

```python
class EarlyStopping:
    """
    早停机制：当验证指标不再改善时停止训练
    
    Args:
        patience: 容忍的 epoch 数
        min_delta: 最小改善阈值
        mode: 'min' (损失) 或 'max' (准确率)
    """
    
    def __init__(self, patience=10, min_delta=0.0001, mode='min'):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.counter = 0
        self.best_value = None
        self.early_stop = False
        
    def __call__(self, current_value):
        """
        检查是否应该早停
        
        Returns:
            bool: True 表示应该停止
        """
        if self.best_value is None:
            self.best_value = current_value
            return False
        
        # 判断是否改善
        if self.mode == 'min':
            # 损失：越小越好
            improved = current_value < self.best_value - self.min_delta
        else:
            # 准确率：越大越好
            improved = current_value > self.best_value + self.min_delta
        
        if improved:
            self.best_value = current_value
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        
        return self.early_stop
```

### 4.2 早停配置建议

| 场景 | patience | min_delta |
|------|----------|-----------|
| 快速实验 | 5 | 0.001 |
| 标准训练 | 10 | 0.0001 |
| 精细调优 | 20 | 0.00001 |
| 大数据集 | 15 | 0.0001 |

---

## 5. 学习率调度

### 5.1 支持的调度器

```python
def get_scheduler(optimizer, config):
    """
    根据配置获取学习率调度器
    """
    if config.lr_scheduler == 'cosine_annealing':
        return torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config.num_epochs,
            eta_min=config.lr_min
        )
    
    elif config.lr_scheduler == 'reduce_on_plateau':
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            min_lr=config.lr_min
        )
    
    elif config.lr_scheduler == 'step':
        return torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=30,
            gamma=0.1
        )
    
    elif config.lr_scheduler == 'one_cycle':
        return torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=config.learning_rate,
            epochs=config.num_epochs,
            steps_per_epoch=len(train_loader)
        )
    
    else:
        # 无调度
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lambda epoch: 1.0)
```

### 5.2 预热 (Warmup) 策略

```python
class WarmupScheduler:
    """
    学习率预热调度器
    
    在前 warmup_epochs 个 epoch 线性增加学习率
    """
    
    def __init__(self, base_scheduler, optimizer, warmup_epochs, total_epochs):
        self.base_scheduler = base_scheduler
        self.optimizer = optimizer
        self.warmup_epochs = warmup_epochs
        self.total_epochs = total_epochs
        self.base_lr = optimizer.param_groups[0]['lr']
        
    def step(self, epoch):
        if epoch < self.warmup_epochs:
            # 线性预热
            warmup_lr = self.base_lr * (epoch + 1) / self.warmup_epochs
            for param_group in self.optimizer.param_groups:
                param_group['lr'] = warmup_lr
        else:
            # 基础调度器
            self.base_scheduler.step()
```

### 5.3 学习率调度曲线

```
学习率
  │
  │     /\
  │    /  \
  │   /    \________
  │  /              \
  │ /                \
  │/                  \______
  └──────────────────────────→ Epoch
     预热    主训练    衰减
```

---

## 6. GPU 优化技术

### 6.1 混合精度训练 (AMP)

```python
# 初始化 GradScaler
scaler = torch.cuda.amp.GradScaler()

# 训练循环中的使用
for batch in train_loader:
    optimizer.zero_grad()
    
    # 自动混合精度上下文
    with torch.cuda.amp.autocast():
        outputs = model(X)
        loss = criterion(outputs, y)
    
    # 缩放梯度 + 反向传播
    scaler.scale(loss).backward()
    
    # 梯度裁剪 (需要先 unscale)
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    # 优化器步长 + 更新 scaler
    scaler.step(optimizer)
    scaler.update()
```

**收益:**
- 显存占用减少 ~50%
- 训练速度提升 ~30%
- 模型精度无明显损失

### 6.2 梯度累积

```python
# 配置
gradient_accumulation_steps = 4  # 等效 batch_size * 4

# 使用方式
for batch_idx, batch in enumerate(train_loader):
    # 前向 + 反向
    loss = compute_loss(batch)
    loss = loss / gradient_accumulation_steps  # 重要：缩放损失
    loss.backward()
    
    # 每 N 步更新一次
    if (batch_idx + 1) % gradient_accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**收益:**
- 等效更大的 batch_size
- 更稳定的梯度估计
- 适合显存受限场景

### 6.3 DataLoader 优化

```python
from torch.utils.data import DataLoader

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,  # 多进程数据加载
    pin_memory=True,  # 锁定内存加速 GPU 传输
    prefetch_factor=2,  # 预取批次
    persistent_workers=True,  # 持久化 worker
    drop_last=True  # 丢弃最后不完整批次
)
```

### 6.4 GPU 内存优化

```python
# 清理缓存
torch.cuda.empty_cache()

# 内存使用监控
def get_gpu_memory():
    allocated = torch.cuda.memory_allocated() / 1024**2
    reserved = torch.cuda.memory_reserved() / 1024**2
    print(f"已分配：{allocated:.1f}MB | 预留：{reserved:.1f}MB")

# 自动混合精度 + 梯度检查点 (超大模型)
from torch.utils.checkpoint import checkpoint

def forward_with_checkpoint(model, x):
    return checkpoint(model._forward, x)
```

---

## 7. 多任务学习训练

### 7.1 损失权重策略

```python
class MultiTaskLoss:
    """
    多任务损失加权
    """
    
    def __init__(self, weights=None, auto_adjust=False):
        self.weights = weights or {
            'direction': 1.0,
            'return': 0.5,
            'confidence': 0.3
        }
        self.auto_adjust = auto_adjust
        self.loss_history = {k: [] for k in self.weights}
        
    def compute(self, outputs, targets):
        """
        计算加权多任务损失
        """
        # 各任务损失
        loss_direction = nn.BCEWithLogitsLoss()(outputs['direction'], targets['direction'])
        loss_return = nn.MSELoss()(outputs['return'], targets['return'])
        loss_confidence = nn.BCELoss()(outputs['confidence'], targets['confidence'])
        
        # 记录历史 (用于自动调整)
        self.loss_history['direction'].append(loss_direction.item())
        self.loss_history['return'].append(loss_return.item())
        self.loss_history['confidence'].append(loss_confidence.item())
        
        # 自动权重调整 (基于不确定性)
        if self.auto_adjust:
            weights = self._adjust_weights()
        else:
            weights = self.weights
        
        # 加权总损失
        total_loss = (
            weights['direction'] * loss_direction +
            weights['return'] * loss_return +
            weights['confidence'] * loss_confidence
        )
        
        return total_loss, {
            'direction': loss_direction.item(),
            'return': loss_return.item(),
            'confidence': loss_confidence.item()
        }
    
    def _adjust_weights(self):
        """
        基于最近损失历史自动调整权重
        使用不确定性加权 (Kendall et al., 2018)
        """
        # 简化版：基于损失大小反比调整
        recent_losses = {
            k: sum(v[-10:]) / len(v[-10:]) if v else 1.0
            for k, v in self.loss_history.items()
        }
        
        # 归一化
        total = sum(recent_losses.values())
        weights = {k: (1.0 / v) / sum(1.0 / vl for vl in recent_losses.values())
                   for k, v in recent_losses.items()}
        
        return weights
```

### 7.2 梯度平衡

```python
class GradNorm:
    """
    GradNorm: 多任务梯度平衡
    参考: Chen et al., "GradNorm: Gradient Normalization for Multi-Task Learning"
    """
    
    def __init__(self, model, task_names, alpha=1.5):
        self.model = model
        self.task_names = task_names
        self.alpha = alpha
        self.initial_losses = None
        
    def compute_loss_weights(self, losses, shared_layer):
        """
        计算动态损失权重以平衡梯度
        """
        if self.initial_losses is None:
            self.initial_losses = {k: v for k, v in losses.items()}
        
        # 计算相对训练速率
        r = {k: losses[k] / self.initial_losses[k] for k in self.task_names}
        
        # 计算平均速率
        r_mean = sum(r.values()) / len(r)
        
        # 计算梯度范数目标
        targets = {k: r[k] ** self.alpha for k in self.task_names}
        
        # 返回归一化权重
        total = sum(targets.values())
        weights = {k: v / total * len(self.task_names) for k, v in targets.items()}
        
        return weights
```

---

## 8. 训练监控与日志

### 8.1 TensorBoard 集成

```python
from torch.utils.tensorboard import SummaryWriter

class TrainingMonitor:
    def __init__(self, log_dir='logs'):
        self.writer = SummaryWriter(log_dir)
        self.step = 0
        
    def log_metrics(self, epoch, metrics, phase='train'):
        """
        记录指标到 TensorBoard
        """
        for name, value in metrics.items():
            self.writer.add_scalar(f'{phase}/{name}', value, epoch)
    
    def log_learning_rate(self, epoch, lr):
        self.writer.add_scalar('optimizer/learning_rate', lr, epoch)
    
    def log_model_weights(self, model, epoch, sample_interval=100):
        """
        记录模型权重直方图
        """
        if epoch % sample_interval == 0:
            for name, param in model.named_parameters():
                self.writer.add_histogram(f'weights/{name}', param, epoch)
    
    def close(self):
        self.writer.close()

# 使用示例
monitor = TrainingMonitor(log_dir='logs/experiment_001')

for epoch in range(num_epochs):
    train_metrics = train_one_epoch(...)
    val_metrics = validate(...)
    
    monitor.log_metrics(epoch, train_metrics, phase='train')
    monitor.log_metrics(epoch, val_metrics, phase='val')
    monitor.log_learning_rate(epoch, current_lr)

monitor.close()
```

### 8.2 训练日志格式

```
2026-03-06 10:30:00 | INFO | 开始训练 | model=LSTM | epochs=100
2026-03-06 10:30:01 | INFO | 设备：cuda:0 | 显存：7.8GB
2026-03-06 10:30:05 | INFO | Epoch 1/100 开始
2026-03-06 10:32:15 | INFO | Epoch 1/100 完成 | train_loss=0.6523 | time=130s
2026-03-06 10:32:45 | INFO | 验证完成 | val_loss=0.6891 | accuracy=0.5234
2026-03-06 10:32:45 | INFO | ✨ 保存最优模型
2026-03-06 10:32:45 | INFO | 学习率：0.001000
...
2026-03-06 14:20:00 | INFO | ⏹️ 早停触发 @ Epoch 47
2026-03-06 14:20:00 | INFO | 最优 Epoch: 37 | 最优 val_loss: 0.5234
2026-03-06 14:20:01 | INFO | 训练完成 | 总时间：3h50m
```

---

## 9. 检查点管理

### 9.1 检查点保存

```python
def save_checkpoint(model, optimizer, scheduler, epoch, metrics, filepath):
    """
    保存训练检查点
    
    Args:
        model: 模型
        optimizer: 优化器
        scheduler: 调度器
        epoch: 当前 epoch
        metrics: 验证指标
        filepath: 保存路径
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
        'metrics': metrics,
        'config': {
            'model_type': model.__class__.__name__,
            'timestamp': datetime.now().isoformat()
        }
    }
    
    # 创建目录
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 保存
    torch.save(checkpoint, filepath)
    print(f"💾 检查点已保存：{filepath}")
```

### 9.2 检查点加载

```python
def load_checkpoint(model, filepath, optimizer=None, scheduler=None, device='cuda'):
    """
    加载训练检查点
    
    Returns:
        model: 加载权重后的模型
        checkpoint: 完整检查点字典
    """
    checkpoint = torch.load(filepath, map_location=device)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    
    if optimizer:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    if scheduler and checkpoint.get('scheduler_state_dict'):
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    
    print(f"📥 检查点已加载：{filepath} (epoch {checkpoint['epoch']})")
    
    return model, checkpoint
```

### 9.3 检查点管理策略

```yaml
# 检查点配置
checkpoint:
  # 保存频率
  save_every: 5  # 每 5 个 epoch
  
  # 保存策略
  save_best_only: true  # 仅保存最优
  save_last: true  # 始终保存最后一个
  
  # 保留策略
  keep_last_n: 3  # 保留最近 N 个
  keep_best: true  # 保留最优
  
  # 监控指标
  monitor: val_loss
  mode: min
```

---

## 10. 伪代码与示例

### 10.1 完整训练脚本

```python
#!/usr/bin/env python3
"""
深度学习预测模型训练脚本

用法:
    python train.py --config config/training.yaml --data data/processed
"""

import argparse
import yaml
from pathlib import Path

from model import LSTMPredictorMultiTask, TransformerPredictorMultiTask
from data import create_dataloaders
from train import train_model
from utils import setup_logging, set_seed

def main():
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--data', type=str, required=True)
    parser.add_argument('--output', type=str, default='outputs')
    parser.add_argument('--resume', type=str, default=None)
    args = parser.parse_args()
    
    # 加载配置
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # 设置随机种子
    set_seed(42)
    
    # 设置日志
    setup_logging(Path(args.output) / 'training.log')
    
    # 准备数据
    train_loader, val_loader, test_loader = create_dataloaders(
        args.data,
        batch_size=config.batch_size,
        sequence_length=config.sequence_length
    )
    
    # 初始化模型
    if config.model_type == 'lstm':
        model = LSTMPredictorMultiTask(
            input_size=config.input_size,
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            dropout=config.dropout
        )
    else:
        model = TransformerPredictorMultiTask(
            input_size=config.input_size,
            d_model=config.d_model,
            nhead=config.nhead,
            num_layers=config.num_layers,
            dropout=config.dropout
        )
    
    # 恢复训练 (可选)
    if args.resume:
        model, _ = load_checkpoint(model, args.resume)
    
    # 开始训练
    history, trained_model = train_model(
        model,
        train_loader,
        val_loader,
        config,
        checkpoint_dir=Path(args.output) / 'checkpoints'
    )
    
    # 测试集评估
    test_results = evaluate(trained_model, test_loader, config)
    print(f"\n📊 测试集结果：{test_results}")
    
    # 保存最终模型
    torch.save(trained_model.state_dict(), Path(args.output) / 'final_model.pth')
    
    # 保存训练历史
    import json
    with open(Path(args.output) / 'training_history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    print("\n✅ 训练完成!")

if __name__ == '__main__':
    main()
```

### 10.2 训练配置文件示例

```yaml
# config/training_lstm.yaml
experiment:
  name: lstm_baseline_v1
  seed: 42

model:
  type: lstm
  input_size: 38
  hidden_size: 128
  num_layers: 2
  dropout: 0.2
  bidirectional: true

data:
  sequence_length: 60
  train_ratio: 0.7
  val_ratio: 0.15
  test_ratio: 0.15

training:
  num_epochs: 100
  batch_size: 64
  optimizer: adamw
  learning_rate: 0.001
  weight_decay: 0.01
  
  lr_scheduler: cosine_annealing
  lr_min: 0.00001
  warmup_epochs: 5
  
  early_stopping:
    enabled: true
    patience: 10
    min_delta: 0.0001

gpu:
  enabled: true
  mixed_precision: true
  gradient_accumulation_steps: 1
  gradient_clip_val: 1.0

multi_task:
  enabled: true
  loss_weights:
    direction: 1.0
    return: 0.5
    confidence: 0.3

checkpoint:
  save_every: 5
  save_best_only: true
  keep_last_n: 3
```

---

## 📎 附录

### A. 训练时间预估

| 模型 | 数据量 | GPU | 预计时间 |
|------|--------|-----|---------|
| LSTM | 10 万条 | RTX 2070 | 30-45 分钟 |
| LSTM | 50 万条 | RTX 2070 | 2-3 小时 |
| Transformer | 10 万条 | RTX 2070 | 1-2 小时 |
| Transformer | 50 万条 | RTX 2070 | 5-8 小时 |

### B. 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 显存溢出 | batch_size 过大 | 减小 batch_size 或使用梯度累积 |
| 训练不收敛 | 学习率过高 | 降低学习率或添加 warmup |
| 过拟合 | 模型过于复杂 | 增加 dropout 或早停 |
| 梯度消失 | 网络过深 | 使用残差连接或梯度裁剪 |
| 训练波动大 | batch_size 过小 | 增大 batch_size 或梯度累积 |

---

**文档状态:** ✅ 已完成  
**下次审查:** CODE-DL-005 实现后
