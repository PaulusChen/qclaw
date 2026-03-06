# 推理服务详细设计

**文档版本:** v1.0  
**创建日期:** 2026-03-06  
**作者:** qclaw-designer  
**状态:** ✅ 已完成  
**关联任务:** DESIGN-DL-002, CODE-DL-008

---

## 📋 目录

1. [推理服务概述](#1-推理服务概述)
2. [推理 API 设计](#2-推理-api-设计)
3. [批量推理优化](#3-批量推理优化)
4. [结果缓存策略](#4-结果缓存策略)
5. [性能监控](#5-性能监控)
6. [服务部署架构](#6-服务部署架构)
7. [伪代码与示例](#7-伪代码与示例)

---

## 1. 推理服务概述

### 1.1 服务目标

推理服务负责将训练好的深度学习模型部署到生产环境，为 WebUI 和量化策略提供实时/批量的预测结果。

**核心需求:**
- 低延迟：单次推理 < 50ms
- 高吞吐：支持并发请求
- 高可用：99.9% 服务可用性
- 可扩展：支持水平扩展

### 1.2 服务架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   WebUI     │  │  策略引擎   │  │  定时任务   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │ HTTP/gRPC                             │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 网关层                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  负载均衡 (Nginx/HAProxy)                                │    │
│  │  - 请求路由                                              │    │
│  │  - 限流/熔断                                             │    │
│  │  - SSL 终止                                               │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       推理服务层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Instance 1 │  │  Instance 2 │  │  Instance N │              │
│  │  (Flask)    │  │  (Flask)    │  │  (Flask)    │              │
│  │             │  │             │  │             │              │
│  │  ┌───────┐  │  │  ┌───────┐  │  │  ┌───────┐  │              │
│  │  │ 模型  │  │  │  │ 模型  │  │  │  │ 模型  │  │              │
│  │  │ Loader│  │  │  │ Loader│  │  │  │ Loader│  │              │
│  │  └───────┘  │  │  └───────┘  │  │  └───────┘  │              │
│  │             │  │             │  │             │              │
│  │  ┌───────┐  │  │  ┌───────┐  │  │  ┌───────┐  │              │
│  │  │ 缓存  │  │  │  │ 缓存  │  │  │  │ 缓存  │  │              │
│  │  │  Redis│  │  │  │  Redis│  │  │  │  Redis│  │              │
│  │  └───────┘  │  │  └───────┘  │  │  └───────┘  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Redis     │  │  PostgreSQL │  │  MinIO/S3   │              │
│  │  (缓存)     │  │  (元数据)    │  │  (模型文件)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 技术选型

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| Web 框架 | Flask/FastAPI | 轻量、易用、生态丰富 |
| 模型格式 | PyTorch (.pt) / ONNX | 原生支持/跨平台优化 |
| 缓存 | Redis | 高性能、支持过期策略 |
| 部署 | Docker + Kubernetes | 容器化、弹性伸缩 |
| 监控 | Prometheus + Grafana | 标准化监控方案 |

---

## 2. 推理 API 设计

### 2.1 API 端点

```yaml
# RESTful API 设计
/base_url: /api/v1/prediction

端点:
  # 单次预测
  - path: /predict
    method: POST
    description: 对单个股票进行预测
    rate_limit: 100 req/min
    
  # 批量预测
  - path: /predict/batch
    method: POST
    description: 对多个股票进行批量预测
    rate_limit: 20 req/min
    
  # 预测历史查询
  - path: /predict/history
    method: GET
    description: 查询历史预测记录
    rate_limit: 60 req/min
    
  # 模型健康检查
  - path: /health
    method: GET
    description: 服务健康状态检查
    rate_limit: unlimited
    
  # 模型信息
  - path: /model/info
    method: GET
    description: 获取当前模型版本和元数据
    rate_limit: 30 req/min
```

### 2.2 请求/响应格式

#### 2.2.1 单次预测请求

```json
// POST /api/v1/prediction/predict
{
  "stock_code": "000001.SZ",
  "date": "2026-03-06",
  "features": {
    "close": 15.23,
    "open": 15.10,
    "high": 15.45,
    "low": 15.05,
    "volume": 12345678,
    "ma5": 15.18,
    "ma10": 15.05,
    "ma20": 14.92,
    "macd": 0.15,
    "macd_signal": 0.12,
    "rsi": 58.5,
    // ... 其他 25+ 特征
  },
  "model_version": "v1.0.0",
  "include_confidence": true
}
```

#### 2.2.2 单次预测响应

```json
{
  "request_id": "req_20260306_112345_abc123",
  "status": "success",
  "data": {
    "stock_code": "000001.SZ",
    "predict_date": "2026-03-07",
    "predictions": {
      "direction": {
        "value": 1,
        "label": "up",
        "confidence": 0.72
      },
      "return_rate": {
        "value": 0.0185,
        "confidence": 0.65
      },
      "volatility": {
        "value": 0.023,
        "confidence": 0.58
      }
    },
    "model_version": "v1.0.0",
    "inference_time_ms": 23,
    "cache_hit": false
  },
  "timestamp": "2026-03-06T11:23:45.123Z"
}
```

#### 2.2.3 批量预测请求

```json
// POST /api/v1/prediction/predict/batch
{
  "stocks": [
    {
      "stock_code": "000001.SZ",
      "features": { ... }
    },
    {
      "stock_code": "000002.SZ",
      "features": { ... }
    }
    // ... 最多 50 只股票
  ],
  "model_version": "v1.0.0"
}
```

#### 2.2.4 错误响应

```json
{
  "request_id": "req_20260306_112345_abc123",
  "status": "error",
  "error": {
    "code": "MODEL_NOT_LOADED",
    "message": "模型 v1.0.0 未加载，请使用 /model/load 端点加载",
    "details": {
      "available_versions": ["v0.9.5", "v0.9.6"]
    }
  },
  "timestamp": "2026-03-06T11:23:45.123Z"
}
```

### 2.3 错误码定义

| 错误码 | HTTP 状态码 | 说明 |
|--------|-----------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `STOCK_NOT_FOUND` | 404 | 股票代码不存在 |
| `MODEL_NOT_LOADED` | 503 | 模型未加载 |
| `FEATURE_MISSING` | 400 | 缺少必需特征 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超出速率限制 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `TIMEOUT` | 504 | 推理超时 |

---

## 3. 批量推理优化

### 3.1 批处理策略

```python
# 批处理配置
BATCH_CONFIG = {
    'max_batch_size': 64,        # 最大批量大小
    'min_batch_size': 8,         # 最小批量大小 (触发推理)
    'max_wait_time_ms': 50,      # 最大等待时间 (ms)
    'dynamic_batching': True,    # 启用动态批处理
}
```

### 3.2 动态批处理流程

```
请求队列 → 累积请求 → 达到阈值？→ 批量推理 → 分发结果
              │            │
              │            ├─ 数量达到 max_batch_size
              │            └─ 等待时间达到 max_wait_time_ms
              │
              └─ 新请求持续加入
```

### 3.3 批处理伪代码

```python
class BatchInference:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.request_queue = asyncio.Queue()
        self.result_map = {}  # request_id -> result
        
    async def enqueue(self, request_id, features):
        """添加请求到队列"""
        future = asyncio.Future()
        self.request_queue.put((request_id, features, future))
        return future
        
    async def process_batch(self):
        """批处理协程"""
        while True:
            batch = []
            start_time = time.time()
            
            # 累积请求
            while len(batch) < self.config['max_batch_size']:
                try:
                    timeout = self.config['max_wait_time_ms'] / 1000
                    if batch:
                        # 已有请求，缩短等待时间
                        timeout = min(timeout, 0.01)
                    
                    item = await asyncio.wait_for(
                        self.request_queue.get(), 
                        timeout=timeout
                    )
                    batch.append(item)
                except asyncio.TimeoutError:
                    break
            
            if not batch:
                continue
            
            # 批量推理
            request_ids = [item[0] for item in batch]
            features_batch = torch.stack([item[1] for item in batch])
            futures = [item[2] for item in batch]
            
            with torch.inference_mode():
                predictions = self.model(features_batch)
            
            # 分发结果
            for i, (req_id, _, future) in enumerate(batch):
                result = predictions[i].cpu().numpy()
                future.set_result(result)
```

### 3.4 性能优化技术

| 优化技术 | 预期提升 | 实现方式 |
|---------|---------|---------|
| 批量推理 | 5-10x 吞吐 | 动态批处理 |
| 模型量化 (INT8) | 2-4x 加速 | PyTorch Quantization |
| ONNX Runtime | 1.5-3x 加速 | 模型导出 + ORT |
| GPU 批处理 | 10-50x 加速 | CUDA Batch Inference |
| 特征预处理并行 | 2-3x 加速 | multiprocessing |

---

## 4. 结果缓存策略

### 4.1 缓存架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   请求      │ ──→ │  缓存检查   │ ──→ │  Redis      │
│             │     │  (Cache Key)│     │  (存储)     │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    Cache Miss?
                           │
                           ▼
                    ┌─────────────┐
                    │  模型推理   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  缓存写入   │
                    └─────────────┘
```

### 4.2 缓存键设计

```python
def generate_cache_key(stock_code, date, features_hash, model_version):
    """生成缓存键"""
    # features_hash = hashlib.md5(json.dumps(features, sort_keys=True)).hexdigest()
    return f"pred:{stock_code}:{date}:{features_hash[:16]}:{model_version}"

# 示例:
# pred:000001.SZ:2026-03-06:a1b2c3d4e5f6:v1.0.0
```

### 4.3 缓存策略配置

```yaml
cache:
  enabled: true
  backend: redis
  
  # 连接配置
  redis:
    host: localhost
    port: 6379
    db: 0
    password: ${REDIS_PASSWORD}
  
  # TTL 配置 (秒)
  ttl:
    intraday: 300      # 日内预测：5 分钟
    daily: 3600        # 日级预测：1 小时
    weekly: 86400      # 周级预测：24 小时
  
  # 淘汰策略
  eviction:
    max_memory: 2gb
    policy: allkeys-lru  # LRU 淘汰
  
  # 缓存命中率监控
  metrics:
    enabled: true
    sample_rate: 0.1
```

### 4.4 缓存失效策略

| 场景 | 失效方式 | 说明 |
|------|---------|------|
| 模型更新 | 删除所有旧版本缓存 | 模型版本变更时 |
| 数据修正 | 删除特定股票缓存 | 历史数据修正时 |
| 定期清理 | TTL 自动过期 | 基于时间过期 |
| 内存压力 | LRU 淘汰 | Redis 内存满时 |

---

## 5. 性能监控

### 5.1 监控指标

```yaml
# Prometheus 指标定义
metrics:
  # 延迟指标
  - name: inference_latency_seconds
    type: histogram
    buckets: [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    labels: [model_version, stock_market]
    
  # 吞吐指标
  - name: inference_requests_total
    type: counter
    labels: [status, model_version]
    
  # 缓存指标
  - name: cache_hits_total
    type: counter
    labels: [cache_type]
    
  - name: cache_hit_ratio
    type: gauge
    
  # 资源指标
  - name: gpu_memory_usage_bytes
    type: gauge
    labels: [gpu_id]
    
  - name: model_load_time_seconds
    type: histogram
```

### 5.2 Grafana 看板

```
┌─────────────────────────────────────────────────────────────────┐
│                    qclaw 推理服务监控                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   QPS (请求/秒)  │  │  P99 延迟 (ms)   │  │  缓存命中率 (%)  │ │
│  │      245        │  │       42        │  │       78.5      │ │
│  │   ▲ +12%        │  │   ▼ -5%         │  │   ▲ +2.3%       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              请求延迟分布 (过去 1 小时)                      │   │
│  │  ████▇▅▃▂▁                                              │   │
│  │  0    25   50   75  100  125  150  175  200 (ms)         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │   GPU 使用率 (%)    │  │  模型内存 (MB)    │                    │
│  │  ████████░░  78%   │  │   2,456 / 8,192  │                    │
│  └──────────────────┘  └──────────────────┘                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              错误率趋势 (过去 24 小时)                       │   │
│  │  ▁▁▁▂▃▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁  │   │
│  │  00   04   08   12   16   20   00 (小时)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 告警规则

```yaml
# Alertmanager 告警配置
groups:
  - name: inference_service
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(inference_latency_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "推理延迟过高 (P99 > 100ms)"
          
      - alert: HighErrorRate
        expr: rate(inference_requests_total{status="error"}[5m]) / rate(inference_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "推理错误率过高 (> 5%)"
          
      - alert: LowCacheHitRatio
        expr: cache_hit_ratio < 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "缓存命中率过低 (< 50%)"
          
      - alert: GPUHighMemory
        expr: gpu_memory_usage_bytes / gpu_memory_total_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU 内存使用率过高 (> 90%)"
```

---

## 6. 服务部署架构

### 6.1 Docker 容器化

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ ./src/
COPY models/ ./models/
COPY config/ ./config/

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/models
ENV CONFIG_PATH=/app/config

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/prediction/health || exit 1

# 启动命令
CMD ["uvicorn", "src.inference.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Kubernetes 部署

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qclaw-inference
  namespace: qclaw
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inference
  template:
    metadata:
      labels:
        app: inference
    spec:
      containers:
        - name: inference
          image: qclaw/inference:v1.0.0
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "2Gi"
              cpu: "1000m"
              nvidia.com/gpu: "1"
            limits:
              memory: "4Gi"
              cpu: "2000m"
              nvidia.com/gpu: "1"
          env:
            - name: REDIS_HOST
              valueFrom:
                configMapKeyRef:
                  name: qclaw-config
                  key: redis-host
            - name: MODEL_VERSION
              value: "v1.0.0"
          livenessProbe:
            httpGet:
              path: /api/v1/prediction/health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/v1/prediction/health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: qclaw-inference-service
  namespace: qclaw
spec:
  selector:
    app: inference
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: qclaw-inference-hpa
  namespace: qclaw
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: qclaw-inference
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: inference_requests_per_second
        target:
          type: AverageValue
          averageValue: 100
```

### 6.3 部署流程

```
1. 构建镜像
   docker build -t qclaw/inference:v1.0.0 .

2. 推送镜像
   docker push qclaw/inference:v1.0.0

3. 更新 Kubernetes
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/hpa.yaml

4. 验证部署
   kubectl get pods -n qclaw
   kubectl logs -n qclaw -l app=inference

5. 滚动更新 (零停机)
   kubectl set image deployment/qclaw-inference \
     inference=qclaw/inference:v1.0.1 -n qclaw
```

---

## 7. 伪代码与示例

### 7.1 推理服务主流程

```python
# src/inference/service.py
import torch
import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib

class InferenceService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.device = None
        self.redis_client = None
        self.metrics = MetricsCollector()
        
    def initialize(self):
        """初始化服务"""
        # 1. 设置设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 2. 加载模型
        self.model = self._load_model(self.config['model_path'])
        self.model.to(self.device)
        self.model.eval()
        
        # 3. 连接 Redis
        self.redis_client = redis.Redis(
            host=self.config['redis']['host'],
            port=self.config['redis']['port'],
            db=self.config['redis']['db']
        )
        
    def _load_model(self, model_path: str) -> torch.nn.Module:
        """加载模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        model = PredictionModel(**checkpoint['config'])
        model.load_state_dict(checkpoint['state_dict'])
        return model
        
    def predict(self, stock_code: str, features: Dict, 
                include_confidence: bool = True) -> Dict[str, Any]:
        """单次预测"""
        start_time = time.time()
        request_id = generate_request_id()
        
        # 1. 检查缓存
        cache_key = self._generate_cache_key(stock_code, features)
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result:
            self.metrics.record_cache_hit()
            cached_result['cache_hit'] = True
            return cached_result
        
        self.metrics.record_cache_miss()
        
        # 2. 特征预处理
        feature_tensor = self._preprocess_features(features)
        feature_tensor = feature_tensor.to(self.device)
        
        # 3. 模型推理
        with torch.inference_mode():
            output = self.model(feature_tensor.unsqueeze(0))
        
        # 4. 后处理
        prediction = self._postprocess_output(output, include_confidence)
        
        # 5. 构建响应
        result = {
            'request_id': request_id,
            'status': 'success',
            'data': {
                'stock_code': stock_code,
                'predictions': prediction,
                'model_version': self.config['model_version'],
                'inference_time_ms': (time.time() - start_time) * 1000,
                'cache_hit': False
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 6. 写入缓存
        self._write_to_cache(cache_key, result)
        
        # 7. 记录指标
        self.metrics.record_latency(result['data']['inference_time_ms'])
        self.metrics.record_request()
        
        return result
        
    def _preprocess_features(self, features: Dict) -> torch.Tensor:
        """特征预处理"""
        # 标准化
        normalized = self._normalize_features(features)
        
        # 转换为张量
        feature_vector = [normalized[f] for f in self.config['feature_list']]
        tensor = torch.tensor(feature_vector, dtype=torch.float32)
        
        return tensor
        
    def _postprocess_output(self, output: torch.Tensor, 
                            include_confidence: bool) -> Dict:
        """输出后处理"""
        direction_logits = output['direction']
        return_logits = output['return_rate']
        
        direction_prob = torch.softmax(direction_logits, dim=-1)
        direction_pred = torch.argmax(direction_prob).item()
        
        result = {
            'direction': {
                'value': direction_pred,
                'label': 'up' if direction_pred == 1 else 'down',
            },
            'return_rate': {
                'value': return_logits.item()
            }
        }
        
        if include_confidence:
            result['direction']['confidence'] = direction_prob[direction_pred].item()
            result['return_rate']['confidence'] = self._estimate_confidence(output)
        
        return result
        
    def _generate_cache_key(self, stock_code: str, features: Dict) -> str:
        """生成缓存键"""
        features_hash = hashlib.md5(
            json.dumps(features, sort_keys=True).encode()
        ).hexdigest()[:16]
        return f"pred:{stock_code}:{datetime.now().strftime('%Y-%m-%d')}:{features_hash}:{self.config['model_version']}"
        
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """从缓存获取"""
        if not self.config['cache']['enabled']:
            return None
            
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
        
    def _write_to_cache(self, cache_key: str, result: Dict):
        """写入缓存"""
        if not self.config['cache']['enabled']:
            return
            
        ttl = self.config['cache']['ttl']['intraday']
        self.redis_client.setex(
            cache_key, 
            ttl, 
            json.dumps(result)
        )
```

### 7.2 FastAPI 端点示例

```python
# src/inference/api.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio

app = FastAPI(title="qclaw Prediction API", version="1.0.0")

# 请求模型
class PredictRequest(BaseModel):
    stock_code: str = Field(..., description="股票代码", example="000001.SZ")
    date: str = Field(..., description="预测日期", example="2026-03-06")
    features: Dict[str, float] = Field(..., description="特征字典")
    model_version: Optional[str] = Field("v1.0.0", description="模型版本")
    include_confidence: bool = Field(True, description="是否包含置信度")

class BatchPredictRequest(BaseModel):
    stocks: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50)
    model_version: Optional[str] = Field("v1.0.0")

# 响应模型
class PredictResponse(BaseModel):
    request_id: str
    status: str
    data: Dict[str, Any]
    timestamp: str

# 全局服务实例
inference_service: Optional[InferenceService] = None

@app.on_event("startup")
async def startup_event():
    global inference_service
    inference_service = InferenceService(load_config())
    inference_service.initialize()

@app.post("/api/v1/prediction/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """单次预测"""
    try:
        result = inference_service.predict(
            stock_code=request.stock_code,
            features=request.features,
            include_confidence=request.include_confidence
        )
        return PredictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/prediction/predict/batch")
async def predict_batch(request: BatchPredictRequest):
    """批量预测"""
    tasks = []
    for stock in request.stocks:
        task = asyncio.create_task(
            inference_service.predict_async(
                stock_code=stock['stock_code'],
                features=stock['features']
            )
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        'status': 'success',
        'count': len(results),
        'results': results,
        'timestamp': datetime.utcnow().isoformat()
    }

@app.get("/api/v1/prediction/health")
async def health_check():
    """健康检查"""
    return {
        'status': 'healthy',
        'model_loaded': inference_service.model is not None,
        'redis_connected': inference_service.redis_client.ping(),
        'timestamp': datetime.utcnow().isoformat()
    }

@app.get("/api/v1/prediction/model/info")
async def model_info():
    """模型信息"""
    return {
        'model_version': inference_service.config['model_version'],
        'model_path': inference_service.config['model_path'],
        'feature_count': len(inference_service.config['feature_list']),
        'device': str(inference_service.device),
        'timestamp': datetime.utcnow().isoformat()
    }
```

---

## 8. 验收标准

- [x] API 端点设计完整 (单次/批量/健康检查)
- [x] 请求/响应格式明确定义
- [x] 批量推理优化方案 (动态批处理)
- [x] 缓存策略设计 (Redis + LRU)
- [x] 性能监控指标定义 (Prometheus + Grafana)
- [x] 部署架构设计 (Docker + K8s)
- [x] 伪代码和示例完整

---

**文档状态:** ✅ 已完成  
**下一步:** 开始 CODE-DL-008 (推理服务实现)
