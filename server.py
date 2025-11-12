#!/usr/bin/env python3
"""
Product Hunt MCP Server (Remote HTTP Mode)

这个 MCP server 提供访问 Product Hunt 数据的能力，
包括产品列表、报告等信息。

运行模式：HTTP/SSE 远程服务器，监听在 8080 端口
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

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

# 创建 MCP server 实例
mcp_server = Server("ph-mcp-server")

# 初始化 Supabase 服务
db_service: Optional[SupabaseService] = None


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="get_latest_products",
            description="获取最新的 Product Hunt 产品列表。默认获取今天的数据，可以通过 days_ago 参数指定获取几天前的数据。",
            inputSchema={
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
        ),
        Tool(
            name="get_products_by_date",
            description="根据指定日期获取 Product Hunt 产品列表。日期格式为 YYYY-MM-DD，例如：2024-03-15",
            inputSchema={
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
        ),
        Tool(
            name="search_products",
            description="搜索 Product Hunt 产品。支持按产品名称、标语（tagline）或描述进行模糊搜索。",
            inputSchema={
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
        ),
        Tool(
            name="get_top_products",
            description="获取指定日期投票数最多的热门产品",
            inputSchema={
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
        ),
        Tool(
            name="get_latest_report",
            description="获取最新的 Product Hunt 每日报告。报告包含产品分析和趋势总结。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_report_by_date",
            description="根据指定日期获取 Product Hunt 每日报告。日期格式为 YYYY-MM-DD",
            inputSchema={
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
        ),
        Tool(
            name="get_reports_by_date_range",
            description="获取指定日期范围内的所有报告",
            inputSchema={
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
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    global db_service

    # 延迟初始化数据库服务
    if db_service is None:
        db_service = SupabaseService()

    try:
        if name == "get_latest_products":
            days_ago = arguments.get("days_ago", 0)
            limit = arguments.get("limit", 50)

            products = await db_service.get_latest_products(days_ago=days_ago)

            if not products:
                target_date = datetime.now() - timedelta(days=days_ago)
                return [TextContent(
                    type="text",
                    text=f"未找到 {target_date.strftime('%Y-%m-%d')} 的产品数据"
                )]

            # 限制返回数量
            products = products[:limit]

            result = {
                "date": products[0].get("fetch_date", "").split("T")[0] if products else "",
                "total_count": len(products),
                "products": products
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "get_products_by_date":
            date = arguments["date"]
            limit = arguments.get("limit", 50)

            products = await db_service.get_products_by_date(date=date)

            if not products:
                return [TextContent(
                    type="text",
                    text=f"未找到 {date} 的产品数据"
                )]

            # 限制返回数量
            products = products[:limit]

            result = {
                "date": date,
                "total_count": len(products),
                "products": products
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "search_products":
            keyword = arguments["keyword"]
            days = arguments.get("days", 7)
            limit = arguments.get("limit", 20)

            products = await db_service.search_products(
                keyword=keyword,
                days=days,
                limit=limit
            )

            if not products:
                return [TextContent(
                    type="text",
                    text=f"未找到包含关键词 '{keyword}' 的产品（最近 {days} 天）"
                )]

            result = {
                "keyword": keyword,
                "days": days,
                "total_count": len(products),
                "products": products
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "get_top_products":
            date = arguments.get("date", datetime.now().strftime('%Y-%m-%d'))
            limit = arguments.get("limit", 10)

            products = await db_service.get_top_products_by_votes(
                date=date,
                limit=limit
            )

            if not products:
                return [TextContent(
                    type="text",
                    text=f"未找到 {date} 的产品数据"
                )]

            result = {
                "date": date,
                "total_count": len(products),
                "products": products
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "get_latest_report":
            report = await db_service.get_latest_report()

            if not report:
                return [TextContent(
                    type="text",
                    text="未找到任何报告"
                )]

            return [TextContent(
                type="text",
                text=json.dumps(report, ensure_ascii=False, indent=2)
            )]

        elif name == "get_report_by_date":
            date = arguments["date"]

            report = await db_service.get_report_by_date(date=date)

            if not report:
                return [TextContent(
                    type="text",
                    text=f"未找到 {date} 的报告"
                )]

            return [TextContent(
                type="text",
                text=json.dumps(report, ensure_ascii=False, indent=2)
            )]

        elif name == "get_reports_by_date_range":
            start_date = arguments["start_date"]
            end_date = arguments["end_date"]

            reports = await db_service.get_reports_by_date_range(
                start_date=start_date,
                end_date=end_date
            )

            if not reports:
                return [TextContent(
                    type="text",
                    text=f"未找到 {start_date} 到 {end_date} 之间的报告"
                )]

            result = {
                "start_date": start_date,
                "end_date": end_date,
                "total_count": len(reports),
                "reports": reports
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=f"未知的工具: {name}"
            )]

    except Exception as e:
        logger.error(f"处理工具 {name} 时出错: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"错误: {str(e)}"
        )]


# HTTP 路由处理函数
async def health_check(request):
    """健康检查端点"""
    return JSONResponse({
        "status": "healthy",
        "service": "Product Hunt MCP Server",
        "version": "1.0.0",
        "mode": "remote",
        "port": PORT
    })


async def root(request):
    """根路径信息"""
    return JSONResponse({
        "service": "Product Hunt MCP Server",
        "description": "MCP server for accessing Product Hunt data via SSE",
        "version": "1.0.0",
        "transport": "SSE",
        "port": PORT,
        "endpoints": {
            "health": f"http://{HOST}:{PORT}/health",
            "mcp_sse": f"http://{HOST}:{PORT}/sse (GET)",
            "mcp_messages": f"http://{HOST}:{PORT}/messages (POST)"
        },
        "tools": [
            "get_latest_products",
            "get_products_by_date",
            "search_products",
            "get_top_products",
            "get_latest_report",
            "get_report_by_date",
            "get_reports_by_date_range"
        ],
        "usage": {
            "client_url": f"http://{HOST}:{PORT}/sse",
            "note": "SSE endpoint (GET /sse) and messages endpoint (POST /messages) are both required for MCP",
            "health_check": f"curl http://{HOST}:{PORT}/health"
        }
    })


# 创建 SSE transport
# MCP SSE 需要 POST 端点来接收客户端消息
sse_transport = SseServerTransport("/messages")

# 处理 SSE 连接 (GET 请求建立 SSE 流)
async def handle_sse(scope, receive, send):
    """处理 SSE 连接 (GET)"""
    async with sse_transport.connect_sse(scope, receive, send) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )


# 处理客户端消息 (POST 请求发送消息)
async def handle_messages(scope, receive, send):
    """处理客户端消息 (POST)"""
    async with sse_transport.connect_sse(scope, receive, send) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )


# 创建 Starlette 应用
app = Starlette(
    debug=True,
    routes=[
        Route("/", root),
        Route("/health", health_check),
        Route("/sse", handle_sse, methods=["GET"]),
        Route("/messages", handle_messages, methods=["POST"]),
    ]
)


def main():
    """主函数 - 启动 HTTP 服务器"""
    logger.info("=" * 60)
    logger.info("Product Hunt MCP Server (Remote HTTP Mode)")
    logger.info("=" * 60)
    logger.info(f"服务器地址: http://{HOST}:{PORT}")
    logger.info(f"健康检查: http://{HOST}:{PORT}/health")
    logger.info(f"MCP SSE 端点: http://{HOST}:{PORT}/sse (GET)")
    logger.info(f"MCP 消息端点: http://{HOST}:{PORT}/messages (POST)")
    logger.info("=" * 60)
    logger.info("客户端配置:")
    logger.info(f"  URL: http://{HOST}:{PORT}/sse")
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
