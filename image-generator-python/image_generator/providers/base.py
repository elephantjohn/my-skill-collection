"""
图片生成器基础类
所有提供商必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseProvider(ABC):
    """基础提供商类（抽象类）"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "base"
        self.pricing = 0.0
        self.capabilities: List[str] = []

    @abstractmethod
    def generate(
        self, prompt: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成图片（必须由子类实现）

        Args:
            prompt: 提示词
            options: 选项

        Returns:
            生成结果
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置（必须由子类实现）

        Returns:
            是否有效
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """获取提供商信息"""
        return {
            "name": self.name,
            "pricing": self.pricing,
            "capabilities": self.capabilities,
        }
