#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号历史趣闻类文章写作器
学习当年明月、马伯庸、六神磊磊的写作风格
"""

import os
import random
import logging
from pathlib import Path
from typing import List, Optional, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WechatHistoryWriter:
    """微信公众号历史趣闻类文章写作器"""
    
    def __init__(self):
        """初始化写作器"""
        
        # 标题模板库
        self.title_templates = {
            "suspense": [  # 悬念式
                "你可能不知道，{topic}其实{surprise}",
                "历史上最{adjective}的{topic}，竟然是{truth}",
                "{topic}的背后，藏着一个{secret}",
                "{topic}：{question}？",
            ],
            "contrast": [  # 反差式
                "被误解千年的{topic}",
                "{topic}的另一面：和你想的不一样",
                "正史里的{topic}：{contrast}",
                "{topic}：{expectation}？其实{reality}",
            ],
            "truth": [  # 真相式
                "{topic}的真实面貌：史料记载{truth}",
                "历史上的{topic}：真相是{truth}",
                "揭开{topic}的历史真相",
                "{topic}：{fact}，{evidence}",
            ],
            "fun": [  # 趣味式
                "如果{topic}有朋友圈",
                "{topic}的日常：比现代人还{modern}",
                "{topic}的{aspect}：古代人的智慧",
                "{topic}：{funny}的操作",
            ],
        }
        
        # 文章开头模板
        self.openings = {
            "suspense": [
                "说起{topic}，你可能第一时间想到{stereotype}。但你知道吗？历史的真相，往往藏在细节里。",
                "{topic}这个名字，在历史上可谓如雷贯耳。但你可能不知道，{surprise}。",
                "提到{topic}，很多人的第一反应是{common_view}。然而，翻开史料，我们会发现另一个{topic}。",
            ],
            "contrast": [
                "在演义和戏文里，{topic}一直是{stereotype}的形象。但正史里的记载，却告诉我们一个完全不同的故事。",
                "{topic}被黑了一千多年，直到今天，才有人为他翻案。",
                "你可能听过{topic}的很多故事，但那些大多是后人杜撰的。真实的{topic}，其实是这样的。",
            ],
        }
        
        # 常用过渡语
        self.transitions = [
            "有趣的是，",
            "史料记载，",
            "用现在的话说，",
            "说白了就是，",
            "这操作，绝了。",
            "你想想看，",
            "要知道，",
            "要知道在那个年代，",
        ]
        
        # 结尾金句模板
        self.endings = [
            "历史总是惊人的相似，{topic}的故事，到今天依然有启示意义。",
            "读史使人明智，{topic}的经历，告诉我们{lesson}。",
            "{topic}已经远去，但他留下的{legacy}，至今仍在影响着我们。",
            "历史没有如果，但我们可以从{topic}的故事里，看到{insight}。",
        ]
    
    def write(
        self,
        topic: str,
        style: str = "humorous",
        word_count: int = 3000
    ) -> str:
        """生成历史文章
        
        Args:
            topic: 文章主题
            style: 写作风格（humorous/suspense/truth）
            word_count: 目标字数
            
        Returns:
            文章内容
        """
        logger.info(f"生成历史文章：{topic} (风格：{style})")
        
        # 生成标题
        title = self.generate_titles(topic, count=1)[0]
        
        # 生成文章
        article = self._write_article(title, topic, style, word_count)
        
        return article
    
    def generate_titles(
        self,
        topic: str,
        count: int = 10,
        style: Optional[str] = None
    ) -> List[str]:
        """生成历史趣闻标题
        
        Args:
            topic: 主题
            count: 生成数量
            style: 风格（suspense/contrast/truth/fun）
            
        Returns:
            标题列表
        """
        logger.info(f"生成{count}个历史趣闻标题：{topic}")
        
        titles = []
        
        if style:
            templates = self.title_templates.get(style, [])
            for template in templates:
                title = self._fill_title_template(template, topic)
                if title:
                    titles.append(title)
        else:
            # 混合所有风格
            for style_name, templates in self.title_templates.items():
                for template in templates:
                    title = self._fill_title_template(template, topic)
                    if title:
                        titles.append(title)
        
        # 去重并返回
        unique_titles = list(dict.fromkeys(titles))
        return unique_titles[:count]
    
    def generate_quotes(
        self,
        theme: str,
        count: int = 5
    ) -> List[str]:
        """生成历史金句
        
        Args:
            theme: 主题
            count: 生成数量
            
        Returns:
            金句列表
        """
        logger.info(f"生成{count}个历史金句：{theme}")
        
        quotes = []
        for _ in range(count * 2):
            template = random.choice(self.endings)
            quote = template.format(
                topic=theme,
                lesson="做人做事的道理",
                legacy="精神财富",
                insight="人性的复杂",
            )
            if quote and len(quote) > 15:
                quotes.append(quote)
        
        unique_quotes = list(dict.fromkeys(quotes))
        return unique_quotes[:count]
    
    def _write_article(
        self,
        title: str,
        topic: str,
        style: str,
        word_count: int
    ) -> str:
        """撰写文章"""
        
        article = f"# {title}\n\n"
        
        # 开头
        article += self._write_opening(topic, style)
        article += "\n\n"
        
        # 正文（简化实现）
        for i in range(4):
            article += f"## 第{i+1}部分\n\n"
            article += self._write_section(topic, style)
            article += "\n\n"
        
        # 结尾
        article += self._write_ending(topic)
        
        return article
    
    def _write_opening(self, topic: str, style: str) -> str:
        """写开头"""
        
        openings = self.openings.get(style, self.openings["suspense"])
        template = random.choice(openings)
        
        opening = template.format(
            topic=topic,
            stereotype="某个固定印象",
            surprise="另有隐情",
            common_view="某个常见观点",
        )
        
        return opening
    
    def _write_section(self, topic: str, style: str) -> str:
        """写正文段落"""
        
        transition = random.choice(self.transitions)
        
        return f"""{transition}关于{topic}，史料中有不少记载。

