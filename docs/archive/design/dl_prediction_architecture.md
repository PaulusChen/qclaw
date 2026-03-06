<!-- ARCHIVED: 已合并到 dl-architecture.md -->

<!-- ARCHIVED: 已压缩至 check-history-summary.md -->

# 深度学习量化预测系统架构设计

**文档 ID:** ARCH-DL-001  
**创建日期:** 2026-03-06  
**版本:** v1.0  
**状态:** 待评审  
**关联需求:** REQ-DL-001

---

## 1. 架构概述

### 1.1 设计原则

- **模块化**: 高内聚低耦合，各模块职责清晰
- **可扩展**: 支持模型热更新、水平扩展
- **高性能**: 单次预测 < 500ms，批量预测 > 100 只/秒
- **可维护**: 完善的日志、监控、版本管理
- **安全性**: API 认证、数据脱敏、模型加密

### 1.2 系统边界

```
┌─────────────────────────────────────────────────────────────────┐
│                        QCLaw 生态系统                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   WebUI     │    │  数据服务    │    │  深度学习预测服务    │  │
│  │  (前端展示)  │◄──►│ (AKShare)   │◄──►│  (本架构设计范围)    │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                              ▲                                   │
│                              │                                   │
│                     ┌────────┴────────┐                         │
│                     │   Qlib 框架      │                         │
│                     │  (回测引擎)      │                         │
│                     └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 系统整体架构

### 2.1 逻辑架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           深度学习预测系统架构                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         API Gateway Layer                            │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │              RESTful API (FastAPI) + JWT Auth                │   │   │
│  │  │  /api/v1/predict/single    /api/v1/predict/batch             │   │   │
│  │  │  /api/v1/predict/history   /api/v1/model/info                │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Service Layer                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ PredictSvc   │  │  ModelSvc    │  │  FeatureSvc  │              │   │
│  │  │ (预测服务)    │  │ (模型服务)    │  │ (特征服务)    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  CacheSvc    │  │  MonitorSvc  │  │  ExplainSvc  │              │   │
│  │  │ (缓存服务)    │  │ (监控服务)    │  │ (解释服务)    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Core Layer                                  │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Model Engine                               │   │   │
│  │  │  ┌─────────────────┐    ┌─────────────────┐                  │   │   │
│  │  │  │ Transformer     │    │    LSTM         │                  │   │   │
│  │  │  │ (注意力机制)     │    │ (序列建模)       │                  │   │   │
│  │  │  └─────────────────┘    └─────────────────┘                  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                   Feature Engine                              │   │   │
│  │  │  数据预处理 │ 特征工程 │ 标准化 │ 异常检测                    │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Data Layer                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  PostgreSQL  │  │    Redis     │  │   MinIO/S3   │              │   │
│  │  │ (预测结果)    │  │ (缓存/会话)  │  │ (模型文件)    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │              QCLaw Data Service (Parquet/HDF5)               │   │   │
│  │  │                    行情数据 │ 技术指标数据                     │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 物理部署架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           生产环境部署架构                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Load Balancer (Nginx)                        │   │
│  │                         端口：80/443                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                    ┌────────────────┼────────────────┐                      │
│                    ▼                ▼                ▼                      │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐   │
│  │   API Container 1   │ │   API Container 2   │ │   API Container 3   │   │
│  │   FastAPI + Uvicorn │ │   FastAPI + Uvicorn │ │   FastAPI + Uvicorn │   │
│  │   CPU: 4 core       │ │   CPU: 4 core       │ │   CPU: 4 core       │   │
│  │   Memory: 8GB       │ │   Memory: 8GB       │ │   Memory: 8GB       │   │
│  │   Port: 8000        │ │   Port: 8000        │ │   Port: 8000        │   │
│  └─────────────────────┘ └─────────────────────┘ └─────────────────────┘   │
│                    │                │                │                      │
│                    └────────────────┼────────────────┘                      │
│                                     │                                       │
│                    ┌────────────────┼────────────────┐                      │
│                    ▼                ▼                ▼                      │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐   │
│  │  Inference Worker 1 │ │  Inference Worker 2 │ │   Training Worker   │   │
│  │  GPU: RTX 3090      │ │  GPU: RTX 3090      │ │   GPU: RTX 3090     │   │
│  │  CUDA 11.7+         │ │  CUDA 11.7+         │ │   (离线训练)         │   │
│  │  Memory: 24GB       │ │  Memory: 24GB       │ │   Memory: 32GB      │   │
│  └─────────────────────┘ └─────────────────────┘ └─────────────────────┘   │
│                    │                │                                       │
│                    └────────────────┼────────────────┐                      │
│                                     ▼                ▼                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Data Services                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  PostgreSQL  │  │    Redis     │  │   MinIO/S3   │              │   │
│  │  │  Port: 5432  │  │  Port: 6379  │  │  Port: 9000  │              │   │
│  │  │  100GB SSD   │  │  16GB RAM    │  │  500GB HDD   │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 模块划分和接口定义

### 3.1 模块职责

| 模块 | 职责 | 技术选型 |
|------|------|---------|
| **API Gateway** | HTTP 请求路由、认证、限流 | FastAPI + JWT |
| **Predict Service** | 预测请求处理、结果组装 | Python Async |
| **Model Service** | 模型加载、热更新、版本管理 | PyTorch + ONNX |
| **Feature Service** | 特征计算、预处理、标准化 | Pandas + Scikit-learn |
| **Cache Service** | 预测结果缓存、会话管理 | Redis |
| **Monitor Service** | 性能监控、日志记录、告警 | Prometheus + Grafana |
| **Explain Service** | 特征重要性、预测解释 | SHAP + Attention Viz |

### 3.2 目录结构

```
qclaw/
├── src/
│   └── dl_prediction/
│       ├── __init__.py
│       ├── api/                    # API 层
│       │   ├── __init__.py
│       │   ├── main.py            # FastAPI 应用入口
│       │   ├── routes/
│       │   │   ├── predict.py     # 预测路由
│       │   │   ├── model.py       # 模型管理路由
│       │   │   └── health.py      # 健康检查路由
│       │   ├── middleware/
│       │   │   ├── auth.py        # JWT 认证中间件
│       │   │   └── logging.py     # 日志中间件
│       │   └── schemas/
│       │       ├── request.py     # 请求模型
│       │       └── response.py    # 响应模型
│       ├── services/               # 服务层
│       │   ├── __init__.py
│       │   ├── predict_service.py
│       │   ├── model_service.py
│       │   ├── feature_service.py
│       │   ├── cache_service.py
│       │   └── monitor_service.py
│       ├── core/                   # 核心层
│       │   ├── __init__.py
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   ├── transformer.py # Transformer 模型
│       │   │   └── lstm.py        # LSTM 模型
│       │   ├── features/
│       │   │   ├── __init__.py
│       │   │   ├── preprocessing.py
│       │   │   ├── engineering.py
│       │   │   └── normalization.py
│       │   └── inference/
│       │       ├── __init__.py
│       │       └── engine.py      # 推理引擎
│       ├── utils/                  # 工具层
│       │   ├── __init__.py
│       │   ├── logger.py
│       │   ├── config.py
│       │   └── metrics.py
│       └── config/                 # 配置层
│           ├── __init__.py
│           ├── default.yaml
│           └── production.yaml
├── models/                         # 模型文件存储
│   ├── transformer/
│   └── lstm/
├── tests/                          # 测试
│   ├── unit/
│   ├── integration/
│   └── performance/
└── docs/
    ├── api/                       # API 文档
    └── deployment/                # 部署文档
