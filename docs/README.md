# qclaw 项目文档

**最后更新:** 2026-03-06  
**文档整理:** ✅ 已完成深度合并

---

## 📋 文档目录结构

```
docs/
├── design/                 # 设计文档
│   ├── design-overview.md  # WebUI 设计总览 ⭐
│   ├── dl-architecture.md  # 深度学习架构 ⭐
│   ├── check-history-summary.md  # 设计检查摘要
│   └── detailed-designs/   # 详细设计
├── review/                 # 审查文档
│   ├── design-reviews.md   # 设计审查汇总 ⭐
│   └── check-history-summary.md  # 审查检查摘要
├── reports/                # 报告文档
│   ├── progress-summary.md # 进度报告汇总 ⭐
│   ├── test-summary.md     # 测试报告汇总 ⭐
│   ├── bug-fixes.md        # Bug 修复汇总 ⭐
│   ├── performance-reports.md  # 性能测试汇总 ⭐
│   ├── e2e-verification.md # E2E 验证汇总 ⭐
│   └── ...                 # 其他有效文档
├── archive/                # 归档文档
│   ├── design/             # 已归档设计文档
│   ├── review/             # 已归档审查文档
│   └── reports/            # 已归档报告文档
├── requirements/           # 需求文档
├── research/               # 调研报告
├── standards/              # 标准规范
├── tasks/                  # 任务文档
└── logs/                   # 日志文件
```

---

## 📊 文档整理统计

### 合并前后对比

| 目录 | 合并前 | 合并后 | 减少 |
|------|--------|--------|------|
| design/ | 11 | 5 | -55% |
| review/ | 28 | 2 | -93% |
| reports/ | 127 | 11 | -91% |
| **总计** | **166** | **18** | **-89%** |

### 有效文档清单

**设计文档 (5 个):**
- design-overview.md
- dl-architecture.md
- check-history-summary.md
- detailed_design_data_preprocessing.md
- detailed_design_lstm.md

**审查文档 (2 个):**
- design-reviews.md
- check-history-summary.md

**报告文档 (11 个):**
- progress-summary.md
- test-summary.md
- bug-fixes.md
- performance-reports.md
- e2e-verification.md
- progress-history-summary.md (保留)
- test-history-summary.md (保留)
- daily-report-template.md (保留)
- operations_manual.md (保留)
- test-cases.md (保留)
- quick_reference.md (保留)

---

## 🔍 文档阅读指南

### 快速了解项目状态

**推荐阅读顺序:**
1. `reports/progress-summary.md` - 最新项目进度
2. `reports/test-summary.md` - 测试状态
3. `design/check-history-summary.md` - 设计阶段状态
4. `review/check-history-summary.md` - 审查阶段状态

### 按任务类型查阅

**开发任务:**
- 设计参考 → `design/design-overview.md`, `design/dl-architecture.md`
- 详细设计 → `design/detailed_design_*.md`

**测试任务:**
- 测试汇总 → `reports/test-summary.md`
- 测试用例 → `reports/test-cases.md`
- E2E 验证 → `reports/e2e-verification.md`

**项目管理:**
- 进度跟踪 → `reports/progress-summary.md`
- Bug 修复 → `reports/bug-fixes.md`
- 性能指标 → `reports/performance-reports.md`

---

## 📁 归档说明

所有已合并的原始文档已添加归档标记并移至 `archive/` 目录:
- `<!-- ARCHIVED: 已合并到 xxx.md -->`

归档文档保留用于历史参考，新工作请参考有效文档。

---

## 🔗 子目录索引

- [设计文档](design/README.md)
- [审查文档](review/README.md)
- [报告文档](reports/README.md)
- [归档文档](archive/)

---

**文档维护:** qclaw-pm  
**合并日期:** 2026-03-06  
**Git 提交:** 待提交
