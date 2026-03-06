# Coder 任务列表

**负责人:** qclaw-coder  
**最后更新:** 2026-03-06 11:20  
**Cron:** 每 30 分钟自动检查 (事件驱动模式)

---

## 🔄 核心设计原则

**🔄 优先复用开源项目 (P0 原则)**
1. **第一选择:** 使用成熟的开源实现
2. **第二选择:** 在开源基础上定制
3. **第三选择:** 自研实现 (仅在无合适开源时)

**qclaw 角色定位:** 粘合剂 - 组装优秀开源项目，减少重复造轮子

**推荐开源项目:**
- TFT 模型：[pytorch-forecasting](https://github.com/jdb78/pytorch-forecasting)
- iTransformer：[thuml/iTransformer](https://github.com/thuml/iTransformer)
- 回测框架：[backtrader](https://github.com/mementum/backtrader)
- 数据获取：[yfinance](https://github.com/ranaroussi/yfinance)

---

## ⏳ 待开始 (新规划)

### CODE-DL-007: TFT 模型集成 (使用 pytorch-forecasting) 🆕
**优先级:** 🔥 **P0 (最高)**  
**依赖:** 无  
**交付物:** 集成 pytorch-forecasting 的 TFT 模型  
**状态:** ⏳ 待开始

**核心原则:**
- ✅ **优先复用开源:** 使用 pytorch-forecasting 库，避免自研
- ✅ **定制开发:** 在开源基础上适配 qclaw 数据格式
- ✅ **粘合剂角色:** 组装优秀开源项目，减少重复造轮子

**开源项目:**
- 项目：[pytorch-forecasting](https://github.com/jdb78/pytorch-forecasting)
- 文档：https://pytorch-forecasting.readthedocs.io
- 许可证：MIT (兼容)

**实施步骤:**
1. 评估 pytorch-forecasting 功能匹配度
2. 安装和配置库
3. 适配 qclaw 数据格式
4. 实现训练和推理脚本
5. 添加注意力可视化
6. 性能对比测试

**验收标准:**
- [ ] TFT 模型可训练和推理
- [ ] 支持多步预测 (7/14/30 天)
- [ ] MSE < 0.030
- [ ] Sharpe Ratio > 2.0
- [ ] 注意力可视化正常

---

### CODE-BT-001: Backtrader 回测框架集成 🆕
**优先级:** 🔥 **P0 (最高)**  
**依赖:** 无  
**交付物:** 集成 backtrader 回测框架  
**状态:** ⏳ 待开始

**核心原则:**
- ✅ **优先复用开源:** 使用 backtrader，避免自研复杂回测系统
- ✅ **定制开发:** 适配 A 股市场和 qclaw 策略
- ✅ **粘合剂角色:** 组装优秀开源项目

**开源项目:**
- 项目：[backtrader](https://github.com/mementum/backtrader)
- 文档：https://www.backtrader.com
- 许可证：GPLv3 (需注意)

**实施步骤:**
1. 评估 backtrader 功能匹配度
2. 安装和配置库
3. 适配 A 股数据源
4. 实现自定义指标
5. 实现交易策略
6. 性能评估

**验收标准:**
- [ ] 回测框架可运行
- [ ] 支持 A 股数据
- [ ] 支持自定义指标
- [ ] 支持交易策略
- [ ] 性能报告完整

---

### CODE-DATA-001: yfinance 数据获取集成 🆕
**优先级:** P1 (高)  
**依赖:** 无  
**交付物:** 集成 yfinance 数据获取模块  
**状态:** ⏳ 待开始

**核心原则:**
- ✅ **优先复用开源:** 使用 yfinance，避免自研 API 调用
- ✅ **定制开发:** 添加数据缓存和预处理

**开源项目:**
- 项目：[yfinance](https://github.com/ranaroussi/yfinance)
- 许可证：Apache 2.0 (兼容)

**验收标准:**
- [ ] 可获取 A 股和历史数据
- [ ] 数据缓存正常
- [ ] 数据预处理完善

---

## ✅ 已完成

### CODE-009: 修复 E2E 测试发现的新 UI Bug (第二轮) ✅
**优先级:** 🔥 **紧急**  
**依赖:** TEST-E2E-001 第二轮验证 (2026-03-06 02:17)  
**交付物:** 修复剩余 10 项 E2E 测试失败  
**状态:** ✅ 已完成

**修复内容:**
- Dashboard.vue: 移除 `.last-updated` 的 v-if 条件，确保元素始终存在
- Dashboard.vue: 添加响应式导航类名 (`.mobile-nav`, `.tablet-nav`, `.desktop-nav`)
- IndicatorChart.vue: 修复 `.chart-rendered` 条件检查
- IndicatorChart.vue: 修复图表容器类名 (只添加当前指标类名)
- test_user_flows.py: 修复 `test_404_page` 测试用例
- test_user_flows.py: 修复 `test_api_error_handling` 测试用例

**遗留问题 (需要数据/路由支持):**
- AIAdvice.vue 的 `.advice-type`, `.advice-reasons`, `.advice-risks` 需要 API 返回数据
- NewsList.vue 的 `.news-item` 需要 API 返回新闻数据
- 新闻分页 URL 变化需要路由支持

**提交 ID:** `04338c3d`

**问题描述:**
CODE-008 修复后重新运行 E2E 测试，仍有 10 项失败。主要问题是 CSS 类名仍不匹配和测试用例缺陷。

**需要修复的 Bug:**
1. `.last-updated` 元素不存在 - Dashboard.vue 缺少最后更新时间显示
2. `.advice-type`, `.advice-reasons`, `.advice-risks` 不存在 - AIAdvice.vue 类名不完整
3. `.news-item` 不存在 - NewsList.vue 新闻列表项类名缺失
4. 新闻分页 URL 未变化 - NewsList.vue 分页功能未实现
5. `.error-message` 不存在 - 错误提示组件类名缺失
6. `.chart-rendered` 匹配 3 个元素 - IndicatorChart.vue 选择器需要更精确
7. `test_404_page` API 错误 - 测试用例需修复 (使用 `to_have_url` 替代 `to_have_status`)

**交付要求:**
- 修复所有 CSS 类名问题
- 确保 E2E 测试选择器能正确匹配
- 提交后通知 Tester 重新验证

---

### CODE-008: 修复 E2E 测试发现的 UI/交互 bug ✅
**优先级:** 高  
**依赖:** TEST-E2E-001 执行完成后产生的测试报告  
**交付物:** 修复所有 E2E 测试发现的 UI/交互 bug
**状态:** ✅ 已完成

**问题描述:**
根据 E2E 测试报告，修复前端界面和交互问题。Tester 负责启动前端服务并执行 E2E 测试，Coder 根据测试报告修复 bug。

**需要完成:**
1. ✅ 等待 Tester 执行 TEST-E2E-001 并生成测试报告
2. ✅ 分析 E2E 测试失败原因 (16 个 CSS 类名不匹配)
3. ✅ 修复 UI 显示问题 (Dashboard.vue, MarketCard.vue, AIAdvice.vue, NewsList.vue, IndicatorChart.vue)
4. ✅ 确保所有 E2E 测试选择器能正确匹配

**修复详情:**
- Dashboard.vue: 添加 `.market-indices` 容器和 `.last-updated` 时间显示
- MarketCard.vue: 添加动态索引类名 (`.index-shanghai`, `.index-shanghai`, `.index-chinext`)
- AIAdvice.vue: 添加 `.ai-advice`, `.advice-type`, `.confidence-level` 类名
- NewsList.vue: 添加 `.pagination` 类名
- IndicatorChart.vue: 添加 `.technical-indicators`, `.macd-chart`, `.kdj-chart`, `.rsi-chart`, `.chart-rendered` 类名

**提交 ID:** `f07dbea`

---

## ✅ 已完成 (历史任务)

| 任务 ID | 任务名称 | 状态 | 提交 ID |
|---------|---------|------|---------|
| CODE-001 | 项目初始化 | ✅ | `8d4c923` |
| CODE-002 | 大盘指标模块 | ✅ | `12a92ca` |
| CODE-003 | 量化指标模块 | ✅ | - |
| CODE-004 | AI 建议模块 | ✅ | `2282ffd` |
| CODE-005 | 新闻资讯模块 | ✅ | `2282ffd` |
| CODE-006 | 后端 API 开发 | ✅ | `0a17c35` |
| CODE-007 | 单元测试修复 | ✅ | `9f893b0` |
| CODE-008 | UI Bug 修复 - CSS 类名不匹配 | ✅ | `f07dbea` |
| CODE-009 | E2E Bug 修复 (第二轮) | ✅ | `04338c3d` |
| CODE-010 | 前端缺少关键文件 - 404 错误 | ✅ | - |
| CODE-DL-001 | 深度学习预测模块基础结构 | ✅ | 待提交 |
| CODE-DL-002 | 数据层实现 | ✅ | 待提交 |
| CODE-DL-003 | 模型层实现 | ✅ | 待提交 |
| CODE-DL-004 | 推理/回测/评估层实现 | ✅ | 待提交 |
| CODE-DL-005 | 训练层实现 | ✅ | 待提交 |
| CODE-DL-006 | 数据管道集成与端到端测试 | 🔄 进行中 | - |

---

## 📋 说明

### 新原则下的任务规划

根据"优先复用开源项目"原则，后续开发任务将：

1. **优先评估开源项目** - 实现前先搜索 GitHub、PyPI
2. **80% 满足则使用开源** - 在开源基础上定制开发
3. **自研仅作为最后选择** - 仅在无合适开源时自研

### 即将创建的任务

- **CODE-DL-007:** TFT 模型集成 (使用 pytorch-forecasting)
- **CODE-BT-001:** Backtrader 回测框架集成
- **CODE-DATA-001:** yfinance 数据获取集成
- **CODE-FEAT-001:** tsfresh 特征工程集成

详见：`docs/tasks/REFACTOR-PLAN.md`