```

### 3.3 RESTful API 设计

#### 3.3.1 预测接口

```yaml
# 单只股票预测
POST /api/v1/predict/single
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "symbol": "000001.SZ",
  "features": {
    "prices": [10.5, 10.6, 10.4, ...],  # 20-60 日
    "volumes": [1000000, 1200000, ...],
    "indicators": {
      "ma5": [...],
      "ma10": [...],
      "rsi": [...],
      "macd": [...],
      ...
    }
  },
  "prediction_horizon": 5,  # T+1 到 T+5
  "model_version": "transformer-v1.0"
}

Response:
{
  "code": 0,
  "message": "success",
  "data": {
    "symbol": "000001.SZ",
    "timestamp": "2026-03-06T15:00:00+08:00",
    "predictions": [
      {
        "horizon": 1,
        "direction": "up",
        "direction_prob": 0.68,
        "return_pred": 1.25,
        "return_ci": [0.5, 2.0],
        "signal": "buy",
        "confidence": 0.72
      },
      ...
    ],
    "model_version": "transformer-v1.0",
    "latency_ms": 125
  }
}
```

```yaml
# 批量预测
POST /api/v1/predict/batch
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "symbols": ["000001.SZ", "000002.SZ", ...],
  "prediction_horizon": 5,
  "model_version": "transformer-v1.0"
}

