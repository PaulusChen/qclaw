# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-06 00:38  
**Cron:** 每 30 分钟自动检查 (事件驱动模式)

---

## 🚨 新任务 - 请处理

### CODE-008: 修复 E2E 测试发现的 UI/交互 bug
**优先级:** 高  
**依赖:** TEST-E2E-001 执行完成后产生的测试报告  
**交付物:** 修复所有 E2E 测试发现的 UI/交互 bug
**状态:** 🔄 进行中

**问题描述:**
根据 E2E 测试报告，修复前端界面和交互问题。Tester 负责启动前端服务并执行 E2E 测试，Coder 根据测试报告修复 bug。

**需要完成:**
1. ✅ 等待 Tester 执行 TEST-E2E-001 并生成测试报告
2. 🔄 分析 E2E 测试失败原因
3. ⏳ 修复 UI 显示问题
4. ⏳ 修复交互逻辑 bug
5. ⏳ 确保所有 E2E 测试通过

**详细 Bug 列表:**

| # | 测试用例 | CSS 选择器 | 问题 | 状态 |
|---|---------|-----------|------|------|
| 1 | test_homepage_loads_successfully | h1 | 期望"QCLaw", 实际"大盘指数" | ⏳ |
| 2 | test_homepage_shows_market_indices | .market-indices | 元素不存在 | ⏳ |
| 3 | test_homepage_auto_refresh | .last-updated | 元素不存在 | ⏳ |
| 4 | test_view_ai_advice | .ai-advice | 元素不存在 | ⏳ |
| 5 | test_advice_shows_reasons | .advice-reasons | 元素不存在 | ⏳ |
| 6 | test_advice_shows_risks | .advice-risks | 元素不存在 | ⏳ |
| 7 | test_news_list_loads | .news-list | 元素不存在 | ⏳ |
| 8 | test_news_pagination | .pagination | 元素不存在 | ⏳ |
| 9 | test_news_detail_page | .news-detail | 元素不存在 | ⏳ |
| 10 | test_technical_indicators_load | .technical-indicators | 元素不存在 | ⏳ |
| 11 | test_indicators_chart_rendering | .indicators-chart | 元素不存在 | ⏳ |
| 12 | test_404_page | .error-page | 元素不存在 | ⏳ |
| 13 | test_api_error_handling | .error-message | 元素不存在 | ⏳ |
| 14 | test_mobile_viewport | .mobile-nav | 元素不存在 | ⏳ |
| 15 | test_tablet_viewport | .tablet-nav | 元素不存在 | ⏳ |
| 16 | test_desktop_viewport | .desktop-nav | 元素不存在 | ⏳ |

**修复建议:**
1. 检查 webui/src/views/Dashboard.vue 中的 class 命名
2. 确保所有组件使用正确的 CSS 类名
3. 添加缺失的 UI 组件或更新测试选择器
4. 修复 h1 标题文本或更新测试期望值

**测试验证:**
```bash
cd webui
npm run dev
# 访问 http://localhost:3000 确认页面加载
# 等待 Tester 执行 E2E 测试并查看报告
```

---

### CODE-009: 补充前端组件单元测试
**优先级:** 中  
**依赖:** CODE-008  
**交付物:** webui/src/components/ 下的组件测试文件
**状态:** ⏳ 待开始

**需要完成:**
1. 为 MarketCard 组件添加完整单元测试
2. 为 IndicatorChart 组件添加完整单元测试
3. 为 AIAdvice 组件添加完整单元测试
4. 为 NewsList 组件添加完整单元测试
5. 确保测试覆盖率 >80%

**参考:** 现有测试文件 `webui/src/store/slices/*.test.ts`

---

## 🎉 已完成任务

所有 CODE-001 到 CODE-007 任务已完成并归档至 `completed.md`

**最近检查:** 2026-03-06 00:38 - CODE-008 进行中，CODE-009 待开始

---

## 🔔 新通知 (2026-03-06 00:38)

**来自:** PM (事件驱动工作流)  
**事件:** E2E 测试完成，发现 16 个 UI bug  
**行动:** 立即修复 CODE-008  
**验证:** 修复后通知 Tester 重新运行 E2E 测试  

**事件流:**
1. ✅ Tester 执行 TEST-E2E-001
2. ✅ 发现 16 个 CSS 选择器不匹配问题
3. ✅ 创建 CODE-008 任务
4. 🔄 Coder 分析并修复 bug
5. ⏳ Coder 提交修复
6. ⏳ Tester 重新验证

---

**说明:** 本文件仅供 qclaw-coder 读取，避免上下文污染。
