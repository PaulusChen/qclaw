# Tauri 桌面应用配置指南

**创建时间:** 2026-03-06  
**状态:** ✅ 配置完成

---

## 📦 项目结构

```
qclaw/
├── src-tauri/              # Tauri 桌面应用
│   ├── tauri.conf.json    # Tauri 配置
│   ├── Cargo.toml         # Rust 依赖
│   └── src/
│       └── main.rs        # Rust 主入口
├── webui/                  # React 前端
│   └── dist/              # 构建输出
└── docs/
    └── design/
        └── TAURI-SETUP-GUIDE.md
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Tauri CLI
cargo install tauri-cli

# 安装系统依赖 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf
```

### 2. 开发模式

```bash
cd /home/openclaw/.openclaw/workspace-qclaw
cargo tauri dev
```

### 3. 构建发布

```bash
cargo tauri build
```

**输出:**
- Linux: `src-tauri/target/release/bundle/deb/*.deb`
- macOS: `src-tauri/target/release/bundle/dmg/*.dmg`
- Windows: `src-tauri/target/release/bundle/msi/*.msi`

---

## 📊 配置说明

### tauri.conf.json

| 配置项 | 值 | 说明 |
|--------|-----|------|
| productName | QCLaw | 应用名称 |
| version | 1.0.0 | 版本号 |
| width | 1400 | 窗口宽度 |
| height | 900 | 窗口高度 |
| devUrl | http://localhost:3000 | 开发服务器地址 |

### Cargo.toml

| 依赖 | 版本 | 说明 |
|------|------|------|
| tauri | 2.x | Tauri 核心 |
| tauri-plugin-shell | 2.x | Shell 插件 |
| serde | 1.x | 序列化 |

---

## 🎯 优势对比

| 指标 | Tauri | Electron | 提升 |
|------|-------|----------|------|
| **打包体积** | 3-5 MB | 100+ MB | **20-30 倍** |
| **内存占用** | 50 MB | 300+ MB | **6 倍** |
| **启动速度** | < 1s | 2-3s | **3 倍** |
| **安全性** | Rust 后端 | Node.js | **更高** |

---

## 📝 下一步

1. ✅ 创建 Rust 主入口 (`src/main.rs`)
2. ⏳ 添加应用图标
3. ⏳ 实现系统托盘
4. ⏳ 添加自动更新功能
5. ⏳ 打包测试

---

**状态:** 🟡 配置完成，待开发
