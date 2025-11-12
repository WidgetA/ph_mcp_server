# 快速开始指南

5 分钟快速启动 Product Hunt MCP Server！

## 📋 前置条件

- Python 3.10+
- Git
- Supabase 账号和配置

## 🚀 快速安装

### 选项 1: 自动安装（推荐）⭐

**Windows:**
```bash
# 运行自动设置脚本
setup.bat
```

**Linux/macOS:**
```bash
# 运行自动设置脚本
chmod +x setup.sh
./setup.sh
```

脚本会自动：
1. ✅ 检查并安装 uv
2. ✅ 创建虚拟环境
3. ✅ 安装所有依赖
4. ✅ 创建 .env 文件
5. ✅ 运行测试验证

### 选项 2: 手动安装

#### 步骤 1: 安装 uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 步骤 2: 克隆并设置项目

```bash
# 克隆项目
git clone <repository-url>
cd ph_mcp_server

# 同步依赖（自动创建虚拟环境）
uv sync

# 或使用 Makefile
make sync
```

#### 步骤 3: 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件
# 填入你的 Supabase URL 和 KEY
```

## 🏃 启动服务器

### 使用 Make（最简单）

```bash
make run
```

### 使用启动脚本

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
./start.sh
```

### 直接运行

```bash
python server.py
```

## ✅ 验证安装

访问健康检查端点：

```bash
curl http://localhost:8080/health
```

或在浏览器打开：
```
http://localhost:8080/
```

看到类似输出即为成功：
```json
{
  "status": "healthy",
  "service": "Product Hunt MCP Server",
  "version": "1.0.0"
}
```

## 🔗 连接 MCP 客户端

### Claude Desktop

编辑配置文件：
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加配置：
```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

重启 Claude Desktop 即可使用！

## 📚 常用命令

使用 Make（推荐）:
```bash
make help       # 显示所有命令
make install    # 安装依赖
make run        # 启动服务器
make test       # 运行测试
make clean      # 清理临时文件
```

使用 uv:
```bash
uv sync                  # 同步依赖
uv add package-name      # 添加依赖
uv run server.py         # 运行服务器
```

   ```

2. **依赖安装失败**
   ```bash
   # 清理并重新安装
   make clean
   uv sync --reinstall
   ```

3. **连接 Supabase 失败**
   - 检查 .env 中的 SUPABASE_URL 和 SUPABASE_KEY
   - 确保网络可以访问 Supabase

### 获取帮助

- 📖 详细文档: [README.md](README.md)
- 🔧 开发指南: [DEVELOPMENT.md](DEVELOPMENT.md)
- 📝 更新日志: [CHANGELOG.md](CHANGELOG.md)
- 🐛 报告问题: [GitHub Issues](<your-repo-url>/issues)

## 🎉 成功！

现在你可以在 Claude Desktop 或其他 MCP 客户端中使用以下命令：

- "显示今天 Product Hunt 上的产品"
- "搜索最近一周关于 AI 的产品"
- "今天投票最多的 5 个产品是什么？"
- "给我看看最新的每日报告"

祝你使用愉快！🚀
