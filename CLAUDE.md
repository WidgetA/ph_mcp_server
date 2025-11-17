# CLAUDE.md - Product Hunt MCP Server

## Overview

This is a **Product Hunt MCP (Model Context Protocol) Server** that provides AI assistants with access to Product Hunt and GitHub Trending data via HTTP JSON-RPC. The server exposes 8 tools for querying products and reports from two separate Supabase databases.

**Project Type**: MCP Server (HTTP Transport)
**Language**: Python 3.10+
**Framework**: Starlette (ASGI) + uvicorn
**Protocol**: JSON-RPC 2.0
**Database**: Supabase (PostgreSQL)
**Deployment**: Ubuntu server (8080 port)

---

## Codebase Structure

```
ph_mcp_server/
├── server.py                    # Main HTTP JSON-RPC server
├── config.py                    # Configuration management (environment variables)
├── services/
│   ├── __init__.py
│   └── supabase_service.py     # Database access layer
├── install.sh                   # Installation script (venv + dependencies)
├── run.sh                       # Server startup script
├── requirements.txt             # Python dependencies (4 packages)
├── pyproject.toml              # Project metadata
├── .python-version             # Python 3.10
├── .gitignore                  # Git ignore rules
├── README.md                   # Deployment and usage documentation
├── PROJECT_STRUCTURE.txt       # Project structure overview
└── CLAUDE.md                   # This file
```

### Key Files Explained

#### server.py (623 lines)
- **Purpose**: Main HTTP server implementing MCP protocol via JSON-RPC
- **Port**: 8080 (configurable via MCP_SERVER_PORT env var)
- **Endpoints**:
  - `GET /` - Service information
  - `GET /health` - Health check
  - `POST /mcp` - JSON-RPC endpoint (all MCP requests)
- **JSON-RPC Methods**:
  - `initialize` - MCP protocol initialization
  - `tools/list` - List all available tools
  - `tools/call` - Execute a tool
  - `notifications/initialized` - Initialization notification
  - `ping` - Health check
- **Tool Execution**: `execute_tool()` function (lines 203-445) handles all tool calls
- **Logging**: Comprehensive logging to stdout

#### config.py (25 lines)
- **Purpose**: Centralized configuration management
- **Pattern**: Settings class reading from environment variables
- **No .env files**: Environment variables must be set at system level
- **Databases**:
  - Product Hunt: `SUPABASE_URL` + `SUPABASE_KEY`
  - GitHub Trending: `GITHUB_SUPABASE_URL` + `GITHUB_SUPABASE_KEY`

#### services/supabase_service.py (235 lines)
- **Purpose**: Database access layer for both Supabase instances
- **Pattern**: Async methods returning typed data
- **Two Clients**:
  - `self.client` - Product Hunt database
  - `self.github_client` - GitHub Trending database
- **Methods**: 9 async methods for data retrieval
- **Error Handling**: All methods catch exceptions and return empty results

---

## Architecture

### MCP Protocol Flow

```
Client (Claude Desktop/Chatbox)
    ↓ HTTP POST (JSON-RPC)
    ↓
server.py (Starlette ASGI)
    ↓
mcp_handler() → route by method
    ↓
execute_tool() → call SupabaseService
    ↓
SupabaseService → query Supabase
    ↓
Return JSON response
```

### Tool System

**8 Tools Total**:
- **Product Hunt (7 tools)**: Products and reports from `ph_products` and `ph_daily_reports` tables
- **GitHub Trending (1 tool)**: Reports from `github_trending_reports` table

**Tool Definition Structure** (lines 49-200):
```python
{
    "name": "get_latest_products",
    "description": "...",
    "inputSchema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```

**Tool Execution Pattern** (lines 203-445):
1. Extract arguments from `params.arguments`
2. Call corresponding SupabaseService method
3. Format response as MCP content (text/JSON)
4. Handle errors with `isError: True`

### Database Schema

#### Product Hunt Database (SUPABASE_URL)

**Table: ph_products** (default name, configurable via PRODUCTS_TABLE)
```
Columns (inferred from queries):
- id (primary key)
- fetch_date (timestamp) - indexed for queries
- rank (integer) - product ranking
- name (text) - product name
- tagline (text) - short description
- description (text) - full description
- votes_count (integer) - number of votes
- [other fields returned as-is]

Indexes:
- fetch_date (for date range queries)
- rank (for ordering)
- votes_count (for top products)
```

