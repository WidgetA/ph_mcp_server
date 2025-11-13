# Product Hunt MCP Server

基于 HTTP JSON-RPC 的 Product Hunt 数据访问服务器。

## 功能

提供 7 个工具访问 Supabase 中的 Product Hunt 数据：

- get_latest_products - 获取最新产品
- get_products_by_date - 按日期查询
- search_products - 关键词搜索
- get_top_products - 热门产品
- get_latest_report - 最新报告
- get_report_by_date - 按日期报告
- get_reports_by_date_range - 范围报告

## 部署（Ubuntu）

### 1. 配置环境变量

在服务器配置（如 `.bashrc` 或 `.profile`）：

```bash
# 必需
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your-anon-key

# 可选（有默认值）
export PRODUCTS_TABLE=ph_products          # 默认: ph_products
export REPORTS_TABLE=ph_daily_reports      # 默认: ph_daily_reports
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
| SUPABASE_URL | ✅ | - | Supabase 项目 URL |
| SUPABASE_KEY | ✅ | - | Supabase 匿名密钥 |
| PRODUCTS_TABLE | ❌ | ph_products | Product Hunt 产品表名 |
| REPORTS_TABLE | ❌ | ph_daily_reports | 每日报告表名 |

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
