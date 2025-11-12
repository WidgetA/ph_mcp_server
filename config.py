import os
from typing import Optional


class Settings:
    """应用配置 - 从环境变量读取"""

    # Supabase 配置
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # 数据库表名
    PRODUCTS_TABLE: str = os.getenv("PRODUCTS_TABLE", "ph_products")
    REPORTS_TABLE: str = os.getenv("REPORTS_TABLE", "ph_daily_reports")


settings = Settings()
