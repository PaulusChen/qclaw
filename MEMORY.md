# QCLaw 项目长期记忆

**创建日期:** 2026-03-05  
**维护者:** qclaw-pm

---

## ⚠️ 重要规则：目录隔离

### 📂 目录用途

| 目录 | 用途 | 包含内容 |
|------|------|---------|
| `~/qclaw/` | **项目源代码目录** | 源代码、文档、配置、测试 |
| `~/.openclaw/workspace-qclaw/` | **OpenClaw 工作空间** | Agent 配置、记忆、状态 |

### ❌ 禁止行为

**不要在 `~/qclaw/` 中存放以下 OpenClaw 工作空间文件：**
- `AGENTS.md` ❌
- `BOOTSTRAP.md` ❌
- `SOUL.md` ❌
- `USER.md` ❌
- `IDENTITY.md` ❌
- `TOOLS.md` ❌
- `HEARTBEAT.md` ❌
- `COMMIT_HISTORY.md` ❌
- `memory/` ❌
- `.openclaw/` ❌

**这些文件应该存放在：** `~/.openclaw/workspace-qclaw/`

### ✅ 正确做法

**`~/qclaw/` 项目代码目录应该包含：**
- ✅ `src/` - Python 源代码
- ✅ `webui/` - 前端代码
- ✅ `tests/` - 测试文件
- ✅ `docs/` - 项目文档（需求、设计、任务、报告）
- ✅ `Dockerfile`, `docker-compose.yml` - Docker 配置
- ✅ `requirements.txt` - Python 依赖
- ✅ `package.json` - Node 依赖
- ✅ `README.md` - 项目说明
- ✅ `.gitignore` - Git 忽略规则

**`~/.openclaw/workspace-qclaw/` 工作空间应该包含：**
- ✅ `AGENTS.md` - Agent 配置
- ✅ `SOUL.md` - Agent 人格
- ✅ `USER.md` - 用户信息
- ✅ `IDENTITY.md` - 身份标识
- ✅ `TOOLS.md` - 工具配置
- ✅ `HEARTBEAT.md` - 心跳任务
- ✅ `BOOTSTRAP.md` - 启动引导
- ✅ `COMMIT_HISTORY.md` - 提交历史
- ✅ `memory/` - 日常记忆
- ✅ `.openclaw/` - 工作空间状态

---

## 📋 项目信息

**项目名称:** QCLaw - AI 驱动的智能量化分析平台  
**GitHub:** https://github.com/PaulusChen/qclaw  
**技术栈:** Python + React + TypeScript + Qlib + AKShare

### 核心功能
1. 大盘指标监控（上证指数、深证成指、创业板指）
2. 量化技术指标（MACD、KDJ、RSI、布林带）
3. AI 投资建议（大语言模型分析）
4. 智能资讯聚合（财经新闻、政策解读）

### Agent 团队
- **qclaw-pm** - 项目管理、进度监控、日报生成
- **qclaw-designer** - UI/UX 设计、技术方案
- **qclaw-reviewer** - 设计审核、代码审查
- **qclaw-coder** - 代码开发
- **qclaw-tester** - 测试验证

### Cron 配置
- **项目监控:** 每 5 分钟检查所有角色任务状态
- **项目日报:** 每天 10:00 自动生成过去 24 小时报告

---

## 📝 历史教训

**2026-03-05:** 多次错误地将 OpenClaw 工作空间文件放入项目代码目录

**问题:**
- 混淆了 `~/qclaw/` 和 `~/.openclaw/workspace-qclaw/` 的用途
- 导致项目代码目录中包含大量无关的 Markdown 文件

**解决方案:**
1. 清理 `~/qclaw/` 中的所有 OpenClaw 工作空间文件
2. 在 `.gitignore` 中明确禁止提交这些文件
3. 记录到长期记忆中，避免再次犯错

**原则:**
- **项目代码目录** (`~/qclaw/`) = 干净的源代码仓库
- **OpenClaw 工作空间** (`~/.openclaw/workspace-qclaw/`) = Agent 配置和状态

---

**最后更新:** 2026-03-05 19:01
