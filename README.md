# QCLaw 项目组工作空间

**注意:** 这是 QCLaw 项目组的 **OpenClaw 工作空间**，不是源代码仓库。

## 📂 目录说明

| 目录/文件 | 用途 |
|-----------|------|
| `AGENTS.md` | Agent 配置说明 |
| `SOUL.md` | Agent 人格定义 |
| `USER.md` | 用户信息 |
| `IDENTITY.md` | 身份标识 |
| `TOOLS.md` | 工具配置 |
| `HEARTBEAT.md` | 心跳任务 |
| `BOOTSTRAP.md` | 启动引导 |
| `COMMIT_HISTORY.md` | 项目提交历史记录 |
| `memory/` | 日常记忆文件 |
| `.openclaw/` | 工作空间状态 |

## 📁 源代码位置

**源代码仓库:** `~/qclaw/`  
**GitHub:** https://github.com/PaulusChen/qclaw

```bash
# 查看源代码
cd ~/qclaw

# 查看工作空间
cd /home/openclaw/.openclaw/workspace-qclaw/
```

## 👥 项目组成员

| 角色 | Agent ID | 职责 |
|------|----------|------|
| PM | `qclaw-pm` | 项目管理、任务协调 |
| Designer | `qclaw-designer` | UI/UX 设计、技术方案 |
| Reviewer | `qclaw-reviewer` | 设计审核、代码审查 |
| Coder | `qclaw-coder` | 代码开发 |
| Tester | `qclaw-tester` | 测试验证 |

## ⏰ 定时任务

所有角色每 5 分钟自动检查任务列表并执行。

**Cron 配置:** `/home/openclaw/.openclaw/cron/jobs.json`

---

**工作空间路径:** `/home/openclaw/.openclaw/workspace-qclaw/`  
**源代码路径:** `~/qclaw/`
