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
| 1 | `.market-indices` | (缺失) | `Dashboard.vue` | ⏳ 待修复 |
| 2 | `.index-shanghai` | (缺失) | `MarketCard.vue` | ⏳ 待修复 |
| 3 | `.index-shenzhen` | (缺失) | `MarketCard.vue` | ⏳ 待修复 |
| 4 | `.index-chinext` | (缺失) | `MarketCard.vue` | ⏳ 待修复 |
| 5 | `.last-updated` | `.update-time` | `MarketCard.vue` | ⏳ 待修复 |
| 6 | `.ai-advice` | `.ai-advice-container` | `AIAdvice.vue` | ⏳ 待修复 |
| 7 | `.advice-type` | (缺失) | `AIAdvice.vue` | ⏳ 待修复 |
| 8 | `.confidence-level` | `.confidence-bar` | `AIAdvice.vue` | ⏳ 待修复 |
| 9 | `.advice-reasons` | ✅ 已有 | `AIAdvice.vue` | ✅ 通过 |
| 10 | `.advice-risks` | ✅ 已有 | `AIAdvice.vue` | ✅ 通过 |
| 11 | `.news-list` | ✅ 已有 | `NewsList.vue` | ✅ 通过 |
| 12 | `.news-item` | ✅ 已有 | `NewsList.vue` | ✅ 通过 |
| 13 | `.pagination` | (缺失，只有 load-more) | `NewsList.vue` | ⏳ 待修复 |
| 14 | `.news-detail` | (缺失) | (需要标记) | ⏳ 待修复 |
| 15 | `.technical-indicators` | (缺失) | `IndicatorChart.vue` | ⏳ 待修复 |
| 16 | `.macd-chart`, `.kdj-chart`, `.rsi-chart`, `.chart-rendered` | (缺失) | `IndicatorChart.vue` | ⏳ 待修复 |

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
**实际完成时间:** -  
**提交 ID:** -
