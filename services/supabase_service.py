from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabase 数据库服务"""

    def __init__(self):
        # Product Hunt 数据库客户端
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("Product Hunt Supabase 客户端已初始化")

        # GitHub Trending 数据库客户端
        self.github_client: Client = create_client(
            settings.GITHUB_SUPABASE_URL,
            settings.GITHUB_SUPABASE_KEY
        )
        logger.info("GitHub Trending Supabase 客户端已初始化")

    async def get_latest_products(self, days_ago: int = 0) -> List[Dict[str, Any]]:
        """获取最近的产品数据（默认获取今天的数据）"""
        try:
            # 计算查询日期
            target_date = datetime.now() - timedelta(days=days_ago)
            date_str = target_date.strftime('%Y-%m-%d')

            # 查询数据
            response = self.client.table(settings.PRODUCTS_TABLE)\
                .select("*")\
                .gte('fetch_date', f'{date_str}T00:00:00')\
                .lte('fetch_date', f'{date_str}T23:59:59')\
                .order('rank')\
                .execute()

            products = response.data if response.data else []
            logger.info(f"从 Supabase 获取了 {len(products)} 个产品 (日期: {date_str})")

            return products

        except Exception as e:
            logger.error(f"获取产品数据失败: {str(e)}")
            return []

    async def get_products_by_date(self, date: str) -> List[Dict[str, Any]]:
        """根据日期获取产品数据"""
        try:
            response = self.client.table(settings.PRODUCTS_TABLE)\
                .select("*")\
                .gte('fetch_date', f'{date}T00:00:00')\
                .lte('fetch_date', f'{date}T23:59:59')\
                .order('rank')\
                .execute()

            products = response.data if response.data else []
            logger.info(f"获取了 {len(products)} 个产品 (日期: {date})")

            return products

        except Exception as e:
            logger.error(f"根据日期获取产品失败: {str(e)}")
            return []

    async def search_products(
        self,
        keyword: str,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """搜索产品（按名称、标语或描述）"""
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            # 使用 ilike 进行模糊搜索（同时搜索中英文字段）
            keyword_pattern = f"%{keyword}%"

            response = self.client.table(settings.PRODUCTS_TABLE)\
                .select("*")\
                .gte('fetch_date', f'{start_str}T00:00:00')\
                .lte('fetch_date', f'{end_str}T23:59:59')\
                .or_(f"name.ilike.{keyword_pattern},tagline.ilike.{keyword_pattern},description.ilike.{keyword_pattern},tagline_cn.ilike.{keyword_pattern},description_cn.ilike.{keyword_pattern}")\
                .order('fetch_date', desc=True)\
                .order('rank')\
                .limit(limit)\
                .execute()

            products = response.data if response.data else []
            logger.info(f"搜索 '{keyword}' 找到 {len(products)} 个产品")

            return products

        except Exception as e:
            logger.error(f"搜索产品失败: {str(e)}")
            return []

    async def get_report_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """根据日期获取报告"""
        try:
            response = self.client.table(settings.REPORTS_TABLE)\
                .select("*")\
                .eq('report_date', date)\
                .limit(1)\
                .execute()

            if response.data and len(response.data) > 0:
                logger.info(f"获取了日期 {date} 的报告")
                return response.data[0]

            logger.info(f"未找到日期 {date} 的报告")
            return None

        except Exception as e:
            logger.error(f"根据日期获取报告失败: {str(e)}")
            return None

    async def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """获取最新的日报"""
        try:
            response = self.client.table(settings.REPORTS_TABLE)\
                .select("*")\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()

            if response.data and len(response.data) > 0:
                logger.info("获取了最新的日报")
                return response.data[0]

            logger.info("未找到任何日报")
            return None

        except Exception as e:
            logger.error(f"获取最新日报失败: {str(e)}")
            return None

    async def get_reports_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """根据日期范围获取报告"""
        try:
            response = self.client.table(settings.REPORTS_TABLE)\
                .select("*")\
                .gte('report_date', start_date)\
                .lte('report_date', end_date)\
                .order('report_date', desc=True)\
                .execute()

            reports = response.data if response.data else []
            logger.info(f"获取了 {len(reports)} 个报告 ({start_date} 到 {end_date})")

            return reports

        except Exception as e:
            logger.error(f"根据日期范围获取报告失败: {str(e)}")
            return []

    async def get_top_products_by_votes(
        self,
        date: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取指定日期投票数最多的产品"""
        try:
            response = self.client.table(settings.PRODUCTS_TABLE)\
                .select("*")\
                .gte('fetch_date', f'{date}T00:00:00')\
                .lte('fetch_date', f'{date}T23:59:59')\
                .order('votes_count', desc=True)\
                .limit(limit)\
                .execute()

            products = response.data if response.data else []
            logger.info(f"获取了 {len(products)} 个高票产品 (日期: {date})")

            return products

        except Exception as e:
            logger.error(f"获取高票产品失败: {str(e)}")
            return []

    async def get_github_trending_report_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """根据日期获取 GitHub Trending 日报"""
        try:
            response = self.github_client.table(settings.GITHUB_REPORTS_TABLE)\
                .select("*")\
                .eq('report_date', date)\
                .limit(1)\
                .execute()

            if response.data and len(response.data) > 0:
                logger.info(f"获取了日期 {date} 的 GitHub Trending 日报")
                return response.data[0]

            logger.info(f"未找到日期 {date} 的 GitHub Trending 日报")
            return None

        except Exception as e:
            logger.error(f"根据日期获取 GitHub Trending 日报失败: {str(e)}")
            return None

    async def get_latest_github_trending_report(self) -> Optional[Dict[str, Any]]:
        """获取最新的 GitHub Trending 日报"""
        try:
            response = self.github_client.table(settings.GITHUB_REPORTS_TABLE)\
                .select("*")\
                .order('report_date', desc=True)\
                .limit(1)\
                .execute()

            if response.data and len(response.data) > 0:
                logger.info("获取了最新的 GitHub Trending 日报")
                return response.data[0]

            logger.info("未找到任何 GitHub Trending 日报")
            return None

        except Exception as e:
            logger.error(f"获取最新 GitHub Trending 日报失败: {str(e)}")
            return None