Response:
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 100,
    "success": 98,
    "failed": 2,
    "predictions": [...],
    "latency_ms": 450
  }
}
```

#### 3.3.2 模型管理接口

```yaml
# 获取模型信息
GET /api/v1/model/info

Response:
{
  "code": 0,
  "data": {
    "current_model": "transformer-v1.0",
    "available_models": [
      {"version": "transformer-v1.0", "status": "active"},
      {"version": "lstm-v1.0", "status": "available"},
      {"version": "transformer-v0.9", "status": "archived"}
    ],
    "last_updated": "2026-03-05T10:00:00+08:00",
    "performance": {
      "accuracy": 0.58,
      "mae": 1.8,
      "last_eval_date": "2026-03-05"
    }
  }
}

# 切换模型版本
POST /api/v1/model/switch
{
  "target_version": "lstm-v1.0"
}

# 触发模型重训练
POST /api/v1/model/retrain
{
  "model_type": "transformer",
  "training_data_end": "2026-03-05"
}
```

#### 3.3.3 健康检查接口

```yaml
# 服务健康检查
GET /api/v1/health

Response:
{
  "code": 0,
  "data": {
    "status": "healthy",
    "services": {
      "api": "up",
      "model": "up",
      "cache": "up",
      "database": "up"
    },
    "uptime_seconds": 86400,
    "requests_total": 15000,
    "avg_latency_ms": 120
  }
}
```

---

## 4. 数据流和处理流程

### 4.1 预测数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────►│ API Gateway │────►│Predict Service│
│ (WebUI/APP) │     │  (FastAPI)  │     │              │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Redis     │◄────│ Cache Check │◄────│Feature Service│
│  (缓存)      │     │  (缓存检查)  │     │  (特征处理)   │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                   │
                    ┌──────┴──────┐            │
                    │   Cache Hit │            │
                    │   直接返回   │            │
                    └─────────────┘            │
                                               ▼
                                       ┌─────────────┐
                                       │Model Service│
                                       │ (模型服务)   │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │Model Engine │
                                       │ (推理引擎)   │
                                       └──────┬──────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
            ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
            │  Direction  │           │   Return    │           │   Signal    │
            │  (涨跌方向)  │           │ (收益率预测) │           │ (买卖信号)  │
            └──────┬──────┘           └──────┬──────┘           └──────┬──────┘
                   │                         │                         │
                   └─────────────────────────┼─────────────────────────┘
                                             │
                                             ▼
                                       ┌─────────────┐
                                       │  Assemble   │
                                       │  (结果组装)  │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │   Redis     │
                                       │ (结果缓存)   │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │   Client    │
                                       │  (响应返回)  │
                                       └─────────────┘
```

### 4.2 模型训练数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ QCLaw Data  │────►│  Feature    │────►│   Dataset   │
│   Service   │     │  Engineering│     │   Builder   │
│ (原始数据)   │     │ (特征工程)   │     │  (数据集构建) │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                       ┌─────────────┐
                                       │   Split     │
                                       │ Train/Val/Test│
                                       └──────┬──────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
            ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
            │  Training   │           │ Validation  │           │    Test     │
            │   Set 70%   │           │   Set 15%   │           │   Set 15%   │
            └──────┬──────┘           └──────┬──────┘           └──────┬──────┘
                   │                         │                         │
                   ▼                         │                         │
            ┌─────────────┐                 │                         │
            │   Model     │─────────────────┘                         │
            │  Training   │                                           │
            │  (GPU)      │                                           │
            └──────┬──────┘                                           │
                   │                                                  │
                   ▼                                                  │
            ┌─────────────┐                                          │
            │   Early     │                                          │
            │   Stopping  │                                          │
            └──────┬──────┘                                          │
                   │                                                 │
                   ▼                                                 │
            ┌─────────────┐                                         │
            │  Best Model │                                         │
            │   Save      │                                         │
            └──────┬──────┘                                         │
                   │                                                 │
                   └─────────────────────────┬───────────────────────┘
                                             │
                                             ▼
                                     ┌─────────────┐
                                     │   Evaluate  │
                                     │ (测试集评估) │
                                     └──────┬──────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │   Model     │
                                     │   Registry  │
                                     │ (模型注册表) │
                                     └──────┬──────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │   Deploy    │
                                     │ (热更新部署) │
                                     └─────────────┘
