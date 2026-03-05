# QCLaw

> 🤖 AI 驱动的智能量化分析平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)]()

---

## 📖 项目简介

**QCLaw** 是一个基于 AI 大语言模型的智能量化分析平台，整合了传统量化技术指标与 AI 智能分析能力，为投资者提供全面的市场分析和投资建议。

### ✨ 核心特性

- 📊 **大盘指标监控** - 实时跟踪上证指数、深证成指、创业板指
- 📈 **量化技术指标** - MACD、KDJ、RSI、布林带等经典指标
- 🤖 **AI 投资建议** - 基于大语言模型的市场分析和投资建议
- 📰 **智能资讯聚合** - 财经新闻、政策解读、舆情分析
- 🔄 **自动化工作流** - 多 Agent 协作，自动化任务执行

---

## 🛠️ 技术栈

### 后端
- **Python 3.9+** - 主要开发语言
- **Qlib** - 量化分析框架
- **AKShare** - A 股数据源
- **FastAPI** - API 服务框架
- **Redis** - 数据缓存

### 前端
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite 5** - 构建工具
- **Ant Design 5** - UI 组件库
- **ECharts 5** - 图表库
- **Redux Toolkit** - 状态管理

### 基础设施
- **Docker** - 容器化部署
- **OpenClaw** - AI Agent 协作框架

---

## 📦 项目结构

```
qclaw/
├── src/                      # Python 源代码
│   ├── config.py             # 配置管理
│   ├── utils.py              # 工具函数
│   ├── data/                 # 数据模块
│   │   └── qlib_data.py      # Qlib 数据获取
│   ├── indicators/           # 技术指标
│   │   └── moving_average.py # 移动平均线
│   └── integration/          # OpenClaw 集成
│       └── openclaw_client.py
├── webui/                    # 前端项目
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── pages/            # 页面组件
│   │   ├── store/            # Redux 状态管理
│   │   ├── services/         # API 服务
│   │   └── assets/           # 静态资源
│   ├── package.json
│   └── vite.config.ts
├── tests/                    # 测试文件
├── docs/                     # 项目文档
│   ├── requirements/         # 需求文档
│   ├── design/               # 设计文档
│   ├── review/               # 审核报告
│   ├── tasks/                # 任务管理
│   └── reports/              # 进度报告
├── Dockerfile                # Docker 镜像配置
├── docker-compose.yml        # Docker Compose 配置
├── requirements.txt          # Python 依赖
└── README.md                 # 项目说明
```

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (可选)
- Redis (可选，用于缓存)

### 1. 克隆项目

```bash
git clone https://github.com/PaulusChen/qclaw.git
cd qclaw
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd webui
npm install
```

### 4. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env 文件，填入实际配置
```

### 5. 启动开发服务器

```bash
# 启动前端开发服务器
cd webui
npm run dev

# 启动后端服务 (另开终端)
cd ..
python -m uvicorn server.main:app --reload
```

### 6. Docker 部署 (可选)

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📚 使用文档

### WebUI 界面

访问 `http://localhost:3000` 打开投资分析仪表盘，包含以下模块：

1. **大盘指标** - 查看三大指数实时走势
2. **量化指标** - MACD、KDJ、RSI 等技术指标
3. **AI 建议** - 大模型分析的投资建议
4. **新闻资讯** - 财经新闻和政策解读

### API 接口

后端服务启动后访问 `http://localhost:8000/docs` 查看 API 文档。

主要接口：
- `GET /api/market/indices` - 大盘指数数据
- `GET /api/indicators/technical` - 技术指标数据
- `GET /api/advice/daily` - AI 投资建议
- `GET /api/news/list` - 新闻资讯列表

---

## 🤖 AI Agent 协作

本项目采用 OpenClaw 多 Agent 协作框架，包含以下角色：