**Table: ph_daily_reports** (default name, configurable via REPORTS_TABLE)
```
Columns:
- id (primary key)
- report_date (date) - unique report identifier
- created_at (timestamp) - for ordering
- [report content fields]
```

#### GitHub Trending Database (GITHUB_SUPABASE_URL)

**Table: github_trending_reports** (default name, configurable via GITHUB_REPORTS_TABLE)
```
Columns:
- id (primary key)
- report_date (date) - unique report identifier
- [report content fields]
```

---

## Environment Variables

### Required (MUST be set)

```bash
# Product Hunt Database
export SUPABASE_URL=https://your-ph-project.supabase.co
export SUPABASE_KEY=your-ph-anon-key

# GitHub Trending Database
export GITHUB_SUPABASE_URL=https://your-github-project.supabase.co
export GITHUB_SUPABASE_KEY=your-github-anon-key
```

### Optional (with defaults)

```bash
# Table names (default values shown)
export PRODUCTS_TABLE=ph_products
export REPORTS_TABLE=ph_daily_reports
export GITHUB_REPORTS_TABLE=github_trending_reports

# Server configuration
export MCP_SERVER_PORT=8080
export MCP_SERVER_HOST=0.0.0.0
```

### Configuration Pattern

**IMPORTANT**: This project does NOT use `.env` files. All environment variables MUST be configured at the system level (in `.bashrc`, `.profile`, or system service files).

```bash
# Add to ~/.bashrc or ~/.profile
export SUPABASE_URL=...
export SUPABASE_KEY=...
# ... other vars

# Then reload
source ~/.bashrc
```

---

## Available Tools

### Product Hunt Tools (7)