```

### 4.3 特征工程流程

```
原始技术指标数据
       │
       ▼
┌─────────────┐
│ 缺失值处理   │ ────► 前向填充 / 插值
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 异常值检测   │ ────► 3σ原则 / 孤立森林
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 滞后特征    │ ────► t-1, t-2, ..., t-n
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 滚动统计量   │ ────► 滚动均值、标准差、偏度
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 标准化      │ ────► Z-Score / Min-Max
└──────┬──────┘
       │
       ▼
最终特征矩阵 (seq_len, feature_dim)
```

---

## 5. 技术栈详细选型

### 5.1 核心技术栈

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| **Web 框架** | FastAPI | 0.100+ | 高性能异步、自动文档、类型安全 |
| **深度学习** | PyTorch | 2.0+ | 灵活、生态丰富、GPU 支持好 |
| **模型部署** | ONNX Runtime | 1.15+ | 跨平台、推理优化、CPU/GPU 通用 |
| **数据处理** | Pandas + NumPy | 2.0+ / 1.24+ | 成熟稳定、生态完善 |
| **特征工程** | Scikit-learn | 1.3+ | 标准化、预处理工具丰富 |
| **缓存** | Redis | 7.0+ | 高性能、支持过期策略 |
| **数据库** | PostgreSQL | 15+ | 可靠、JSON 支持、时序扩展 |
| **对象存储** | MinIO | 2023+ | S3 兼容、自部署、成本低 |

### 5.2 辅助工具栈

| 用途 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **API 认证** | PyJWT | 2.8+ | JWT Token 生成验证 |
| **配置管理** | PyYAML + Pydantic | 6.0+ / 2.0+ | 配置解析和验证 |
| **日志** | Loguru | 0.7+ | 简洁、功能丰富 |
| **监控** | Prometheus + Grafana | 2.40+ / 10.0+ | 指标收集和可视化 |
| **可解释性** | SHAP | 0.42+ | 特征重要性分析 |
| **测试** | Pytest | 7.3+ | 单元测试框架 |
| **性能测试** | Locust | 2.15+ | 负载测试 |
| **容器化** | Docker + Docker Compose | 24+ / 2.20+ | 环境隔离、部署简化 |

### 5.3 模型架构选型

#### 推荐方案：Transformer 为主，LSTM 为辅

**Transformer 架构 (主力模型)**
```python
class StockTransformer(nn.Module):
    - Input Embedding: feature_dim → d_model (256)
    - Positional Encoding: 可学习位置编码
    - Transformer Encoder: 3 层，8 头注意力
    - Hidden Dim: 256
    - Dropout: 0.3
    - Output Heads:
      - Direction: Linear(256, 2)  # 二分类
      - Return: Linear(256, 1)     # 回归
      - Signal: Linear(256, 3)     # 三分类
```

**LSTM 架构 (备选/对比模型)**
```python
class StockLSTM(nn.Module):
    - Input: feature_dim
    - BiLSTM: 2 层，hidden=128
    - Dropout: 0.3
    - Attention: 注意力池化
    - Output Heads: 同 Transformer
```

**选型理由:**
- Transformer 并行计算能力强，训练速度快
- 自注意力机制更适合捕捉技术指标间的关联
- LSTM 作为对比基线和备选方案
- 支持多模型 ensemble 提升准确率

---

## 6. 部署架构和资源配置

### 6.1 开发环境

| 组件 | 配置 | 数量 |
|------|------|------|
| 开发机 | CPU 8 核，内存 32GB，GPU RTX 3090 | 1 |
| 存储 | SSD 500GB | 1 |

### 6.2 测试环境

| 组件 | 配置 | 数量 |
|------|------|------|
| API 服务 | CPU 4 核，内存 8GB | 1 |
| 推理服务 | CPU 4 核，内存 16GB，GPU RTX 3080 | 1 |
| PostgreSQL | CPU 2 核，内存 4GB，SSD 50GB | 1 |
| Redis | CPU 1 核，内存 2GB | 1 |

### 6.3 生产环境

| 组件 | 配置 | 数量 | 说明 |
|------|------|------|------|
| Nginx LB | CPU 2 核，内存 4GB | 2 | 负载均衡 |
| API 服务 | CPU 4 核，内存 8GB | 3 | 水平扩展 |
| 推理服务 | CPU 8 核，内存 16GB，GPU RTX 3090 | 2 | GPU 推理 |
| 训练服务 | CPU 16 核，内存 32GB，GPU RTX 3090 | 1 | 离线训练 |
| PostgreSQL | CPU 4 核，内存 16GB，SSD 200GB | 1 | 主从复制 |
| Redis | CPU 2 核，内存 8GB | 1 | 哨兵模式 |
| MinIO | CPU 4 核，内存 8GB，HDD 1TB | 2 | 分布式存储 |
| Prometheus | CPU 2 核，内存 4GB，SSD 50GB | 1 | 监控 |
| Grafana | CPU 2 核，内存 4GB | 1 | 可视化 |

### 6.4 Docker Compose 配置示例

```yaml
version: '3.8'

