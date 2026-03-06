# CODE-API-001: 完善后端 API 端点

**优先级:** 🔥 **P0 (最高)**  
**创建日期:** 2026-03-07 01:46  
**负责人:** qclaw-coder  
**依赖:** 无  
**状态:** ⏳ 待开始

---

## 📋 任务描述

完善后端 API 端点，解决 E2E 测试和前端调用返回 404 的问题。

---

## 🎯 需要实现的 API 端点

### 1. 市场数据 API

**端点:** `GET /api/market/indices`

**功能:** 返回大盘指标数据

**响应示例:**
```json
{
  "timestamp": "2026-03-07T01:46:00+08:00",
  "indices": {
    "shanghai": {
      "name": "上证指数",
      "value": 3400.50,
      "change": 1.25,
      "changePercent": 0.37
    },
    "shenzhen": {
      "name": "深证成指",
      "value": 11200.80,
      "change": -0.85,
      "changePercent": -0.08
    },
    "chinext": {
      "name": "创业板指",
      "value": 2350.20,
      "change": 2.10,
      "changePercent": 0.09
    }
  }
}
```

**实现文件:** `server/api/market.py`

---

### 2. AI 建议 API

**端点:** `GET /api/advice`

**功能:** 返回 AI 投资建议

**响应示例:**
```json
{
  "timestamp": "2026-03-07T01:46:00+08:00",
  "advice": {
    "type": "买入",
    "confidence": 0.85,
    "reasons": [
      "技术指标显示超卖",
      "资金流入明显",
      "市场情绪乐观"
    ],
    "risks": [
      "短期波动风险",
      "政策不确定性"
    ],
    "targets": [
      {"symbol": "600519", "name": "贵州茅台", "weight": 0.3},
      {"symbol": "300750", "name": "宁德时代", "weight": 0.2}
    ]
  }
}
```

**实现文件:** `server/api/advice.py`

---

### 3. 健康检查 API

**端点:** `GET /api/health`

**功能:** 服务健康检查

**响应示例:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-07T01:46:00+08:00",
  "services": {
    "api": "ok",
    "database": "ok",
    "redis": "ok"
  }
}
```

**实现文件:** `server/api/health.py`

---

### 4. 深度学习模型 API

**端点:** `GET /api/v1/dl/models`

**功能:** 返回可用模型列表

**响应示例:**
```json
{
  "models": [
    {
      "id": "lstm_real_600519",
      "name": "LSTM 贵州茅台预测",
      "type": "LSTM",
      "status": "active",
      "accuracy": 0.85,
      "last_trained": "2026-03-06T22:00:00+08:00"
    }
  ]
}
```

**实现文件:** `server/api/dl/models.py`

---

### 5. 模型预测 API

**端点:** `POST /api/v1/dl/predict`

**功能:** 执行模型预测

**请求:**
```json
{
  "model_id": "lstm_real_600519",
  "symbol": "600519",
  "days": 5
}
```

**响应:**
```json
{
  "prediction": [
    {"day": 1, "price": 1450.00},
    {"day": 2, "price": 1465.50},
    {"day": 3, "price": 1478.20},
    {"day": 4, "price": 1490.80},
    {"day": 5, "price": 1505.30}
  ],
  "confidence": 0.82,
  "timestamp": "2026-03-07T01:46:00+08:00"
}
```

**实现文件:** `server/api/dl/predict.py`

---

## 📝 实施步骤

### 步骤 1: 创建 API 路由 (30 分钟)

```python
# server/api/market.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/indices")
async def get_market_indices():
    """获取大盘指标"""
    return {
        "timestamp": datetime.now().isoformat(),
        "indices": {
            "shanghai": {"name": "上证指数", "value": 3400.50, "change": 1.25, "changePercent": 0.37},
            "shenzhen": {"name": "深证成指", "value": 11200.80, "change": -0.85, "changePercent": -0.08},
            "chinext": {"name": "创业板指", "value": 2350.20, "change": 2.10, "changePercent": 0.09}
        }
    }
```

### 步骤 2: 注册路由 (10 分钟)

```python
# server/api/__init__.py
from .market import router as market_router
from .advice import router as advice_router
from .health import router as health_router
from .dl.models import router as dl_models_router
from .dl.predict import router as dl_predict_router

__all__ = ['market_router', 'advice_router', 'health_router', 'dl_models_router', 'dl_predict_router']
```

### 步骤 3: 更新主应用 (10 分钟)

```python
# server/main.py
from api import market_router, advice_router, health_router, dl_models_router, dl_predict_router

app.include_router(market_router, prefix="/api/market", tags=["market"])
app.include_router(advice_router, prefix="/api/advice", tags=["advice"])
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(dl_models_router, prefix="/api/v1/dl", tags=["deep-learning"])
app.include_router(dl_predict_router, prefix="/api/v1/dl", tags=["deep-learning"])
```

### 步骤 4: 测试验证 (30 分钟)

```bash
# 测试 API 端点
curl http://localhost:8000/api/market/indices
curl http://localhost:8000/api/advice
curl http://localhost:8000/api/health
curl http://localhost:8000/api/v1/dl/models
```

---

## ✅ 验收标准

- [ ] 所有 5 个 API 端点正常工作
- [ ] 返回正确的 JSON 格式
- [ ] 响应时间 < 100ms
- [ ] E2E 测试通过率提升至 80%+
- [ ] 前端页面正常显示数据

---

## 📦 交付物

- `server/api/market.py` - 市场数据 API
- `server/api/advice.py` - AI 建议 API (如未实现)
- `server/api/health.py` - 健康检查 API
- `server/api/dl/models.py` - 模型列表 API
- `server/api/dl/predict.py` - 模型预测 API
- `server/api/__init__.py` - 路由注册更新
- `server/main.py` - 主应用更新

---

**预计完成时间:** 1.5 小时  
**下一步:** 执行 E2E 测试验证
