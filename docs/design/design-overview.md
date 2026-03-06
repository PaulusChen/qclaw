# qclaw WebUI 设计总览

**文档版本:** v1.0  
**创建日期:** 2026-03-06  
**合并自:** ui-design.md, technical-design.md, design_review_report.md, deep_learning_research.md  
**状态:** ✅ 已合并

---

## 📋 目录

1. [UI 设计稿](#1-ui-设计稿)
2. [技术方案设计](#2-技术方案设计)
3. [设计复查报告](#3-设计复查报告)
4. [深度学习技术调研](#4-深度学习技术调研)

---

## 1. UI 设计稿

### 1.1 整体布局

#### 响应式栅格系统

```
桌面端 (≥1200px):     平板端 (768-1199px):   移动端 (<768px):
┌─────────────────┐   ┌───────────────┐   ┌─────────┐
│   Header        │   │   Header      │   │ Header  │
├─────────────────┤   ├───────────────┤   ├─────────┤
│ [Col1] [Col2]   │   │ [Col1]        │   │ [Col1]  │
│ [Col3] [Col4]   │   │ [Col2]        │   │ [Col2]  │
│                 │   │ [Col3]        │   │ [Col3]  │
│                 │   │ [Col4]        │   │ [Col4]  │
└─────────────────┘   └───────────────┘   └─────────┘
```

#### 配色方案 (金融类规范)

| 用途 | 颜色 | Hex | 使用场景 |
|------|------|-----|----------|
| 主色 | 深蓝 | `#1E3A8A` | Header、主按钮、品牌元素 |
| 辅助色 | 青蓝 | `#3B82F6` | 次级按钮、链接、高亮 |
| 上涨 | 红色 | `#DC2626` | 涨幅、正向指标 |
| 下跌 | 绿色 | `#16A34A` | 跌幅、负向指标 |
| 背景 | 浅灰 | `#F3F4F6` | 页面背景 |
| 卡片 | 纯白 | `#FFFFFF` | 内容卡片 |
| 文字 | 深灰 | `#1F2937` | 主要文字 |
| 次要文字 | 中灰 | `#6B7280` | 辅助说明 |

### 1.2 四大核心模块

#### 模块 1: 大盘指标 (Market Overview)
- 位置：首页顶部，全宽卡片
- 内容：四大指数、K 线图、成交量、涨跌统计
- 交互：点击展开、图表缩放、周期切换

#### 模块 2: 量化指标 (Quantitative Indicators)
- 位置：首页左侧，50% 宽度
- 内容：趋势/动量/成交量指标
- 交互：策略切换、指标详情、信号提示

#### 模块 3: AI 建议 (AI Recommendations)
- 位置：首页右侧，50% 宽度
- 内容：核心观点、推荐标的、风险提示
- 交互：置信度展示、详细分析、策略回测

#### 模块 4: 新闻资讯 (News Feed)
- 位置：首页底部，全宽卡片
- 内容：重要性分级新闻
- 交互：来源筛选、重要性过滤、自动更新

### 1.3 组件库规范

```css
.card {
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 16px;
  margin: 12px;
}

.btn-primary {
  background: #1E3A8A;
  color: #FFFFFF;
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
}
```

---

## 2. 技术方案设计

### 2.1 技术架构概览

```
前端展示层 (React 18 + TypeScript)
       │
       ▼
状态管理层 (Zustand)
       │
       ▼
API 服务层 (Axios + React Query)
       │
       ▼
后端服务层 (FastAPI + qlib)
```

### 2.2 技术栈选型

#### 前端技术栈

| 类别 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| 框架 | React | 18.x | 生态成熟、组件丰富 |
| 语言 | TypeScript | 5.x | 类型安全、IDE 支持好 |
| 构建工具 | Vite | 5.x | 极速启动、热更新 |
| 状态管理 | Zustand | 4.x | 轻量、API 简洁 |
| 数据请求 | React Query | 5.x | 缓存、重试、乐观更新 |
| UI 组件库 | Ant Design | 5.x | 金融类常用、组件齐全 |
| 图表库 | ECharts | 5.x | K 线图支持好 |
| 样式方案 | Tailwind CSS | 3.x | 原子化 CSS、开发效率高 |

#### 后端技术栈

| 类别 | 技术 | 版本 | 选型理由 |
|------|------|------|----------|
| 框架 | FastAPI | 0.100+ | 高性能、自动文档 |
| 量化引擎 | qlib | 最新 | 微软开源、A 股支持好 |
| 缓存 | Redis | 7.x | 高频数据缓存 |
| 数据库 | PostgreSQL | 15.x | 时序数据支持好 |

### 2.3 项目结构

```
qclaw-webui/
├── src/
│   ├── components/          # 通用组件
│   ├── modules/             # 业务模块 (market/indicators/ai/news)
│   ├── stores/              # 状态管理
│   ├── services/            # API 服务
│   ├── hooks/               # 自定义 Hooks
│   ├── types/               # TypeScript 类型
│   └── utils/               # 工具函数
├── tests/                   # 测试文件
└── config/                  # 配置文件
```

### 2.4 API 接口设计

```typescript
// 大盘指标 API
export const marketApi = {
  getIndices: () => apiClient.get<MarketIndex[]>('/api/v1/market/indices'),
  getKlineData: (indexCode, period) => apiClient.get(`/api/v1/market/kline/${indexCode}`, { params: { period } }),
  getMarketStats: () => apiClient.get<MarketStats>('/api/v1/market/stats'),
};

// 量化指标 API
export const indicatorApi = {
  getIndicators: (category) => apiClient.get('/api/v1/indicators', { params: { category } }),
  calculateIndicator: (symbol, indicator, params) => apiClient.post('/api/v1/indicators/calculate', { symbol, indicator, params }),
};

// AI 建议 API
export const aiApi = {
  getAdvice: () => apiClient.get<AIAdvice>('/api/v1/ai/advice'),
  getRecommendations: () => apiClient.get<StockRecommendation[]>('/api/v1/ai/recommendations'),
};
```

### 2.5 性能优化

- **代码分割:** 路由级 lazy loading + Suspense
- **图表懒加载:** ECharts 按需加载
- **数据缓存:** React Query staleTime=10s, cacheTime=5m
- **自动刷新:** 30 秒轮询更新

---

## 3. 设计复查报告

### 3.1 执行摘要

**复查日期:** 2026-03-06  
**复查结论:** 整体设计合理，建议按修订意见改进

**核心发现:**
- ✅ 模型架构选型合理 (LSTM + Transformer 双模型)
- ⚠️ 特征工程需要补充更多特征类型
- ⚠️ GPU 训练优化需要更详细的配置
- ⚠️ 任务列表需要补充数据验证和模型监控任务

### 3.2 模型架构验证

#### 合理的设计

| 设计项 | 当前方案 | 评估 |
|--------|---------|------|
| 双模型架构 | LSTM (Phase 1) + Transformer (Phase 2) | ✅ 合理 |
| LSTM 配置 | hidden_size=128, num_layers=2, dropout=0.2 | ✅ 标准配置 |
| Transformer 配置 | d_model=128, nhead=8, num_layers=4 | ✅ 合理 |
| 序列长度 | seq_len=60 | ✅ 合理 (约 3 个月交易日) |

#### 建议改进

| 问题 | 当前设计 | 建议 | 优先级 |
|------|---------|------|--------|
| 模型输出头 | 单一输出 | 多任务学习：direction + return + confidence | P1 |
| 注意力机制 | 标准 Transformer | 添加 Temporal Attention | P1 |
| 模型对比基线 | 无 | 添加 LR/RF/XGBoost 基线 | P1 |
| 集成策略 | 未明确 | 设计 ensemble 策略 | P2 |

### 3.3 特征工程验证

#### 现有特征 (25 个)
- 基础价格：5 个
- 价格衍生：4 个
- 移动平均：4 个
- MACD/RSI/KDJ/CCI/ROC/ADX/SAR: 12 个

#### 建议补充的特征

| 特征类别 | 具体特征 | 优先级 |
|---------|---------|--------|
| 波动率指标 | atr14, volatility_20 | P0 |
| 成交量指标 | volume_ratio, turnover_rate | P0 |
| 布林带 | boll_upper/middle/lower, boll_width | P1 |
| OBV | On-Balance Volume | P1 |
| 价格位置 | close_vs_ma20, close_vs_ma60 | P1 |
| 滞后特征 | close_t-1, close_t-5, return_lag_* | P0 |

**建议特征总数:** 25 → 35-40 个

### 3.4 GPU 配置验证

#### 配置合理

| 配置项 | 当前设计 | 评估 |
|--------|---------|------|
| GPU 型号 | RTX 2070 8GB | ✅ 足够 |
| CUDA 版本 | 12.1 | ✅ 最新稳定版 |
| cuDNN 版本 | 8.9+ | ✅ 匹配 |
| PyTorch 版本 | 2.0+ | ✅ 支持 |

#### 建议补充

| 项目 | 建议 | 优先级 |
|------|------|--------|
| 混合精度训练 | AMP (Automatic Mixed Precision) | P0 |
| 梯度累积 | gradient_accumulation_steps | P1 |
| 数据加载优化 | num_workers, pin_memory | P0 |
| GPU 监控 | 显存使用监控 | P1 |

### 3.5 任务拆分更新

**新增开发任务:**
- CODE-DL-009: 添加基线模型对比 (P1)
- CODE-DL-010: 实现多任务学习输出头 (P1)
- CODE-DL-011: 实现模型集成策略 (P2)
- CODE-DL-012: 添加 GPU 训练优化 (P0)
- CODE-DL-013: 实现特征重要性分析 (P2)
- CODE-DL-014: 添加数据质量验证模块 (P0)
- CODE-DL-015: 实现模型性能监控和告警 (P1)

**新增测试任务:**
- TEST-DL-007: 数据质量测试 (P0)
- TEST-DL-008: 基线模型对比测试 (P1)
- TEST-DL-009: 模型稳定性测试 (P1)
- TEST-DL-010: 特征消融实验 (P2)
- TEST-DL-011: GPU 加速效果验证 (P1)

### 3.6 设计评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 模型架构 | ⭐⭐⭐⭐⭐ | 双模型设计合理 |
| 特征工程 | ⭐⭐⭐⭐ | 基础完整，建议补充 |
| 技术选型 | ⭐⭐⭐⭐⭐ | PyTorch + FastAPI 合理 |
| GPU 配置 | ⭐⭐⭐⭐ | 硬件足够，需补充优化 |
| 任务拆分 | ⭐⭐⭐⭐ | 清晰合理 |
| 测试覆盖 | ⭐⭐⭐⭐ | 核心测试完整 |
| **总体** | ⭐⭐⭐⭐ | **设计合理，建议改进** |

---

## 4. 深度学习技术调研

### 4.1 主流技术路线

| 技术路线 | 适用场景 | 优势 | 劣势 |
|---------|---------|------|------|
| LSTM/GRU | 中短期序列预测 | 捕捉长期依赖，训练稳定 | 序列长时梯度消失 |
| Transformer | 多因子/长序列 | 并行计算，注意力机制强大 | 需要大量数据 |
| Temporal Fusion Transformer | 多变量时间序列 | 可解释性强 | 实现复杂 |
| N-BEATS | 纯时间序列预测 | 无需特征工程 | 可解释性较弱 |

### 4.2 LSTM vs Transformer 对比

| 维度 | LSTM | Transformer | 推荐 |
|------|------|-------------|------|
| 序列长度 | 适合中等长度 (50-200) | 适合长序列 (200+) | 根据数据选择 |
| 训练速度 | 较慢 (序列依赖) | 较快 (并行计算) | Transformer |
| 数据需求 | 中等 | 较大 | LSTM (小数据) |
| 捕捉依赖 | 短期 + 中期 | 长距离 | Transformer |
| 实现复杂度 | 低 | 中 | LSTM |
| GPU 内存 | 较低 | 较高 | LSTM |

### 4.3 开源项目参考

**Microsoft Qlib (强烈推荐):**
- GitHub: https://github.com/microsoft/qlib
- 包含 LSTM、Transformer、TabNet 等模型
- 提供完整的数据处理、训练、回测流程

### 4.4 GPU 训练优化

| 优化技术 | 说明 | 预期收益 |
|---------|------|---------|
| 混合精度训练 (AMP) | FP16+FP32 混合精度 | 内存 -50%, 速度 +30% |
| 梯度累积 | 多批次累积后更新 | 等效更大 batch size |
| 梯度裁剪 | 防止梯度爆炸 | 训练稳定性 |
| 学习率调度 | ReduceLROnPlateau/Cosine | 收敛更好 |
| 数据预取 | DataLoader 多进程 | 减少 GPU 等待 |

### 4.5 模型评估指标

| 指标 | 公式 | 目标值 |
|------|------|--------|
| IC (Information Coefficient) | corr(pred, return) | > 0.03 |
| ICIR | IC / std(IC) | > 0.5 |
| 年化收益 | (1 + daily_return)^252 - 1 | > 15% |
| 夏普比率 | (return - risk_free) / std(return) | > 1.0 |
| 最大回撤 | max(peak - trough) / peak | < 20% |
| 胜率 | win_days / total_days | > 55% |

### 4.6 技术实施建议

**推荐技术栈:**
```yaml
深度学习框架：PyTorch 2.0+
量化平台：QLib (Microsoft)
数据处理：Pandas + NumPy
可视化：Matplotlib + Plotly
实验管理：MLflow / W&B
部署：ONNX Runtime + FastAPI
```

**开发路线图:**
```
Phase 1 (2 周): Baseline 建立
├── 数据预处理 pipeline
├── LSTM baseline 模型
├── 基础评估指标
└── 简单回测框架

Phase 2 (3 周): 模型优化
├── Transformer 实现
├── 超参数调优
├── 特征工程优化
└── 混合精度训练

Phase 3 (2 周): 系统集成
├── 与 WebUI 集成
├── 实时预测 pipeline
├── 模型监控告警
└── 文档完善
```

---

## 附录

### A. 文档合并说明

本文档合并自以下原始文件:
- `ui-design.md` - WebUI 界面设计稿
- `technical-design.md` - 技术方案设计
- `design_review_report.md` - 设计复查报告
- `deep_learning_research.md` - 深度学习技术调研

原始文件已添加归档标记并保留在 archive/ 目录。

### B. 相关文档

- `dl-architecture.md` - 深度学习架构详细设计
- `detailed-designs/` - 详细设计文档目录

---

**文档创建时间:** 2026-03-06  
**合并执行者:** qclaw-pm (subagent)  
**文档状态:** ✅ 已完成合并
