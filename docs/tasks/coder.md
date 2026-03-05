# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-06 00:45  
**Cron:** 每 30 分钟自动检查 (事件驱动模式)

---

## 🚨 新任务 - 请处理

### CODE-008: 修复 E2E 测试发现的 UI/交互 bug
**优先级:** 高  
**依赖:** TEST-E2E-001 执行完成后产生的测试报告  
**交付物:** 修复所有 E2E 测试发现的 UI/交互 bug
**状态:** ✅ 已完成

**问题描述:**
根据 E2E 测试报告，修复前端界面和交互问题。Tester 负责启动前端服务并执行 E2E 测试，Coder 根据测试报告修复 bug。

**需要完成:**
1. ✅ 等待 Tester 执行 TEST-E2E-001 并生成测试报告
2. ✅ 分析 E2E 测试失败原因 (16 个 CSS 类名不匹配)
3. ✅ 修复 UI 显示问题 (Dashboard.vue, MarketCard.vue, AIAdvice.vue, NewsList.vue, IndicatorChart.vue)
4. ✅ 确保所有 E2E 测试选择器能正确匹配

**修复详情:**
- Dashboard.vue: 添加 `.market-indices` 容器和 `.last-updated` 时间显示
- MarketCard.vue: 添加动态索引类名 (`.index-shanghai`, `.index-shenzhen`, `.index-chinext`)
- AIAdvice.vue: 添加 `.ai-advice`, `.advice-type`, `.confidence-level` 类名
- NewsList.vue: 添加 `.pagination` 类名
- IndicatorChart.vue: 添加 `.technical-indicators`, `.macd-chart`, `.kdj-chart`, `.rsi-chart`, `.chart-rendered` 类名

**提交 ID:** `f07dbea`

---

## ✅ 已完成

| 任务 ID | 任务名称 | 状态 | 提交 ID |
|---------|---------|------|---------|
| CODE-001 | 项目初始化 | ✅ | `8d4c923` |
| CODE-002 | 大盘指标模块 | ✅ | `12a92ca` |
| CODE-003 | 量化指标模块 | ✅ | - |
| CODE-004 | AI 建议模块 | ✅ | `2282ffd` |
| CODE-005 | 新闻资讯模块 | ✅ | `2282ffd` |
| CODE-006 | 后端 API 开发 | ✅ | `0a17c35` |
| CODE-007 | 单元测试修复 | ✅ | `9f893b0` |
| CODE-008 | UI Bug 修复 - CSS 类名不匹配 | ✅ | `f07dbea` |

---

## 📦 交付成果

### 前端 (webui/)
- React 18 + TypeScript + Vite 项目框架
- MarketCard 组件 - 大盘 K 线图 (MA5/MA10/MA20)
- IndicatorChart 组件 - 技术指标 (MACD/KDJ/RSI)
- AIAdvice 组件 - AI 投资建议
- NewsList 组件 - 财经新闻列表
- Dashboard 页面 - 大盘指数展示
- 单元测试套件 - 21 个测试用例全部通过 ✅

### 后端 (server/)
- FastAPI 后端服务
- AKShare 数据集成
- Redis 缓存
- RESTful API 接口

---

**说明:** 本文件仅供 qclaw-coder 读取，避免上下文污染。
