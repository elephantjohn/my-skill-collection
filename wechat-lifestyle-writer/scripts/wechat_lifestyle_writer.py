#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号生活美学类文章写作器
分享有品味的生活方式
"""

import random
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WechatLifestyleWriter:
    """生活美学类文章写作器"""
    
    title_templates = [
        "如何{topic}，提升生活品质",
        "{topic}：一种生活的仪式感",
        "关于{topic}，我的{number}个建议",
        "把{topic}做到极致，是什么体验",
    ]
    
    def write(self, topic: str, word_count: int = 3000) -> str:
        """生成生活美学文章"""
        logger.info(f"生成生活美学文章：{topic}")
        title = self.generate_titles(topic, count=1)[0]
        
        article = f"# {title}\n\n"
        article += self._write_opening(topic) + "\n\n"
        
        for i in range(4):
            article += f"## {self._get_section(i)}\n\n"
            article += self._write_section(topic) + "\n\n"
        
        article += self._write_ending(topic)
        return article
    
    def generate_titles(self, topic: str, count: int = 10) -> List[str]:
        """生成标题"""
        titles = []
        for template in self.title_templates:
            title = template.format(
                topic=topic,
                number=random.choice(["3", "5", "7"])
            )
            titles.append(title)
        return titles[:count]
    
    def _get_section(self, index: int) -> str:
        sections = ["理念篇", "方法篇", "实践篇", "感悟篇"]
        return sections[index % len(sections)]
    
    def _write_opening(self, topic: str) -> str:
        return f"生活需要仪式感，{topic}就是一种很好的方式。"
    
    def _write_section(self, topic: str) -> str:
        return f"关于{topic}，我的理解是...\n\n具体来说，可以这样做...\n\n最重要的是..."
    
    def _write_ending(self, topic: str) -> str:
        return f"希望{topic}能让你的生活更美好。"


def write_lifestyle_article(topic: str) -> str:
    writer = WechatLifestyleWriter()
    return writer.write(topic)
