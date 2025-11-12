"""
测试 MCP Server 的基本功能
"""

import asyncio
import json
from datetime import datetime


async def test_supabase_connection():
    """测试 Supabase 连接"""
    print("\n=== 测试 Supabase 连接 ===")

    try:
        from services.supabase_service import SupabaseService

        db = SupabaseService()
        print("✓ Supabase 连接成功")

        # 测试获取最新产品
        print("\n测试获取最新产品...")
        products = await db.get_latest_products(days_ago=0)

        if products:
            print(f"✓ 获取到 {len(products)} 个产品")
            print(f"\n第一个产品示例:")
            print(json.dumps(products[0], ensure_ascii=False, indent=2))
        else:
            print("⚠ 今天没有产品数据，尝试获取昨天的...")
            products = await db.get_latest_products(days_ago=1)
            if products:
                print(f"✓ 获取到昨天的 {len(products)} 个产品")
            else:
                print("✗ 未找到任何产品数据")

        # 测试获取最新报告
        print("\n测试获取最新报告...")
        report = await db.get_latest_report()

        if report:
            print("✓ 获取到最新报告")
            print(f"  报告日期: {report.get('report_date')}")
            print(f"  内容长度: {len(report.get('report_content', ''))} 字符")
        else:
            print("⚠ 未找到报告数据")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_search_products():
    """测试产品搜索功能"""
    print("\n=== 测试产品搜索 ===")

    try:
        from services.supabase_service import SupabaseService

        db = SupabaseService()

        # 搜索 AI 相关产品
        keyword = "AI"
        print(f"\n搜索关键词: {keyword}")
        products = await db.search_products(keyword=keyword, days=30, limit=5)

        if products:
            print(f"✓ 找到 {len(products)} 个相关产品")
            for i, product in enumerate(products[:3], 1):
                print(f"\n{i}. {product.get('name')}")
                print(f"   标语: {product.get('tagline')}")
                print(f"   日期: {product.get('fetch_date', '')[:10]}")
        else:
            print(f"⚠ 未找到包含 '{keyword}' 的产品")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_top_products():
    """测试获取热门产品"""
    print("\n=== 测试获取热门产品 ===")

    try:
        from services.supabase_service import SupabaseService

        db = SupabaseService()

        # 获取今天的热门产品
        date = datetime.now().strftime('%Y-%m-%d')
        print(f"\n日期: {date}")
        products = await db.get_top_products_by_votes(date=date, limit=5)

        if not products:
            # 如果今天没有数据，尝试昨天
            from datetime import timedelta
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"今天没有数据，尝试昨天: {date}")
            products = await db.get_top_products_by_votes(date=date, limit=5)

        if products:
            print(f"✓ 找到 {len(products)} 个热门产品")
            for i, product in enumerate(products, 1):
                print(f"\n{i}. {product.get('name')}")
                print(f"   票数: {product.get('votes_count')}")
                print(f"   排名: {product.get('rank')}")
        else:
            print("⚠ 未找到热门产品数据")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("Product Hunt MCP Server - 功能测试")
    print("=" * 60)

    results = []

    # 运行各项测试
    results.append(await test_supabase_connection())
    results.append(await test_search_products())
    results.append(await test_top_products())

    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("✓ 所有测试通过！")
    else:
        print("⚠ 部分测试失败")

    print("\n提示: 如果测试失败，请检查:")
    print("1. .env 文件是否正确配置")
    print("2. Supabase 数据库是否可访问")
    print("3. 数据库中是否有数据")


if __name__ == "__main__":
    asyncio.run(main())
