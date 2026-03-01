#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini 图像生成器
使用 Gemini 3.1 Flash Image Preview 模型生成高质量图片
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict

try:
    from google import genai
    from google.genai import types
    from PIL import Image
except ImportError as e:
    print(f"错误：需要安装依赖包")
    print(f"运行：pip install google-genai pillow")
    sys.exit(1)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiImageGenerator:
    """Gemini 图像生成器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化生成器
        
        Args:
            api_key: Gemini API 密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('GEMINI3PRO_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置 GEMINI3PRO_API_KEY 环境变量")
        
        # 初始化客户端（必须传入 api_key）
        self.client = genai.Client(api_key=self.api_key)
        
        # 设置日志目录
        self.logs_dir = Path("logs/gemini_image")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 提示词风格模板
        self.style_templates = {
            "人生思考": "极简艺术风格，禅意美学，留白构图，淡雅色彩，抽象表达，高质量",
            "童话故事": "梦幻插画风格，水彩画，温暖色调，柔和光线，童话场景，高质量",
            "科技探索": "科幻概念艺术，未来主义风格，蓝紫色调，科技感光效，高质量",
            "美食文化": "美食摄影风格，高清特写，暖色调，诱人光泽，生活场景，高质量",
            "旅行游记": "风景摄影风格，广角镜头，自然光，高饱和度，真实场景，高质量",
        }
    
    def generate(
        self,
        prompt: str,
        save_path: str,
        model: str = "gemini-3.1-flash-image-preview",
        max_retries: int = 3
    ) -> Optional[str]:
        """生成单张图片
        
        Args:
            prompt: 图片描述
            save_path: 保存路径
            model: 使用的模型
            max_retries: 最大重试次数
            
        Returns:
            保存的文件路径，失败返回 None
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"生成图片：{prompt[:50]}... (尝试 {attempt+1}/{max_retries})")
                
                response = self.client.models.generate_content(
                    model=model,
                    contents=[prompt]
                )
                
                # 处理响应
                for part in response.parts:
                    if part.inline_data is not None:
                        # 转换为 PIL Image 并保存
                        image = part.as_image()
                        
                        # 确保保存目录存在
                        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                        
                        # 保存为 PNG
                        if not save_path.lower().endswith('.png'):
                            save_path = save_path.rsplit('.', 1)[0] + '.png'
                        
                        image.save(save_path, 'PNG')
                        logger.info(f"✅ 图片已保存：{save_path}")
                        
                        return save_path
                
                logger.error(f"❌ 响应中没有图片数据")
                return None
                
            except Exception as e:
                logger.error(f"生成失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"❌ 超过最大重试次数")
                    return None
        
        return None
    
    def generate_for_article(
        self,
        title: str,
        content: str,
        count: int = 2,
        category: str = "人生思考",
        save_dir: str = "./article_images"
    ) -> List[Optional[str]]:
        """为文章生成配图
        
        Args:
            title: 文章标题
            content: 文章内容
            count: 生成图片数量
            category: 文章类别
            save_dir: 保存目录
            
        Returns:
            图片路径列表
        """
        logger.info(f"为文章生成配图：{title}")
        logger.info(f"类别：{category}, 数量：{count}")
        
        # 获取风格模板
        style = self.style_templates.get(category, "现代艺术风格，高清摄影，高质量")
        
        # 生成提示词
        prompts = self._generate_prompts(title, content, category, count, style)
        
        # 批量生成
        images = []
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        for i, prompt in enumerate(prompts):
            save_path = f"{save_dir}/article_{Path(title).stem}_{i+1}.png"
            image_path = self.generate(prompt, save_path)
            images.append(image_path)
        
        return images
    
    def _generate_prompts(
        self,
        title: str,
        content: str,
        category: str,
        count: int,
        style: str
    ) -> List[str]:
        """根据文章内容生成图片提示词
        
        Args:
            title: 标题
            content: 内容
            category: 类别
            count: 数量
            style: 风格
            
        Returns:
            提示词列表
        """
        prompts = []
        
        # 提取关键词（简单实现）
        keywords = self._extract_keywords(content)
        
        if category == "人生思考":
            # 人生思考类：情感、意境
            prompts = [
                f"{style}，{title}，{keywords.get('emotion', '思考')}，{keywords.get('scene', '城市')}，插画",
                f"{style}，{title}，{keywords.get('theme', '成长')}，{keywords.get('mood', '孤独')}，艺术感"
            ]
        elif category == "童话故事":
            # 童话类：梦幻、温馨
            prompts = [
                f"{style}，{title}，{keywords.get('character', '主角')}，{keywords.get('setting', '森林')}，童话场景",
                f"{style}，{title}，{keywords.get('magic', '魔法')}，{keywords.get('adventure', '冒险')}，梦幻"
            ]
        elif category == "科技探索":
            # 科技类：未来、概念
            prompts = [
                f"{style}，{title}，{keywords.get('tech', '科技')}，未来主义，概念艺术",
                f"{style}，{title}，{keywords.get('innovation', '创新')}，数字化，科幻"
            ]
        elif category == "美食文化":
            # 美食类：诱人、特写
            prompts = [
                f"{style}，{title}，{keywords.get('food', '美食')}，高清特写，诱人",
                f"{style}，{title}，{keywords.get('cooking', '烹饪')}，{keywords.get('taste', '味道')}，生活"
            ]
        elif category == "旅行游记":
            # 旅行类：风景、人文
            prompts = [
                f"{style}，{title}，{keywords.get('place', '地点')}，{keywords.get('scenery', '风景')}，广角",
                f"{style}，{title}，{keywords.get('culture', '文化')}，{keywords.get('people', '人文')}，真实"
            ]
        else:
            # 默认
            prompts = [
                f"{style}，{title}，{keywords.get('main', '主题')}，高质量",
                f"{style}，{title}，{keywords.get('secondary', '次要')}，艺术感"
            ]
        
        # 确保数量匹配
        while len(prompts) < count:
            prompts.append(f"{style}，{title}，高质量配图 {len(prompts)+1}")
        
        return prompts[:count]
    
    def _extract_keywords(self, content: str) -> Dict[str, str]:
        """从内容中提取关键词（简单实现）
        
        Args:
            content: 文章内容
            
        Returns:
            关键词字典
        """
        # 简单实现，实际可以用 NLP 模型优化
        keywords = {
            "emotion": "情感",
            "scene": "场景",
            "theme": "主题",
            "mood": "心情",
            "main": "主要",
            "secondary": "次要"
        }
        
        # 简单匹配
        if "离别" in content or "告别" in content:
            keywords["emotion"] = "离别不舍"
        if "城市" in content or "都市" in content:
            keywords["scene"] = "城市夜景"
        if "成长" in content or "梦想" in content:
            keywords["theme"] = "成长梦想"
        if "孤独" in content or "一个人" in content:
            keywords["mood"] = "孤独坚定"
        
        return keywords
    
    def batch_generate(
        self,
        prompts: List[str],
        save_dir: str,
        prefix: str = "image"
    ) -> List[Optional[str]]:
        """批量生成图片
        
        Args:
            prompts: 提示词列表
            save_dir: 保存目录
            prefix: 文件名前缀
            
        Returns:
            图片路径列表
        """
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        images = []
        for i, prompt in enumerate(prompts):
            save_path = f"{save_dir}/{prefix}_{i+1}.png"
            image_path = self.generate(prompt, save_path)
            images.append(image_path)
        
        return images
    
    def optimize_prompt(
        self,
        prompt: str,
        category: str = "人生思考",
        style: Optional[str] = None
    ) -> str:
        """优化提示词
        
        Args:
            prompt: 原始提示词
            category: 类别
            style: 风格（可选）
            
        Returns:
            优化后的提示词
        """
        if not style:
            style = self.style_templates.get(category, "现代艺术风格，高清摄影")
        
        return f"{style}，{prompt}"


def generate_image(
    prompt: str,
    save_path: str,
    api_key: Optional[str] = None
) -> Optional[str]:
    """便捷函数：生成单张图片"""
    generator = GeminiImageGenerator(api_key)
    return generator.generate(prompt, save_path)


def generate_article_images(
    title: str,
    content: str,
    category: str = "人生思考",
    count: int = 2,
    save_dir: str = "./article_images"
) -> List[Optional[str]]:
    """便捷函数：为文章生成配图"""
    generator = GeminiImageGenerator()
    return generator.generate_for_article(title, content, count, category, save_dir)


if __name__ == "__main__":
    # 测试
    import sys
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
    
    print(f"生成图片：{prompt}")
    image_path = generate_image(prompt, "test_output.png")
    
    if image_path:
        print(f"✅ 图片已生成：{image_path}")
    else:
        print("❌ 生成失败")
