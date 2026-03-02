#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号书评影评类文章写作器
提供有深度的作品解读
"""

import random
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WechatReviewWriter:
    """书评影评类文章写作器"""
    
    title_templates = [
        "{work}：{viewpoint}",
        "看完{work}，我想说...",
        "{work}：被{overlook}的{detail}",
        "深度解读{work}：{theme}",
    ]
    
    def write(self, work: str, work_type: str = "书", word_count: int = 3000) -> str:
        """生成书评/影评"""
        logger.info(f"生成{work_type}评：{work}")
        title = self.generate_titles(work, count=1)[0]
        
        article = f"# {title}\n\n"
        article += self._write_opening(work, work_type) + "\n\n"
        
        for i in range(4):
            article += f"## {self._get_section(i)}\n\n"
            article += self._write_section(work, work_type) + "\n\n"
        
        article += self._write_ending(work, work_type)
        return article
    
    def generate_titles(self, work: str, count: int = 10) -> List[str]:
        """生成标题"""
        titles = []
        for template in self.title_templates:
            title = template.format(
                work=work,
                viewpoint="被低估的佳作",
                overlook="忽略",
                detail="细节",
                theme="人性的复杂"
            )
            titles.append(title)
        return titles[:count]
    
    def _get_section(self, index: int) -> str:
        sections = ["主题解读", "人物分析", "艺术特色", "现实意义"]
        return sections[index % len(sections)]
    
    def _write_opening(self, work: str, work_type: str) -> str:
        return f"最近{work_type}了《{work}》，有些感触，想和大家分享一下。"
    
    def _write_section(self, work: str, work_type: str) -> str:
        return f"这部作品的{work_type}...\n\n让我印象最深的是...\n\n这引发了我的思考..."
    
    def _write_ending(self, work: str, work_type: str) -> str:
        return f"总的来说，《{work}》是一部值得{work_type}的作品。推荐指数：⭐⭐⭐⭐"


def write_review_article(work: str, work_type: str = "书") -> str:
    writer = WechatReviewWriter()
    return writer.write(work, work_type)
