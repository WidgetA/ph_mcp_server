# CLAUDE.md - AI Assistant Guide for Product Hunt MCP Server

This document provides comprehensive guidance for AI assistants working with the Product Hunt MCP Server codebase.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Key Components](#key-components)
5. [Development Workflow](#development-workflow)
6. [Coding Conventions](#coding-conventions)
7. [Environment & Configuration](#environment--configuration)
8. [Common Tasks](#common-tasks)
9. [Testing & Deployment](#testing--deployment)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Product Hunt MCP Server** is an HTTP JSON-RPC based Model Context Protocol (MCP) server that provides access to Product Hunt data stored in Supabase. It enables AI assistants and other clients to query product information and daily reports through a standardized MCP interface.

### Key Features

- **7 MCP Tools** for accessing Product Hunt data:
  - `get_latest_products` - Fetch latest products
  - `get_products_by_date` - Query products by specific date
  - `search_products` - Keyword-based product search
  - `get_top_products` - Get products by vote count
  - `get_latest_report` - Fetch most recent daily report
  - `get_report_by_date` - Get report for specific date
  - `get_reports_by_date_range` - Fetch reports in date range

### Technology Stack

- **Language**: Python 3.10+
- **Web Framework**: Starlette (ASGI)
- **Server**: uvicorn
- **Database**: Supabase (PostgreSQL)
- **Protocol**: JSON-RPC 2.0 over HTTP
- **Dependencies**:
  - `supabase==2.10.0` - Database client
  - `httpx==0.27.2` - HTTP client
  - `uvicorn[standard]>=0.32.0` - ASGI server
  - `starlette>=0.35.0` - Web framework

---

## Codebase Structure

```
ph_mcp_server/
├── server.py                    # Main HTTP JSON-RPC server
├── config.py                    # Configuration management (env vars)
├── services/
│   ├── __init__.py
│   └── supabase_service.py     # Database access layer
├── requirements.txt             # pip dependencies
├── pyproject.toml              # Project metadata & build config
├── install.sh                  # Installation script
├── run.sh                      # Startup script
├── .python-version             # Python 3.10
├── .gitignore                  # Git ignore patterns
├── README.md                   # User documentation (Chinese)
├── PROJECT_STRUCTURE.txt       # Detailed structure reference
└── CLAUDE.md                   # This file
```

### File Responsibilities

| File | Purpose | Key Functions |
|------|---------|---------------|
| `server.py` | HTTP server & JSON-RPC handler | `mcp_handler()`, `execute_tool()`, `main()` |
| `config.py` | Environment variable configuration | `Settings` class |
| `services/supabase_service.py` | Database operations | All data access methods |
| `install.sh` | Setup virtual environment & install deps | - |
| `run.sh` | Start server with activated venv | - |

---

## Architecture & Design Patterns

### Design Principles

1. **Layered Architecture**:
   - **HTTP Layer**: Starlette handles HTTP requests/responses
   - **RPC Layer**: JSON-RPC 2.0 protocol implementation
   - **Service Layer**: Business logic and data access (`SupabaseService`)
   - **Configuration Layer**: Environment-based config (`config.py`)

2. **Separation of Concerns**:
   - Server logic (`server.py`) is separate from data access (`services/`)
   - Configuration is externalized to environment variables
   - No `.env` files - configuration happens at system level

3. **Async/Await Pattern**:
   - All database operations use async/await
   - ASGI server for concurrent request handling
   - Non-blocking I/O for better performance

### HTTP Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Service information & metadata |
| GET | `/health` | Health check (returns service status) |
| POST | `/mcp` | JSON-RPC endpoint (all MCP requests) |

### JSON-RPC Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `initialize` | Establish MCP connection | None |
| `notifications/initialized` | Acknowledge initialization | None |
| `tools/list` | List all available tools | None |
| `tools/call` | Execute a specific tool | `name`, `arguments` |
| `ping` | Heartbeat check | None |

---

## Key Components

### 1. Server (`server.py`)

**Main Entry Point**: Lines 549-577

```python
def main():
    """Starts uvicorn server on HOST:PORT"""
```

**Core Functions**:

- `get_db_service()` (40-45): Lazy initialization of Supabase client
- `execute_tool()` (189-400): Routes tool calls to appropriate handlers
- `mcp_handler()` (437-535): Processes JSON-RPC requests
- `health_check()` (404-412): Health endpoint
- `root()` (415-434): Service info endpoint

**Tool Definitions**: Lines 49-186 - Array of tool schemas with JSON Schema validation

### 2. Configuration (`config.py`)

**Settings Class**: Lines 5-17

Environment variables (loaded at runtime):
- `SUPABASE_URL` (required)
- `SUPABASE_KEY` (required)
- `PRODUCTS_TABLE` (default: `ph_products`)
- `REPORTS_TABLE` (default: `ph_daily_reports`)

**Important**: No `.env` file support - variables must be set system-wide (in `.bashrc` or `.profile`)

### 3. Database Service (`services/supabase_service.py`)

**SupabaseService Class**: Lines 11-186

All methods are async and return structured data:

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_latest_products(days_ago)` | `List[Dict]` | Products from N days ago |
| `get_products_by_date(date)` | `List[Dict]` | Products for specific date |
| `search_products(keyword, days, limit)` | `List[Dict]` | Fuzzy search in name/tagline/description |
| `get_top_products_by_votes(date, limit)` | `List[Dict]` | Sorted by votes_count |
| `get_latest_report()` | `Optional[Dict]` | Most recent report |
| `get_report_by_date(date)` | `Optional[Dict]` | Report for specific date |
| `get_reports_by_date_range(start, end)` | `List[Dict]` | Reports in date range |

**Error Handling**: All methods catch exceptions, log errors, and return empty results rather than raising

---

## Development Workflow

### Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd ph_mcp_server

# 2. Configure environment variables
# Edit ~/.bashrc or ~/.profile:
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your-anon-key
# Optional:
export PRODUCTS_TABLE=ph_products
export REPORTS_TABLE=ph_daily_reports

# 3. Load environment
source ~/.bashrc

# 4. Install dependencies
./install.sh

# 5. Run server
./run.sh
```

### Git Workflow

**Current Branch**: `claude/claude-md-mi37op91rhpvvrix-015fCDYJGxc2ypLFUffGh4Ua`

**Important Git Rules**:
1. Always work on designated feature branch
2. Branch names must start with `claude/` and end with session ID
3. Push failures with 403 indicate branch naming issues
4. Use `git push -u origin <branch-name>` for first push
5. Retry network failures up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Making Changes

1. **Before Modifying Code**:
   - Read relevant files first
   - Understand the layered architecture
   - Check if changes affect multiple layers

2. **When Adding Features**:
   - Add tool definition to `TOOLS` array in `server.py`
   - Implement handler in `execute_tool()` function
   - Add data access method to `SupabaseService` if needed
   - Update this documentation

3. **When Fixing Bugs**:
   - Check logs for error context
   - Verify environment variables are set
   - Test database connectivity
   - Ensure JSON-RPC response format is correct

### Testing Changes

```bash
# 1. Start server
./run.sh

# 2. Test health endpoint
curl http://localhost:8080/health

# 3. Test JSON-RPC (initialize)
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

# 4. Test tool listing
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'

# 5. Test tool execution
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_latest_products","arguments":{}},"id":3}'
```

---

## Coding Conventions

### Python Style

1. **Type Hints**: Use type hints for all function parameters and return values
   ```python
   async def get_products(limit: int) -> List[Dict[str, Any]]:
   ```

2. **Async/Await**: All I/O operations must be async
   ```python
   async def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
   ```

3. **Logging**: Use structured logging with appropriate levels
   ```python
   logger.info(f"获取了 {len(products)} 个产品")
   logger.error(f"处理工具 {name} 时出错: {str(e)}", exc_info=True)
   ```

4. **Error Handling**: Catch exceptions, log them, return graceful errors
   ```python
   try:
       # operation
   except Exception as e:
       logger.error(f"错误: {str(e)}")
       return {"content": [{"type": "text", "text": f"错误: {str(e)}"], "isError": True}
   ```

### JSON-RPC Response Format

**Success Response**:
```python
{
    "content": [
        {
            "type": "text",
            "text": json.dumps(result, ensure_ascii=False, indent=2)
        }
    ]
}
```

**Error Response**:
```python
{
    "content": [
        {
            "type": "text",
            "text": "错误描述"
        }
    ],
    "isError": True
}
```

### Database Queries

- Use method chaining for Supabase queries
- Always use date range queries for time-based data: `.gte()` and `.lte()`
- Use `.order()` for consistent result ordering
- Apply `.limit()` when pagination is needed
- Use `.ilike` for case-insensitive fuzzy matching
- Use `.or_()` for multiple column searches

Example:
```python
response = self.client.table(settings.PRODUCTS_TABLE)\
    .select("*")\
    .gte('fetch_date', f'{date}T00:00:00')\
    .lte('fetch_date', f'{date}T23:59:59')\
    .order('rank')\
    .execute()
```

---

## Environment & Configuration

### Required Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | ✅ | - | Supabase project URL |
| `SUPABASE_KEY` | ✅ | - | Supabase anonymous key |
| `PRODUCTS_TABLE` | ❌ | `ph_products` | Products table name |
| `REPORTS_TABLE` | ❌ | `ph_daily_reports` | Reports table name |
| `MCP_SERVER_HOST` | ❌ | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT` | ❌ | `8080` | Server port |

### Configuration Location

**Production**: Set in `~/.bashrc` or `~/.profile`
```bash
export SUPABASE_URL=https://xxx.supabase.co
export SUPABASE_KEY=eyJhb...
```

**Important**: Do NOT use `.env` files - this server relies on system-level environment variables

### Client Configuration

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
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

---

## Common Tasks

### Adding a New Tool

1. **Define tool schema** in `TOOLS` array (server.py:49-186):
```python
{
    "name": "my_new_tool",
    "description": "Tool description in Chinese",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
}
```

2. **Add handler** in `execute_tool()` function (server.py:189-400):
```python
elif name == "my_new_tool":
    param1 = arguments["param1"]

    result = await db.my_new_method(param1)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, ensure_ascii=False, indent=2)
        }]
    }
```

3. **Implement database method** in `SupabaseService` (services/supabase_service.py):
```python
async def my_new_method(self, param1: str) -> List[Dict[str, Any]]:
    """Method description"""
    try:
        response = self.client.table(settings.PRODUCTS_TABLE)\
            .select("*")\
            .eq('some_column', param1)\
            .execute()

        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return []
```

### Modifying Database Queries

When changing how data is queried:

1. **Locate the method** in `services/supabase_service.py`
2. **Understand the query chain**:
   - `.select("*")` - columns to fetch
   - `.gte()`, `.lte()`, `.eq()` - filters
   - `.order()` - sorting
   - `.limit()` - result count
3. **Test query logic** before deploying
4. **Update tool description** if behavior changes

### Updating Configuration

1. **For new config values**:
   - Add to `Settings` class in `config.py`
   - Document in `README.md` and this file
   - Provide sensible defaults

2. **For changed defaults**:
   - Update `Settings` class
   - Update documentation
   - Consider backward compatibility

---

## Testing & Deployment

### Local Testing

```bash
# 1. Set environment variables
export SUPABASE_URL=https://test.supabase.co
export SUPABASE_KEY=test-key

# 2. Run server
./run.sh

# 3. In another terminal, test endpoints
curl http://localhost:8080/health
```

### Deployment to Ubuntu Server

```bash
# 1. Configure environment on server
ssh user@server
nano ~/.bashrc
# Add exports, then:
source ~/.bashrc

# 2. Upload code
tar -czf ph_mcp_server.tar.gz ph_mcp_server/
scp ph_mcp_server.tar.gz user@server:~/

# 3. Extract and install
ssh user@server
tar -xzf ph_mcp_server.tar.gz && cd ph_mcp_server
./install.sh

# 4. Run server
./run.sh
```

### Production Considerations

- Server runs on port 8080 by default
- Logs output to stdout (capture with external logging)
- Use reverse proxy (nginx/caddy) for HTTPS
- Consider systemd service for auto-restart
- Monitor health endpoint for uptime checks

---

## Troubleshooting

### Common Issues

#### 1. "未找到 python3"
**Cause**: Python not installed
**Solution**: Install Python 3.10+
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### 2. Database Connection Errors
**Cause**: Invalid Supabase credentials or URL
**Solution**:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Check credentials in Supabase dashboard
- Test connectivity: `curl $SUPABASE_URL`

#### 3. "未找到 X 的产品数据"
**Cause**: No data for requested date
**Solution**:
- Query a different date
- Check if data exists in Supabase
- Verify table names match configuration

#### 4. JSON-RPC Parse Errors
**Cause**: Malformed JSON in request
**Solution**:
- Validate JSON syntax
- Check Content-Type header is `application/json`
- Ensure proper escaping of strings

#### 5. Tool Not Found
**Cause**: Tool name mismatch or not implemented
**Solution**:
- Check tool name matches `TOOLS` array
- Verify handler exists in `execute_tool()`
- List available tools with `tools/list` method

### Debugging Steps

1. **Check logs**: Server outputs detailed logs to stdout
2. **Verify environment**: `echo $SUPABASE_URL` etc.
3. **Test connectivity**: `curl http://localhost:8080/health`
4. **Test initialize**: Send JSON-RPC initialize request
5. **Inspect database**: Check Supabase dashboard for data
6. **Review code**: Use line numbers from error messages

### Log Analysis

Logs include:
- Request method and ID
- Query results (row counts)
- Error messages with stack traces
- Server startup information

Example log entry:
```
2024-03-15 10:30:45 - __main__ - INFO - 收到请求: method=tools/call, id=3
2024-03-15 10:30:45 - services.supabase_service - INFO - 获取了 10 个产品 (日期: 2024-03-15)
```

---

## Database Schema Reference

### Products Table (`ph_products`)

Key columns:
- `id`: Primary key
- `name`: Product name
- `tagline`: Product tagline
- `description`: Full description
- `votes_count`: Number of votes
- `rank`: Product ranking
- `fetch_date`: Timestamp of data fetch
- `url`: Product URL
- `thumbnail_url`: Image URL

### Reports Table (`ph_daily_reports`)

Key columns:
- `id`: Primary key
- `report_date`: Date of report (YYYY-MM-DD)
- `created_at`: Creation timestamp
- `report_content`: Full report text/JSON
- Additional analysis fields (varies by implementation)

---

## Best Practices for AI Assistants

### When Working with This Codebase

1. **Always read before writing**: Use Read tool to understand existing code
2. **Preserve structure**: Maintain the layered architecture
3. **Follow async patterns**: Keep all I/O operations async
4. **Use type hints**: Add proper type annotations
5. **Log appropriately**: Add logging for debugging
6. **Handle errors gracefully**: Don't let exceptions crash the server
7. **Test changes**: Verify with curl commands before committing
8. **Update documentation**: Keep this file synchronized with code changes

### Code Modification Checklist

- [ ] Read relevant files first
- [ ] Understand the change's scope (which layers affected)
- [ ] Maintain async/await pattern
- [ ] Add/update type hints
- [ ] Include error handling
- [ ] Add logging statements
- [ ] Update tool descriptions if needed
- [ ] Test with curl commands
- [ ] Update CLAUDE.md if architecture changes
- [ ] Commit with clear message
- [ ] Push to correct branch

### Communication Style

- Code comments: Chinese (matches existing style)
- Documentation: English (this file) or Chinese (README.md)
- Log messages: Chinese (matches existing logs)
- Variable names: English (Python convention)

---

## Quick Reference

### Start Development
```bash
./install.sh && ./run.sh
```

### Test Health
```bash
curl http://localhost:8080/health
```

### Test MCP
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

### View Logs
```bash
# Logs go to stdout when running ./run.sh
```

### File Locations
- Main server: `server.py`
- Database: `services/supabase_service.py`
- Config: `config.py`
- Tools: `server.py` lines 49-186
- Handlers: `server.py` lines 189-400

---

## Version History

- **1.0.0** (2024): Initial HTTP JSON-RPC implementation
  - 7 tools for Product Hunt data access
  - Supabase integration
  - Starlette + uvicorn server
  - Environment-based configuration

---

## Additional Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **Supabase Python Client**: https://github.com/supabase-community/supabase-py
- **Starlette Framework**: https://www.starlette.io/
- **JSON-RPC 2.0 Spec**: https://www.jsonrpc.org/specification
- **Project README**: `README.md` (Chinese)
- **Structure Reference**: `PROJECT_STRUCTURE.txt`

---

*This document should be updated whenever significant architectural changes are made to the codebase.*
