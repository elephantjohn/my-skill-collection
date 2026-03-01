"""
API 选择器
根据场景、预算、需求智能评分各 API
"""

import re
from typing import Dict, List, Any


class ImageSelector:
    """API 选择器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # API 基础评分（1-5 分）
        self.api_ratings = {
            "imagen-4-fast": {
                "quality": 3.5,
                "speed": 5,
                "cost": 5,
                "text": 4,
                "art": 3,
            },
            "imagen-4": {
                "quality": 4,
                "speed": 4,
                "cost": 4,
                "text": 4.5,
                "art": 3.5,
            },
            "imagen-4-ultra": {
                "quality": 5,
                "speed": 3,
                "cost": 3,
                "text": 5,
                "art": 4,
            },
            "seadream-v1": {
                "quality": 3,
                "speed": 5,
                "cost": 5,
                "text": 2,
                "art": 5,
            },
            "seadream-v2": {
                "quality": 4.5,
                "speed": 4,
                "cost": 4,
                "text": 2.5,
                "art": 5,
            },
        }

    def score(self, options: Dict[str, Any]) -> Dict[str, float]:
        """
        为每个 API 评分

        Args:
            options: 选项（prompt, scenario, budget, available_apis）

        Returns:
            各 API 评分字典
        """
        prompt = options.get("prompt", "")
        scenario = options.get("scenario", {})
        budget = options.get("budget", "medium")
        available_apis = options.get("available_apis", [])

        scores = {}

        for api in available_apis:
            rating = self.api_ratings.get(api)
            if not rating:
                continue

            score = 0.0

            # 1. 场景权重
            score += self._score_by_scenario(rating, scenario)

            # 2. 预算权重
            score += self._score_by_budget(rating, budget)

            # 3. 提示词分析
            score += self._score_by_prompt(rating, prompt)

            scores[api] = score

        return scores

    def _score_by_scenario(
        self, rating: Dict[str, float], scenario: Dict[str, Any]
    ) -> float:
        """按场景评分"""
        priority = scenario.get("priority", "balance")
        text_rendering = scenario.get("text_rendering", False)
        score = 0.0

        # 优先级评分
        if priority == "quality":
            score += rating["quality"] * 2
        elif priority == "speed":
            score += rating["speed"] * 2
        elif priority == "cost":
            score += rating["cost"] * 2
        elif priority == "artistic":
            score += rating["art"] * 2
        elif priority == "text_accuracy":
            score += rating["text"] * 2
        else:
            score += (rating["quality"] + rating["speed"] + rating["cost"]) / 3

        # 文字渲染需求
        if text_rendering:
            score += rating["text"] * 1.5

        return score

    def _score_by_budget(
        self, rating: Dict[str, float], budget: str
    ) -> float:
        """按预算评分"""
        if budget == "low":
            return rating["cost"] * 2
        elif budget == "medium":
            return rating["cost"] + rating["quality"]
        elif budget == "high":
            return rating["quality"] * 2
        else:
            return rating["cost"] + rating["quality"]

    def _score_by_prompt(
        self, rating: Dict[str, float], prompt: str
    ) -> float:
        """按提示词分析评分"""
        prompt_lower = prompt.lower()
        score = 0.0

        # 检测是否需要文字渲染
        if re.search(r"(text|word|letter|title|logo|sign)", prompt_lower):
            score += rating["text"] * 1.5

        # 检测艺术风格
        if re.search(r"(illustration|anime|art|painting|drawing)", prompt_lower):
            score += rating["art"] * 1.5

        # 检测真实感需求
        if re.search(r"(realistic|photo|portrait|landscape)", prompt_lower):
            score += rating["quality"] * 1.5

        return score

    def recommend(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        推荐 API（带原因）

        Args:
            options: 选项

        Returns:
            推荐结果
        """
        scores = self.score(options)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_scores:
            return {"api": None, "score": 0, "reasons": []}

        best_api, best_score = sorted_scores[0]
        second_api, second_score = (
            sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)
        )

        reasons = self._get_recommendation_reasons(best_api, options)

        return {
            "api": best_api,
            "score": best_score,
            "reasons": reasons,
            "alternative": second_api,
            "all_scores": scores,
        }

    def _get_recommendation_reasons(
        self, api: str, options: Dict[str, Any]
    ) -> List[str]:
        """获取推荐原因"""
        scenario = options.get("scenario", {})
        budget = options.get("budget", "medium")
        rating = self.api_ratings.get(api, {})

        reasons = []

        if scenario.get("priority") == "quality" and rating.get("quality", 0) >= 4:
            reasons.append("高质量输出")
        if scenario.get("priority") == "artistic" and rating.get("art", 0) >= 4:
            reasons.append("艺术风格优秀")
        if scenario.get("text_rendering") and rating.get("text", 0) >= 4:
            reasons.append("文字渲染准确")
        if budget == "low" and rating.get("cost", 0) >= 4:
            reasons.append("成本低")
        if rating.get("speed", 0) >= 4:
            reasons.append("生成速度快")

        return reasons
