<!-- ARCHIVED: 已压缩至 check-history-summary.md -->

# 深度学习量化预测技术方案

**文档版本:** v1.1  
**创建日期:** 2026-03-06  
**更新日期:** 2026-03-06  
**负责人:** qclaw-pm  
**状态:** 设计中

---

## 1. 需求背景

为 qclaw 项目补充基于深度神经网络的量化预测机制，利用历史行情数据和技术指标，通过深度学习模型预测未来股价走势，为投资决策提供 AI 驱动的量化支持。

---

## 2. 现有技术指标分析

### 2.1 已实现的技术指标

qclaw 项目已实现以下技术指标模块（`src/indicators/`）：

| 指标类别 | 指标名称 | 参数 | 说明 |
|---------|---------|------|------|
| **移动平均线** | MA5/10/20/60/120/250 | 周期 5-250 | 趋势跟踪基础指标 |
| **趋势指标** | MACD | (12,26,9) | 快慢 EMA 差值 + 信号线 |
| **趋势指标** | ADX | 周期 14 | 趋势强度指标 |
| **趋势指标** | SAR | 加速因子 0.02 | 抛物线转向指标 |
| **动量指标** | RSI | 周期 14 | 相对强弱指数 (0-100) |
| **动量指标** | ROC | 周期 12 | 变化率指标 |
| **动量指标** | CCI | 周期 20 | 商品通道指数 |
| **动量指标** | KDJ (Stochastic) | (14,3) | 随机指标 K/D/J 三线 |

### 2.2 技术指标作为模型特征

上述技术指标可作为深度学习模型的输入特征。根据设计复查 (DESIGN-REVIEW-001)，特征工程已扩展至 **35-40 个特征**：

#### 基础特征 (9 个)
- 基础价格：open, high, low, close, volume
- 价格衍生：price_change, price_change_pct, high_low_range, open_close_diff

#### 移动平均线 (4 个)
- ma5, ma10, ma20, ma60

#### 趋势指标 (5 个)
- macd, macd_signal, macd_histogram, adx14, sar

#### 动量指标 (5 个)
- rsi14, roc12, cci20, stoch_k, stoch_d, stoch_j

#### 波动率指标 (2 个) ⭐ 新增
- atr14 (Average True Range)
- volatility_20 (20 日收益率标准差)

#### 成交量指标 (1 个) ⭐ 新增
- volume_ratio (量比)

#### 布林带指标 (2 个) ⭐ 新增
- boll_width (布林带宽度)
- close_vs_boll (价格相对布林带位置)

#### 位置特征 (2 个) ⭐ 新增
- close_vs_ma20 (价格相对 MA20 位置)
- close_vs_ma60 (价格相对 MA60 位置)

#### 滞后特征 (6 个) ⭐ 新增
- close_lag_1, close_lag_5, close_lag_10
- return_lag_1, return_lag_5, return_lag_10

**总计:** 35-40 个特征 (根据具体实现可能略有调整)

---

## 3. 模型选型分析

### 3.1 Transformer vs LSTM 对比

| 维度 | Transformer | LSTM | 推荐 |
|-----|-----------|------|------|
| **长序列依赖** | ⭐⭐⭐⭐⭐ 注意力机制 | ⭐⭐⭐ 梯度消失问题 | Transformer |
| **并行计算** | ⭐⭐⭐⭐⭐ 完全并行 | ⭐⭐ 序列依赖 | Transformer |
| **训练速度** | ⭐⭐⭐⭐ 快 | ⭐⭐ 慢 | Transformer |
| **数据需求** | ⭐⭐⭐ 需要大量数据 | ⭐⭐⭐⭐ 中小数据也可 | LSTM |
| **实现复杂度** | ⭐⭐ 较复杂 | ⭐⭐⭐ 相对简单 | LSTM |

### 3.2 推荐方案：双模型架构

**Phase 1: LSTM 模型 (优先实现)**
- 理由：实现简单、训练稳定、对数据量要求较低
- 适用场景：短期预测 (1-5 天)、快速验证
- 开发周期：3-5 天

**Phase 2: Transformer 模型 (进阶实现)**
- 理由：捕捉长期依赖、更好的预测精度
- 适用场景：中长期预测 (5-20 天)、生产环境
- 开发周期：7-10 天

---

## 4. 技术方案设计

### 4.1 整体架构

```
数据层 → 模型层 (LSTM/Transformer) → 输出层 → 应用层
  ↓           ↓                        ↓          ↓
历史行情    深度学习模型            预测目标    训练/预测 API
技术指标    特征工程                分类/回归   可视化
```