services:
  api:
    build: ./src/dl_prediction
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - REDIS_URL=redis://redis:6379
      - DB_URL=postgresql://user:pass@postgres:5432/qclaw_dl
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 3

  inference:
    build: ./src/dl_prediction
    command: uvicorn app.inference:app --host 0.0.0.0 --port 8001
    environment:
      - MODEL_PATH=/models/transformer-v1.0.pt
      - DEVICE=cuda
    volumes:
      - ./models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=qclaw_dl
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

volumes:
  redis_data:
  postgres_data:
  minio_data:
  prometheus_data:
  grafana_data:
```

---

## 7. 关键设计点详解

### 7.1 模型热更新机制

```
┌─────────────────────────────────────────────────────────────────┐
│                      模型热更新流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 新模型训练完成 ────► 保存到模型注册表 (MinIO)                │
│                                                                 │
│  2. 触发更新通知 ────► Model Service 监听变更事件               │
│                                                                 │
│  3. 预加载新模型 ────► 后台加载到备用内存区域                    │
│                                                                 │
│  4. 验证新模型 ────► 使用验证集进行快速验证                      │
│                                                                 │
│  5. 原子切换 ────► 更新模型指针，新请求使用新模型                │
│                                                                 │
│  6. 旧模型保留 ────► 保留最近 3 个版本，支持快速回滚             │
│                                                                 │
│  7. 通知完成 ────► 记录更新日志，发送告警通知                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

实现要点:
- 使用版本号管理模型 (semantic versioning)
- 模型文件存储于 MinIO，支持版本控制
- 使用双缓冲机制，切换时不影响正在进行的推理
- 回滚机制：保存最近 3 个版本，支持一键回滚
```

### 7.2 缓存策略

```yaml
缓存层级:
  L1 - 内存缓存:
    位置：应用进程内
    内容：热点股票预测结果
    过期时间：5 分钟
    大小限制：100MB

  L2 - Redis 缓存:
    位置：独立 Redis 服务
    内容：所有预测结果
    过期时间：30 分钟
    大小限制：1GB

缓存键设计:
  格式：prediction:{symbol}:{date}:{model_version}:{horizon}
  示例：prediction:000001.SZ:20260306:transformer-v1.0:1

缓存策略:
  - 相同股票 + 日期 + 模型版本 + 预测周期 → 直接返回缓存
  - 缓存穿透：使用布隆过滤器过滤不存在的股票
  - 缓存雪崩：过期时间添加随机偏移 (±5 分钟)
  - 缓存击穿：对热点 key 使用互斥锁
```

### 7.3 性能优化策略

#### 推理优化

| 优化点 | 方案 | 预期提升 |
|--------|------|---------|
| **模型推理** | ONNX Runtime + TensorRT | 30-50% |
| **批量推理** | 动态 batching，最大 batch=32 | 2-5x 吞吐 |
| **特征计算** | 向量化计算 (NumPy) | 5-10x |
| **数据加载** | 预加载 + 异步 IO | 减少 50% 等待 |
| **缓存** | 多级缓存策略 | 减少 80% 重复计算 |
| **连接池** | 数据库/Redis 连接池 | 减少连接开销 |

#### GPU 训练优化 ⭐ 设计复查更新

| 优化技术 | 方案 | 预期提升 | 实现复杂度 |
|---------|------|---------|-----------|
| **混合精度训练 (AMP)** | torch.cuda.amp.autocast + GradScaler | 1.5-2x 加速，50% 显存节省 | 低 |
| **梯度累积** | accumulation_steps=4-8 | 模拟更大 batch_size | 低 |
| **DataLoader 优化** | num_workers=4, pin_memory=True, persistent_workers=True | 2-3x 数据加载加速 | 低 |
| **梯度检查点** | torch.utils.checkpoint | 节省显存，支持更大模型 | 中 |
| **学习率调度** | CosineAnnealingLR + Warmup | 更快收敛，更好效果 | 低 |

**混合精度训练实现:**
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for epoch in range(epochs):
    for batch in train_loader:
        optimizer.zero_grad()
        
        with autocast():  # 自动混合精度
            outputs = model(batch['inputs'])
            loss = criterion(outputs, batch['targets'])
        
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
```

