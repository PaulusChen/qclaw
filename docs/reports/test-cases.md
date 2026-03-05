# TEST-001 测试用例文档

**任务 ID:** TEST-001  
**测试负责人:** qclaw-tester  
**创建日期:** 2026-03-05  
**版本:** v1.0

---

## 📋 测试范围

根据 UI 设计稿和技术方案，测试覆盖以下 4 个核心模块：

| 模块 | 测试类型 | 优先级 |
|------|---------|--------|
| 大盘指标模块 | 单元测试 + 集成测试 | P0 |
| 量化指标模块 | 单元测试 + 集成测试 | P0 |
| AI 建议模块 | 单元测试 + API 测试 | P1 |
| 新闻资讯模块 | 单元测试 + API 测试 | P1 |

---

## 🧪 量化指标模块测试用例

### 趋势指标测试 (test_trend_indicators.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| TI-001 | MACD 基础计算 | `test_macd_calculation_basic` | 返回 macd, signal, histogram 三个序列 |
| TI-002 | MACD 自定义参数 | `test_macd_custom_periods` | 支持自定义快慢线周期 |
| TI-003 | MACD 金叉检测 | `test_detect_macd_golden_cross` | 正确识别金叉信号 |
| TI-004 | MACD 死叉检测 | `test_detect_macd_death_cross` | 正确识别死叉信号 |
| TI-005 | ADX 基础计算 | `test_adx_calculation` | 返回 0-100 之间的 ADX 值 |
| TI-006 | ADX 趋势强度 | `test_adx_trend_strength` | ADX>25 识别为强趋势 |
| TI-007 | SAR 基础计算 | `test_sar_calculation` | SAR 值跟随趋势反转 |
| TI-008 | SAR 趋势反转 | `test_sar_trend_reversal` | 价格突破 SAR 时趋势反转 |
| TI-009 | TrendIndicatorCalculator 初始化 | `test_initialization` | 正确初始化计算器 |
| TI-010 | 链式调用 | `test_chaining` | 支持 add_macd().add_adx() 链式调用 |

### 动量指标测试 (test_momentum_indicators.py) ✅ 已完成

| 用例 ID | 测试项 | 状态 |
|---------|--------|------|
| MI-001 | RSI 基础计算 | ✅ |
| MI-002 | RSI 超买超卖 | ✅ |
| MI-003 | ROC 基础计算 | ✅ |
| MI-004 | CCI 基础计算 | ✅ |
| MI-005 | Stochastic 计算 | ✅ |
| MI-006 | RSI 信号检测 | ✅ |
| MI-007 | Stochastic 信号检测 | ✅ |
| MI-008 | 动量得分计算 | ✅ |

### 移动平均线测试 (test_moving_average.py) ✅ 已完成

| 用例 ID | 测试项 | 状态 |
|---------|--------|------|
| MA-001 | MA 基础计算 | ✅ |
| MA-002 | 多周期 MA | ✅ |
| MA-003 | 金叉/死叉检测 | ✅ |
| MA-004 | MA 排列检测 | ✅ |
| MA-005 | 边界情况处理 | ✅ |

---

## 📊 大盘指标模块测试用例

### API 测试 (test_market_api.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| MO-001 | 获取指数列表 | `test_get_indices` | 返回主要指数数据 |
| MO-002 | 获取 K 线数据 | `test_get_kline_data` | 返回 OHLCV 数据 |
| MO-003 | 获取市场统计 | `test_get_market_stats` | 返回成交量、涨跌比等 |
| MO-004 | 实时行情查询 | `test_get_realtime_quote` | 返回最新价格 |
| MO-005 | 数据刷新机制 | `test_refresh_mechanism` | 支持定时刷新 |

### 组件测试 (test_market_components.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| MC-001 | 指数卡片渲染 | `test_index_card_render` | 正确显示指数名称和价格 |
| MC-002 | 涨跌幅颜色 | `test_change_color` | 涨红跌绿 |
| MC-003 | K 线图渲染 | `test_kline_chart_render` | 正确绘制 K 线图 |
| MC-004 | 时间周期切换 | `test_period_switch` | 日/周/月切换正常 |
| MC-005 | 刷新按钮 | `test_refresh_button` | 点击刷新数据 |

---

## 🤖 AI 建议模块测试用例

