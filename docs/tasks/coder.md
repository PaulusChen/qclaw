# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-05  
**Cron:** 每 5 分钟自动检查

---

## 🔄 进行中

*无*

---

## ⏳ 待开始

| 任务 ID | 任务名称 | 依赖 | 备注 |
|---------|---------|------|------|
| CODE-006 | 后端 API 开发 | CODE-001 | FastAPI |

---

## ✅ 已完成

| 任务 ID | 任务名称 | 完成日期 | 交付物 |
|---------|---------|----------|--------|
| CODE-005 | 新闻资讯模块 | 2026-03-05 | `webui/src/components/NewsList/`, `webui/src/services/newsApi.ts`, `webui/src/types/news.ts` |
| CODE-004 | AI 建议模块 | 2026-03-05 | `webui/src/components/AIAdvice/`, `webui/src/services/adviceApi.ts`, `webui/src/types/advice.ts` |
| CODE-003 | 量化指标模块 | 2026-03-05 | `webui/src/components/IndicatorChart/`, `webui/src/services/indicatorApi.ts` |
| CODE-002 | 大盘指标模块 | 2026-03-05 | `webui/src/components/MarketCard/`, `webui/src/pages/Dashboard/` |
| CODE-001 | 项目初始化 | 2026-03-05 | `webui/` |

---

## 📋 任务说明

### CODE-002: 大盘指标模块 🔄

**描述:** 实现上证指数、深证成指、创业板指的 K 线图展示  
**技术要点:**
- ECharts K 线图组件
- MA5/MA10/MA20 均线
- 实时数据更新

**交付物:**
- `webui/src/components/MarketCard/`
- `webui/src/pages/Dashboard/` (更新)

### CODE-003: 量化指标模块 ⏳

**描述:** 实现 MACD、KDJ、RSI 等技术指标图表  
**技术要点:**
- ECharts 多图表布局
- 指标数据计算
- 交互式图表

**交付物:**
- `webui/src/components/IndicatorChart/`

### CODE-004: AI 建议模块 ⏳

**描述:** 集成 OpenClaw API，展示 AI 投资建议  
**技术要点:**
- OpenClaw API 调用
- 建议展示组件
- 置信度显示

**交付物:**
- `webui/src/components/AIAdvice/`
- `webui/src/services/adviceApi.ts`

### CODE-005: 新闻资讯模块 ⏳

**描述:** 实现财经新闻、政策解读列表  
**技术要点:**
- 新闻列表组件
- 情感分析标签
- 分页加载

**交付物:**
- `webui/src/components/NewsList/`
- `webui/src/services/newsApi.ts`

### CODE-006: 后端 API 开发 ⏳

**描述:** 实现 FastAPI 后端服务  
**技术要点:**
- FastAPI 框架
- AKShare 数据集成
- Redis 缓存

**交付物:**
- `server/main.py`
- `server/api/`
- `server/services/`

### CODE-001: 项目初始化 ✅

**描述:** 搭建前端项目框架  
**交付物:** `webui/` 目录  
**提交 ID:** `8d4c923`

---

**说明:** 本文件仅供 qclaw-coder 读取，避免上下文污染。
