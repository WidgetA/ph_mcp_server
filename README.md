# Product Hunt MCP Server

基于 HTTP JSON-RPC 的多数据源访问服务器，支持 Product Hunt、GitHub Trending 和美股科技股票资讯。

## 功能

### Product Hunt 数据（7 个工具）

- get_latest_products - 获取最新产品
- get_products_by_date - 按日期查询
- search_products - 关键词搜索
- get_top_products - 热门产品
- get_latest_report - 最新报告
- get_report_by_date - 按日期报告
- get_reports_by_date_range - 范围报告

### GitHub Trending 数据（1 个工具）

- get_github_trending_report - 获取 GitHub Trending 日报（支持指定日期或获取最新）

### 美股科技股票（1 个工具）

- get_latest_stock_news - 获取最新美股科技股票资讯（自动处理周末不开盘）

## 部署（Ubuntu）

### 1. 配置环境变量

在服务器配置（如 `.bashrc` 或 `.profile`）：

```bash
# Product Hunt 数据库配置（必需）
export SUPABASE_URL=https://your-ph-project.supabase.co
export SUPABASE_KEY=your-ph-anon-key

# GitHub Trending 数据库配置（必需）
export GITHUB_SUPABASE_URL=https://your-github-project.supabase.co
export GITHUB_SUPABASE_KEY=your-github-anon-key

# 美股科技股票 PostgreSQL 数据库配置（必需）
export POSTGRES_HOST=your-postgres-host.com
export POSTGRES_PORT=6438
export POSTGRES_DB=your-database
export POSTGRES_USER=your-user
export POSTGRES_PASSWORD=your-password
export POSTGRES_SCHEMA=public                        # 默认: public

# 可选（有默认值）
export PRODUCTS_TABLE=ph_products                    # 默认: ph_products
export REPORTS_TABLE=ph_daily_reports                # 默认: ph_daily_reports
export GITHUB_REPORTS_TABLE=github_trending_reports  # 默认: github_trending_reports
export STOCK_TABLE=tech_stocks                       # 默认: tech_stocks
```

然后加载环境变量：

```bash
source ~/.bashrc
```

### 2. 上传代码

```bash
tar -czf ph_mcp_server.tar.gz ph_mcp_server/
scp ph_mcp_server.tar.gz user@your-server:~/
```

### 3. 安装运行

```bash
ssh user@your-server
tar -xzf ph_mcp_server.tar.gz && cd ph_mcp_server
./install.sh
./run.sh
```

完成！服务运行在 8080 端口，日志输出到 stdout。

## 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| SUPABASE_URL | ✅ | - | Product Hunt Supabase 项目 URL |
| SUPABASE_KEY | ✅ | - | Product Hunt Supabase 匿名密钥 |
| GITHUB_SUPABASE_URL | ✅ | - | GitHub Trending Supabase 项目 URL |
| GITHUB_SUPABASE_KEY | ✅ | - | GitHub Trending Supabase 匿名密钥 |
| POSTGRES_HOST | ✅ | - | PostgreSQL 数据库主机地址（美股） |
| POSTGRES_PORT | ✅ | 5432 | PostgreSQL 数据库端口 |
| POSTGRES_DB | ✅ | - | PostgreSQL 数据库名 |
| POSTGRES_USER | ✅ | - | PostgreSQL 数据库用户 |
| POSTGRES_PASSWORD | ✅ | - | PostgreSQL 数据库密码 |
| POSTGRES_SCHEMA | ❌ | public | PostgreSQL schema 名称 |
| PRODUCTS_TABLE | ❌ | ph_products | Product Hunt 产品表名 |
| REPORTS_TABLE | ❌ | ph_daily_reports | Product Hunt 日报表名 |
| GITHUB_REPORTS_TABLE | ❌ | github_trending_reports | GitHub Trending 日报表名 |
| STOCK_TABLE | ❌ | tech_stocks | 股票资讯表名 |

**注意**：环境变量需在服务器全局配置，不使用 .env 文件。

## 客户端配置

### Claude Desktop

配置文件：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "https://your-domain.com/mcp",
      "transport": "http"
    }
  }
}
```

### Chatbox

配置 URL: `https://your-domain.com/mcp`

### HTTP API

直接使用 JSON-RPC 调用：

```bash
# 初始化
curl -X POST https://your-domain.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

# 列出工具
curl -X POST https://your-domain.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'

# 调用工具
curl -X POST https://your-domain.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_latest_products","arguments":{}},"id":3}'
```

**注意**: 服务器监听 8080 端口，线上基础设施自动处理 HTTPS。

## 技术栈

- Python 3.10+
- Starlette + uvicorn
- Supabase
- JSON-RPC 2.0

## 许可

MIT License
