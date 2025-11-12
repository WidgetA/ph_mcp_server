from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # Supabase 配置
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # OpenAI 配置（可选，用于未来功能扩展）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # 数据库表名
    PRODUCTS_TABLE: str = "ph_products"
    REPORTS_TABLE: str = "ph_daily_reports"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
