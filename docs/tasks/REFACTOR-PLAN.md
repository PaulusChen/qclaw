# qclaw 技术栈重构计划 - 基于开源优先原则

**创建日期:** 2026-03-06  
**优先级:** P0 (最高)  
**状态:** 📋 规划中

---

## 🎯 重构目标

### 第一目标：引入最先进技术
- ✅ 使用 2024-2026 年最先进的深度学习框架
- ✅ 采用业界最佳实践的量化交易技术
- ✅ 保持技术栈的先进性和竞争力

### 第二目标：优先复用开源项目
- ✅ 减少重复造轮子，开发量减少 70%+
- ✅ qclaw 作为"粘合剂"组装优秀开源项目
- ✅ 核心精力放在业务逻辑和差异化功能

---

## 📦 推荐技术栈 (开源优先)

### 1. 深度学习框架

| 组件 | 推荐方案 | 开源项目 | 自研替代 | 优先级 |
|------|---------|---------|---------|--------|
| **时间序列预测** | TFT | [pytorch-forecasting](https://github.com/jdb78/pytorch-forecasting) | 自研 TFT | P0 |
| **Transformer 架构** | iTransformer | [thuml/iTransformer](https://github.com/thuml/iTransformer) | 参考论文自研 | P1 |
| **LLM 集成** | Time-LLM | [KimMeen/Time-LLM](https://github.com/KimMeen/Time-LLM) | 暂不自研 | P2 |
| **状态空间模型** | Mamba | [state-spaces/mamba](https://github.com/state-spaces/mamba) | 暂不自研 | P2 |
| **基础模型** | PyTorch | [pytorch/pytorch](https://github.com/pytorch/pytorch) | - | P0 |

### 2. 量化交易框架

| 组件 | 推荐方案 | 开源项目 | 自研替代 | 优先级 |
|------|---------|---------|---------|--------|
| **回测框架** | Backtrader | [backtrader](https://github.com/mementum/backtrader) | 自研简单回测 | P0 |
| **量化分析** | empyrical | [quantopian/empyrical](https://github.com/quantopian/empyrical) | 自研指标计算 | P1 |
| **投资组合优化** | PyPortfolioOpt | [robertmartin8/PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) | 自研基础优化 | P1 |
| **技术指标** | ta-lib | [mrjbq7/ta-lib](https://github.com/mrjbq7/ta-lib) | 使用 pandas-ta | P0 |

### 3. 数据处理

| 组件 | 推荐方案 | 开源项目 | 自研替代 | 优先级 |
|------|---------|---------|---------|--------|
| **数据获取** | yfinance | [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) | 自研 API 调用 | P0 |
| **数据处理** | pandas | [pandas-dev/pandas](https://github.com/pandas-dev/pandas) | - | P0 |
| **特征工程** | tsfresh | [blue-yonder/tsfresh](https://github.com/blue-yonder/tsfresh) | 自研特征 | P1 |
| **数据可视化** | plotly | [plotly/plotly](https://github.com/plotly/plotly) | 使用 matplotlib | P1 |

### 4. 前端框架

| 组件 | 推荐方案 | 开源项目 | 自研替代 | 优先级 |
|------|---------|---------|---------|--------|
| **UI 框架** | React 18 + TypeScript | [facebook/react](https://github.com/facebook/react) | - | P0 |
| **图表库** | ECharts | [apache/echarts](https://github.com/apache/echarts) | 使用 Chart.js | P0 |
| **组件库** | Ant Design | [ant-design/ant-design](https://github.com/ant-design/ant-design) | 自研组件 | P1 |
| **状态管理** | Zustand | [pmndrs/zustand](https://github.com/pmndrs/zustand) | 使用 Context | P1 |

### 5. 基础设施

| 组件 | 推荐方案 | 开源项目 | 自研替代 | 优先级 |
|------|---------|---------|---------|--------|
| **API 框架** | FastAPI | [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | 使用 Flask | P0 |
| **任务队列** | Celery | [celery/celery](https://github.com/celery/celery) | 使用 asyncio | P1 |
| **缓存** | Redis | [redis/redis](https://github.com/redis/redis) | 使用内存缓存 | P1 |
| **数据库** | PostgreSQL | [postgresql/postgresql](https://github.com/postgresql/postgresql) | 使用 SQLite | P0 |

---

## 🔄 实施策略

### 阶段 1: 评估与选型 (1 周)

**Week 1:**
- [ ] 评估 `pytorch-forecasting` 的 TFT 实现
  - 是否支持我们的数据格式？
  - 是否支持多步预测？
  - 是否支持注意力可视化？
  - 许可证是否兼容？

- [ ] 评估 `backtrader` 回测框架
  - 是否支持 A 股市场？
  - 是否支持自定义指标？
  - 性能是否满足需求？

- [ ] 评估其他关键开源项目
  - 功能匹配度
  - 社区活跃度
  - 文档完整性
  - 许可证兼容性

**交付物:** `docs/research/open-source-evaluation.md`

### 阶段 2: 集成与定制 (2-3 周)

**Week 2-3: 深度学习集成**
- [ ] 集成 `pytorch-forecasting` 的 TFT 模型
  - 适配 qclaw 数据格式
  - 添加自定义特征
  - 实现注意力可视化
  - 编写训练脚本

- [ ] 集成 `iTransformer` (如需要)
  - 参考官方实现
  - 适配多变量预测
  - 性能对比测试

**Week 4: 回测框架集成**
- [ ] 集成 `backtrader`
  - 配置 A 股数据源
  - 添加自定义指标
  - 实现交易策略
  - 性能评估

**交付物:**
- `src/models/tft_integration.py`
- `src/backtest/backtrader_wrapper.py`
- `examples/tft_training.py`
- `examples/backtest_example.py`

### 阶段 3: 优化与文档 (1 周)

**Week 5:**
- [ ] 性能优化
  - 训练速度优化
  - 推理延迟优化
  - 内存占用优化

- [ ] 文档完善
  - 使用指南
  - API 文档
  - 最佳实践

- [ ] 测试覆盖
  - 单元测试
  - 集成测试
  - E2E 测试

**交付物:**
- `docs/models/tft_usage.md`
- `docs/backtest/backtrader_guide.md`
- 完整的测试套件

---

## 📊 预期收益

### 开发效率提升

| 指标 | 自研方案 | 开源集成 | 提升 |
|------|---------|---------|------|
| **开发时间** | 12 周 | 4 周 | **70% 减少** |
| **代码量** | 10,000 行 | 3,000 行 | **70% 减少** |
| **测试工作量** | 高 | 中 | **50% 减少** |
| **维护成本** | 高 | 低 | **60% 减少** |

### 技术先进性

| 指标 | 自研方案 | 开源集成 | 提升 |
|------|---------|---------|------|
| **模型性能** | 中等 | SOTA | **显著提升** |
| **功能完整性** | 基础 | 完整 | **显著提升** |
| **可维护性** | 低 | 高 | **显著提升** |
| **社区支持** | 无 | 活跃 | **显著提升** |

---

## ⚠️ 风险评估

### 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 开源项目不满足需求 | 中 | 低 | 详细评估、准备备选方案 |
| 许可证冲突 | 高 | 低 | 法律审查、选择宽松许可证 |
| 开源项目停止维护 | 中 | 低 | 选择活跃项目、准备 fork |
| 集成复杂度高 | 中 | 中 | 充分测试、逐步集成 |

### 缓解策略

1. **详细评估:** 每个开源项目都要进行功能、性能、许可证评估
2. **渐进式集成:** 先在小范围试点，验证后再全面推广
3. **备选方案:** 关键组件准备 2-3 个备选开源项目
4. **文档记录:** 详细记录集成过程和问题解决方案

---

## 📋 任务分解

### Coder 任务

| 任务 ID | 任务名称 | 优先级 | 预计工时 | 依赖 |
|---------|---------|--------|---------|------|
| CODE-DL-007 | TFT 模型集成 (使用 pytorch-forecasting) | P0 | 3-4 天 | 无 |
| CODE-DL-008 | iTransformer 集成 (参考官方实现) | P1 | 2-3 天 | CODE-DL-007 |
| CODE-BT-001 | Backtrader 回测框架集成 | P0 | 3-4 天 | 无 |
| CODE-DATA-001 | yfinance 数据获取集成 | P0 | 1-2 天 | 无 |
| CODE-FEAT-001 | tsfresh 特征工程集成 | P1 | 2-3 天 | CODE-DATA-001 |
| CODE-VIZ-001 | ECharts 图表集成 | P1 | 2-3 天 | 无 |

### Tester 任务

| 任务 ID | 任务名称 | 优先级 | 预计工时 | 依赖 |
|---------|---------|--------|---------|------|
| TEST-OPEN-001 | 开源项目评估测试 | P0 | 2-3 天 | 无 |
| TEST-DL-001 | TFT 模型性能测试 | P0 | 2-3 天 | CODE-DL-007 |
| TEST-BT-001 | 回测框架功能测试 | P0 | 2-3 天 | CODE-BT-001 |
| TEST-INT-002 | 开源集成测试 | P1 | 3-4 天 | 所有集成任务 |
| TEST-PERF-001 | 性能基准测试 | P1 | 2-3 天 | 所有集成任务 |

---

## 🎯 下一步行动

### 立即执行 (本周)

1. **评估 `pytorch-forecasting`**
   - 功能验证
   - 性能测试
   - 许可证审查
   - 输出评估报告

2. **创建 CODE-DL-007 任务**
   - 明确使用 pytorch-forecasting
   - 定义集成范围
   - 制定验收标准

3. **创建 CODE-BT-001 任务**
   - 评估 backtrader
   - 定义集成方案
   - 制定验收标准

### 中期规划 (2-4 周)

1. **完成深度学习框架集成**
   - TFT 模型
   - iTransformer (可选)
   - 训练和推理管道

2. **完成回测框架集成**
   - backtrader 配置
   - 策略实现
   - 性能评估

3. **完成数据和处理框架集成**
   - yfinance 数据获取
   - tsfresh 特征工程
   - 数据可视化

### 长期规划 (1-2 月)

1. **优化与完善**
   - 性能优化
   - 文档完善
   - 测试覆盖

2. **扩展功能**
   - 更多模型支持
   - 更多数据源
   - 更多交易策略

---

## 📚 参考资料

### 开源项目
1. https://github.com/jdb78/pytorch-forecasting
2. https://github.com/thuml/iTransformer
3. https://github.com/mementum/backtrader
4. https://github.com/ranaroussi/yfinance

### 调研文档
1. `docs/research/advanced-model-architectures-2024-2026.md` - 先进模型架构
2. `docs/research/quantitative-deep-learning-survey.md` - 量化深度学习调研

---

**创建时间:** 2026-03-06 11:20  
**状态:** 📋 待审批  
**下一步:** 更新 coder.md 和 tester.md 添加具体任务
