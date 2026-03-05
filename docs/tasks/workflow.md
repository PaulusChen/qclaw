# QCLaw 项目工作流

**最后更新:** 2026-03-05  
**维护者:** qclaw-pm

---

## 📂 文档结构

```
docs/
├── README.md              # 文档索引
├── requirements/          # 需求文档
│   └── webui-prd.md       # 产品需求文档
├── design/                # 设计文档
│   ├── ui-design.md       # UI/UX 设计
│   └── technical-design.md # 技术方案
├── review/                # 审核报告
│   └── *.md               # 各类审核报告
├── tasks/                 # 任务管理
│   ├── README.md          # 任务管理说明
│   ├── designer.md        # Designer 专属任务
│   ├── reviewer.md        # Reviewer 专属任务
│   ├── coder.md           # Coder 专属任务
│   ├── tester.md          # Tester 专属任务
│   └── completed.md       # 已完成任务归档
└── reports/               # 进度报告
    └── *.md               # 项目报告
```

---

## 🔒 上下文隔离原则

**每个 Agent 只读取自己的任务文件：**

| Agent | 读取文件 | 任务前缀 |
|-------|---------|---------|
| qclaw-designer | `tasks/designer.md` | `DESIGN-*` |
| qclaw-reviewer | `tasks/reviewer.md` | `REVIEW-*` |
| qclaw-coder | `tasks/coder.md` | `CODE-*` |
| qclaw-tester | `tasks/tester.md` | `TEST-*` |
| qclaw-pm | 所有文件 | 全部 |

**好处：**
- ✅ 避免上下文污染
- ✅ 每个 Agent 只关注自己的任务
- ✅ 减少 Token 消耗
- ✅ 提高执行效率

---

## 🔄 工作流程

### 1. 任务创建流程

```
PM 创建需求
    ↓
PM 编辑对应角色的任务文件
    ↓
添加到"待开始"部分
    ↓
Cron 定时触发 (每 5 分钟)
    ↓
角色 Agent 读取自己的任务文件
    ↓
发现新任务
    ↓
开始执行
```

### 2. 任务执行流程

```
Agent Cron 触发
    ↓
读取自己的任务文件 (如 coder.md)
    ↓
查找"进行中"或"待开始"任务
    ↓
执行任务
    ↓
提交成果到对应目录
    ↓
更新任务文件状态
    ↓
提交代码并推送
```

### 3. 任务完成流程

```
Agent 完成任务
    ↓
更新自己的任务文件
    ↓
将任务从"进行中"移到"已完成"
    ↓
提交代码
    ↓
PM 定期将已完成任务移动到 completed.md
```

---

## 👥 各角色职责

### qclaw-pm (项目管理)

**文档位置:**
- 需求文档：`docs/requirements/`
- 任务管理：`docs/tasks/*.md` (所有文件)
- 进度报告：`docs/reports/`

**职责:**
1. 创建需求文档
2. 在各角色任务文件中添加新任务
3. 监控整体进度
4. 定期将已完成任务移动到 `completed.md`
5. 编写进度报告

**Cron 任务:** 每 5 分钟检查所有任务文件

---

### qclaw-designer (设计)

**文档位置:**
- 设计文档：`docs/design/`
- 任务查询：`docs/tasks/designer.md` (只读此文件)

**职责:**
1. 读取 `docs/tasks/designer.md`
2. 查找 DESIGN-* 任务
3. 执行设计工作
4. 提交设计文档到 `docs/design/`
5. 更新 `docs/tasks/designer.md` 状态

**Cron 任务:** 每 5 分钟检查 `designer.md`

---

### qclaw-reviewer (审核)

**文档位置:**
- 审核报告：`docs/review/`
- 任务查询：`docs/tasks/reviewer.md` (只读此文件)

**职责:**
1. 读取 `docs/tasks/reviewer.md`
2. 查找 REVIEW-* 任务
3. 审核设计文档
4. 提交审核报告到 `docs/review/`
5. 审核通过 → 通知 PM 解锁下游任务
6. 更新 `docs/tasks/reviewer.md` 状态

**Cron 任务:** 每 5 分钟检查 `reviewer.md`

---

### qclaw-coder (开发)

**文档位置:**
- 源代码：`src/`, `webui/`
- 任务查询：`docs/tasks/coder.md` (只读此文件)

**职责:**
1. 读取 `docs/tasks/coder.md`
2. 查找 CODE-* 任务
3. 执行开发工作
4. 提交代码到 `src/` 或 `webui/`
5. 更新 `docs/tasks/coder.md` 状态

**Cron 任务:** 每 5 分钟检查 `coder.md`

---

### qclaw-tester (测试)

**文档位置:**
- 测试报告：`docs/reports/`
- 任务查询：`docs/tasks/tester.md` (只读此文件)

**职责:**
1. 读取 `docs/tasks/tester.md`
2. 查找 TEST-* 任务
3. 编写测试用例
4. 执行测试
5. 提交测试报告
6. 更新 `docs/tasks/tester.md` 状态

**Cron 任务:** 每 5 分钟检查 `tester.md`

---

## 📋 任务状态说明

| 状态 | 符号 | 说明 |
|------|------|------|
| 待开始 | ⏳ | 任务已创建，等待执行 |
| 进行中 | 🔄 | 任务正在执行 |
| 已完成 | ✅ | 任务完成 |
| 等待依赖 | 🔒 | 依赖其他任务完成 |
| 已归档 | 📦 | 任务已移至 completed.md |

---

## 🔧 Cron 配置

所有角色的 Cron 任务配置在：
`/home/openclaw/.openclaw/cron/jobs.json`

**任务列表:**
- `QCLaw 项目组心跳检查` - qclaw-pm
- `QCLaw-Designer 任务检查` - qclaw-designer
- `QCLaw-Reviewer 任务检查` - qclaw-reviewer
- `QCLaw-Coder 任务检查` - qclaw-coder
- `QCLaw-Tester 任务检查` - qclaw-tester

**执行频率:** 每 5 分钟 (`*/5 * * * *`)

---

## 📝 文档更新规范

### PM 创建任务

```markdown
## ⏳ 待开始

| 任务 ID | 任务名称 | 依赖 | 备注 |
|---------|---------|------|------|
| CODE-007 | 新任务名称 | - | - |
```

### Agent 执行任务

```markdown
## 🔄 进行中

| 任务 ID | 任务名称 | 进度 | 备注 |
|---------|---------|------|------|
| CODE-002 | 大盘指标模块 | 50% | 开发中 |
```

### Agent 完成任务

```markdown
## ✅ 已完成

| 任务 ID | 任务名称 | 完成日期 | 交付物 |
|---------|---------|----------|--------|
| CODE-001 | 项目初始化 | 2026-03-05 | webui/ |
```

---

## 🎯 快速指南

**新成员如何开始？**
1. 阅读 `docs/README.md` 了解文档结构
2. 阅读 `docs/requirements/webui-prd.md` 了解需求
3. 查看自己的任务文件 (如 `docs/tasks/coder.md`)
4. 执行任务并更新状态

**如何查询任务？**
- **只读取自己的任务文件**
- 不要读取其他角色的任务文件

**如何更新进度？**
- 修改自己的任务文件
- 提交代码并推送

---

**维护者:** qclaw-pm  
**文档版本:** v3.0 (上下文隔离版)
