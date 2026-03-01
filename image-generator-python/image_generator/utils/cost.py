"""
成本追踪器
记录和统计 API 使用成本
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CostTracker:
    """成本追踪器"""

    def __init__(self, max_daily_cost: float = 10.0):
        """
        初始化

        Args:
            max_daily_cost: 每日预算上限
        """
        self.max_daily_cost = max_daily_cost
        self.records: List[Dict[str, Any]] = []

    def record(
        self, api: str, cost: float, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        记录一次使用

        Args:
            api: 使用的 API
            cost: 成本
            metadata: 元数据
        """
        now = datetime.now()
        record = {
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "api": api,
            "cost": cost,
            **(metadata or {}),
        }

        self.records.append(record)
        logger.info(f"💰 记录成本：${cost:.4f} ({api})")

    def can_spend(self, estimated_cost: float) -> bool:
        """
        检查是否可以支出

        Args:
            estimated_cost: 预计成本

        Returns:
            是否可以支出
        """
        today = datetime.now().strftime("%Y-%m-%d")
        today_cost = sum(
            r["cost"] for r in self.records if r["date"] == today
        )

        return today_cost + estimated_cost <= self.max_daily_cost

    def get_today_cost(self) -> float:
        """获取今日已用成本"""
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(r["cost"] for r in self.records if r["date"] == today)

    def get_stats(
        self, period: str = "day", api: str = "all"
    ) -> Dict[str, Any]:
        """
        获取统计信息

        Args:
            period: 时间范围 (day|week|month)
            api: API 名称或 all

        Returns:
            统计信息
        """
        now = datetime.now()
        filtered = self.records

        # 按 API 筛选
        if api != "all":
            filtered = [r for r in filtered if r["api"] == api]

        # 按时间筛选
        if period == "day":
            today = now.strftime("%Y-%m-%d")
            filtered = [r for r in filtered if r["date"] == today]
        elif period == "week":
            week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
            filtered = [r for r in filtered if r["date"] >= week_ago]
        elif period == "month":
            month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
            filtered = [r for r in filtered if r["date"] >= month_ago]

        total_cost = sum(r["cost"] for r in filtered)
        count = len(filtered)

        # 按 API 分组
        by_api: Dict[str, Dict[str, float]] = {}
        for record in filtered:
            api_name = record["api"]
            if api_name not in by_api:
                by_api[api_name] = {"cost": 0.0, "count": 0}
            by_api[api_name]["cost"] += record["cost"]
            by_api[api_name]["count"] += 1

        return {
            "period": period,
            "total_cost": total_cost,
            "count": count,
            "avg_cost": total_cost / count if count > 0 else 0.0,
            "by_api": by_api,
            "remaining_budget": self.max_daily_cost - self.get_today_cost(),
        }

    def reset(self) -> None:
        """重置记录"""
        self.records = []

    def export(self) -> str:
        """导出记录（JSON）"""
        import json
        return json.dumps(self.records, ensure_ascii=False)

    def import_records(self, json_str: str) -> None:
        """导入记录"""
        import json
        try:
            self.records = json.loads(json_str)
        except Exception as e:
            logger.error(f"导入记录失败：{str(e)}")
