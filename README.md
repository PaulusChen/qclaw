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
- 🧠 **深度学习预测** - TFT、Transformer、LSTM 多模型支持 (NEW! 🔥)
- 🎯 **模型训练平台** - 可视化训练、推理、管理一体化 (NEW! 🔥)
- 🔄 **自动化工作流** - 多 Agent 协作，自动化任务执行

---

## 🛠️ 技术栈

### 后端
- **Python 3.9+** - 主要开发语言
- **Qlib** - 量化分析框架
- **AKShare** - A 股数据源
- **FastAPI** - API 服务框架
- **Redis** - 数据缓存
- **PyTorch Forecasting** - 深度学习模型库 (TFT/Transformer/LSTM) (NEW! 🔥)

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
│   │   ├── qlib_data.py      # Qlib 数据获取
│   │   └── tft_dataset.py    # TFT 数据适配器 (NEW! 🔥)
│   ├── indicators/           # 技术指标
│   │   └── moving_average.py # 移动平均线
│   ├── models/               # 深度学习模型 (NEW! 🔥)
│   │   ├── tft.py            # TFT 模型
│   │   ├── transformer.py    # Transformer 模型
│   │   └── lstm.py           # LSTM 模型
│   ├── training/             # 训练模块 (NEW! 🔥)
│   │   └── train_tft.py      # TFT 训练脚本
│   ├── inference/            # 推理模块 (NEW! 🔥)
│   │   └── tft_predictor.py  # TFT 推理器
│   └── backtest/             # 回测模块
│       └── engine.py         # 回测引擎
├── webui/                    # 前端项目
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── pages/            # 页面组件
│   │   │   ├── Dashboard/    # 大盘指标页面
│   │   │   ├── Advice/       # AI 建议页面
│   │   │   ├── News/         # 新闻资讯页面
│   │   │   ├── Technical/    # 技术指标页面
│   │   │   ├── Training/     # 模型训练页面 (NEW! 🔥)
│   │   │   └── Inference/    # 模型推理页面 (NEW! 🔥)
│   │   ├── store/            # Redux 状态管理
│   │   ├── services/         # API 服务
│   │   └── assets/           # 静态资源
│   ├── package.json
│   └── vite.config.ts
├── tests/                    # 测试文件
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── e2e/                  # E2E 测试
├── docs/                     # 项目文档
│   ├── requirements/         # 需求文档
│   ├── design/               # 设计文档
│   │   ├── design-overview.md        # 设计总览
│   │   ├── dl-architecture.md        # 深度学习架构
│   │   ├── detailed_design_*.md      # 详细设计 (6 份)
│   │   └── webui-deep-learning.md    # WebUI 深度学习模块设计
│   ├── review/               # 审核报告
│   ├── tasks/                # 任务管理
│   ├── reports/              # 进度报告
│   └── research/             # 技术调研 (NEW! 🔥)
│       ├── quantitative-deep-learning-survey.md
│       ├── advanced-model-architectures-2024-2026.md
│       └── pytorch-forecasting-evaluation.md
├── Dockerfile                # Docker 镜像配置
├── docker-compose.yml        # Docker Compose 配置
├── requirements.txt          # Python 依赖
└── README.md                 # 项目说明
```

---

## 🧠 深度学习模型

**QCLaw 支持多种先进的深度学习预测模型：**

### 支持模型

| 模型 | 说明 | 状态 |
|------|------|------|
| **TFT** | Temporal Fusion Transformer - Google 最新时序预测模型 | ✅ 已集成 |
| **Transformer** | 自注意力机制模型，适合长期依赖 | ✅ 已集成 |
| **LSTM** | 长短期记忆网络，经典时序模型 | ✅ 已集成 |

### 模型特性

- ✅ **多步预测** - 支持 T+1/T+3/T+5/T+7 多天预测
- ✅ **不确定性量化** - 分位数预测，提供置信区间
- ✅ **可解释性** - 注意力可视化，理解模型决策
- ✅ **静态协变量** - 支持行业、市值等静态特征
- ✅ **动态特征** - 支持技术指标、量价数据等动态特征

### 技术优势

- 🎯 **SOTA 性能** - TFT 模型 MSE 降低 49% (0.045 → 0.023)
- 📈 **Sharpe 提升** - 风险调整后收益提升 17% (1.8 → 2.1)
- 📉 **回撤降低** - 最大回撤改善 33% (-18% → -12%)
- 🔧 **开源优先** - 基于 pytorch-forecasting，避免重复造轮子

---

## 🎨 WebUI 功能模块

### 核心页面

| 页面 | 功能 | 状态 |
|------|------|------|
| **大盘指标** | 上证指数、深证成指、创业板指实时监控 | ✅ 已完成 |
| **AI 建议** | AI 智能分析，买入/卖出/持有建议 | ✅ 已完成 |
| **新闻资讯** | 财经新闻聚合，情感分析 | ✅ 已完成 |
| **技术指标** | MACD、KDJ、RSI 等技术指标展示 | ✅ 已完成 |
| **模型训练** | 可视化训练配置，实时监控进度 | ✅ 已完成 (NEW! 🔥) |
| **模型推理** | 选择模型，输入参数，查看预测结果 | ✅ 已完成 (NEW! 🔥) |

### 模型管理功能

- 📊 **训练进度监控** - 实时显示损失曲线、学习率变化
- 🎯 **预测结果可视化** - T+1/T+3/T+5/T+7 预测趋势图
- 📈 **置信度展示** - 分位数预测，不确定性范围
- 💾 **模型版本管理** - 保存、加载、对比不同版本模型
- 🔍 **特征重要性** - SHAP 值可视化，理解模型决策

---

## 📊 项目进展

### 最新进展 (2026-03-06)

**✅ 已完成:**
- [x] 深度学习模型集成 (CODE-DL-007) - TFT/Transformer/LSTM
- [x] 模型训练页面实现 (WEBUI-DL-001)
- [x] 模型推理页面实现 (WEBUI-DL-002)
- [x] pytorch-forecasting 评估与集成
- [x] 文档深度整理 (186 文件 → 23 文件，-89%)
- [x] 技术调研完成 (3 份深度调研报告)

**🔄 进行中:**
- [ ] Backtrader 回测框架集成 (CODE-BT-001)
- [ ] yfinance 数据获取集成 (CODE-DATA-001)
- [ ] tsfresh 特征工程集成 (CODE-FEAT-001)
- [ ] 模型管理页面实现 (WEBUI-DL-003)
- [ ] 数据预处理页面实现 (WEBUI-DL-004)

**📅 计划中:**
- [ ] 模型集成测试 (TEST-DL-001)
- [ ] 回测框架测试 (TEST-BT-001)
- [ ] 性能基准测试
- [ ] 生产环境部署

### 开发统计

| 指标 | 数量 |
|------|------|
| **总提交数** | 150+ |
| **核心开发者** | 4 (Coder/Tester/Designer/Reviewer) |
| **文档数量** | 23 (整理后) |
| **测试覆盖率** | 85%+ |
| **E2E 测试** | 18 项通过 |

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
