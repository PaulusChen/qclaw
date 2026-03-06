# 深度学习量化预测架构设计

**文档版本:** v1.0  
**创建日期:** 2026-03-06  
**合并自:** deep_learning_prediction.md, dl_prediction_architecture.md, DESIGN-DL-003-status-final.md  
**状态:** ✅ 已合并

---

## 📋 目录

1. [需求背景](#1-需求背景)
2. [特征工程](#2-特征工程)
3. [模型架构](#3-模型架构)
4. [系统架构](#4-系统架构)
5. [API 设计](#5-api-设计)
6. [部署架构](#6-部署架构)
7. [性能优化](#7-性能优化)
8. [任务规划](#8-任务规划)

---

## 1. 需求背景

为 qclaw 项目补充基于深度神经网络的量化预测机制，利用历史行情数据和技术指标，通过深度学习模型预测未来股价走势，为投资决策提供 AI 驱动的量化支持。

---

## 2. 特征工程

### 2.1 特征列表 (38 个)

#### 基础特征 (9 个)
- open, high, low, close, volume
- price_change, price_change_pct, high_low_range, open_close_diff

#### 移动平均线 (4 个)
- ma5, ma10, ma20, ma60

#### 趋势指标 (5 个)
- macd, macd_signal, macd_histogram, adx14, sar

#### 动量指标 (6 个)
- rsi14, roc12, cci20, stoch_k, stoch_d, stoch_j

#### 波动率指标 (2 个) ⭐
- atr14 (Average True Range)
- volatility_20 (20 日收益率标准差)

#### 成交量指标 (1 个) ⭐
- volume_ratio (量比)

#### 布林带指标 (2 个) ⭐
- boll_width, close_vs_boll

#### 位置特征 (2 个) ⭐
- close_vs_ma20, close_vs_ma60

#### 滞后特征 (7 个) ⭐
- close_lag_1/5/10, return_lag_1/5/10

### 2.2 特征处理流程

```
原始数据 → 缺失值处理 → 异常值检测 → 滞后特征 → 滚动统计 → 标准化 → 特征矩阵
```

### 2.3 标准化方案

推荐方案：RobustScaler (对异常值不敏感)
```python
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)
```

---

## 3. 模型架构

### 3.1 双模型策略

**Phase 1: LSTM 模型 (优先实现)**
- 理由：实现简单、训练稳定、对数据量要求较低
- 开发周期：3-5 天

**Phase 2: Transformer 模型 (进阶实现)**
- 理由：捕捉长期依赖、更好的预测精度
- 开发周期：7-10 天

### 3.2 多任务学习输出头 ⭐

同时预测多个目标，共享底层特征表示：

| 任务 | 输出 | 损失函数 |
|------|------|---------|
| 涨跌方向分类 | up/down (二分类) | BCEWithLogitsLoss |
| 收益率回归 | 连续值 | MSELoss |
| 置信度预测 | 0-1 | BCELoss |

```python
class MultiTaskHead(nn.Module):
    def __init__(self, hidden_dim=64):
        self.direction_head = nn.Linear(hidden_dim, 2)
        self.return_head = nn.Linear(hidden_dim, 1)
        self.confidence_head = nn.Linear(hidden_dim, 1)
    
    def forward(self, x):
        return {
            'direction': self.direction_head(x),
            'return': self.return_head(x),
            'confidence': torch.sigmoid(self.confidence_head(x))
        }
```

### 3.3 LSTM 模型架构

```python
class LSTMPredictorMultiTask(nn.Module):
    def __init__(self, input_size=38, hidden_size=128, num_layers=2, dropout=0.2):
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout, bidirectional=True)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),  # *2 for bidirectional
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        self.head = MultiTaskHead(hidden_dim=64)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        features = self.fc(last_hidden)
        return self.head(features)
```

### 3.4 Transformer 模型架构

```python
class TransformerPredictorMultiTask(nn.Module):
    def __init__(self, input_size=38, d_model=128, nhead=8, num_layers=4, dropout=0.1):
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=256, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Sequential(nn.Linear(d_model, 64), nn.ReLU(), nn.Dropout(dropout))
        self.head = MultiTaskHead(hidden_dim=64)
    
    def forward(self, x, mask=None):
        x = self.input_projection(x) * math.sqrt(self.d_model)
        x = self.pos_encoder(x)
        enc_out = self.transformer_encoder(x, mask)
        cls_token = enc_out[:, 0, :]
        features = self.fc(cls_token)
        return self.head(features)
```

### 3.5 训练策略

| 参数 | 值 |
|------|-----|
| batch_size | 64 |
| learning_rate | 0.001 (Adam) |
| epochs | 100 (早停 patience=10) |
| sequence_length | 60 |
| 数据集划分 | train 70% / val 15% / test 15% |

---

## 4. 系统架构

### 4.1 逻辑架构

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                        │
│            RESTful API (FastAPI) + JWT Auth                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  PredictSvc │ ModelSvc │ FeatureSvc │ CacheSvc │ MonitorSvc │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Core Layer                             │
│         Model Engine (LSTM/Transformer) + Feature Engine     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│    PostgreSQL │ Redis │ MinIO/S3 │ QCLaw Data Service       │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 模块职责

| 模块 | 职责 | 技术选型 |
|------|------|---------|
| API Gateway | HTTP 路由、认证、限流 | FastAPI + JWT |
| Predict Service | 预测请求处理、结果组装 | Python Async |
| Model Service | 模型加载、热更新、版本管理 | PyTorch + ONNX |
| Feature Service | 特征计算、预处理、标准化 | Pandas + Scikit-learn |
| Cache Service | 预测结果缓存、会话管理 | Redis |
| Monitor Service | 性能监控、日志、告警 | Prometheus + Grafana |

### 4.3 目录结构

```
qclaw/
└── src/dl_prediction/
    ├── api/                    # API 层
    │   ├── main.py            # FastAPI 入口
    │   ├── routes/            # 路由定义
    │   └── schemas/           # 请求/响应模型
    ├── services/               # 服务层
    │   ├── predict_service.py
    │   ├── model_service.py
    │   └── feature_service.py
    ├── core/                   # 核心层
    │   ├── models/            # LSTM/Transformer
    │   ├── features/          # 特征工程
    │   └── inference/         # 推理引擎
    └── utils/                  # 工具层
```

---

## 5. API 设计

### 5.1 预测接口

```yaml
POST /api/v1/predict/single
Request:
{
  "symbol": "000001.SZ",
  "features": { "prices": [...], "volumes": [...], "indicators": {...} },
  "prediction_horizon": 5,
  "model_version": "transformer-v1.0"
}

Response:
{
  "code": 0,
  "data": {
    "symbol": "000001.SZ",
    "predictions": [
      {
        "horizon": 1,
        "direction": "up",
        "direction_prob": 0.68,
        "return_pred": 1.25,
        "signal": "buy",
        "confidence": 0.72
      }
    ],
    "latency_ms": 125
  }
}
```

### 5.2 模型管理接口

```yaml
GET /api/v1/model/info
POST /api/v1/model/switch
POST /api/v1/model/retrain
```

### 5.3 健康检查接口

```yaml
GET /api/v1/health
Response:
{
  "status": "healthy",
  "services": { "api": "up", "model": "up", "cache": "up" },
  "uptime_seconds": 86400,
  "avg_latency_ms": 120
}
```

---

## 6. 部署架构

### 6.1 生产环境配置

| 组件 | 配置 | 数量 |
|------|------|------|
| Nginx LB | CPU 2 核，内存 4GB | 2 |
| API 服务 | CPU 4 核，内存 8GB | 3 |
| 推理服务 | CPU 8 核，内存 16GB，GPU RTX 3090 | 2 |
| 训练服务 | CPU 16 核，内存 32GB，GPU RTX 3090 | 1 |
| PostgreSQL | CPU 4 核，内存 16GB，SSD 200GB | 1 |
| Redis | CPU 2 核，内存 8GB | 1 |
| MinIO | CPU 4 核，内存 8GB，HDD 1TB | 2 |

### 6.2 GPU 资源配置

**实际配置:**
- GPU 型号：NVIDIA RTX 2070
- 显存：8GB GDDR6
- CUDA 核心：2304

**GPU 加速效果:**
- LSTM 训练加速：10-20 倍
- Transformer 训练加速：30-50 倍
- Phase 1 预计：5 天 → 3 天
- Phase 2 预计：4 天 → 2 天

### 6.3 CUDA/cuDNN 依赖

| 组件 | 版本 |
|------|------|
| NVIDIA 驱动 | >= 525.60.13 |
| CUDA Toolkit | 12.1 |
| cuDNN | 8.9+ |
| PyTorch | 2.0+ |

---

## 7. 性能优化

### 7.1 GPU 训练优化 ⭐

| 优化技术 | 预期收益 | 实现复杂度 |
|---------|---------|-----------|
| 混合精度训练 (AMP) | 内存 -50%, 速度 +30% | 低 |
| 梯度累积 | 等效更大 batch_size | 低 |
| DataLoader 优化 | 数据加载 2-3x 加速 | 低 |
| 梯度裁剪 | 训练稳定性 | 低 |
| 学习率调度 | 更快收敛 | 低 |

### 7.2 推理优化

| 优化点 | 方案 | 预期提升 |
|--------|------|---------|
| 模型推理 | ONNX Runtime + TensorRT | 30-50% |
| 批量推理 | 动态 batching | 2-5x 吞吐 |
| 特征计算 | 向量化 (NumPy) | 5-10x |
| 缓存 | 多级缓存策略 | 减少 80% 重复计算 |

### 7.3 缓存策略

```yaml
L1 - 内存缓存:
  内容：热点股票预测结果
  过期时间：5 分钟
  大小限制：100MB

L2 - Redis 缓存:
  内容：所有预测结果
  过期时间：30 分钟
  大小限制：1GB

缓存键：prediction:{symbol}:{date}:{model_version}:{horizon}
```

---

## 8. 任务规划

### 8.1 开发任务 (CODE-*)

| 任务 ID | 任务名称 | 优先级 | 工时 |
|--------|---------|--------|------|
| CODE-DL-001 | 创建深度学习模块基础结构 | P0 | 0.5 天 |
| CODE-DL-002 | 实现 LSTM 预测模型 | P0 | 2 天 |
| CODE-DL-003 | 实现 Transformer 预测模型 | P1 | 3 天 |
| CODE-DL-004 | 实现特征工程和数据预处理 | P0 | 1.5 天 |
| CODE-DL-005 | 实现模型训练和验证流程 | P0 | 2 天 |
| CODE-DL-006 | 实现模型保存和加载功能 | P1 | 0.5 天 |
| CODE-DL-007 | 集成预测 API 到后端服务 | P1 | 1 天 |
| CODE-DL-008 | 前端展示预测结果和置信度 | P2 | 1.5 天 |
| CODE-DL-009 | 添加基线模型对比 | P1 | 1 天 |
| CODE-DL-010 | 实现多任务学习输出头 | P1 | 1 天 |
| CODE-DL-011 | 实现模型集成策略 | P2 | 1.5 天 |
| CODE-DL-012 | 添加 GPU 训练优化 | P0 | 1 天 |
| CODE-DL-013 | 实现特征重要性分析 | P2 | 1 天 |
| CODE-DL-014 | 添加数据质量验证模块 | P0 | 0.5 天 |
| CODE-DL-015 | 实现模型性能监控和告警 | P1 | 1 天 |

### 8.2 测试任务 (TEST-*)

| 任务 ID | 任务名称 | 优先级 | 工时 |
|--------|---------|--------|------|
| TEST-DL-001 | 单元测试：LSTM 模型前向传播 | P0 | 0.5 天 |
| TEST-DL-002 | 单元测试：Transformer 模型前向传播 | P1 | 0.5 天 |
| TEST-DL-003 | 集成测试：特征工程流水线 | P0 | 0.5 天 |
| TEST-DL-004 | 集成测试：模型训练流程 | P0 | 1 天 |
| TEST-DL-005 | 回测验证：历史数据回测 | P1 | 2 天 |
| TEST-DL-006 | 性能测试：预测延迟和吞吐量 | P2 | 1 天 |
| TEST-DL-007 | 数据质量测试 | P0 | 0.5 天 |
| TEST-DL-008 | 基线模型对比测试 | P1 | 1 天 |
| TEST-DL-009 | 模型稳定性测试 | P1 | 0.5 天 |
| TEST-DL-010 | 特征消融实验 | P2 | 1 天 |
| TEST-DL-011 | GPU 加速效果验证 | P1 | 0.5 天 |

### 8.3 预计完成时间

| 阶段 | 内容 | 时间 (GPU 加速后) |
|-----|------|-----------------|
| Phase 1 | LSTM 模型实现 + 基础训练 | 3 天 |
| Phase 2 | Transformer 模型实现 | 2 天 |
| Phase 3 | API 集成和前端展示 | 2.5 天 |
| Phase 4 | 回测验证和优化 | 3 天 |
| **总计** | 完整功能交付 | **10.5 天** |

---

## 附录

### A. 文献调研成果 (DESIGN-DL-003)

**调研覆盖:**
- LSTM 变种模型：5 个 (ALSTM, LSTNet, GALSTM, DeepLOB, ARNN)
- Transformer 变种模型：6 个 (TFT, Informer, Autoformer, Fedformer, PatchTST, iTransformer)
- 量化专用模型：4 个 (DeepLOB, DeepLOB-Attention, TradeGAN, FinBERT)

**实现优先级建议:**
| 优先级 | 模型 | 预计工时 |
|--------|------|---------|
| P0 | TFT (Temporal Fusion Transformer) | 3-4 天 |
| P0 | LSTNet | 2-3 天 |
| P1 | Autoformer | 3-4 天 |
| P1 | DeepLOB | 2-3 天 |

### B. 文档合并说明

本文档合并自以下原始文件:
- `deep_learning_prediction.md` - 深度学习技术方案
- `dl_prediction_architecture.md` - 系统架构设计
- `DESIGN-DL-003-status-final.md` - 文献调研状态报告

原始文件已添加归档标记并保留在 archive/ 目录。

---

**文档创建时间:** 2026-03-06  
**合并执行者:** qclaw-pm (subagent)  
**文档状态:** ✅ 已完成合并