具体来说，{topic}的故事要从那个时代说起。当时的背景是......

有趣的是，{topic}的处理方式，即使放在今天，也很有借鉴意义。

用现在的话说，这就是{topic}的智慧。"""
    
    def _write_ending(self, topic: str) -> str:
        """写结尾"""
        
        template = random.choice(self.endings)
        
        ending = template.format(
            topic=topic,
            lesson="做人做事的道理",
            legacy="精神财富",
            insight="人性的复杂",
        )
        
        return ending
    
    def _fill_title_template(self, template: str, topic: str) -> str:
        """填充标题模板"""
        
        # 清理 topic，避免重复
        clean_topic = topic.replace("的真实面貌", "").replace("的真实生活", "").strip()
        if not clean_topic:
            clean_topic = topic
        
        try:
            title = template.format(
                topic=clean_topic,
                surprise="另有隐情",
                adjective="有争议",
                truth="这样",
                secret="不为人知的秘密",
                question="真相是什么",
                contrast="颠覆你的认知",
                expectation="你很熟悉",
                reality="完全不是那么回事",
                fact="史料记载明确",
                evidence="有据可查",
                modern="会玩",
                aspect="生活方式",
                funny="让人意想不到",
            )
            return title
        except KeyError as e:
            logger.warning(f"标题模板填充失败：{e}")
            return f"{topic}：被误解的历史真相"


def write_history_article(
    topic: str,
    style: str = "humorous"
) -> str:
    """便捷函数：生成历史文章"""
    writer = WechatHistoryWriter()
    return writer.write(topic, style)


def generate_history_titles(
    topic: str,
    count: int = 10
) -> List[str]:
    """便捷函数：生成历史标题"""
    writer = WechatHistoryWriter()
    return writer.generate_titles(topic, count)


if __name__ == "__main__":
    # 测试
    import sys
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "曹操的真实面貌"
    
    print(f"生成历史文章：{topic}\n")
    
    writer = WechatHistoryWriter()
    titles = writer.generate_titles(topic, count=10)
    
    print("=== 生成的标题 ===")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    print("\n=== 生成的金句 ===")
    quotes = writer.generate_quotes("历史智慧", count=5)
    for i, quote in enumerate(quotes, 1):
        print(f"{i}. {quote}")
