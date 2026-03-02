#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号科普知识类文章写作器
用通俗易懂的语言讲解科学知识
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


class WechatScienceWriter:
    """微信公众号科普知识类文章写作器"""
    
    # 权威来源列表
    AUTHORITATIVE_SOURCES = [
        "自然", "science", "科学", "cell",
        "中科院", "科学院", "科学院",
        "清华", "北大", "大学",
        "卫健委", "疾控中心", "医院",
        "研究", "实验", "数据",
        "论文", "期刊", "杂志",
    ]
    
    # 禁止词汇（绝对化、伪科学）
    FORBIDDEN_WORDS = [
        "绝对", "肯定", "一定", "百分百",
        "包治", "根治", "永不", "所有",
        "据说", "相传", "有人说",
        "神奇", "奇迹", "不可思议",  # 过度渲染
    ]
    
    # 标题模板
    title_templates = {
        "explanation": [  # 解释型
            "为什么{topic}？科学解释来了",
            "{topic}的背后，藏着什么科学原理",
            "关于{topic}，你可能不知道的科学真相",
            "{topic}是怎么回事？一文讲清楚",
        ],
        "news": [  # 新知型
            "最新研究：{topic}原来是这样",
            "科学家发现，{topic}的秘密",
            "{topic}：{discovery}",
            "颠覆认知！{topic}的真相",
        ],
        "myth": [  # 辟谣型
            "{topic}是真的吗？科学告诉你",
            "别再信了！{topic}的{count}个误区",
            "{topic}：{myth}还是{truth}",
            "关于{topic}，{number}个你必须知道的真相",
        ],
    }
    
    def write(
        self,
        topic: str,
        style: str = "explanation",
        word_count: int = 3000,
        verify: bool = True
    ) -> str:
        """生成科普文章
        
        Args:
            topic: 文章主题
            style: 写作风格（explanation/news/myth）
            word_count: 目标字数
            verify: 是否验证内容准确性
            
        Returns:
            文章内容
        """
        logger.info(f"生成科普文章：{topic} (风格：{style})")
        
        # 生成标题
        title = self.generate_titles(topic, count=1, style=style)[0]
        
        # 生成文章
        article = self._write_article(title, topic, style, word_count)
        
        # 验证内容
        if verify:
            check_result = self.verify_content(article)
            if not check_result["is_valid"]:
                logger.warning(f"⚠️ 内容验证警告：{check_result['warnings']}")
            else:
                logger.info("✅ 内容验证通过")
        
        return article
    
    def generate_titles(
        self,
        topic: str,
        count: int = 10,
        style: Optional[str] = None
    ) -> List[str]:
        """生成科普标题"""
        logger.info(f"生成{count}个科普标题：{topic}")
        
        titles = []
        
        if style:
            templates = self.title_templates.get(style, [])
            for template in templates:
                title = self._fill_title_template(template, topic, style)
                if title:
                    titles.append(title)
        else:
            for style_name, templates in self.title_templates.items():
                for template in templates:
                    title = self._fill_title_template(template, topic, style_name)
                    if title:
                        titles.append(title)
        
        unique_titles = list(dict.fromkeys(titles))
        return unique_titles[:count]
    
    def verify_content(self, content: str) -> Dict:
        """验证内容质量
        
        Args:
            content: 文章内容
            
        Returns:
            验证结果
        """
        result = {
            "has_sources": any(source in content for source in self.AUTHORITATIVE_SOURCES),
            "has_forbidden": any(word in content for word in self.FORBIDDEN_WORDS),
            "word_count": len(content),
            "warnings": [],
        }
        
        # 检查数据来源
        if not result["has_sources"]:
            result["warnings"].append("未找到权威来源引用")
        
        # 检查禁止词汇
        if result["has_forbidden"]:
            result["warnings"].append("包含绝对化或不当表述")
        
        result["is_valid"] = result["has_sources"] and not result["has_forbidden"]
        
        return result
    
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
        
        # 正文
        for i in range(4):
            article += f"## {self._get_section_title(i, topic)}\n\n"
            article += self._write_section(topic, style)
            article += "\n\n"
        
        # 结尾
        article += self._write_ending(topic, style)
        
        return article
    
    def _write_opening(self, topic: str, style: str) -> str:
        """写开头"""
        
        openings = [
            f"说起{topic}，你可能有很多疑问。今天，我们就从科学的角度，把这件事讲清楚。",
            f"{topic}是个很有意思的现象。用通俗的话说，这背后的原理其实不难理解。",
            f"关于{topic}，网上流传着很多说法。哪些是真的？哪些是假的？让我们用科学来验证。",
        ]
        
        return random.choice(openings)
    
    def _get_section_title(self, index: int, topic: str) -> str:
        """获取小标题"""
        
        titles = [
            "现象描述",
            "科学原理解释",
            "研究数据支撑",
            "实际应用与启示",
            "常见误区澄清",
        ]
        
        return titles[index % len(titles)]
    
    def _write_section(self, topic: str, style: str) -> str:
        """写正文段落"""
        
        return f"""关于{topic}，科学家们进行了大量研究。

用通俗的话说，这个现象可以用{topic}的原理来解释。具体来说，当...时，就会发生...。

研究表明，{topic}与多个因素有关。据《科学》杂志的一项研究显示，...。

需要注意的是，{topic}的影响因素很复杂，不能简单地一概而论。"""
    
    def _write_ending(self, topic: str, style: str) -> str:
        """写结尾"""
        
        endings = [
            f"总的来说，{topic}是一个复杂的科学现象。希望这篇文章能帮你更好地理解它。",
            f"关于{topic}，我们还有很多未知等待探索。科学在进步，认知在更新，保持好奇心很重要。",
            f"下次遇到{topic}，希望你能用科学的眼光看待。记住，理性思考比盲目相信更重要。",
        ]
        
        return random.choice(endings)
    
    def _fill_title_template(self, template: str, topic: str, style: str) -> str:
        """填充标题模板"""
        
        try:
            title = template.format(
                topic=topic,
                discovery="新突破",
                myth="误解",
                truth="真相",
                count="3",
                number="5",
            )
            return title
        except KeyError as e:
            logger.warning(f"标题模板填充失败：{e}")
            return f"{topic}：科学解释来了"


def write_science_article(topic: str, style: str = "explanation") -> str:
    """便捷函数：生成科普文章"""
    writer = WechatScienceWriter()
    return writer.write(topic, style)


def generate_science_titles(topic: str, count: int = 10) -> List[str]:
    """便捷函数：生成科普标题"""
    writer = WechatScienceWriter()
    return writer.generate_titles(topic, count)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "为什么天空是蓝色的"
    
    print(f"生成科普文章：{topic}\n")
    
    writer = WechatScienceWriter()
    titles = writer.generate_titles(topic, count=10)
    
    print("=== 生成的标题 ===")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    print("\n=== 内容验证 ===")
    article = writer.write(topic, style="explanation", verify=False)
    result = writer.verify_content(article)
    print(f"数据来源：{'✅' if result['has_sources'] else '❌'}")
    print(f"禁止词汇：{'❌' if result['has_forbidden'] else '✅'}")
    print(f"验证结果：{'✅ 通过' if result['is_valid'] else '⚠️ 需修改'}")