**梯度累积实现:**
```python
accumulation_steps = 4

for i, batch in enumerate(train_loader):
    outputs = model(batch['inputs'])
    loss = criterion(outputs, batch['targets'])
    loss = loss / accumulation_steps  # 损失平均
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**DataLoader 优化配置:**
```python
from torch.utils.data import DataLoader

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,           # CPU 核心数
    pin_memory=True,         # 锁定内存加速 GPU 传输
    persistent_workers=True, # 持久化 worker
    prefetch_factor=2        # 预加载 batch 数
)
```

**GPU 显存监控:**
```python
def log_gpu_memory():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f'GPU Memory - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB')

# 在训练循环中定期调用
if step % 100 == 0:
    log_gpu_memory()
```

**预期训练性能 (RTX 2070 8GB):**
| 配置 | 单 epoch 时间 | 显存占用 | 100 epoch 总时间 |
|------|------------|---------|----------------|
| CPU (baseline) | ~2 小时 | N/A | ~200 小时 |
| GPU (基础) | ~10 分钟 | 4-5GB | ~17 小时 |
| GPU + AMP | ~6 分钟 | 2-3GB | ~10 小时 |
| GPU + AMP + 梯度累积 | ~7 分钟 | 1.5-2GB | ~12 小时 |

### 7.4 监控和告警

```yaml
监控指标:
  业务指标:
    - 预测请求量 (QPS)
    - 预测延迟 (P50/P95/P99)
    - 预测准确率 (日/周/月)
    - 缓存命中率

  系统指标:
    - CPU 使用率
    - 内存使用率
    - GPU 使用率/显存
    - 磁盘 IO

  服务指标:
    - API 响应时间
    - 错误率 (4xx/5xx)
    - 模型加载时间
    - 数据库连接数

告警规则:
  - 预测延迟 P95 > 500ms → 警告
  - 错误率 > 1% → 警告
  - GPU 显存 > 90% → 警告
  - 服务不可用 → 严重
  - 预测准确率连续 5 日 < 50% → 警告

告警渠道:
  - 企业微信/钉钉机器人
  - 邮件
  - 短信 (严重级别)
```

### 7.5 安全设计

```yaml
认证授权:
  - JWT Token 认证，有效期 24 小时
  - API Key 用于服务间调用
  - RBAC 权限控制 (管理员/开发者/普通用户)

数据安全:
  - 敏感数据脱敏 (股票代码部分隐藏)
  - 传输加密 (HTTPS/TLS 1.3)
  - 存储加密 (模型文件 AES-256)

访问控制:
  - API 限流 (100 请求/分钟/用户)
  - IP 白名单 (内部服务)
  - 预测结果访问权限控制

审计日志:
  - 所有 API 请求记录
  - 模型更新操作审计
  - 异常行为检测
```

---

## 8. 与现有系统集成

### 8.1 与 QCLaw 数据服务集成

```python
# 数据服务接口调用示例
class QclawDataClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def get_stock_features(self, symbol: str, days: int = 60) -> dict:
        """获取股票技术指标数据"""
        url = f"{self.base_url}/api/v1/features/{symbol}"
        params = {"days": days}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()
    
    async def get_market_data(self, date: str) -> dict:
        """获取大盘指标数据"""
        url = f"{self.base_url}/api/v1/market/{date}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
```

### 8.2 与 Qlib 框架集成

```python
# Qlib 回测集成
from qlib.backtest import backtest, executor
from qlib.strategy.base import BaseStrategy