#### 1. get_latest_products
- **Description**: Get latest products (default: today's data)
- **Parameters**:
  - `days_ago` (integer, default=0): How many days ago (0=today, 1=yesterday)
  - `limit` (integer, default=50, max=100): Number of products to return
- **Returns**: Array of products ordered by rank
- **Implementation**: server.py:208-235, supabase_service.py:29-51

#### 2. get_products_by_date
- **Description**: Get products for a specific date
- **Parameters**:
  - `date` (string, required): Format YYYY-MM-DD
  - `limit` (integer, default=50, max=100)
- **Returns**: Array of products ordered by rank
- **Implementation**: server.py:237-263, supabase_service.py:53-70

#### 3. search_products
- **Description**: Search products by keyword (name, tagline, description)
- **Parameters**:
  - `keyword` (string, required): Search term
  - `days` (integer, default=7, max=90): Search last N days
  - `limit` (integer, default=20, max=50)
- **Returns**: Array of matching products
- **Implementation**: server.py:265-296, supabase_service.py:72-107
- **Query**: Uses Supabase `.or_()` with `.ilike` for fuzzy matching

#### 4. get_top_products
- **Description**: Get products with most votes for a date
- **Parameters**:
  - `date` (string, optional): Format YYYY-MM-DD, defaults to today
  - `limit` (integer, default=10, max=50)
- **Returns**: Array of products ordered by votes_count DESC
- **Implementation**: server.py:298-326, supabase_service.py:172-194

#### 5. get_latest_report
- **Description**: Get the most recent Product Hunt daily report
- **Parameters**: None
- **Returns**: Single report object
- **Implementation**: server.py:328-344, supabase_service.py:129-147
- **Query**: Orders by `created_at DESC`, limit 1

#### 6. get_report_by_date
- **Description**: Get report for a specific date
- **Parameters**:
  - `date` (string, required): Format YYYY-MM-DD
- **Returns**: Single report object or null
- **Implementation**: server.py:346-364, supabase_service.py:109-127

#### 7. get_reports_by_date_range
- **Description**: Get all reports within a date range
- **Parameters**:
  - `start_date` (string, required): Format YYYY-MM-DD
  - `end_date` (string, required): Format YYYY-MM-DD
- **Returns**: Array of reports ordered by date DESC
- **Implementation**: server.py:366-395, supabase_service.py:149-170

### GitHub Trending Tools (1)

#### 8. get_github_trending_report
- **Description**: Get GitHub Trending daily report
- **Parameters**:
  - `date` (string, optional): Format YYYY-MM-DD, if omitted returns latest
- **Returns**: Single report object
- **Implementation**: server.py:397-426, supabase_service.py:196-234
- **Logic**: If date provided, query by date; otherwise get latest

---

## Development Workflows

### Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd ph_mcp_server

# 2. Configure environment variables (system-wide)
# Edit ~/.bashrc or ~/.profile and add:
export SUPABASE_URL=...
export SUPABASE_KEY=...
export GITHUB_SUPABASE_URL=...
export GITHUB_SUPABASE_KEY=...

# 3. Reload environment
source ~/.bashrc

# 4. Install dependencies
./install.sh

# 5. Run server
./run.sh
```

### Development Cycle

```bash
# 1. Make changes to code
vim server.py  # or services/supabase_service.py

# 2. Test manually with curl
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'

# 3. Test tool execution
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_latest_products","arguments":{}},"id":3}'

# 4. Check health
curl http://localhost:8080/health

# 5. Restart server (Ctrl+C then ./run.sh)
```

### Testing with Claude Desktop

**Config File Location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "http://localhost:8080/mcp",
      "transport": "http"
    }
  }
}
```

**Testing Flow**:
1. Start server: `./run.sh`
2. Restart Claude Desktop
3. Check MCP icon in Claude Desktop
4. Ask Claude to use the tools: "Show me today's top Product Hunt products"

### Deployment to Production

```bash
# 1. Package code
tar -czf ph_mcp_server.tar.gz ph_mcp_server/

# 2. Upload to server
scp ph_mcp_server.tar.gz user@your-server:~/

# 3. SSH to server and extract
ssh user@your-server
tar -xzf ph_mcp_server.tar.gz
cd ph_mcp_server

# 4. Configure environment variables (server-side)
# Edit ~/.bashrc and add exports
source ~/.bashrc

# 5. Install and run
./install.sh
./run.sh

# Server now runs on port 8080
# Configure reverse proxy (nginx/caddy) for HTTPS
```

---

## Coding Conventions

### Python Style

- **PEP 8**: Follow standard Python conventions
- **Type Hints**: Use typing module for function signatures
- **Async/Await**: All database methods are async
- **Docstrings**: All functions have Chinese docstrings explaining purpose
- **Logging**: Use `logger.info()` and `logger.error()` extensively

### Naming Conventions

- **Functions**: Snake_case (e.g., `get_latest_products`)
- **Classes**: PascalCase (e.g., `SupabaseService`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `TOOLS`, `PORT`)
- **Tool Names**: Snake_case matching function names
- **Table Names**: Snake_case with prefixes (e.g., `ph_products`, `github_trending_reports`)

### Error Handling Pattern

**Consistent across all methods**:
```python
try:
    # Query database
    response = self.client.table(...).execute()
    logger.info(f"Success message")
    return response.data
except Exception as e:
    logger.error(f"Error message: {str(e)}")
    return []  # or None for single objects
```

**Tool execution error handling**:
```python
return {
    "content": [{
        "type": "text",
        "text": f"错误: {str(e)}"
    }],
    "isError": True
}
```

### Response Format Pattern

**All tool responses use MCP content format**:
```python
return {
    "content": [{
        "type": "text",
        "text": json.dumps(result, ensure_ascii=False, indent=2)
    }]
}
```

**JSON serialization**: Always use `ensure_ascii=False` for Chinese text

### Database Query Patterns

**Date range queries**:
```python
.gte('fetch_date', f'{date}T00:00:00')
.lte('fetch_date', f'{date}T23:59:59')
```

**Fuzzy search**:
```python
.or_(f"name.ilike.{pattern},tagline.ilike.{pattern},description.ilike.{pattern}")
```

**Ordering**:
```python
.order('field_name', desc=True)  # Descending
.order('field_name')              # Ascending
```

---

## Adding New Features

### Adding a New Tool

**Example: Add a tool to get products by topic**

1. **Define the tool** in `server.py` TOOLS list (after line 200):

```python
{
    "name": "get_products_by_topic",
    "description": "Get products filtered by topic",
    "inputSchema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Topic name (e.g., AI, SaaS, Mobile)"
            },
            "limit": {
                "type": "integer",
                "description": "Number of products to return",
                "default": 20,
                "minimum": 1,
                "maximum": 50
            }
        },
        "required": ["topic"]
    }
}
```

2. **Add handler** in `execute_tool()` function (server.py, before line 428):

```python
elif name == "get_products_by_topic":
    topic = arguments["topic"]
    limit = arguments.get("limit", 20)

    products = await db.get_products_by_topic(
        topic=topic,
        limit=limit
    )

    if not products:
        return {
            "content": [{
                "type": "text",
                "text": f"未找到主题 '{topic}' 的产品"
            }]
        }

    result = {
        "topic": topic,
        "total_count": len(products),
        "products": products
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, ensure_ascii=False, indent=2)
        }]
    }
```

3. **Add database method** in `services/supabase_service.py`:

```python
async def get_products_by_topic(
    self,
    topic: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """获取指定主题的产品"""
    try:
        # Assuming there's a 'topics' field in the database
        response = self.client.table(settings.PRODUCTS_TABLE)\
            .select("*")\
            .contains('topics', [topic])\
            .order('fetch_date', desc=True)\
            .limit(limit)\
            .execute()

        products = response.data if response.data else []
        logger.info(f"获取了 {len(products)} 个主题为 '{topic}' 的产品")

        return products

    except Exception as e:
        logger.error(f"获取主题产品失败: {str(e)}")
        return []
```

4. **Test the new tool**:

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "params":{
      "name":"get_products_by_topic",
      "arguments":{"topic":"AI","limit":10}
    },
    "id":1
  }'
