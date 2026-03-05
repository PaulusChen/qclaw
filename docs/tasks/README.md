# 任务管理说明

**最后更新:** 2026-03-05  
**维护者:** qclaw-pm

---

## 📂 文件结构

```
docs/tasks/
├── README.md          # 本文档
├── designer.md        # Designer 专属任务（仅 qclaw-designer 读取）
├── reviewer.md        # Reviewer 专属任务（仅 qclaw-reviewer 读取）
├── coder.md           # Coder 专属任务（仅 qclaw-coder 读取）
├── tester.md          # Tester 专属任务（仅 qclaw-tester 读取）
└── completed.md       # 已完成任务归档（所有角色可查）
```

---

## 🔒 上下文隔离原则

**每个 Agent 只读取自己的任务文件：**

| Agent | 读取文件 | 任务前缀 |
|-------|---------|---------|
| qclaw-designer | `designer.md` | `DESIGN-*` |
| qclaw-reviewer | `reviewer.md` | `REVIEW-*` |
| qclaw-coder | `coder.md` | `CODE-*` |
| qclaw-tester | `tester.md` | `TEST-*` |
| qclaw-pm | 所有文件 | 全部 |

**好处：**
- ✅ 避免上下文污染
- ✅ 每个 Agent 只关注自己的任务
- ✅ 减少 Token 消耗
- ✅ 提高执行效率

---

## 📋 任务文件格式

```markdown
# [角色] 任务列表

**最后更新:** 2026-03-05

## 🔄 进行中

| 任务 ID | 任务名称 | 状态 | 备注 |
|---------|---------|------|------|
| CODE-002 | 大盘指标模块 | 🔄 进行中 | - |

## ⏳ 待开始

| 任务 ID | 任务名称 | 依赖 | 备注 |
|---------|---------|------|------|
| CODE-003 | 量化指标模块 | CODE-001 | - |

## ✅ 已完成

| 任务 ID | 任务名称 | 完成日期 | 交付物 |
|---------|---------|----------|--------|
| CODE-001 | 项目初始化 | 2026-03-05 | webui/ |
```

---

## 🔄 任务流转

```
PM 创建任务
    ↓
添加到对应角色的任务文件
    ↓
Agent Cron 触发（每 5 分钟）
    ↓
Agent 读取自己的任务文件
    ↓
执行任务
    ↓
更新任务状态
    ↓
完成后移动到 completed.md
```

---

## 📝 更新规范

### PM 创建任务

```bash
# 编辑对应角色的任务文件
# 添加到"待开始"部分
```

### Agent 执行任务

```bash
# 读取自己的任务文件
# 执行任务
# 更新状态为"进行中"
# 完成后更新为"已完成"并移动任务到 completed.md
```

---

**注意:** 不要读取其他角色的任务文件，避免上下文污染！
