import os
from typing import Optional


class Settings:
    """应用配置 - 从环境变量读取"""

    # Product Hunt Supabase 配置
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Product Hunt 数据库表名
    PRODUCTS_TABLE: str = os.getenv("PRODUCTS_TABLE", "ph_products")
    REPORTS_TABLE: str = os.getenv("REPORTS_TABLE", "ph_daily_reports")

    # GitHub Trending Supabase 配置
    GITHUB_SUPABASE_URL: str = os.getenv("GITHUB_SUPABASE_URL", "")
    GITHUB_SUPABASE_KEY: str = os.getenv("GITHUB_SUPABASE_KEY", "")

    # GitHub Trending 日报表名
    GITHUB_REPORTS_TABLE: str = os.getenv("GITHUB_REPORTS_TABLE", "github_trending_reports")

    # PostgreSQL 数据库配置（美股科技股票）
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_SCHEMA: str = os.getenv("POSTGRES_SCHEMA", "public")

    # 股票数据表名
    STOCK_TABLE: str = os.getenv("STOCK_TABLE", "tech_stocks")


settings = Settings()