| Agent | 职责 | 任务文件 |
|-------|------|---------|
| **qclaw-pm** | 项目管理、进度监控 | `docs/tasks/pm.md` |
| **qclaw-designer** | UI/UX 设计、技术方案 | `docs/tasks/designer.md` |
| **qclaw-reviewer** | 设计审核、代码审查 | `docs/tasks/reviewer.md` |
| **qclaw-coder** | 代码开发 | `docs/tasks/coder.md` |
| **qclaw-tester** | 测试验证 | `docs/tasks/tester.md` |

所有 Agent 每 5 分钟自动检查任务状态，PM 每天 10:00 自动生成项目日报。

---

## 📋 开发指南

### 代码规范

- Python: 遵循 PEP 8 规范
- TypeScript: 使用 ESLint + Prettier
- Git 提交：使用约定式提交规范

### 提交流程

```bash
# 1. 查看自己的任务
cat docs/tasks/<your-role>.md

# 2. 执行任务

# 3. 提交代码
git add .
git commit -m "[Role] 任务描述"
git push origin main

# 4. 更新任务状态
# 编辑 docs/tasks/<your-role>.md
```

### 分支策略

- `main` - 主分支，生产环境
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - 修复分支

---

## 🧪 测试

### 测试职责分工

| 测试类型 | 负责角色 | 说明 |
|---------|---------|------|
| **单元测试** | Coder | 测试自己的代码 |
| **集成测试** | Tester | 模块间集成测试 |
| **系统测试** | Tester | Docker 环境自动化测试 |
| **E2E 测试** | Tester | 端到端流程测试 |

### 后端测试（Coder）

```bash
# 运行 Python 单元测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 前端测试（Coder）

```bash
cd webui

# 安装依赖（首次运行）
npm install

# 运行所有测试
npm test

# 运行测试并监听文件变化
npm test -- --watch

# 运行测试并生成覆盖率报告
npm run test:coverage

# 打开测试 UI 界面
npm run test:ui
```

### 集成测试（Tester）

```bash
# 运行 API 集成测试
pytest tests/integration/ -v

# 运行数据库集成测试
pytest tests/integration/test_database.py -v
```

### 系统测试（Tester）

```bash
# 使用 Docker 运行系统测试
./scripts/test-system.sh

# 或手动运行
docker-compose up -d
docker-compose exec -T api pytest tests/system/ -v
docker-compose down
```

### 测试覆盖率

目标覆盖率：
- **单元测试（Coder）**: >80%
- **集成测试（Tester）**: >60%
- **系统测试（Tester）**: 关键服务 100%

---

## 🔄 CI/CD

项目配置了完整的 CI/CD 流程：

### GitHub Actions

推送代码后自动运行：
- ✅ 后端 Python 测试
- ✅ 前端 React 测试
- ✅ Docker 构建测试
- ✅ 集成测试
- ✅ 代码质量检查

### 配置文件

- `.github/workflows/ci.yml` - CI/CD 流程定义
- `Dockerfile` - 后端 Docker 镜像
- `Dockerfile.frontend` - 前端 Docker 镜像
- `docker-compose.yml` - 多服务编排
- `scripts/test-system.sh` - 系统测试脚本

### 本地运行 CI

```bash
# 运行完整测试流程
./scripts/test-system.sh

# 或分步运行
docker-compose up -d
docker-compose exec -T api pytest tests/ -v
docker-compose down
```

---

## 🙏 致谢

- [Qlib](https://github.com/microsoft/qlib) - 微软量化分析框架
- [AKShare](https://github.com/akfamily/akshare) - A 股数据接口
- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent 协作框架
- [Ant Design](https://ant.design/) - 企业级 UI 组件库
- [ECharts](https://echarts.apache.org/) - 数据可视化图表库

---

## 📬 联系方式

- **GitHub:** https://github.com/PaulusChen/qclaw
- **Issues:** https://github.com/PaulusChen/qclaw/issues

---

**⚠️ 风险提示:** 本项目仅供学习研究使用，不构成任何投资建议。股市有风险，投资需谨慎。
