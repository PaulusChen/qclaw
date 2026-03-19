# QClaw Coder - 开发记录

## 2026-03-09: Docker 端口映射配置（局域网访问）

### 需求
让 192.168.50.0/24 网段的其他机器可以访问 QClaw 服务

### 物理 IP 地址
- **主机 IP:** 192.168.50.105

### 端口映射配置
修改 `docker-compose.yml`，将所有服务端口绑定到 `0.0.0.0`（所有网卡）：

```yaml
services:
  api:
    ports:
      - "0.0.0.0:8000:8000"  # API 服务
  frontend:
    ports:
      - "0.0.0.0:80:80"      # 前端服务
  redis:
    ports:
      - "0.0.0.0:6379:6379"  # Redis（可选）
```

### 访问地址
同一网段（192.168.50.0/24）的其他机器可通过以下地址访问：
- **API:** http://192.168.50.105:8000
- **前端:** http://192.168.50.105:80
- **Redis:** 192.168.50.105:6379（如需外部访问）

### 防火墙检查
- UFW 状态：未激活（无需额外配置）

### 注意事项
- 端口绑定到 0.0.0.0 表示监听所有网卡
- 确保路由器/防火墙允许相应端口的入站连接
- Redis 端口仅在内网暴露，建议不要对外开放

---

## 2026-03-09: Docker 构建网络问题修复

### 问题描述
Docker 容器构建时无法访问 PyPI，SSL 连接失败：
```
SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF)'))
ERROR: Could not find a version that satisfies the requirement fastapi>=0.109.0
```

### 根本原因
1. Docker 守护进程配置了代理，但代理地址与实际可用代理不一致
2. 任务描述中的代理配置 `http://bL8qpf@10.0.50.106:7890` 不可用
3. 实际可用的代理配置来自 Docker 守护进程：`http://clash:bH8qpf@192.168.50.106:7890`

### 解决方案
配置 Docker 使用正确的 Clash 代理（http://clash:bH8qpf@192.168.50.106:7890）：

#### 1. Dockerfile 添加代理环境变量
```dockerfile
ENV HTTP_PROXY=http://clash:bH8qpf@192.168.50.106:7890
ENV HTTPS_PROXY=http://clash:bH8qpf@192.168.50.106:7890
ENV NO_PROXY=localhost,127.0.0.1,192.168.0.0/16,*.paulchen.cn
```

#### 2. docker-compose.yml 添加代理环境变量
在 `api` 和 `test` 服务中添加：
```yaml
environment:
  - HTTP_PROXY=http://clash:bH8qpf@192.168.50.106:7890
  - HTTPS_PROXY=http://clash:bH8qpf@192.168.50.106:7890
  - NO_PROXY=localhost,127.0.0.1,192.168.0.0/16,*.paulchen.cn
```

#### 3. Docker 客户端配置 ~/.docker/config.json
```json
{
  "proxies": {
    "default": {
      "httpProxy": "http://clash:bH8qpf@192.168.50.106:7890",
      "httpsProxy": "http://clash:bH8qpf@192.168.50.106:7890",
      "noProxy": "localhost,127.0.0.1,192.168.0.0/16,*.paulchen.cn"
    }
  }
}
```

### 验证结果
```bash
cd ~/qclaw
docker compose build api
# ✅ 构建成功，所有依赖安装完成
```

### 代理来源
Docker 守护进程配置：`systemctl show docker --property=Environment`
实际可用代理：`http://clash:bH8qpf@192.168.50.106:7890`

### 注意事项
- 不要使用 ~/clash_proxy.sh 中的代理配置（10.0.50.106 不可达）
- 使用 Docker 守护进程中配置的实际可用代理（192.168.50.106）

---

## 2026-03-19 21:03 - Tester 发现的 P0 Bug 修复任务

**来源:** QClaw Tester 自动检查 (Cron: qclaw-tester-check)  
**优先级:** P0 (阻塞测试执行)  
**状态:** 🔄 待修复

