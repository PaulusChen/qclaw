# 事件驱动工作流

**创建时间:** 2026-03-06 00:30  
**目的:** 自动化角色间协作，减少 Cron 轮询，节省 60% token
**最后更新:** 2026-03-06 00:38

---

## 🔄 核心机制

### 1. Tester → Coder (Bug 报告)

**触发条件:** E2E 测试发现失败
**动作:**
1. 自动创建 CODE-* 任务到 `docs/tasks/coder.md`
2. 附加测试失败详情
3. 通知 Coder 立即处理

**模板:**
```markdown
### CODE-{AUTO}-{timestamp}: 修复 E2E 测试失败
**优先级:** 高
**来源:** TEST-E2E-001
**失败用例:** {test_name}
**错误信息:** {error_message}
**期望:** {expected}
**实际:** {actual}
```

### 2. Coder → Tester (修复完成)

**触发条件:** 代码提交包含 bug 修复
**动作:**
1. 更新 CODE-* 任务状态为"已完成"
2. 通知 Tester 重新验证
3. 附加 Git 提交 hash

### 3. PM 监控关键路径

**职责:**
- 监控任务流转是否阻塞
- 只在状态变化时生成报告
- 协调跨角色依赖

---

## 📊 当前事件流

### 事件 #1: E2E 测试失败 → Bug 创建 ✅

**时间:** 2026-03-06 00:30
**来源:** TEST-E2E-001
**发现:** 16 项 E2E 测试失败
**创建任务:** CODE-008
**状态:** ⏳ 等待 Coder 处理

**失败详情:**
| 测试用例 | 错误类型 | CSS 选择器 |
|---------|---------|-----------|
| test_homepage_loads_successfully | 文本不匹配 | h1 (期望"QCLaw", 实际"大盘指数") |
| test_homepage_shows_market_indices | 元素不存在 | .market-indices |
| test_homepage_auto_refresh | 元素不存在 | .last-updated |
| test_view_ai_advice | 元素不存在 | .ai-advice |
| test_advice_shows_reasons | 元素不存在 | .advice-reasons |
| test_advice_shows_risks | 元素不存在 | .advice-risks |
| test_news_list_loads | 元素不存在 | .news-list |
| test_news_pagination | 元素不存在 | .pagination |
| test_news_detail_page | 元素不存在 | .news-detail |
| test_technical_indicators_load | 元素不存在 | .technical-indicators |
| test_indicators_chart_rendering | 元素不存在 | .indicators-chart |
| test_404_page | 元素不存在 | .error-page |
| test_api_error_handling | 元素不存在 | .error-message |
| test_mobile_viewport | 元素不存在 | .mobile-nav |
| test_tablet_viewport | 元素不存在 | .tablet-nav |
| test_desktop_viewport | 元素不存在 | .desktop-nav |

### 事件 #2: Coder 修复 → Tester 验证 ⏳

**时间:** 等待中
**触发条件:** CODE-008 完成
**状态:** ⏳ 等待 Coder 提交修复
**下一步:** 
1. Coder 修复 16 个 UI/CSS 问题
2. 提交代码并更新 coder.md
3. 通知 Tester 重新运行 E2E 测试
4. Tester 验证修复并更新测试报告

---

## 🎯 优化效果

### Token 节省对比

| 角色 | 优化前 | 优化后 | 节省 |
|-----|-------|-------|------|
| PM | */5 (每 5 分钟) | */15 (每 15 分钟) | 66% |
| Designer | */5 (启用) | 禁用 (PM 触发) | 100% |
| Reviewer | */5 (启用) | 禁用 (PM 触发) | 100% |
| Coder | */5 (每 5 分钟) | */30 (每 30 分钟) | 83% |
| Tester | */5 (每 5 分钟) | 0 */60 (每小时) | 92% |

**总体节省:** ~60% token 消耗

### 响应时间对比

| 机制 | 平均响应时间 | 说明 |
|-----|------------|------|
| Cron 轮询 | 2.5 分钟 | 平均等待下一次 Cron |
| 事件驱动 | <10 秒 | 即时触发 |

---

## 📝 实施清单

- [x] 更新 PM cron: `*/5` → `*/15`
- [x] 禁用 Designer cron
- [x] 禁用 Reviewer cron
- [x] 更新 Coder cron: `*/5` → `*/30`
- [x] 更新 Tester cron: `*/5` → `0 * * * *` (每小时)
- [x] PM 报告改为状态变化时生成
- [x] 启动前端服务 (已运行在 localhost:3000)
- [x] 执行 E2E 测试
- [x] 创建 bug 任务通知 Coder (CODE-008)
- [ ] Coder 修复 bug (CODE-008)
- [ ] Tester 验证修复 (TEST-E2E-001)
- [ ] PM 生成最终报告

---

## 📈 当前状态摘要

| 任务 | 负责人 | 状态 | 阻塞 |
|------|--------|------|------|
| CODE-008 | qclaw-coder | 🔄 进行中 | 无 |
| TEST-E2E-001 | qclaw-tester | ⏳ 等待验证 | CODE-008 |
| TEST-SYS-001 | qclaw-tester | 🔄 85% | 无 |

**关键路径:** CODE-008 → TEST-E2E-001 完成 → 测试阶段完成

---

**下一步:** Coder 立即处理 CODE-008，修复所有 UI/CSS 选择器问题
