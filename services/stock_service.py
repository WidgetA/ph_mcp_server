import psycopg2
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from config import settings

logger = logging.getLogger(__name__)


class StockService:
    """PostgreSQL 数据库服务 - 美股科技股票资讯"""

    def __init__(self):
        self.conn_params = {
            "host": settings.POSTGRES_HOST,
            "port": int(settings.POSTGRES_PORT),
            "dbname": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "sslmode": "require"
        }
        logger.info("Stock Service 已初始化")

    def _get_connection(self):
        """获取数据库连接"""
        conn = psycopg2.connect(**self.conn_params)
        cur = conn.cursor()
        # 设置 schema
        cur.execute(f"SET search_path TO {settings.POSTGRES_SCHEMA}")
        return conn, cur

    async def get_latest_stock_news(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        获取最新的股票资讯

        由于股票周末不开盘，会自动向前查找最近 days_back 天内的数据

        Args:
            days_back: 向前查找的天数，默认7天

        Returns:
            股票资讯列表
        """
        try:
            conn, cur = self._get_connection()

            # 查询最近几天的数据，按创建时间降序
            # 使用 DATE(created_at) 来按日期分组，获取最新交易日的所有资讯
            query = f"""
                SELECT title, content, source, created_at, updated_at
                FROM {settings.STOCK_TABLE}
                WHERE created_at >= NOW() - INTERVAL '{days_back} days'
                ORDER BY created_at DESC
                LIMIT 100
            """

            cur.execute(query)
            rows = cur.fetchall()

            if not rows:
                logger.info(f"未找到最近 {days_back} 天的股票资讯")
                cur.close()
                conn.close()
                return []

            # 转换为字典列表
            result = []
            for row in rows:
                result.append({
                    "title": row[0],
                    "content": row[1],
                    "source": row[2],
                    "created_at": row[3].isoformat() if row[3] else None,
                    "updated_at": row[4].isoformat() if row[4] else None
                })

            # 获取最新交易日日期
            latest_date = rows[0][3].date() if rows[0][3] else None
            logger.info(f"获取了 {len(result)} 条股票资讯，最新交易日: {latest_date}")

            cur.close()
            conn.close()

            return result

        except Exception as e:
            logger.error(f"获取股票资讯失败: {str(e)}")
            return []

    async def get_latest_trading_day_news(self) -> Dict[str, Any]:
        """
        获取最新交易日的所有股票资讯

        自动处理周末和节假日，返回最近一个交易日的数据

        Returns:
            包含交易日期和资讯列表的字典
        """
        try:
            conn, cur = self._get_connection()

            # 先找到最新的交易日日期
            query = f"""
                SELECT DATE(created_at) as trading_date
                FROM {settings.STOCK_TABLE}
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at) DESC
                LIMIT 1
            """

            cur.execute(query)
            row = cur.fetchone()

            if not row:
                logger.info("未找到最近7天的股票资讯")
                cur.close()
                conn.close()
                return {
                    "trading_date": None,
                    "news_count": 0,
                    "news": []
                }

            latest_trading_date = row[0]

            # 获取该交易日的所有资讯
            query = f"""
                SELECT title, content, source, created_at, updated_at
                FROM {settings.STOCK_TABLE}
                WHERE DATE(created_at) = %s
                ORDER BY created_at DESC
            """

            cur.execute(query, (latest_trading_date,))
            rows = cur.fetchall()

            # 转换为字典列表
            news_list = []
            for row in rows:
                news_list.append({
                    "title": row[0],
                    "content": row[1],
                    "source": row[2],
                    "created_at": row[3].isoformat() if row[3] else None,
                    "updated_at": row[4].isoformat() if row[4] else None
                })

            logger.info(f"获取了最新交易日 {latest_trading_date} 的 {len(news_list)} 条资讯")

            cur.close()
            conn.close()

            return {
                "trading_date": str(latest_trading_date),
                "news_count": len(news_list),
                "news": news_list
            }

        except Exception as e:
            logger.error(f"获取最新交易日资讯失败: {str(e)}")
            return {
                "trading_date": None,
                "news_count": 0,
                "news": [],
                "error": str(e)
            }