### Bug #1: E2E 测试端口配置错误

**问题描述:**
E2E 测试用例中硬编码的前端地址 `localhost:3000` 与实际运行端口 `localhost:80` 不匹配，导致 46 个 E2E 测试失败。

**影响范围:**
- `tests/e2e/test_user_flows.py` - 所有测试用例 (约 12 个)
- `tests/e2e/test_edge_cases.py` - 部分测试用例 (约 4 个)
- `tests/e2e/test_error_handling.py` - 部分测试用例 (约 4 个)
- 总计：约 46 个 E2E 测试失败

**修复方案:**
将所有 E2E 测试中的前端 URL 从 `localhost:3000` 改为 `localhost:80`

**修改文件:**
```bash
# 方案 1: 直接替换
sed -i 's|localhost:3000|localhost:80|g' tests/e2e/*.py

# 方案 2: 使用环境变量 (推荐)
# 在 tests/e2e/conftest.py 中定义:
# BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:80")
```

**验证方法:**
```bash
cd ~/qclaw
python3 -m pytest tests/e2e/ -v --tb=short
# 预期：E2E 测试通过率从 23.3% 提升至 90%+
```

---

### Bug #2: Unit 测试导入路径/依赖问题

**问题描述:**
Unit 测试无法执行，原因有两个：
1. server/venv 虚拟环境缺少 fastapi 等核心依赖
2. pytest 运行时 PYTHONPATH 配置不正确

**错误信息:**
```
ModuleNotFoundError: No module named 'fastapi'
ModuleNotFoundError: No module named 'api'
```

**影响范围:**
- `tests/unit/api/test_advice_api.py` - 无法执行
- `tests/unit/api/test_dl_api.py` - 无法执行
- `tests/unit/api/test_health_api.py` - 无法执行
- `tests/unit/api/test_market_api.py` - 无法执行
- 总计：4 个 Unit 测试文件无法收集

**修复方案:**

**方案 A: 安装依赖 (推荐)**
```bash
cd ~/qclaw
source server/venv/bin/activate
pip install -r server/requirements.txt pytest pytest-mock
```

**方案 B: 修复 pytest 路径配置**
修改 `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
env =
    PYTHONPATH=server
```

**验证方法:**
```bash
cd ~/qclaw
source server/venv/bin/activate
PYTHONPATH=server python3 -m pytest tests/unit/api/ -v --tb=short
# 预期：4 个测试文件正常收集并执行
```

---

### Bug #3: System 测试缺少数据文件 (P1)

**问题描述:**
System 测试需要真实股票数据和模型检查点，但文件不存在。

**缺少文件:**
- `data/real/600519_贵州茅台.csv`
- `checkpoints/lstm_real_600519.pth`

**影响:** `tests/system/test_full_pipeline.py` 全部失败

**修复方案:**
1. 下载真实股票数据到 `data/real/` 目录
2. 训练或下载预训练模型到 `checkpoints/` 目录
3. 或：修改测试使用模拟数据

---

### Bug #4: TFT 性能测试代码错误 (P1)

**错误信息:**
```
TypeError: tuple indices must be integers or slices, not tuple
AttributeError: 'Output' object has no attribute 'shape'
```

**影响:** `tests/performance/` 中约 50% 测试失败

**修复方案:** 检查 TFT 模型输出处理代码，修复类型错误

---

### Bug #5: 语法错误 (P2)

**文件:** `tests/system/test_load_stress.py:161`  
**问题:** 缩进错误  
**修复:** 修正缩进

---

### 修复后验证清单

- [ ] E2E 测试通过率 > 90%
- [ ] Unit 测试全部执行通过
- [ ] System 测试数据文件准备完成
- [ ] Performance 测试代码修复
- [ ] 语法错误修正

**通知:** 修复完成后请通知 qclaw-tester 重新执行测试验证