### 4.2 预测目标定义

#### 推荐方案：多任务学习 (Multi-Task Learning) ⭐ 设计复查更新

同时预测多个目标，共享底层特征表示，提升模型泛化能力：

**任务 1: 涨跌方向分类 (主任务)**
- 预测未来 N 天的涨跌方向 (二分类：up/down)
- 评估指标：Accuracy, F1-Score, AUC
- 损失函数：BCEWithLogitsLoss

**任务 2: 收益率回归 (辅助任务)**
- 预测未来 N 天的收益率 (连续值)
- 评估指标：RMSE, MAE, R²
- 损失函数：MSELoss

**任务 3: 置信度预测 (辅助任务)**
- 预测模型对当前预测的置信度 (0-1)
- 评估指标：Calibration Error
- 损失函数：BCELoss

**多任务损失函数:**
```python
def multi_task_loss(outputs, targets):
    direction_loss = BCEWithLogitsLoss(outputs['direction'], targets['direction'])
    return_loss = MSELoss(outputs['return'], targets['return'])
    confidence_loss = BCELoss(outputs['confidence'], targets['confidence'])
    # 加权组合
    return direction_loss + 0.5 * return_loss + 0.3 * confidence_loss
```

**优势:**
- 共享特征表示，提升泛化能力
- 同时输出多个预测结果，信息更丰富
- 置信度输出帮助用户判断预测可靠性

---

#### 备选方案 (单任务)

**方案 A: 涨跌方向分类 (推荐初期)**
- 预测未来 N 天的涨跌方向 (二分类)
- 评估指标：Accuracy, F1-Score, AUC

**方案 B: 收益率回归**
- 预测未来 N 天的收益率 (连续值)
- 评估指标：RMSE, MAE, R²

**方案 C: 买卖信号多分类**
- 预测买卖信号：-1 (卖出), 0 (持有), 1 (买入)
- 评估指标：Accuracy, Confusion Matrix

### 4.3 LSTM 模型架构

#### 基础架构

```python
class LSTMPredictor(nn.Module):
    def __init__(self, input_size=35, hidden_size=128, 
                 num_layers=2, dropout=0.2):
        # input_size 更新为 35 (扩展后的特征数)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 64)
        )
```

#### 多任务输出头 ⭐ 设计复查更新

```python
class MultiTaskHead(nn.Module):
    def __init__(self, hidden_dim=64):
        super().__init__()
        self.direction_head = nn.Linear(hidden_dim, 2)  # 涨跌分类 (二分类)
        self.return_head = nn.Linear(hidden_dim, 1)     # 收益率回归
        self.confidence_head = nn.Linear(hidden_dim, 1) # 置信度 (sigmoid)
    
    def forward(self, x):
        return {
            'direction': self.direction_head(x),
            'return': self.return_head(x),
            'confidence': torch.sigmoid(self.confidence_head(x))
        }

# 完整模型
class LSTMPredictorMultiTask(nn.Module):
    def __init__(self, input_size=35, hidden_size=128, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.head = MultiTaskHead(hidden_dim=64)
    
    def forward(self, x):
        # x shape: (batch, seq_len, features)
        lstm_out, (h_n, c_n) = self.lstm(x)
        # 使用最后时刻的隐藏状态
        last_hidden = lstm_out[:, -1, :]  # (batch, hidden_size)
        features = self.fc(last_hidden)
        return self.head(features)
```

### 4.4 Transformer 模型架构

#### 基础架构

```python
class TransformerPredictor(nn.Module):
    def __init__(self, input_size=35, d_model=128, nhead=8,
                 num_layers=4, dropout=0.1):
        # input_size 更新为 35 (扩展后的特征数)
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=256, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
```

#### 多任务输出头 ⭐ 设计复查更新

```python
class TransformerPredictorMultiTask(nn.Module):
    def __init__(self, input_size=35, d_model=128, nhead=8, num_layers=4, dropout=0.1):
        super().__init__()
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=256, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.head = MultiTaskHead(hidden_dim=64)
    
    def forward(self, x, mask=None):
        # x shape: (batch, seq_len, features)
        x = self.input_projection(x) * math.sqrt(self.d_model)
        x = self.pos_encoder(x)
        # Transformer encoder
        enc_out = self.transformer_encoder(x, mask)
        # 使用 [CLS] token 或全局平均池化
        cls_token = enc_out[:, 0, :]  # (batch, d_model)
        features = self.fc(cls_token)
        return self.head(features)
```

