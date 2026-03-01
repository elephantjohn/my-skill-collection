"""
Image Generator Python SDK
智能选择最优图片生成 API
"""

from .generator import ImageGenerator
from .selector import ImageSelector
from .providers.imagen import ImagenProvider
from .providers.seadream import SeaDreamProvider

__version__ = "1.0.0"
__all__ = [
    "ImageGenerator",
    "ImageSelector",
    "ImagenProvider",
    "SeaDreamProvider",
]
