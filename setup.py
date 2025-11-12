#!/usr/bin/env python3
"""
快速设置脚本 - 帮助配置 MCP Server
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """创建 .env 文件"""
    print("=" * 60)
    print("Product Hunt MCP Server - 配置向导")
    print("=" * 60)

    env_file = Path(".env")

    if env_file.exists():
        response = input("\n.env 文件已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return False

    print("\n请输入以下配置信息:")
    print("(按 Ctrl+C 取消)\n")

    try:
        supabase_url = input("Supabase URL: ").strip()
        if not supabase_url:
            print("错误: Supabase URL 不能为空")
            return False

        supabase_key = input("Supabase Key: ").strip()
        if not supabase_key:
            print("错误: Supabase Key 不能为空")
            return False

        # 可选配置
        products_table = input("Products 表名 (默认: ph_products): ").strip() or "ph_products"
        reports_table = input("Reports 表名 (默认: ph_daily_reports): ").strip() or "ph_daily_reports"

        # 写入 .env 文件
        env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# Database Tables
PRODUCTS_TABLE={products_table}
REPORTS_TABLE={reports_table}
"""

        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)

        print("\n✓ .env 文件创建成功！")
        return True

    except KeyboardInterrupt:
        print("\n\n已取消")
        return False
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return False


def test_connection():
    """测试数据库连接"""
    print("\n测试数据库连接...")

    try:
        import asyncio
        from services.supabase_service import SupabaseService

        async def test():
            db = SupabaseService()
            products = await db.get_latest_products(days_ago=0)
            return len(products) if products else 0

        count = asyncio.run(test())
        print(f"✓ 连接成功！找到 {count} 个产品")
        return True

    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        print("\n请检查:")
        print("1. Supabase URL 和 Key 是否正确")
        print("2. 网络连接是否正常")
        print("3. 数据库表是否存在")
        return False


def generate_mcp_config():
    """生成 MCP 配置示例"""
    current_dir = Path.cwd().resolve()
    server_path = current_dir / "server.py"

    # 读取 .env 文件
    env_vars = {}
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

    config = {
        "mcpServers": {
            "ph-mcp-server": {
                "command": "python",
                "args": [str(server_path).replace("\\", "\\\\")],
                "env": env_vars
            }
        }
    }

    print("\n" + "=" * 60)
    print("MCP 客户端配置示例")
    print("=" * 60)
    print("\n将以下配置添加到你的 MCP 客户端配置文件中:\n")

    import json
    print(json.dumps(config, indent=2, ensure_ascii=False))

    print("\n配置文件位置:")
    print("  Claude Desktop (macOS): ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Claude Desktop (Windows): %APPDATA%\\Claude\\claude_desktop_config.json")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 只测试连接
        test_connection()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        # 只生成配置
        generate_mcp_config()
        return

    # 完整设置流程
    if not create_env_file():
        return

    # 测试连接
    response = input("\n是否测试数据库连接？(Y/n): ")
    if response.lower() != 'n':
        test_connection()

    # 生成配置
    response = input("\n是否生成 MCP 客户端配置？(Y/n): ")
    if response.lower() != 'n':
        generate_mcp_config()

    print("\n" + "=" * 60)
    print("设置完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 将上面的配置添加到你的 MCP 客户端配置文件")
    print("2. 重启 MCP 客户端")
    print("3. 开始使用 Product Hunt MCP Server！")
    print("\n运行测试:")
    print("  python tests/test_server.py")


if __name__ == "__main__":
    main()
