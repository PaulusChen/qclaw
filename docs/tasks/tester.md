# Tester 任务列表

**负责人:** qclaw-tester  
**最后更新:** 2026-03-05 20:10  
**Cron:** 每 5 分钟自动检查

---

## 📍 工作流说明

**任务读取位置:** `docs/tasks/tester.md` (本文件)  
**交付物提交位置:** `tests/integration/`, `tests/e2e/`, `docs/reports/`  
**提交流程:**
```bash
git add tests/integration/ tests/e2e/ docs/reports/
git commit -m "[Test] 任务名称"
git push origin main
```

---

## 🔄 进行中

| 任务 ID | 任务名称 | 进度 | 备注 |
|---------|---------|------|------|
| TEST-INT-001 | API 集成测试 | 0% | 开始编写 |
| TEST-SYS-001 | Docker 系统测试 | 0% | 配置环境 |
| TEST-INT-002 | 数据库集成测试 | 0% | 依赖已满足，可启动 |
| TEST-E2E-001 | 端到端流程测试 | 0% | 依赖已满足，可启动 |

---

## ⏳ 待开始

| 任务 ID | 任务名称 | 依赖 | 优先级 |
|---------|---------|------|--------|
| TEST-PERF-001 | 性能基准测试 | CODE-006 | 中 |
| TEST-LOAD-001 | 负载压力测试 | CODE-006 | 低 |

---

## ✅ 已完成

| 任务 ID | 任务名称 | 完成日期 | 交付物 |
|---------|---------|----------|--------|
| TEST-MVP | MVP 功能测试和性能测试 | 2026-03-05 | `docs/test/test_report_2026-03-05.md` ✅ (已归档) |

---

## 📋 详细任务说明

### TEST-INT-001: API 集成测试 🔄

**描述:** 测试 API 模块间集成和数据流  
**依赖:** CODE-006 后端 API 完成  
**交付物:** `tests/integration/test_api_*.py`

**测试场景:**
- [ ] 大盘指标 API 集成测试
- [ ] 技术指标 API 集成测试
- [ ] AI 建议 API 集成测试
- [ ] 新闻资讯 API 集成测试
- [ ] 错误处理和异常流程
- [ ] 数据库事务测试
- [ ] Redis 缓存测试

**命令:**
```bash
docker-compose up -d
docker-compose exec -T api pytest tests/integration/ -v
```

### TEST-SYS-001: Docker 系统测试 🔄

**描述:** 在 Docker 环境中进行系统级自动化测试  
**交付物:** `tests/system/`, `scripts/test-docker.sh`

**测试内容:**
- [ ] Docker 容器启动测试
- [ ] 服务间通信测试
- [ ] 环境变量配置测试
- [ ] 数据持久化测试
- [ ] 健康检查测试
- [ ] 日志收集测试

**命令:**
```bash
# 启动完整系统
docker-compose up -d

# 运行系统测试
./scripts/test-system.sh

# 查看测试结果
docker-compose logs test
```

### TEST-INT-002: 数据库集成测试 ⏳

**描述:** 测试数据库操作和事务  
**依赖:** CODE-006 后端完成  
**交付物:** `tests/integration/test_database.py`

**测试范围:**
- [ ] 数据读写测试
- [ ] 事务回滚测试
- [ ] 并发访问测试
- [ ] 数据迁移测试

### TEST-E2E-001: 端到端流程测试 ⏳

**描述:** 完整用户流程的 E2E 测试  
**依赖:** CODE-006 前后端完成  
**技术栈:** Playwright  
**交付物:** `tests/e2e/`

**测试场景:**
- [ ] 用户访问首页 → 查看大盘指标
- [ ] 用户查看 AI 投资建议
- [ ] 用户查看新闻资讯
- [ ] 数据自动刷新流程
- [ ] 错误页面显示

**命令:**
```bash
cd tests/e2e
npx playwright test
```

### TEST-PERF-001: 性能基准测试 ⏳

**描述:** 系统性能基准测试  
**依赖:** CODE-006 完成  
**交付物:** `docs/reports/performance-benchmark.md`

**测试指标:**
- [ ] 页面加载时间 < 3s
- [ ] API 响应时间 < 500ms
- [ ] 图表渲染时间 < 1s
- [ ] 并发用户支持 > 100
- [ ] 内存使用 < 512MB
- [ ] CPU 使用率 < 80%

### TEST-LOAD-001: 负载压力测试 ⏳

**描述:** 高负载下的系统稳定性测试  
**依赖:** CODE-006 完成  
**技术栈:** locust  
**交付物:** `docs/reports/load-test-report.md`

**测试场景:**
- [ ] 100 并发用户
- [ ] 500 并发用户
- [ ] 1000 并发用户
- [ ] 长时间运行测试 (24h)

---

## 🐳 Docker 测试环境

### 本地测试

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
docker-compose exec test pytest tests/integration/ -v

# 运行系统测试
docker-compose exec test pytest tests/system/ -v

# 查看测试报告
docker-compose logs test

# 停止测试环境
docker-compose -f docker-compose.test.yml down
```

### CI/CD 测试

```bash
# GitHub Actions 自动运行
# 参考 .github/workflows/ci.yml
```

---

## 📊 测试覆盖率目标

| 测试类型 | 负责角色 | 覆盖率目标 |
|---------|---------|-----------|
| 单元测试 | Coder | >80% |
| 集成测试 | Tester | >60% |
| E2E 测试 | Tester | 核心流程 100% |
| 系统测试 | Tester | 关键服务 100% |

---

## 📝 测试规范

### 集成测试命名
```python
def test_api_market_indices_success():
    """测试大盘指标 API 成功场景"""
    pass

def test_api_advice_daily_with_cache():
    """测试 AI 建议 API 缓存场景"""
    pass
```

### 系统测试脚本
```bash
#!/bin/bash
# tests/system/run.sh
docker-compose up -d
sleep 30
pytest tests/system/ -v
docker-compose down
```

---

**说明:** 
- ✅ 专注于集成测试和系统测试
- ✅ 使用 Docker 环境进行自动化测试
- ✅ 单元测试由 Coder 负责
