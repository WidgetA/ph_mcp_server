# Product Hunt MCP Server - 项目总结

## 🎯 项目概述

这是一个基于 MCP (Model Context Protocol) 的远程服务器，提供 Product Hunt 数据访问能力。

**特点**:
- ✅ HTTP/SSE 远程模式，监听 8080 端口
- ✅ 使用 uv 进行快速包管理
- ✅ 专为 Ubuntu 服务器优化
- ✅ 完整的 systemd 服务集成

## 📁 项目结构

```
ph_mcp_server/
├── 📄 核心文件
│   ├── server.py              # MCP HTTP/SSE 服务器 (8080端口)
│   ├── config.py              # 配置管理
│   ├── pyproject.toml         # uv 项目配置
│   ├── .python-version        # Python 3.10
│   ├── .env.example           # 环境变量模板
│   └── requirements.txt       # pip 兼容（备份）
│
├── 📦 服务模块
│   └── services/
│       ├── __init__.py
│       └── supabase_service.py  # Supabase 数据库服务
│
├── 🧪 测试
│   └── tests/
│       ├── __init__.py
│       └── test_server.py
│
├── 🚀 部署文件 (Ubuntu)
│   └── deploy/
│       ├── deploy.sh          # 自动部署脚本
│       ├── update.sh          # 更新脚本
│       ├── ph-mcp-server.service  # systemd 服务
│       ├── nginx.conf         # Nginx 反向代理配置
│       └── README.md          # 完整部署指南
│
├── 🔧 脚本
│   ├── setup.sh               # 自动安装和配置
│   ├── start.sh               # 启动服务器
│   ├── Makefile               # 常用命令快捷方式
│   └── setup.py               # 交互式配置（保留）
│
└── 📚 文档
    ├── README.md              # 主文档
    ├── QUICKSTART.md          # 5分钟快速开始
    ├── DEVELOPMENT.md         # 开发指南
    ├── CHANGELOG.md           # 更新日志
    └── PROJECT_SUMMARY.md     # 本文件
```

## 🔧 技术栈

### 核心技术
- **Python 3.10+**
- **MCP SDK 1.1.0+** - Model Context Protocol
- **Starlette + uvicorn** - HTTP/SSE 服务器
- **uv** - 快速包管理器

### 数据和存储
- **Supabase** - PostgreSQL 数据库
- **pydantic-settings** - 配置管理

### 部署和运维
- **systemd** - Ubuntu 服务管理
- **Nginx** - 反向代理（可选）

## 🚀 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone <repository-url>
cd ph_mcp_server

# 2. 自动设置
chmod +x setup.sh
./setup.sh

# 3. 配置环境
nano .env  # 填入 Supabase 配置

# 4. 启动服务
make run
# 或
./start.sh
```

### Ubuntu 服务器部署

```bash
# 1. 上传项目
scp -r ph_mcp_server user@server:/tmp/

# 2. SSH 到服务器并部署
ssh user@server
cd /tmp/ph_mcp_server
sudo bash deploy/deploy.sh

# 3. 配置环境变量
sudo nano /opt/ph_mcp_server/.env

# 4. 启动服务
sudo systemctl start ph-mcp-server
sudo systemctl enable ph-mcp-server

# 5. 查看状态
sudo systemctl status ph-mcp-server
sudo journalctl -u ph-mcp-server -f
```

## 🛠️ 常用命令

### Make 命令（推荐）

```bash
make help         # 显示所有命令
make install      # 安装依赖
make dev          # 安装开发依赖
make sync         # 同步所有依赖
make run          # 启动服务器
make test         # 运行测试
make clean        # 清理临时文件
```

### uv 命令

```bash
uv sync                    # 同步依赖
uv add package-name        # 添加依赖
uv add --dev package-name  # 添加开发依赖
uv remove package-name     # 移除依赖
uv run server.py           # 运行服务器
uv run pytest tests/       # 运行测试
```

### systemd 命令（Ubuntu）

```bash
sudo systemctl start ph-mcp-server      # 启动
sudo systemctl stop ph-mcp-server       # 停止
sudo systemctl restart ph-mcp-server    # 重启
sudo systemctl status ph-mcp-server     # 状态
sudo journalctl -u ph-mcp-server -f     # 查看日志
sudo systemctl enable ph-mcp-server     # 开机自启
sudo systemctl disable ph-mcp-server    # 禁用自启
```

## 🔌 MCP 工具列表

服务器提供 7 个 MCP 工具：

1. **get_latest_products** - 获取最新产品列表
2. **get_products_by_date** - 按日期查询产品
3. **search_products** - 关键词搜索产品
4. **get_top_products** - 获取热门产品（按投票）
5. **get_latest_report** - 获取最新报告
6. **get_report_by_date** - 按日期获取报告
7. **get_reports_by_date_range** - 按日期范围获取报告

## 🌐 API 端点

- **根路径**: `http://localhost:8080/` - 服务器信息
- **健康检查**: `http://localhost:8080/health` - 健康状态
- **MCP 端点**: `http://localhost:8080/sse` - MCP 连接

## 📊 配置项

### 环境变量 (.env)

```env
# Supabase 配置（必需）
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# 数据库表名
PRODUCTS_TABLE=ph_products
REPORTS_TABLE=ph_daily_reports

# 服务器配置
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
```

## 🔐 安全建议

1. **使用非 root 用户** - systemd 服务使用 www-data
2. **配置防火墙** - 只开放必要端口
3. **使用 HTTPS** - Nginx + Let's Encrypt
4. **定期更新** - 系统和依赖包
5. **备份数据** - .env 和数据库

## 📖 文档导航

- 🚀 [QUICKSTART.md](QUICKSTART.md) - 5 分钟快速开始
- 🔧 [DEVELOPMENT.md](DEVELOPMENT.md) - 完整开发指南
- 📘 [README.md](README.md) - 主文档和 API 说明
- 🚀 [deploy/README.md](deploy/README.md) - Ubuntu 部署指南
- 📝 [CHANGELOG.md](CHANGELOG.md) - 版本更新历史

## 🎓 使用示例

在 Claude Desktop 中，你可以这样使用：

```
"显示今天 Product Hunt 上的产品"
"搜索最近一周关于 AI 的产品"
"今天投票最多的 5 个产品是什么？"
"给我看看最新的每日报告"
"2024年11月10日有哪些产品上线？"
```

## 🔄 更新和维护

### 更新部署

```bash
# 使用更新脚本
sudo bash deploy/update.sh

# 或手动更新
cd /opt/ph_mcp_server
sudo git pull
sudo -u www-data uv sync --upgrade
sudo systemctl restart ph-mcp-server
```

### 查看日志

```bash
# 实时日志
sudo journalctl -u ph-mcp-server -f

# 查看今天的日志
sudo journalctl -u ph-mcp-server --since today

# 查看错误日志
sudo journalctl -u ph-mcp-server -p err
```

## 📞 获取帮助

- 📖 查看文档: [README.md](README.md)
- 🐛 报告问题: GitHub Issues
- 💬 讨论: GitHub Discussions

---

**版本**: 1.0.0
**更新时间**: 2024-11-12
**目标平台**: Ubuntu 20.04+ LTS
**Python 版本**: 3.10+