### API 测试 (test_ai_api.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| AI-001 | 获取 AI 建议 | `test_get_advice` | 返回投资建议 |
| AI-002 | 置信度分级 | `test_confidence_level` | 高/中/低置信度 |
| AI-003 | 推荐股票列表 | `test_get_recommendations` | 返回推荐标的 |
| AI-004 | 详细分析 | `test_get_analysis` | 返回详细分析 |
| AI-005 | 策略回测 | `test_backtest` | 返回回测结果 |

### 逻辑测试 (test_ai_logic.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| AL-001 | 仓位建议计算 | `test_position_calculation` | 根据置信度计算仓位 |
| AL-002 | 支撑阻力位 | `test_support_resistance` | 正确计算关键价位 |
| AL-003 | 风险提示生成 | `test_risk_warning` | 生成风险列表 |
| AL-004 | 目标价计算 | `test_target_price` | 基于估值计算目标价 |

---

## 📰 新闻资讯模块测试用例

### API 测试 (test_news_api.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| NF-001 | 获取新闻列表 | `test_get_news` | 返回新闻列表 |
| NF-002 | 分类筛选 | `test_category_filter` | 按重要/市场/行业/公司筛选 |
| NF-003 | 来源筛选 | `test_source_filter` | 按来源筛选 |
| NF-004 | 新闻详情 | `test_get_news_detail` | 返回详细内容 |
| NF-005 | 分页加载 | `test_pagination` | 支持分页 |

### 组件测试 (test_news_components.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| NC-001 | 新闻列表渲染 | `test_news_list_render` | 正确显示新闻 |
| NC-002 | 重要性标记 | `test_importance_badge` | 不同颜色标记 |
| NC-003 | 时间格式化 | `test_time_format` | 显示相对时间 |
| NC-004 | 来源筛选器 | `test_source_filter_ui` | 下拉筛选正常 |
| NC-005 | 加载更多 | `test_load_more` | 点击加载更多 |

---

## 🔧 工具函数测试用例

### 格式化工具 (test_format_utils.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| UT-001 | 数字格式化 | `test_format_number` | 12.35 亿 |
| UT-002 | 百分比格式化 | `test_format_percent` | +1.23% / -0.45% |
| UT-003 | 价格格式化 | `test_format_price` | 3,245.67 |
| UT-004 | 时间格式化 | `test_format_time` | 2 分钟前 |

### 数据验证 (test_validation.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| VU-001 | DataFrame 验证 | `test_validate_dataframe` | 检查必需列 |
| VU-002 | 空数据处理 | `test_empty_data` | 优雅处理空数据 |
| VU-003 | 异常值处理 | `test_outlier_handling` | 处理异常值 |

---

## 📈 集成测试用例

### 端到端测试 (test_integration.py)

| 用例 ID | 测试项 | 测试方法 | 预期结果 |
|---------|--------|----------|----------|
| IT-001 | 数据流完整性 | `test_data_flow` | 从 API 到组件数据完整 |
| IT-002 | 状态管理 | `test_state_management` | Zustand 状态正确更新 |
| IT-003 | 错误处理 | `test_error_handling` | API 错误优雅降级 |
| IT-004 | 性能测试 | `test_performance` | 首屏加载 < 2s |
| IT-005 | 内存泄漏检测 | `test_memory_leak` | 无内存泄漏 |

---

## ✅ 验收标准

- [x] 量化指标模块测试覆盖率 ≥ 85%
- [ ] 大盘指标模块测试覆盖率 ≥ 80%
- [ ] AI 建议模块测试覆盖率 ≥ 75%
- [ ] 新闻资讯模块测试覆盖率 ≥ 75%
- [ ] 所有 P0 测试用例通过
- [ ] 无严重 Bug (P0/P1)

---

## 📝 测试执行记录

### 第一轮测试 (2026-03-05)

| 测试文件 | 通过 | 失败 | 跳过 | 覆盖率 |
|---------|------|------|------|--------|
| test_moving_average.py | 25 | 0 | 0 | 92% |
| test_momentum_indicators.py | 32 | 0 | 0 | 89% |
| test_trend_indicators.py | - | - | - | - |
| test_utils.py | - | - | - | - |

**总计:** 57/57 通过 (100%)

---

*文档版本：v1.0 | 下次更新：根据测试执行情况*