#### 位置编码

```python
import math
import torch
import torch.nn as nn

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        # x shape: (batch, seq_len, d_model)
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)
```

### 4.5 训练策略

- batch_size: 64
- learning_rate: 0.001 (Adam 优化器)
- epochs: 100 (早停 patience=10)
- sequence_length: 60 (使用 60 天历史数据)
- 数据集划分：train 70% / val 15% / test 15%

---

## 5. 任务规划

### 5.1 开发任务 (CODE-*)

| 任务 ID | 任务名称 | 优先级 | 预计工时 | 依赖 |
|--------|---------|--------|---------|------|
| CODE-DL-001 | 创建深度学习模块基础结构 | P0 | 0.5 天 | 无 |
| CODE-DL-002 | 实现 LSTM 预测模型 | P0 | 2 天 | CODE-DL-001 |
| CODE-DL-003 | 实现 Transformer 预测模型 | P1 | 3 天 | CODE-DL-001 |
| CODE-DL-004 | 实现特征工程和数据预处理 | P0 | 1 天 | CODE-DL-001 |
| CODE-DL-005 | 实现模型训练和验证流程 | P0 | 1.5 天 | CODE-DL-002/003 |
| CODE-DL-006 | 实现模型保存和加载功能 | P1 | 0.5 天 | CODE-DL-005 |
| CODE-DL-007 | 集成预测 API 到后端服务 | P1 | 1 天 | CODE-DL-005 |
| CODE-DL-008 | 前端展示预测结果和置信度 | P2 | 1.5 天 | CODE-DL-007 |

### 5.2 测试任务 (TEST-*)

| 任务 ID | 任务名称 | 优先级 | 预计工时 | 依赖 |
|--------|---------|--------|---------|------|
| TEST-DL-001 | 单元测试：LSTM 模型前向传播 | P0 | 0.5 天 | CODE-DL-002 |
| TEST-DL-002 | 单元测试：Transformer 模型前向传播 | P1 | 0.5 天 | CODE-DL-003 |
| TEST-DL-003 | 集成测试：特征工程流水线 | P0 | 0.5 天 | CODE-DL-004 |
| TEST-DL-004 | 集成测试：模型训练流程 | P0 | 1 天 | CODE-DL-005 |
| TEST-DL-005 | 回测验证：历史数据回测 | P1 | 2 天 | CODE-DL-007 |
| TEST-DL-006 | 性能测试：预测延迟和吞吐量 | P2 | 1 天 | CODE-DL-007 |

---

## 6. 预计完成时间

| 阶段 | 内容 | 时间 |
|-----|------|------|
| **Phase 1** | LSTM 模型实现 + 基础训练 | 5 天 (2026-03-06 ~ 2026-03-12) |
| **Phase 2** | Transformer 模型实现 | 4 天 (2026-03-13 ~ 2026-03-17) |
| **Phase 3** | API 集成和前端展示 | 2.5 天 (2026-03-18 ~ 2026-03-20) |
| **Phase 4** | 回测验证和优化 | 3 天 (2026-03-21 ~ 2026-03-24) |
| **总计** | 完整功能交付 | **14.5 天** |

---

## 7. 资源需求

### 7.1 计算资源

| 资源 | 最低配置 | 推荐配置 | 实际配置 |
|-----|---------|---------|----------|
| **GPU** | 无 (CPU 训练) | NVIDIA GTX 1060+ / RTX 3060+ | **NVIDIA RTX 2070 (8GB VRAM)** |
| **内存** | 8GB | 16GB+ | 16GB+ |
| **存储** | 10GB | 50GB+ | 50GB+ |

### 7.2 GPU 训练配置

**硬件资源:**
- **GPU 型号**: NVIDIA RTX 2070
- **显存**: 8GB GDDR6
- **CUDA 核心**: 2304
- **用途**: 模型训练和推理加速

**GPU 加速优势:**
- LSTM 模型训练速度提升约 10-20 倍 (相比 CPU)
- Transformer 模型训练速度提升约 30-50 倍 (相比 CPU)
- 支持批量推理，降低预测延迟
- Phase 1 预计从 5 天缩短至 3 天
- Phase 2 预计从 4 天缩短至 2 天

### 7.3 CUDA/cuDNN 依赖

