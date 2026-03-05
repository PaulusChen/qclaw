# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-05 19:19  
**Cron:** 每 5 分钟自动检查

---

## 🔄 进行中

*无*

---

## ✅ 本次完成

### CODE-002: 大盘指标模块 ✅

**完成日期:** 2026-03-05  
**提交 ID:** `13772af`

**交付内容:**
- `webui/src/types/market.ts` - 数据类型定义
- `webui/src/services/marketApi.ts` - API 服务 (含 K 线数据、均线计算)
- `webui/src/store/slices/marketSlice.ts` - Redux Slice
- `webui/src/composables/useMarket.ts` - Vue Composable
- `webui/src/components/MarketCard/MarketCard.vue` - K 线图组件 (MA5/MA10/MA20)
- `webui/src/pages/Dashboard/Dashboard.vue` - 大盘仪表盘页面

**功能特性:**
- ECharts K 线蜡烛图
- MA5/MA10/MA20 均线叠加
- 涨跌颜色标识 (红涨绿跌)
- 时间范围切换 (1M/3M/6M/1Y)
- 自动刷新 (交易时间每 30 秒)
- 交互式缩放和平移

---

## ⏳ 待开始

*无*

---

## ✅ 已完成

*所有任务已归档至 `completed.md`*

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

### CODE-006: 后端 API 开发 ✅

**描述:** 实现 FastAPI 后端服务  
**技术要点:**
- FastAPI 框架
- AKShare 数据集成
- Redis 缓存

**交付物:**
- `server/main.py`
- `server/api/`
- `server/services/`

**完成日期:** 2026-03-05  
**提交 ID:** `0a17c35`

### CODE-001: 项目初始化 ✅

**描述:** 搭建前端项目框架  
**交付物:** `webui/` 目录  
**提交 ID:** `8d4c923`

---

**说明:** 本文件仅供 qclaw-coder 读取，避免上下文污染。