```

### Adding a New Database

**Example: Add a Hacker News database**

1. **Add environment variables** to `config.py`:

```python
class Settings:
    # ... existing settings ...

    # Hacker News Supabase 配置
    HN_SUPABASE_URL: str = os.getenv("HN_SUPABASE_URL", "")
    HN_SUPABASE_KEY: str = os.getenv("HN_SUPABASE_KEY", "")
    HN_STORIES_TABLE: str = os.getenv("HN_STORIES_TABLE", "hn_stories")
```

2. **Add client** in `services/supabase_service.py` `__init__`:

```python
def __init__(self):
    # ... existing clients ...

    # Hacker News 数据库客户端
    self.hn_client: Client = create_client(
        settings.HN_SUPABASE_URL,
        settings.HN_SUPABASE_KEY
    )
    logger.info("Hacker News Supabase 客户端已初始化")
```

3. **Add methods** to access the new database
4. **Add tools** following the pattern above

### Modifying Existing Tools

**Best practices**:
- Keep backward compatibility when possible
- Update both tool definition and implementation
- Test with existing clients before deploying
- Update documentation (README.md)

---

## Common Patterns

### Date Handling

**Getting today's date**:
```python
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
```

**Computing offset dates**:
```python
from datetime import datetime, timedelta
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
```

**Date range queries**:
```python
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')
```

### Pagination

Currently, pagination is handled by the `limit` parameter. There's no offset/cursor pagination implemented.

**To add cursor-based pagination**:
1. Add `cursor` parameter to tool schema
2. Modify query to use `.range(start, end)`
3. Return next cursor in response

### Caching

Currently, there's no caching layer. All requests hit Supabase directly.

**To add caching**:
1. Install Redis: `pip install redis`
2. Add Redis client to `SupabaseService.__init__`
3. Wrap methods with cache check/set logic
4. Use TTL appropriate for data freshness (e.g., 5 minutes for products)

---

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Found
**Error**: `create_client() missing required arguments`

**Solution**:
- Verify environment variables are set: `echo $SUPABASE_URL`
- Reload shell configuration: `source ~/.bashrc`
- Check variable names match exactly (case-sensitive)

#### 2. Database Connection Errors
**Error**: `Supabase client initialization failed`

**Solution**:
- Verify Supabase URLs are accessible
- Check API keys are valid (not expired)
- Test connection manually with Supabase client

#### 3. No Data Returned
**Error**: Tool returns empty results

**Solution**:
- Check table names match environment variables
- Verify date format is YYYY-MM-DD
- Check if data exists for requested date: use Supabase dashboard
- Review database schema matches query expectations

#### 4. Port Already in Use
**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or change port
export MCP_SERVER_PORT=8081
./run.sh
```

