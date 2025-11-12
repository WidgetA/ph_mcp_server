# Product Hunt MCP Server

一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的 Product Hunt 数据服务器，让 AI 助手（如 Claude、ChatGPT 等）能够直接访问和查询 Product Hunt 的产品数据和报告。

**运行模式**: HTTP/SSE 远程服务器（监听在 8080 端口）

## 功能特性

- 🔍 **产品查询**: 获取最新的 Product Hunt 产品列表
- 📅 **日期查询**: 按指定日期查询历史产品数据
- 🔎 **产品搜索**: 支持按关键词搜索产品（名称、标语、描述）
- 🏆 **热门产品**: 获取指定日期投票数最多的产品
- 📊 **每日报告**: 获取 AI 生成的每日产品分析报告
- 📈 **报告查询**: 按日期或日期范围查询历史报告
- 🌐 **远程访问**: 支持通过 HTTP/SSE 协议远程访问

## 系统要求

- Python 3.10+
- pip (Python 包管理器)
- 访问已部署的 ph_bot 项目的 Supabase 数据库
- 开放 8080 端口（或自定义端口）

> **📦 包管理**: 本项目使用 `pip + venv` 进行包管理，稳定可靠，适合生产环境。
>
> 更多详细文档请参考：
> - 🚀 [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
> - 🔧 [DEVELOPMENT.md](DEVELOPMENT.md) - 完整开发指南
> - 🐳 [CONTAINER_SETUP.md](CONTAINER_SETUP.md) - 容器环境配置

## 快速开始

### 方式一：自动安装（推荐）

使用自动设置脚本，一键完成环境配置：

```bash
# 克隆项目
git clone <repository-url>
cd ph_mcp_server

# 运行自动设置脚本
chmod +x setup.sh
./setup.sh

# 配置环境变量
cp .env.example .env
nano .env  # 填入 Supabase 配置

# 启动服务器
python server.py
```

### 方式二：手动安装

#### 1. 克隆项目

```bash
git clone <repository-url>
cd ph_mcp_server
```

#### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
```

#### 3. 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 或使用 Makefile
make install
```

#### 4. 配置环境变量

复制 `.env.example` 并重命名为 `.env`，然后填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Database Tables
PRODUCTS_TABLE=ph_products
REPORTS_TABLE=ph_daily_reports

# Server Configuration
MCP_SERVER_PORT=8080
MCP_SERVER_HOST=0.0.0.0
```

#### 5. 启动服务器

**方式 1: 使用 Makefile（推荐）**

```bash
make run
```

**方式 2: 使用启动脚本**

```bash
chmod +x start.sh
./start.sh
```

**方式 3: 直接运行**

```bash
python server.py
```

服务器启动后，你会看到类似的输出：
```
============================================================
Product Hunt MCP Server (Remote HTTP Mode)
============================================================
服务器地址: http://0.0.0.0:8080
健康检查: http://0.0.0.0:8080/health
MCP 端点: http://0.0.0.0:8080/sse
============================================================
```

#### 6. 验证服务器

在浏览器或使用 curl 访问健康检查端点：

```bash
curl http://localhost:8080/health
```

应该返回：
```json
{
  "status": "healthy",
  "service": "Product Hunt MCP Server",
  "version": "1.0.0",
  "mode": "remote",
  "port": 8080
}
```

## 配置 MCP 客户端

### 在 Claude Desktop 中配置

编辑 Claude Desktop 的配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

**远程服务器模式配置**（推荐）：

```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

或者如果服务器在其他机器上：

```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "http://your-server-ip:8080/sse"
    }
  }
}
```

**注意**:
- 确保 MCP server 已经启动
- 如果服务器在远程机器上，确保防火墙允许 8080 端口访问
- 重启 Claude Desktop 后生效

## 在其他 MCP 客户端中使用

### ChatGPT / Cursor / 其他 MCP 客户端

所有支持 MCP 协议的客户端都可以通过 SSE URL 连接到服务器：

```
http://localhost:8080/sse
```

或远程服务器：
```
http://your-server-ip:8080/sse
```

## 服务器配置选项

可以通过环境变量自定义服务器配置：

```bash
# 自定义端口
export MCP_SERVER_PORT=9000

# 自定义监听地址（默认 0.0.0.0 允许所有 IP 访问）
export MCP_SERVER_HOST=127.0.0.1

# 启动服务器
python server.py
```

或在 [.env](.env) 文件中添加：
```env
MCP_SERVER_PORT=9000
MCP_SERVER_HOST=127.0.0.1
```

## 部署到生产环境

### Ubuntu 服务器部署（推荐）

使用提供的自动部署脚本：

```bash
# 1. 上传项目到服务器
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
```

详细部署文档请参考：[deploy/README.md](deploy/README.md)

### 手动使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/ph-mcp-server.service`:

```ini
[Unit]
Description=Product Hunt MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ph_mcp_server
Environment="PATH=/path/to/.venv/bin"
ExecStart=/path/to/.venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable ph-mcp-server
sudo systemctl start ph-mcp-server
sudo systemctl status ph-mcp-server
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 可用工具 (Tools)

### 1. get_latest_products

获取最新的 Product Hunt 产品列表。

**参数**:
- `days_ago` (可选): 获取几天前的数据，默认为 0（今天）
- `limit` (可选): 返回的产品数量限制，默认 50

**示例**:
```
获取今天的 Product Hunt 产品列表
获取昨天的前 10 个产品
```

### 2. get_products_by_date

根据指定日期获取产品列表。

**参数**:
- `date` (必需): 日期，格式为 YYYY-MM-DD
- `limit` (可选): 返回的产品数量限制，默认 50

**示例**:
```
获取 2024-03-15 的产品列表
```

### 3. search_products

搜索产品（按名称、标语或描述）。

**参数**:
- `keyword` (必需): 搜索关键词
- `days` (可选): 搜索最近多少天的数据，默认 7 天
- `limit` (可选): 返回的产品数量限制，默认 20

**示例**:
```
搜索包含 "AI" 的产品
搜索最近 30 天内关于 "design" 的产品
```

### 4. get_top_products

获取指定日期投票数最多的热门产品。

**参数**:
- `date` (可选): 日期，格式为 YYYY-MM-DD，默认为今天
- `limit` (可选): 返回的产品数量，默认 10

**示例**:
```
获取今天最热门的 10 个产品
获取 2024-03-15 投票数最多的 5 个产品
```

### 5. get_latest_report

获取最新的每日报告。

**参数**: 无

**示例**:
```
显示最新的 Product Hunt 每日报告
```

### 6. get_report_by_date

根据指定日期获取报告。

**参数**:
- `date` (必需): 日期，格式为 YYYY-MM-DD

**示例**:
```
获取 2024-03-15 的报告
```

### 7. get_reports_by_date_range

获取指定日期范围内的所有报告。

**参数**:
- `start_date` (必需): 开始日期，格式为 YYYY-MM-DD
- `end_date` (必需): 结束日期，格式为 YYYY-MM-DD

**示例**:
```
获取 2024-03-01 到 2024-03-15 之间的所有报告
```

## 使用示例

在 Claude Desktop 或其他 MCP 客户端中，你可以这样使用：

1. **查看今天的产品**:
   > "显示今天 Product Hunt 上的产品"

2. **搜索特定主题的产品**:
   > "搜索最近一周关于 AI 的产品"

3. **查看热门产品**:
   > "今天 Product Hunt 上投票最多的 5 个产品是什么？"

4. **查看每日报告**:
   > "给我看看最新的 Product Hunt 每日分析报告"

5. **历史数据查询**:
   > "2024年3月15日有哪些产品上线？"

## 数据结构

### Product 对象

```json
{
  "id": 123,
  "product_id": "ph_product_id",
  "name": "Product Name",
  "tagline": "Product tagline",
  "description": "Product description",
  "website": "https://example.com",
  "topics": ["AI", "Design"],
  "votes_count": 1234,
  "comments_count": 56,
  "rank": 1,
  "ph_url": "https://producthunt.com/...",
  "thumbnail_url": "https://...",
  "featured_at": "2024-03-15T00:00:00",
  "fetch_date": "2024-03-15T09:30:00"
}
```

### Report 对象

```json
{
  "id": 1,
  "report_content": "# Product Hunt 每日报告...",
  "report_date": "2024-03-15",
  "created_at": "2024-03-15T10:00:00"
}
```

## 项目结构

```
ph_mcp_server/
├── server.py              # MCP server 主文件
├── config.py              # 配置管理
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── Makefile              # 常用命令快捷方式
├── pyproject.toml        # 项目配置
├── .env.example          # 环境变量示例
├── .env                  # 环境变量（不提交到 git）
├── .gitignore           # Git 忽略文件
├── README.md            # 项目文档
├── QUICKSTART.md        # 快速开始指南
├── DEVELOPMENT.md       # 开发指南
├── CONTAINER_SETUP.md   # 容器环境配置
├── services/            # 服务模块
│   ├── __init__.py
│   └── supabase_service.py  # Supabase 数据库服务
├── tests/               # 测试文件
│   ├── __init__.py
│   └── test_server.py
└── deploy/              # 部署文件
    ├── deploy.sh        # 自动部署脚本
    ├── update.sh        # 更新脚本
    ├── ph-mcp-server.service  # systemd 服务文件
    └── README.md        # 部署文档
```

## 开发

### 添加新依赖

```bash
# 安装新包
pip install package-name

# 更新 requirements.txt
pip freeze > requirements.txt

# 或手动添加到 requirements.txt
echo "package-name>=1.0.0" >> requirements.txt
pip install -r requirements.txt
```

### 更新依赖

```bash
# 更新所有依赖到最新版本
pip install --upgrade -r requirements.txt

# 或使用 Makefile
make upgrade
```

### 运行测试

```bash
# 使用 Makefile
make test

# 或直接运行
python tests/test_server.py

# 使用 pytest（需先安装开发依赖）
pip install -r requirements-dev.txt
pytest tests/
```

### 代码格式化

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 使用 black 格式化代码
black .

# 使用 ruff 检查代码
ruff check .

# 自动修复问题
ruff check --fix .
```

### 常用 Make 命令

```bash
make help       # 显示所有可用命令
make venv       # 创建虚拟环境
make install    # 安装生产依赖
make dev        # 安装开发依赖
make upgrade    # 升级所有依赖
make run        # 运行服务器
make test       # 运行测试
make clean      # 清理临时文件
```

### 调试

在 [server.py](server.py:28) 中已经配置了日志，运行时会输出详细的调试信息。

## 相关项目

- [ph_bot](https://github.com/yourusername/ph_bot) - Product Hunt 数据采集和报告生成系统

## 技术栈

- **MCP SDK**: Model Context Protocol Python SDK
- **Supabase**: PostgreSQL 数据库
- **Python 3.10+**: 编程语言
- **Starlette + uvicorn**: ASGI web 框架和服务器
- **pip + venv**: Python 标准包管理
- **asyncio**: 异步 I/O

## 文档

- 📚 [README.md](README.md) - 项目主文档（本文件）
- 🚀 [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
- 🔧 [DEVELOPMENT.md](DEVELOPMENT.md) - 完整开发指南
- 🐳 [CONTAINER_SETUP.md](CONTAINER_SETUP.md) - 容器环境配置
- 🚀 [deploy/README.md](deploy/README.md) - Ubuntu 部署指南
- 📝 [CHANGELOG.md](CHANGELOG.md) - 版本更新历史
- 📋 [MIGRATION_TO_PIP.md](MIGRATION_TO_PIP.md) - uv 迁移指南

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请提交 Issue 或联系项目维护者。