**系统要求:**
- **操作系统**: Linux (Ubuntu 20.04+) / Windows 10+ / macOS (M1/M2 支持 MPS)
- **NVIDIA 驱动**: >= 525.60.13 (Linux) / >= 528.33 (Windows)
- **CUDA Toolkit**: 11.8 或 12.1 (推荐 12.1)
- **cuDNN**: 8.7+ (对应 CUDA 11.8) 或 8.9+ (对应 CUDA 12.1)

**安装命令 (Linux):**
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 安装 CUDA 12.1 (参考 NVIDIA 官方文档)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-12-1

# 安装 cuDNN (需要 NVIDIA 开发者账号)
# 下载 cuDNN 8.9+ for CUDA 12.1
sudo cp cudnn-*-archive/cudnn-*.tar.xz /usr/local/cuda-12.1/
sudo tar -xf /usr/local/cuda-12.1/cudnn-*.tar.xz -C /usr/local/cuda-12.1/
```

**验证安装:**
```bash
# 检查 CUDA 版本
nvcc --version

# 检查 cuDNN 版本
cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2

# PyTorch GPU 测试
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```

### 7.4 TensorFlow/PyTorch GPU 版本要求

**PyTorch (推荐):**
```requirements.txt
# PyTorch with CUDA 12.1 support
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0

# 安装命令:
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**TensorFlow (可选):**
```requirements.txt
# TensorFlow with GPU support
tensorflow>=2.13.0
tensorflow-io>=0.34.0

# 注意：TensorFlow 2.13+ 需要 CUDA 11.8 + cuDNN 8.7
# 安装命令:
# pip install tensorflow[and-cuda]
```

**完整依赖列表:**
```requirements.txt
# 深度学习框架
torch>=2.0.0
torchvision>=0.15.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# 可视化
matplotlib>=3.7.0
seaborn>=0.12.0

# 技术指标计算
ta-lib>=0.4.25  # 需要系统安装 TA-Lib
pandas-ta>=0.3.14b

# 模型评估
scikit-learn>=1.3.0
yellowbrick>=1.5

# 实验跟踪 (可选)
tensorboard>=2.13.0
wandb>=0.15.0
```

### 7.5 数据资源

- 历史行情数据：至少 3-5 年日线数据 (推荐 10 年+)
- 数据源：Tushare / AkShare / Yahoo Finance
- 数据频率：日线 (初期), 可扩展至分钟线

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 数据质量差 | 模型效果不佳 | 数据清洗、异常值处理 |
| 过拟合 | 泛化能力差 | Dropout、早停、正则化 |
| 市场风格变化 | 模型失效 | 定期重训练、多模型融合 |
| GPU 显存不足 | 训练中断 | 减小 batch_size、梯度累积、混合精度训练 |
| CUDA 版本不兼容 | 环境配置失败 | 使用 Docker 容器、固定依赖版本 |

---

## 9. Reviewer 审阅要点

### 9.1 GPU 资源配置审核

**审核项:**
- ✅ GPU 型号是否满足训练需求 (RTX 2070 8GB - 合格)
- ✅ 显存是否足够 (8GB - 满足 LSTM/Transformer 训练)
- ✅ CUDA/cuDNN 版本是否匹配 (CUDA 12.1 + cuDNN 8.9+ - 合理)
- ✅ 深度学习框架版本是否支持 GPU (PyTorch 2.0+ - 支持)

**结论:** GPU 资源配置合理，RTX 2070 8GB 足以支持本项目 LSTM 和 Transformer 模型训练。

### 9.2 训练时间预估审核 (GPU 加速后)

**原预估 (CPU):**
- Phase 1 (LSTM): 5 天
- Phase 2 (Transformer): 4 天
- 总计：9 天

**GPU 加速后预估:**
- Phase 1 (LSTM): **3 天** (加速 40%)
- Phase 2 (Transformer): **2 天** (加速 50%)
- 总计：**5 天** (整体加速 44%)

**加速依据:**
- RTX 2070 相比 CPU (假设 i7) 提供约 10-50 倍训练加速
- LSTM 序列模型加速约 10-20 倍
- Transformer 自注意力机制加速约 30-50 倍
- 考虑数据加载、预处理等 CPU 瓶颈，整体加速约 40-50%

**结论:** GPU 加速后预计完成时间从 14.5 天缩短至 **12 天**。

---

## 10. 下一步行动

1. ✅ 技术方案设计完成 (本文档)
2. ✅ GPU 资源配置确认 (RTX 2070 8GB)
3. ⏳ 更新 coder.md 添加 GPU 环境配置任务
4. ⏳ 开始 Phase 1: LSTM 模型实现
5. ⏳ 准备历史行情数据集

---

**文档结束**