#### 5. Tool Not Found
**Error**: `Method not found: tools/call`

**Solution**:
- Verify JSON-RPC request format
- Check method name spelling
- Ensure server is fully initialized (`initialize` called first)

### Logging

All logs go to stdout. To save logs:

```bash
# Redirect to file
./run.sh > server.log 2>&1

# Or use systemd with logging
journalctl -u ph-mcp-server -f
```

### Debugging

**Enable verbose logging**:
```python
# In server.py, change logging level
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Add debug statements**:
```python
logger.debug(f"Received arguments: {arguments}")
logger.debug(f"Query result: {response.data}")
```

---

## Best Practices for AI Assistants

### When Working with This Codebase

1. **Read First**: Always read relevant files before making changes
   - Read `server.py` to understand tool definitions
   - Read `services/supabase_service.py` for database methods
   - Read `config.py` for available settings

2. **Follow Patterns**: Maintain consistency
   - Use existing error handling patterns
   - Follow naming conventions
   - Keep response format consistent

3. **Test Thoroughly**: Don't assume changes work
   - Test with curl after code changes
   - Verify JSON-RPC responses are valid
   - Check logs for errors

4. **Document Changes**: Update documentation
   - Add docstrings to new functions
   - Update README.md if adding features
   - Update this CLAUDE.md if changing architecture

5. **Handle Errors Gracefully**: Never crash the server
   - Wrap database calls in try/except
   - Return empty results instead of raising errors
   - Log all errors with context

6. **Preserve Backward Compatibility**: Don't break existing clients
   - Keep existing tool signatures
   - Add new optional parameters with defaults
   - Don't rename or remove tools without versioning

### Common Tasks for AI Assistants

#### Task: "Fix a bug in product search"
1. Read `services/supabase_service.py:72-107` (search_products method)
2. Identify the issue
3. Fix the method
4. Test with curl
5. Verify logs show correct behavior

#### Task: "Add a new field to product responses"
1. Check if field exists in database (ask user or check Supabase)
2. Update query in relevant method (e.g., `.select("*, new_field")`)
3. No changes needed to tool definition (returns all fields)
4. Test and verify field appears in response

#### Task: "Optimize database queries"
1. Read `services/supabase_service.py` to understand current queries
2. Identify slow queries (check logs)
3. Add indexes (in Supabase dashboard)
4. Optimize query logic (reduce unnecessary filters)
5. Test performance improvement

#### Task: "Deploy to production"
1. Verify environment variables are configured on server
2. Package code: `tar -czf ph_mcp_server.tar.gz ph_mcp_server/`
3. Upload to server
4. Run `./install.sh` then `./run.sh`
5. Configure reverse proxy for HTTPS
6. Test with production URL

---

## Additional Resources

### Documentation
- MCP Protocol: https://modelcontextprotocol.io/
- Supabase Python Client: https://supabase.com/docs/reference/python
- Starlette Framework: https://www.starlette.io/
- JSON-RPC 2.0 Spec: https://www.jsonrpc.org/specification

### Project Files
- `README.md` - Deployment guide (Chinese)
- `PROJECT_STRUCTURE.txt` - Quick reference structure
- `pyproject.toml` - Python project metadata

### Quick Reference

**Test Commands**:
```bash
# Health check
curl http://localhost:8080/health

# Initialize
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

# List tools
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'

# Get latest products
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_latest_products","arguments":{}},"id":3}'
```

**File Locations**:
- Tool definitions: `server.py:49-200`
- Tool handlers: `server.py:203-445`
- Database methods: `services/supabase_service.py`
- Configuration: `config.py`
- Startup scripts: `install.sh`, `run.sh`

---

## Version History

**Current Version**: 1.0.0

**Recent Changes**:
- Initial release with 8 tools
- HTTP JSON-RPC transport
- Dual database support (Product Hunt + GitHub Trending)

---

**Last Updated**: 2025-11-17
**Maintained By**: WidgetA/ph_mcp_server project
