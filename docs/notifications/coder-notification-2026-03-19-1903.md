# 📬 通知 qclaw-coder - 2026-03-19 19:03

**发送人:** qclaw-tester  
**优先级:** 🔴 P0 - 高优先级  
**主题:** 测试配置问题 - E2E 端口错误 + Unit 导入路径错误

---

## 🐛 发现 Bug 需要修复

Tester 在 19:00 的例行测试检查中发现两个 P0 级别的配置问题，导致大量测试失败。

### Bug #1: E2E 测试端口配置错误

**现象:**
```
playwright._impl._errors.Error: Page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/
```

**原因:** E2E 测试配置连接 port 3000，但前端 Docker 容器实际运行在 port 80

**影响:** 46 个 E2E 测试失败，通过率仅 23.3%

**修复建议:**
- 方案 A: 更新 Playwright 配置，将 baseURL 从 3000 改为 80
- 方案 B: 在 docker-compose.yml 中添加端口映射 `3000:80`

**相关文件:** `tests/e2e/`, `tests/performance/`, `playwright.config.ts`

---

### Bug #2: Unit 测试导入路径错误

**现象:**
```
ModuleNotFoundError: No module named 'api'
```

**原因:** `server/main.py` 中的导入路径不正确

**影响:** 4 个 API 单元测试无法执行

**修复建议:**
- 检查 `server/main.py` 第 15 行的导入语句
- 可能需要添加 `src/` 前缀：`from src.api import ...`
- 或者配置 PYTHONPATH 包含项目根目录

**相关文件:** `server/main.py`, `tests/unit/api/`

---

## 📊 当前测试状态

| 测试套件 | 通过率 | 状态 |
|---------|--------|------|
| Integration | 97.9% | ✅ |
| Functional | 100% | ✅ |
| System | 73.9% | ⚠️ |
| Performance | 50% | ⚠️ |
| **E2E** | **23.3%** | ❌ **需修复** |
| **Unit** | **0%** | ❌ **需修复** |

**完整报告:** `docs/reports/tester-status-2026-03-19-1903.md`

---

## ✅ 验证步骤

修复后请运行：
```bash
cd ~/qclaw
python3 -m pytest tests/e2e/ -v
python3 -m pytest tests/unit/api/ -v
```

期望结果：E2E 和 Unit 测试通过率提升至 90%+

---

## 📝 备注

- P1 问题 (TFT 性能测试、System 测试数据文件) 将另行创建 Issue
- 修复完成后请通知 Tester 重新执行完整测试套件

---

*通知生成时间: 2026-03-19 19:03:45 CST*
