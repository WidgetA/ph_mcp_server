# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-12

### Added

- 🎉 Initial release of Product Hunt MCP Server
- 🌐 Remote HTTP/SSE server mode (port 8080)
- 🔧 7 MCP tools for accessing Product Hunt data:
  - `get_latest_products` - Get latest PH products
  - `get_products_by_date` - Query products by specific date
  - `search_products` - Search products by keyword
  - `get_top_products` - Get top products by votes
  - `get_latest_report` - Get latest daily report
  - `get_report_by_date` - Get report by date
  - `get_reports_by_date_range` - Get reports by date range
- 📦 uv package management support
- 🔨 Makefile with common commands
- 📝 Comprehensive documentation
- ✅ Health check endpoint
- 🔒 Environment-based configuration
- 🧪 Test suite

### Technical Details

- Python 3.10+ required
- Uses MCP SDK 1.1.0+
- Supabase for data storage
- Starlette + uvicorn for HTTP server
- SSE (Server-Sent Events) for MCP transport

### Deployment Options

- Local development server
- Ubuntu systemd service
- Nginx reverse proxy support (optional)

## [Unreleased]

### Planned Features

- [ ] Add more advanced search filters
- [ ] Implement caching layer
- [ ] Add metrics and monitoring
- [ ] Support for multiple database backends
- [ ] GraphQL API endpoint
- [ ] WebSocket support
- [ ] Rate limiting
- [ ] Authentication/Authorization
