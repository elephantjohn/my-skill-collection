"""
通用图片生成器
智能选择最优 API，支持多个后端
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .selector import ImageSelector
from .providers.imagen import ImagenProvider
from .providers.seadream import SeaDreamProvider
from .utils.cost import CostTracker

logger = logging.getLogger(__name__)


class ImageGenerator:
    """通用图片生成器"""

    def __init__(
        self,
        google_api_key: Optional[str] = None,
        google_project_id: Optional[str] = None,
        google_location: str = "us-central1",
        seadream_api_key: Optional[str] = None,
        default_api: str = "auto",
        budget_mode: str = "medium",
        max_daily_cost: float = 10.0,
    ):
        """
        初始化生成器

        Args:
            google_api_key: Google API Key
            google_project_id: Google 项目 ID
            google_location: Google Cloud 区域
            seadream_api_key: SeaDream API Key
            default_api: 默认 API（auto 表示自动选择）
            budget_mode: 预算模式 (low|medium|high)
            max_daily_cost: 每日预算上限（美元）
        """
        self.config = {
            "google_api_key": google_api_key or os.getenv("GOOGLE_API_KEY"),
            "google_project_id": google_project_id or os.getenv("GOOGLE_PROJECT_ID"),
            "google_location": google_location,
            "seadream_api_key": seadream_api_key or os.getenv("SEADREAM_API_KEY"),
            "default_api": default_api,
            "budget_mode": budget_mode,
            "max_daily_cost": max_daily_cost,
        }

        # 初始化提供商
        self.providers = {
            "imagen-4-fast": ImagenProvider({**self.config, "version": "4-fast"}),
            "imagen-4": ImagenProvider({**self.config, "version": "4"}),
            "imagen-4-ultra": ImagenProvider({**self.config, "version": "4-ultra"}),
            "seadream-v1": SeaDreamProvider({**self.config, "version": "v1"}),
            "seadream-v2": SeaDreamProvider({**self.config, "version": "v2"}),
        }

        # 初始化选择器和成本追踪
        self.selector = ImageSelector(self.config)
        self.cost_tracker = CostTracker(self.config["max_daily_cost"])

        # 场景配置
        self.scenarios = {
            "cover": {
                "priority": "quality",
                "min_resolution": "2K",
                "preferred_apis": ["imagen-4-ultra", "seadream-v2", "imagen-4"],
            },
            "product": {
                "priority": "accuracy",
                "text_rendering": True,
                "preferred_apis": ["imagen-4-ultra", "imagen-4", "imagen-4-fast"],
            },
            "illustration": {
                "priority": "artistic",
                "preferred_apis": ["seadream-v2", "seadream-v1", "imagen-4-ultra"],
            },
            "text": {
                "priority": "text_accuracy",
                "text_rendering": True,
                "preferred_apis": ["imagen-4-ultra", "imagen-4"],
            },
            "general": {
                "priority": "balance",
                "preferred_apis": ["imagen-4", "imagen-4-fast", "seadream-v2"],
            },
        }

    def generate(
        self,
        prompt: str,
        scenario: str = "general",
        api: str = None,
        budget: str = None,
        negative_prompt: str = None,
        resolution: str = "1024x1024",
        count: int = 1,
    ) -> Dict[str, Any]:
        """
        生成单张图片

        Args:
            prompt: 提示词
            scenario: 场景 (cover|product|illustration|text|general)
            api: 指定 API（None 表示自动选择）
            budget: 预算 (low|medium|high)
            negative_prompt: 负面提示词
            resolution: 分辨率
            count: 数量

        Returns:
            生成结果（包含图片 URL、成本、使用的 API 等）
        """
        api = api or self.config["default_api"]
        budget = budget or self.config["budget_mode"]

        # 检查预算
        estimated_cost = self._estimate_cost(api, count)
        if not self.cost_tracker.can_spend(estimated_cost):
            raise RuntimeError("超出每日预算限制")

        # 智能选择 API
        selected_api = api if api != "auto" else self._select_best_api(
            prompt, scenario, budget
        )

        logger.info(f"🎨 选择 API: {selected_api} (场景：{scenario})")

        # 获取提供商
        provider = self.providers.get(selected_api)
        if not provider:
            raise ValueError(f"不支持的 API: {selected_api}")

        # 生成图片
        result = provider.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            resolution=resolution,
            count=count,
        )

        # 记录成本
        self.cost_tracker.record(selected_api, result["cost"])

        return {
            **result,
            "used_api": selected_api,
            "scenario": scenario,
        }

    def batch_generate(
        self,
        prompts: List[str],
        scenario: str = "general",
        max_cost: float = 10.0,
    ) -> Dict[str, Any]:
        """
        批量生成

        Args:
            prompts: 提示词列表
            scenario: 场景
            max_cost: 预算上限

        Returns:
            批量生成结果
        """
        results = []
        total_cost = 0.0

        for prompt in prompts:
            estimate = self._estimate_cost("auto", 1)
            if total_cost + estimate > max_cost:
                logger.warning(f"⚠️ 达到预算上限，剩余 {len(prompts) - len(results)} 个未生成")
                break

            try:
                result = self.generate(prompt=prompt, scenario=scenario)
                results.append(result)
                total_cost += result["cost"]
            except Exception as e:
                logger.error(f"❌ 生成失败：{prompt} - {str(e)}")
                results.append({"error": str(e), "prompt": prompt})

        return {
            "results": results,
            "total_cost": total_cost,
            "count": len(results),
        }

    def _select_best_api(
        self, prompt: str, scenario: str, budget: str
    ) -> str:
        """智能选择最佳 API"""
        scenario_config = self.scenarios.get(scenario, self.scenarios["general"])

        # 使用选择器评分
        scores = self.selector.score({
            "prompt": prompt,
            "scenario": scenario_config,
            "budget": budget,
            "available_apis": list(self.providers.keys()),
        })

        # 返回最高分的 API
        best_api = max(scores.items(), key=lambda x: x[1])[0]

        logger.debug(f"📊 API 评分：{scores}")

        return best_api or "imagen-4-fast"

    def _estimate_cost(self, api: str, count: int) -> float:
        """估算成本"""
        pricing = {
            "imagen-4-fast": 0.02,
            "imagen-4": 0.04,
            "imagen-4-ultra": 0.06,
            "seadream-v1": 0.01,
            "seadream-v2": 0.03,
        }
        return pricing.get(api, 0.04) * count

    def get_cost_stats(self, period: str = "day", api: str = "all") -> Dict[str, Any]:
        """获取成本统计"""
        return self.cost_tracker.get_stats(period, api)

    def get_supported_apis(self) -> List[Dict[str, Any]]:
        """获取支持的 API 列表"""
        return [
            {
                "name": name,
                "pricing": provider.pricing,
                "capabilities": provider.capabilities,
            }
            for name, provider in self.providers.items()
        ]
