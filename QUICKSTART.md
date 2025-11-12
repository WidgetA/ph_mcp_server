# 快速开始指南

5 分钟快速启动 Product Hunt MCP Server！

## 📋 前置条件

- Python 3.10+
- pip
- Git
- Supabase 账号和配置

## 🚀 快速安装

### 选项 1: 自动安装（推荐）⭐

**Linux/macOS:**
```bash
# 运行自动设置脚本
chmod +x setup.sh
./setup.sh
```

脚本会自动：
1. ✅ 检查 Python 和 pip
2. ✅ 创建虚拟环境
3. ✅ 安装所有依赖
4. ✅ 创建 .env 文件
5. ✅ 运行测试验证

### 选项 2: 手动安装

#### 步骤 1: 克隆项目

```bash
git clone <repository-url>
cd ph_mcp_server
```

#### 步骤 2: 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
```

#### 步骤 3: 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 或使用 Makefile
make install
```

#### 步骤 4: 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Supabase URL 和 KEY
nano .env  # 或使用 vi/vim
```

## 🏃 启动服务器

### 使用 Make（最简单）

```bash
make run
```

### 使用启动脚本

```bash
./start.sh
```

### 直接运行

```bash
# 如果在虚拟环境中
python server.py

# 或使用 python3
python3 server.py
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
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**本地服务器**：
```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

**远程服务器（HTTPS，推荐）**：
```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "https://your-domain.com/sse"
    }
  }
}
```

重启 Claude Desktop 即可使用！

## 📚 常用命令

### 使用 Make（推荐）

```bash
make help       # 显示所有命令
make venv       # 创建虚拟环境
make install    # 安装依赖
make run        # 启动服务器
make test       # 运行测试
make clean      # 清理临时文件
```

### 使用 pip

```bash
# 安装依赖
pip install -r requirements.txt

# 升级依赖
pip install --upgrade -r requirements.txt

# 运行服务器
python server.py

# 运行测试
python tests/test_server.py
```

## 🔧 故障排查

### 1. 端口被占用

```bash
# 检查 8080 端口
sudo lsof -i :8080

# 或修改 .env 中的端口
MCP_SERVER_PORT=8081
```

### 2. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 清理并重新安装
pip install --force-reinstall -r requirements.txt

# 或使用 make
make clean
make install
```

### 3. 连接 Supabase 失败

- 检查 .env 中的 SUPABASE_URL 和 SUPABASE_KEY
- 确保网络可以访问 Supabase
- 验证数据库表是否存在

### 4. 虚拟环境问题

```bash
# 删除旧的虚拟环境
rm -rf .venv

# 重新创建
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📖 获取帮助

- 📘 详细文档: [README.md](README.md)
- 🔧 开发指南: [DEVELOPMENT.md](DEVELOPMENT.md)
- 🐳 容器配置: [CONTAINER_SETUP.md](CONTAINER_SETUP.md)
- 📝 更新日志: [CHANGELOG.md](CHANGELOG.md)
- 🐛 报告问题: [GitHub Issues](<your-repo-url>/issues)

## 🎉 成功！

现在你可以在 Claude Desktop 或其他 MCP 客户端中使用以下命令：

- "显示今天 Product Hunt 上的产品"
- "搜索最近一周关于 AI 的产品"
- "今天投票最多的 5 个产品是什么？"
- "给我看看最新的每日报告"
- "2024年11月有哪些热门产品？"

祝你使用愉快！🚀
