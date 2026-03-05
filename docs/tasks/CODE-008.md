# CODE-008: UI Bug 修复 - CSS 类名不匹配

**创建日期:** 2026-03-06 00:41  
**优先级:** 高  
**执行角色:** qclaw-coder  
**依赖:** TEST-E2E-001 (E2E 测试需要这些类名来验证 UI)

---

## 🐛 问题描述

E2E 测试用例中使用的 CSS 类名选择器与实际 Vue 组件中的类名不匹配，导致 18 项 E2E 测试全部失败。

**根本原因:** 开发时未按照测试用例期望的类名规范来编写 CSS 类。

---

## 📋 Bug 清单 (16 个 UI Bug)

| # | 测试用例期望的类名 | 当前实际类名 | 文件位置 | 状态 |
|---|-------------------|-------------|---------|------|
| 1 | `.market-indices` | ✅ 已添加 | `Dashboard.vue` | ✅ 完成 |
| 2 | `.index-shanghai` | ✅ 已添加 | `MarketCard.vue` | ✅ 完成 |
| 3 | `.index-shenzhen` | ✅ 已添加 | `MarketCard.vue` | ✅ 完成 |
| 4 | `.index-chinext` | ✅ 已添加 | `MarketCard.vue` | ✅ 完成 |
| 5 | `.last-updated` | ✅ 已添加 | `Dashboard.vue` | ✅ 完成 |
| 6 | `.ai-advice` | ✅ 已修改 | `AIAdvice.vue` | ✅ 完成 |
| 7 | `.advice-type` | ✅ 已添加 | `AIAdvice.vue` | ✅ 完成 |
| 8 | `.confidence-level` | ✅ 已添加 | `AIAdvice.vue` | ✅ 完成 |
| 9 | `.advice-reasons` | ✅ 已有 | `AIAdvice.vue` | ✅ 通过 |
| 10 | `.advice-risks` | ✅ 已有 | `AIAdvice.vue` | ✅ 通过 |
| 11 | `.news-list` | ✅ 已有 | `NewsList.vue` | ✅ 通过 |
| 12 | `.news-item` | ✅ 已有 | `NewsList.vue` | ✅ 通过 |
| 13 | `.pagination` | ✅ 已添加 | `NewsList.vue` | ✅ 完成 |
| 14 | `.news-detail` | ⚠️ 需要前端路由支持 | (需要标记) | ⏳ 待处理 |
| 15 | `.technical-indicators` | ✅ 已添加 | `IndicatorChart.vue` | ✅ 完成 |
| 16 | `.macd-chart`, `.kdj-chart`, `.rsi-chart`, `.chart-rendered` | ✅ 已添加 | `IndicatorChart.vue` | ✅ 完成 |

---

## 🔧 修复方案

### 1. Dashboard.vue 修复

**添加类名:**
- `.market-indices` → 包裹市场卡片的容器
- `.index-shanghai`, `.index-shenzhen`, `.index-chinext` → 为每个 MarketCard 添加对应的索引类
- `.last-updated` → 更新时间显示

### 2. MarketCard.vue 修复

**添加动态类名:**
- 根据 `indexKey` prop 动态添加 `.index-shanghai` / `.index-shenzhen` / `.index-chinext`

### 3. AIAdvice.vue 修复

**添加/修改类名:**
- `.ai-advice` → 添加为根容器别名
- `.advice-type` → 建议类型显示区域
- `.confidence-level` → 添加为 `.confidence-bar` 的别名

### 4. NewsList.vue 修复

**添加类名:**
- `.pagination` → 添加给加载更多按钮区域
- `.news-detail` → 标记新闻详情视图 (当前是打开新窗口)

### 5. IndicatorChart.vue 修复

**添加类名:**
- `.technical-indicators` → 根容器
- `.macd-chart`, `.kdj-chart`, `.rsi-chart` → 根据选择的指标动态添加
- `.chart-rendered` → 图表渲染完成后添加

---

## ✅ 验收标准

- [ ] 所有 16 个 CSS 类名都已添加到对应组件
- [ ] E2E 测试能够正确选择到目标元素
- [ ] 不影响现有样式和功能
- [ ] 保持响应式设计
- [ ] 通过 `npx playwright test` 验证

---

## 📝 实施步骤

1. **修改 Dashboard.vue** - 添加市场指数容器类名和索引特定类名
2. **修改 MarketCard.vue** - 添加动态索引类名
3. **修改 AIAdvice.vue** - 添加缺失的类名
4. **修改 NewsList.vue** - 添加分页类名
5. **修改 IndicatorChart.vue** - 添加技术指标相关类名
6. **运行 E2E 测试验证** - 确认修复效果

---

## 🎯 测试命令

```bash
# 启动前端服务
cd ~/qclaw/webui
npm run dev

# 在另一个终端运行 E2E 测试
cd ~/qclaw/tests/e2e
npx playwright test --ui
```

---

**预计完成时间:** 30 分钟  
**实际完成时间:** 2026-03-06 00:50  
**提交 ID:** `764b7c39` (CODE-008), `4666742b` (状态更新)

---

## ✅ 完成总结

**修复的 CSS 类名 (15/16 完成):**

1. ✅ Dashboard.vue - `.market-indices`, `.last-updated`
2. ✅ MarketCard.vue - `.index-shanghai`, `.index-shenzhen`, `.index-chinext`
3. ✅ AIAdvice.vue - `.ai-advice`, `.advice-type`, `.confidence-level`
4. ✅ NewsList.vue - `.pagination`
5. ✅ IndicatorChart.vue - `.technical-indicators`, `.macd-chart`, `.kdj-chart`, `.rsi-chart`, `.chart-rendered`

**遗留问题:**
- `.news-detail` - 需要前端路由支持 (当前新闻点击打开新窗口，无详情页路由)

**下一步:**
- 通知 qclaw-tester 启动前端服务并重新运行 E2E 测试
- 验证 18 个失败的 E2E 测试用例是否通过
