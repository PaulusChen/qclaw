# QCLaw 文档中心

**最后更新:** 2026-03-06  
**文档总数:** 174+ 个 Markdown 文件

---

## 📚 文档导航

| 目录 | 说明 | 文件数 | 摘要文件 |
|------|------|--------|---------|
| [design/](./design/) | 设计文档 | 7+ | [check-history-summary.md](./design/check-history-summary.md) |
| [review/](./review/) | 审查报告 | 25+ | [check-history-summary.md](./review/check-history-summary.md) |
| [reports/](./reports/) | 进度/测试报告 | 126+ | [progress-history-summary.md](./reports/progress-history-summary.md), [test-history-summary.md](./reports/test-history-summary.md) |
| [standards/](./standards/) | 质量标准 | 7 | - |
| [tasks/](./tasks/) | 任务文档 | - | - |
| [requirements/](./requirements/) | 需求文档 | - | - |
| [research/](./research/) | 调研报告 | - | - |
| [archive/](./archive/) | 归档文档 | - | [design-evolution-summary.md](./archive/design-evolution-summary.md) |

---

## 📋 摘要文件清单

**快速了解项目状态，优先阅读摘要文件：**

| 摘要文件 | 压缩文件数 | 说明 |
|---------|-----------|------|
| [docs/design/check-history-summary.md](./design/check-history-summary.md) | 7 个 | 设计检查历史 |
| [docs/review/check-history-summary.md](./review/check-history-summary.md) | 25 个 | 审查检查历史 |
| [docs/reports/progress-history-summary.md](./reports/progress-history-summary.md) | 65 个 | 进度报告历史 |
| [docs/reports/test-history-summary.md](./reports/test-history-summary.md) | 21 个 | 测试报告历史 |
| [docs/archive/design-evolution-summary.md](./archive/design-evolution-summary.md) | 19+ 个 | 设计演进历程 |

**总计:** 约 174 个原始文件 → 5 个摘要文件

---

## 🎯 文档阅读指南

### 新 Agent 首次启动

1. **P0 - 摘要文件 (快速了解项目状态)**
   - 阅读上述 5 个摘要文件
   - 了解项目整体进展和关键决策

2. **P1 - 有效文档 (根据任务需要)**
   - 设计任务 → `docs/design/system_architecture.md`
   - 开发任务 → `docs/design/detailed_design_*.md`
   - 测试任务 → `docs/reports/test-history-summary.md`
   - 最新状态 → `docs/reports/progress_report_2026-03-06_10-05.md`

3. **P2 - 原始记录 (详细历史信息)**
   - 已归档文件带有 `<!-- ARCHIVED: ... -->` 标记
   - 仅在需要详细信息时查阅

### 减少 Token 消耗

- ✅ 优先阅读摘要文件而非所有原始记录
- ✅ 使用 `read` 工具时指定 `offset/limit` 分块读取大文件
- ✅ 避免一次性读取整个目录

---

## 📊 项目状态概览

| 阶段 | 状态 | 完成率 | 文档位置 |
|------|------|--------|---------|
| 设计 | ✅ 完成 | 100% | [design/](./design/) |
| 审查 | ✅ 完成 | 100% | [review/](./review/) |
| 开发 | 🚀 进行中 | ~95% | [reports/](./reports/) |
| 测试 | 🔄 进行中 | ~87% | [reports/](./reports/) |

**整体进度:** ~90%

---

## 🔗 相关链接

- [AGENTS.md](../AGENTS.md) - Agent 工作指南
- [SOUL.md](../SOUL.md) - Agent 身份定义

---

*文档中心由 qclaw-pm 维护*
