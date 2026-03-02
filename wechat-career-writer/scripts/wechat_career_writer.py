#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号职场成长类文章写作器
提供实用的职场建议和成长方法
"""

import random
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WechatCareerWriter:
    """职场成长类文章写作器"""
    
    title_templates = [
        "{topic}：{number}个实用方法",
        "为什么你{topic}总是失败？",
        "{topic}的{number}个误区，你中了几个",
        "高手都是如何{topic}的？",
        "{topic}：从{pain}到{gain}",
    ]
    
    def write(self, topic: str, word_count: int = 3000) -> str:
        """生成职场文章"""
        logger.info(f"生成职场文章：{topic}")
        title = self.generate_titles(topic, count=1)[0]
        
        article = f"# {title}\n\n"
        article += self._write_opening(topic) + "\n\n"
        
        for i in range(4):
            article += f"## 第{i+1}部分\n\n"
            article += self._write_section(topic) + "\n\n"
        
        article += self._write_ending(topic)
        return article
    
    def generate_titles(self, topic: str, count: int = 10) -> List[str]:
        """生成标题"""
        titles = []
        for template in self.title_templates:
            title = template.format(
                topic=topic,
                number=random.choice(["3", "5", "7"]),
                pain="新手",
                gain="高手"
            )
            titles.append(title)
        return titles[:count]
    
    def _write_opening(self, topic: str) -> str:
        return f"在职场中，{topic}是很多人都会遇到的问题。今天，我们就来聊聊这个话题。"
    
    def _write_section(self, topic: str) -> str:
        return f"关于{topic}，我有一个实用的方法。具体来说，就是...\n\n这个方法的核心是...\n\n举个例子，..."
    
    def _write_ending(self, topic: str) -> str:
        return f"总的来说，{topic}需要刻意练习。希望这篇文章对你有帮助。"


def write_career_article(topic: str) -> str:
    writer = WechatCareerWriter()
    return writer.write(topic)
