#!/usr/bin/env python3
"""
Product Hunt MCP Server (HTTP Mode)

这个 MCP server 提供访问 Product Hunt 数据的能力，
包括产品列表、报告等信息。

运行模式：HTTP JSON-RPC，监听在 8080 端口
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request

from services.supabase_service import SupabaseService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")

# 初始化 Supabase 服务
db_service: Optional[SupabaseService] = None


def get_db_service():
    """获取数据库服务实例（延迟初始化）"""
    global db_service
    if db_service is None:
        db_service = SupabaseService()
    return db_service


# MCP 工具定义
TOOLS = [
    {
        "name": "get_latest_products",
        "description": "获取最新的 Product Hunt 产品列表。默认获取今天的数据，可以通过 days_ago 参数指定获取几天前的数据。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days_ago": {
                    "type": "integer",
                    "description": "获取几天前的数据，默认为 0（今天）。例如：1 表示昨天，2 表示前天。",
                    "default": 0,
                    "minimum": 0
                },
                "limit": {
                    "type": "integer",
                    "description": "返回的产品数量限制，默认返回所有产品",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 100
                }
            }
        }
    },
    {
        "name": "get_products_by_date",
        "description": "根据指定日期获取 Product Hunt 产品列表。日期格式为 YYYY-MM-DD，例如：2024-03-15",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "日期，格式为 YYYY-MM-DD，例如：2024-03-15",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回的产品数量限制，默认返回所有产品",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["date"]
        }
    },
    {
        "name": "search_products",
        "description": "搜索 Product Hunt 产品。支持按产品名称、标语（tagline）或描述进行模糊搜索。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词，会在产品名称、标语和描述中搜索"
                },
                "days": {
                    "type": "integer",
                    "description": "搜索最近多少天的数据，默认为 7 天",
                    "default": 7,
                    "minimum": 1,
                    "maximum": 90
                },
                "limit": {
                    "type": "integer",
                    "description": "返回的产品数量限制",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 50
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "get_top_products",
        "description": "获取指定日期投票数最多的热门产品",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "日期，格式为 YYYY-MM-DD。如果不提供，默认为今天",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回的产品数量",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                }
            }
        }
    },
    {
        "name": "get_latest_report",
        "description": "获取最新的 Product Hunt 每日报告。报告包含产品分析和趋势总结。",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_report_by_date",
        "description": "根据指定日期获取 Product Hunt 每日报告。日期格式为 YYYY-MM-DD",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "日期，格式为 YYYY-MM-DD，例如：2024-03-15",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                }
            },
            "required": ["date"]
        }
    },
    {
        "name": "get_reports_by_date_range",
        "description": "获取指定日期范围内的所有报告",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期，格式为 YYYY-MM-DD",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期，格式为 YYYY-MM-DD",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                }
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "get_github_trending_report",
        "description": "获取 GitHub Trending 日报。可以指定日期获取特定日期的日报，不指定则返回最新日报。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "日期，格式为 YYYY-MM-DD。如果不提供，返回最新日报",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                }
            }
        }
    }
]


async def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """执行工具调用"""
    db = get_db_service()

    try:
        if name == "get_latest_products":
            days_ago = arguments.get("days_ago", 0)
            limit = arguments.get("limit", 50)

            products = await db.get_latest_products(days_ago=days_ago)

            if not products:
                target_date = datetime.now() - timedelta(days=days_ago)
                return {
                    "content": [{
                        "type": "text",
                        "text": f"未找到 {target_date.strftime('%Y-%m-%d')} 的产品数据"
                    }]
                }

            products = products[:limit]
            result = {
                "date": products[0].get("fetch_date", "").split("T")[0] if products else "",
                "total_count": len(products),
                "products": products
            }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }

        elif name == "get_products_by_date":
            date = arguments["date"]
            limit = arguments.get("limit", 50)

            products = await db.get_products_by_date(date=date)

            if not products:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"未找到 {date} 的产品数据"
                    }]
                }

            products = products[:limit]
            result = {
                "date": date,
                "total_count": len(products),
                "products": products
            }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }

        elif name == "search_products":
            keyword = arguments["keyword"]
            days = arguments.get("days", 7)
            limit = arguments.get("limit", 20)

            products = await db.search_products(
                keyword=keyword,
                days=days,
                limit=limit
            )

            if not products:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"未找到包含关键词 '{keyword}' 的产品（最近 {days} 天）"
                    }]
                }

            result = {
                "keyword": keyword,
                "days": days,
                "total_count": len(products),
                "products": products
            }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }

        elif name == "get_top_products":
            date = arguments.get("date", datetime.now().strftime('%Y-%m-%d'))
            limit = arguments.get("limit", 10)

            products = await db.get_top_products_by_votes(
                date=date,
                limit=limit
            )

            if not products:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"未找到 {date} 的产品数据"
                    }]
                }

            result = {
                "date": date,
                "total_count": len(products),
                "products": products
            }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }

        elif name == "get_latest_report":
            report = await db.get_latest_report()

            if not report:
                return {
                    "content": [{
                        "type": "text",
                        "text": "未找到任何报告"
                    }]
                }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(report, ensure_ascii=False, indent=2)
                }]
            }

        elif name == "get_report_by_date":
            date = arguments["date"]

            report = await db.get_report_by_date(date=date)

            if not report:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"未找到 {date} 的报告"
                    }]
                }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(report, ensure_ascii=False, indent=2)
                }]
            }

        elif name == "get_reports_by_date_range":
            start_date = arguments["start_date"]
            end_date = arguments["end_date"]

            reports = await db.get_reports_by_date_range(
                start_date=start_date,
                end_date=end_date
            )

            if not reports:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"未找到 {start_date} 到 {end_date} 之间的报告"
                    }]
                }

            result = {
                "start_date": start_date,
                "end_date": end_date,
                "total_count": len(reports),
                "reports": reports
            }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }

        elif name == "get_github_trending_report":
            date = arguments.get("date")

            if date:
                # 获取指定日期的日报
                report = await db.get_github_trending_report_by_date(date=date)
                if not report:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"未找到 {date} 的 GitHub Trending 日报"
                        }]
                    }
            else:
                # 获取最新日报
                report = await db.get_latest_github_trending_report()
                if not report:
                    return {
                        "content": [{
                            "type": "text",
                            "text": "未找到任何 GitHub Trending 日报"
                        }]
                    }

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(report, ensure_ascii=False, indent=2)
                }]
            }

        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"未知的工具: {name}"
                }],
                "isError": True
            }

    except Exception as e:
        logger.error(f"处理工具 {name} 时出错: {str(e)}", exc_info=True)
        return {
            "content": [{
                "type": "text",
                "text": f"错误: {str(e)}"
            }],
            "isError": True
        }


# HTTP 路由处理函数
async def health_check(request):
    """健康检查端点"""
    return JSONResponse({
        "status": "healthy",
        "service": "Product Hunt MCP Server",
        "version": "1.0.0",
        "mode": "http",
        "port": PORT
    })


async def root(request):
    """根路径信息"""
    return JSONResponse({
        "service": "Product Hunt MCP Server",
        "description": "MCP server for accessing Product Hunt data via HTTP",
        "version": "1.0.0",
        "transport": "HTTP",
        "port": PORT,
        "endpoints": {
            "health": f"http://{HOST}:{PORT}/health",
            "mcp": f"http://{HOST}:{PORT}/mcp"
        },
        "tools": [tool["name"] for tool in TOOLS],
        "usage": {
            "endpoint": f"http://{HOST}:{PORT}/mcp",
            "method": "POST",
            "content_type": "application/json",
            "health_check": f"curl http://{HOST}:{PORT}/health"
        }
    })


async def mcp_handler(request: Request):
    """MCP JSON-RPC 端点"""
    try:
        body = await request.json()
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": "Parse error",
                "data": str(e)
            },
            "id": None
        }, status_code=400)

    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    logger.info(f"收到请求: method={method}, id={request_id}")

    # 处理 initialize
    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "ph-mcp-server",
                    "version": "1.0.0"
                }
            },
            "id": request_id
        })

    # 处理 tools/list
    elif method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "tools": TOOLS
            },
            "id": request_id
        })

    # 处理 tools/call
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": "Invalid params: missing tool name"
                },
                "id": request_id
            }, status_code=400)

        result = await execute_tool(tool_name, arguments)

        return JSONResponse({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })

    # 处理 notifications/initialized
    elif method == "notifications/initialized":
        # 这是一个通知，不需要响应
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {},
            "id": request_id
        })

    # 处理 ping
    elif method == "ping":
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {},
            "id": request_id
        })

    # 未知方法
    else:
        logger.warning(f"未知方法: {method}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            },
            "id": request_id
        }, status_code=404)


# 创建 Starlette 应用
app = Starlette(
    debug=True,
    routes=[
        Route("/", root),
        Route("/health", health_check),
        Route("/mcp", mcp_handler, methods=["POST"]),
    ]
)


def main():
    """主函数 - 启动 HTTP 服务器"""
    logger.info("=" * 60)
    logger.info("Product Hunt MCP Server (HTTP Mode)")
    logger.info("=" * 60)
    logger.info(f"服务器地址: http://{HOST}:{PORT}")
    logger.info(f"健康检查: http://{HOST}:{PORT}/health")
    logger.info(f"MCP 端点: http://{HOST}:{PORT}/mcp (POST)")
    logger.info("=" * 60)
    logger.info("客户端配置:")
    logger.info(f"  URL: http://{HOST}:{PORT}/mcp")
    logger.info(f"  Method: POST")
    logger.info(f"  Content-Type: application/json")
    logger.info("=" * 60)
    logger.info("按 Ctrl+C 停止服务器")
    logger.info("=" * 60)

    # 启动 HTTP 服务器
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()