class DLPredictionStrategy(BaseStrategy):
    def __init__(self, dl_api_url: str, model_version: str):
        self.dl_api_url = dl_api_url
        self.model_version = model_version
    
    async def generate_signal(self, instrument: str, date: str) -> int:
        """获取深度学习模型预测信号"""
        # 调用预测 API
        # 返回：1=买入，0=持有，-1=卖出
        pass

# 回测配置
backtest_config = {
    "start_time": "2025-01-01",
    "end_time": "2026-03-01",
    "account": 1000000,
    "exchange_kwargs": {"freq": "day"},
    "executor": executor.SimulatorExecutor(),
    "strategy": DLPredictionStrategy(dl_api_url, model_version),
}
```

### 8.3 与 WebUI 集成

```typescript
// WebUI 预测结果展示组件
interface PredictionResult {
  symbol: string;
  timestamp: string;
  predictions: Array<{
    horizon: number;
    direction: 'up' | 'down';
    directionProb: number;
    returnPred: number;
    returnCi: [number, number];
    signal: 'buy' | 'hold' | 'sell';
    confidence: number;
  }>;
  modelVersion: string;
  latencyMs: number;
}

// API 调用
async function fetchPrediction(symbol: string): Promise<PredictionResult> {
  const response = await fetch('/api/v1/predict/single', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ symbol, prediction_horizon: 5 })
  });
  return response.json();
}
```

---

## 9. 验收标准对照

| 需求项 | 架构设计对应 | 状态 |
|--------|-------------|------|
| 支持 Transformer 和 LSTM | 第 5.3 节，双模型架构 | ✅ |
| 支持 15+ 技术指标输入 | 第 2.1 节，Feature Service | ✅ |
| 三类预测输出 | 第 3.3.1 节，API 响应格式 | ✅ |
| RESTful API | 第 3.3 节，完整 API 设计 | ✅ |
| 历史回测功能 | 第 8.2 节，Qlib 集成 | ✅ |
| 单次预测 < 500ms | 第 7.3 节，性能优化策略 | ✅ |
| 批量预测 > 100 只/秒 | 第 6.3 节，多 GPU 部署 | ✅ |
| 方向准确率 > 55% | 第 7.4 节，监控指标 | ✅ |
| 模型热更新 | 第 7.1 节，热更新机制 | ✅ |
| API 认证 | 第 7.5 节，JWT 认证 | ✅ |

---

## 10. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 模型准确率不达标 | 高 | 多模型 ensemble、持续优化、特征工程迭代 |
| 推理延迟超标 | 中 | ONNX 优化、GPU 部署、缓存策略 |
| 数据质量问题 | 中 | 数据校验、异常检测、数据源冗余 |
| GPU 资源不足 | 中 | 模型量化、CPU 推理降级、资源调度 |
| 市场风格突变 | 高 | 定期重训练、在线学习、多周期模型 |

---

## 11. 后续工作

### 11.1 待办事项

- [ ] 架构设计评审 (qclaw-reviewer)
- [ ] 详细设计文档 (模块内部设计)
- [ ] API 接口详细定义 (OpenAPI/Swagger)
- [ ] 数据库表结构设计
- [ ] 开发环境搭建
- [ ] 原型开发 (MVP)

### 11.2 时间估算

| 阶段 | 工作内容 | 预估时间 |
|------|---------|---------|
| 设计评审 | 架构评审、修改 | 2 天 |
| 基础框架 | 项目骨架、CI/CD | 3 天 |
| 核心开发 | 模型、服务、API | 10 天 |
| 集成测试 | 单元测试、集成测试 | 5 天 |
| 性能优化 | 压测、调优 | 3 天 |
| 部署上线 | 生产环境部署 | 2 天 |
| **总计** | | **25 天** |

---

## 附录

### A. 缩略语

| 缩略语 | 全称 |
|--------|------|
| API | Application Programming Interface |
| JWT | JSON Web Token |
| LSTM | Long Short-Term Memory |
| MAE | Mean Absolute Error |
| ONNX | Open Neural Network Exchange |
| QPS | Queries Per Second |
| RBAC | Role-Based Access Control |
| SHAP | SHapley Additive exPlanations |

### B. 参考文档

1. FastAPI 官方文档：https://fastapi.tiangolo.com/
2. PyTorch 官方文档：https://pytorch.org/docs/
3. ONNX Runtime：https://onnxruntime.ai/
4. Microsoft Qlib：https://qlib.readthedocs.io/

---

**文档变更记录:**

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-03-06 | 初始版本 | qclaw-designer |
