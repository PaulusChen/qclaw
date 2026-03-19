# QClaw 用户配置系统 - 实现进度

## ✅ 已完成

### 1. 前端重构
- [x] 将 Vue + React 混用改为纯 React
- [x] Dashboard 组件用 React 重写
- [x] 移除 Vue 相关依赖
- [x] 构建成功，包体积减少 37%

### 2. 数据库设计
- [x] 创建数据库 Schema (`server/database/schema.py`)
  - `User` - 用户表
  - `DashboardConfig` - 仪表盘配置表
  - `WatchlistStock` - 自选股表
  - `AlertRule` - 预警规则表
  - `UserPreference` - 用户偏好表

- [x] 数据库初始化模块 (`server/database/__init__.py`)
  - SQLAlchemy 引擎配置
  - 自动创建表
  - 会话管理

### 3. 用户认证 API
- [x] 注册接口 `POST /api/auth/register`
- [x] 登录接口 `POST /api/auth/login`
- [x] 获取用户信息 `GET /api/auth/me`
- [x] 更新用户资料 `PUT /api/auth/me`
- [x] JWT Token 认证
- [x] 密码加密（bcrypt）

### 4. 仪表盘配置 API
- [x] 获取配置列表 `GET /api/dashboard/configs`
- [x] 获取默认配置 `GET /api/dashboard/configs/default`
- [x] 创建配置 `POST /api/dashboard/configs`
- [x] 更新配置 `PUT /api/dashboard/configs/{id}`
- [x] 删除配置 `DELETE /api/dashboard/configs/{id}`
- [x] 获取可用组件 `GET /api/dashboard/widgets`

### 5. 后端集成
- [x] 更新 main.py 集成数据库初始化
- [x] 注册认证和配置路由
- [x] 更新 requirements.txt 添加新依赖

---

## ⏳ 进行中

### 6. Docker 镜像构建
- [ ] 重新构建 API 镜像（安装新依赖）
- [ ] 验证数据库初始化
- [ ] 测试 API 端点

---

## 📋 待实现

### 7. 前端用户界面
- [ ] 登录/注册页面
- [ ] 用户资料页面
- [ ] 仪表盘配置界面
- [ ] 组件拖拽布局
- [ ] 主题切换

### 8. 数据持久化
- [ ] 前端本地存储（localStorage）
- [ ] 与后端 API 同步
- [ ] 配置导入/导出

### 9. 高级功能
- [ ] 自选股管理
- [ ] 价格预警
- [ ] 多设备同步
- [ ] 数据导出（CSV/Excel）

---

## 🗄️ 数据库表结构

### User (用户表)
```sql
id              INTEGER PRIMARY KEY
username        VARCHAR(50) UNIQUE NOT NULL
email           VARCHAR(100) UNIQUE NOT NULL
password_hash   VARCHAR(255) NOT NULL
nickname        VARCHAR(50)
avatar_url      VARCHAR(255)
is_active       BOOLEAN DEFAULT TRUE
created_at      DATETIME
updated_at      DATETIME
last_login_at   DATETIME
```

### DashboardConfig (仪表盘配置表)
```sql
id                INTEGER PRIMARY KEY
user_id           INTEGER FOREIGN KEY
name              VARCHAR(100)
is_default        BOOLEAN DEFAULT FALSE
layout_config     JSON
enabled_widgets   JSON
theme_config      JSON
refresh_interval  INTEGER DEFAULT 30
created_at        DATETIME
updated_at        DATETIME
```

### WatchlistStock (自选股表)
```sql
id            INTEGER PRIMARY KEY
user_id       INTEGER FOREIGN KEY
stock_code    VARCHAR(20) NOT NULL
stock_name    VARCHAR(50)
market        VARCHAR(20)
group_name    VARCHAR(50)
sort_order    INTEGER DEFAULT 0
note          TEXT
created_at    DATETIME
```

### AlertRule (预警规则表)
```sql
id                    INTEGER PRIMARY KEY
user_id               INTEGER FOREIGN KEY
name                  VARCHAR(100) NOT NULL
stock_code            VARCHAR(20) NOT NULL
alert_type            VARCHAR(20) NOT NULL
threshold             FLOAT NOT NULL
is_active             BOOLEAN DEFAULT TRUE
notification_methods  JSON
triggered_count       INTEGER DEFAULT 0
last_triggered_at     DATETIME
created_at            DATETIME
updated_at            DATETIME
```

### UserPreference (用户偏好表)
```sql
id            INTEGER PRIMARY KEY
user_id       INTEGER UNIQUE FOREIGN KEY
preferences   JSON
created_at    DATETIME
updated_at    DATETIME
```

---

## 🔑 API 使用示例

### 用户注册
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "nickname": "测试用户"
  }'
```

### 用户登录
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 获取仪表盘配置
```bash
curl -X GET http://localhost:8000/api/dashboard/configs \
  -H "Authorization: Bearer <access_token>"
```

### 创建新配置
```bash
curl -X POST http://localhost:8000/api/dashboard/configs \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的配置",
    "enabled_widgets": ["market_indices", "watchlist", "news"],
    "theme_config": {"theme": "dark"},
    "refresh_interval": 60
  }'
```

---

## 📅 更新日期

**2026-03-11** - 完成数据库设计和 API 实现
