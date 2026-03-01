#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号温情类爆款文章写作器
学习并模仿公众号温情领域的爆款文章风格
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


class WechatEmotionalWriter:
    """微信公众号温情类爆款文章写作器"""
    
    def __init__(self):
        """初始化写作器"""
        
        # 标题模板库
        self.title_templates = {
            "情绪化": [
                "{topic}，我{emotion}了：{insight}",
                "{topic}的那一刻，我才明白{insight}",
                "{topic}：{emotion}的{object}",
                "不是{topic}，而是{insight}",
            ],
            "场景化": [
                "在{place}，我{action}：{insight}",
                "{time}的{place}，{description}",
                "{object}里，藏着{emotion}",
                "{place}的{object}，{description}",
            ],
            "数字对比": [
                "{time1}vs{time2}：{description}",
                "{number}人的{topic}：{description}",
                "{number}年过去了，{insight}",
                "从{time1}到{time2}，{description}",
            ],
            "悬念式": [
                "有些{object}，{action}，就{consequence}",
                "{topic}后，我{action}了",
                "为什么{topic}？{insight}",
                "{topic}的人，后来都{consequence}",
            ],
        }
        
        # 情感词汇库
        self.emotion_words = {
            "亲情": ["不舍", "心疼", "泪目", "感动", "愧疚", "感恩", "温暖"],
            "成长": ["孤独", "迷茫", "挣扎", "坚持", "释然", "成长", "梦想"],
            "爱情": ["遗憾", "错过", "等待", "陪伴", "思念", "释怀", "祝福"],
            "友情": ["散场", "重逢", "默契", "支持", "怀念", "珍惜", "懂得"],
        }
        
        # 场景词汇库
        self.scene_words = {
            "离别": ["高铁站", "机场", "村口", "车站", "后视镜", "行李箱"],
            "日常": ["深夜", "出租屋", "办公室", "地铁", "外卖", "手机"],
            "回忆": ["老家", "童年", "照片", "饭菜", "拥抱", "电话"],
            "成长": ["写字楼", "格子间", "加班", "梦想", "现实", "坚持"],
        }
        
        # 金句模板
        self.quote_templates = [
            "{object}永远在{place}，而你正在{action}",
            "不是{topic}，而是{insight}",
            "{topic}的那一刻，{insight}",
            "你以为{wrong}，其实{right}",
            "成年人的{emotion}，连{action}都要{restrain}",
            "{description}，才是{reality}",
            "从{time1}到{time2}，{change}",
            "{object}里，藏着{emotion}",
        ]
        
        # 文章结构模板
        self.article_templates = {
            "亲情": {
                "开头": "场景切入 + 细节描写",
                "正文": ["离别前的准备", "离别时的场景", "离别后的感受", "感悟与升华"],
                "结尾": "金句收尾 + 互动引导",
            },
            "成长": {
                "开头": "对比手法（小时候 vs 长大后）",
                "正文": ["曾经的梦想", "现实的打击", "挣扎与坚持", "和解与成长"],
                "结尾": "正能量升华",
            },
            "爱情": {
                "开头": "悬念式（有些话没说...）",
                "正文": ["相遇的美好", "错过的原因", "后来的我们", "如果当初"],
                "结尾": "释然与祝福",
            },
            "友情": {
                "开头": "回忆式（那年夏天...）",
                "正文": ["相识的缘分", "相处的时光", "散场的无奈", "重逢的期待"],
                "结尾": "珍惜与感恩",
            },
        }
    
    def write(
        self,
        topic: str,
        category: str = "亲情",
        style: str = "温情治愈",
        word_count: int = 3000
    ) -> str:
        """生成温情文章
        
        Args:
            topic: 文章主题
            category: 文章类别（亲情/成长/爱情/友情）
            style: 写作风格
            word_count: 目标字数
            
        Returns:
            文章内容
        """
        logger.info(f"生成温情文章：{topic} (类别：{category})")
        
        # 生成标题
        title = self.generate_titles(topic, count=1, category=category)[0]
        
        # 生成文章结构
        structure = self._generate_structure(topic, category, style)
        
        # 生成内容
        article = self._write_article(title, structure, word_count)
        
        return article
    
    def generate_titles(
        self,
        topic: str,
        count: int = 10,
        category: str = "亲情",
        style: Optional[str] = None
    ) -> List[str]:
        """生成吸引人的标题
        
        Args:
            topic: 主题
            count: 生成数量
            category: 类别
            style: 风格（情绪化/场景化/数字对比/悬念式）
            
        Returns:
            标题列表
        """
        logger.info(f"生成{count}个标题：{topic}")
        
        titles = []
        
        # 如果指定了风格
        if style:
            templates = self.title_templates.get(style, [])
            for template in templates:
                title = self._fill_template(template, topic, category)
                if title:
                    titles.append(title)
        else:
            # 混合所有风格
            for style_name, templates in self.title_templates.items():
                for template in templates:
                    title = self._fill_template(template, topic, category)
                    if title:
                        titles.append(title)
        
        # 去重并返回指定数量
        unique_titles = list(dict.fromkeys(titles))
        return unique_titles[:count]
    
    def generate_quotes(
        self,
        theme: str,
        count: int = 5
    ) -> List[str]:
        """生成金句
        
        Args:
            theme: 主题
            count: 生成数量
            
        Returns:
            金句列表
        """
        logger.info(f"生成{count}个金句：{theme}")
        
        quotes = []
        
        for _ in range(count * 2):  # 多生成一些用于筛选
            template = random.choice(self.quote_templates)
            quote = self._fill_quote_template(template, theme)
            if quote and len(quote) > 10:
                quotes.append(quote)
        
        # 去重并返回
        unique_quotes = list(dict.fromkeys(quotes))
        return unique_quotes[:count]
    
    def _generate_structure(
        self,
        topic: str,
        category: str,
        style: str
    ) -> Dict:
        """生成文章结构"""
        
        template = self.article_templates.get(category, self.article_templates["亲情"])
        
        return {
            "title": topic,
            "category": category,
            "style": style,
            "structure": template,
        }
    
    def _write_article(
        self,
        title: str,
        structure: Dict,
        word_count: int
    ) -> str:
        """撰写文章"""
        
        # 这里使用简化的实现
        # 实际应该调用 LLM 生成
        
        article = f"# {title}\n\n"
        
        # 开头
        article += self._write_opening(structure)
        article += "\n\n"
        
        # 正文
        for i, section in enumerate(structure["structure"]["正文"], 1):
            article += f"## {section}\n\n"
            article += self._write_section(section, structure)
            article += "\n\n"
        
        # 结尾
        article += self._write_ending(structure)
        
        return article
    
    def _write_opening(self, structure: Dict) -> str:
        """写开头"""
        
        category = structure.get("category", "亲情")
        
        openings = {
            "亲情": """高铁缓缓驶出站台，后视镜里父母的身影越来越小，直到变成一个模糊的点。你低下头，打开手机相册，里面是昨晚全家围坐吃饭的照片。那一刻你明白——年，真的过完了。""",
            
            "成长": """小时候以为长大很自由，长大后才发现自由很昂贵。小时候盼着离开家，长大后却拼命想回去。我们都在成长中学会了一件事：有些路，只能一个人走。""",
            
            "爱情": """有些话，当时没说，就再也没机会说了。有些人，一转身，就是一辈子。后来你才明白，错过不是错，过了才是错。""",
            
            "友情": """那年夏天的风，吹散了很多人。你以为来日方长，其实很多人，见一面就少一面。友情最可怕的不是争吵，而是悄无声息地走散。""",
        }
        
        return openings.get(category, openings["亲情"])
    
    def _write_section(
        self,
        section: str,
        structure: Dict
    ) -> str:
        """写正文段落"""
        
        # 简化实现，返回示例内容
        return f"""这是{section}的内容。

具体的细节描写，让读者身临其境。比如父母的动作、表情、语言，比如环境的描写，比如内心的感受。

用对话增加真实感，用细节打动人心。

**金句点题，引发共鸣。**"""
    
    def _write_ending(self, structure: Dict) -> str:
        """写结尾"""
        
        category = structure.get("category", "亲情")
        
        endings = {
            "亲情": """此刻你可能正在高铁上，可能刚到公司打卡，可能独自坐在出租屋里刷手机。

不管在哪儿，我想跟你说：

你拖着行李箱、挤在人潮里、独自走进写字楼的样子，真的很了不起。

那些塞在行李箱底的土特产、那些"到了吗"的微信消息、那些没说出口的想念——都是你继续走下去的理由。

**故乡永远在身后，而你正在走向配得上这份牵挂的未来。**

加油，异乡人。🏠

📌 **互动话题：** 你的行李箱里，爸妈偷偷塞了什么？评论区说说，我赌你看完别人的故事也会红眼眶。""",
            
            "成长": """成长就是这样，一边失去，一边得到。

愿你历经千帆，归来仍是少年。

**愿你所有的努力，都不被辜负。**

📌 **互动话题：** 哪一刻，你突然觉得自己长大了？""",
            
            "爱情": """后来，你终于学会了珍惜。

可惜，有些人，一旦错过就不再。

**愿你遇到那个人，懂你的欲言又止，懂你的言外之意。**

📌 **互动话题：** 你有没有一个想联系却不能再联系的人？""",
            
            "友情": """朋友就是这样，走着走着就散了。

但总有一些人，即使不联系，也一直在心里。

**致那些陪我走过一程的人，谢谢你们。**

📌 **互动话题：** 你最好的朋友，现在还在联系吗？""",
        }
        
        return endings.get(category, endings["亲情"])
    
    def _fill_template(
        self,
        template: str,
        topic: str,
        category: str
    ) -> str:
        """填充标题模板"""
        
        # 获取情感词和场景词
        emotion = random.choice(self.emotion_words.get(category, ["感动"]))
        scene = random.choice(self.scene_words.get("离别", ["车站"]))
        
        # 填充
        title = template.format(
            topic=topic,
            emotion=emotion,
            insight="那一刻我才明白",
            object="行李箱",
            place=scene,
            action="转身",
            description="藏着说不出的不舍",
            time1="7 天",
            time2="358 天",
            number="2.9 亿",
            consequence="再也见不到了",
            wrong="长大是自由",
            right="长大是责任",
        )
        
        return title
    
    def _fill_quote_template(
        self,
        template: str,
        theme: str
    ) -> str:
        """填充金句模板"""
        
        quote = template.format(
            object="故乡",
            place="身后",
            action="走向配得上这份牵挂的未来",
            topic=theme,
            insight="有些路只能一个人走",
            wrong="长大很自由",
            right="长大很孤独",
            emotion="告别",
            action2="眼泪",
            restrain="忍住",
            description="热闹散场后的安静",
            reality="异乡最真实的底色",
            time1="小时候",
            time2="长大后",
            change="我们都在失去",
        )
        
        return quote


def write_emotional_article(
    topic: str,
    category: str = "亲情",
    style: str = "温情治愈"
) -> str:
    """便捷函数：生成温情文章"""
    writer = WechatEmotionalWriter()
    return writer.write(topic, category, style)


def generate_titles(
    topic: str,
    count: int = 10
) -> List[str]:
    """便捷函数：生成标题"""
    writer = WechatEmotionalWriter()
    return writer.generate_titles(topic, count)


if __name__ == "__main__":
    # 测试
    import sys
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "年过完了，离开老家"
    
    print(f"生成温情文章：{topic}\n")
    
    # 生成标题
    writer = WechatEmotionalWriter()
    titles = writer.generate_titles(topic, count=10)
    
    print("=== 生成的标题 ===")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    print("\n=== 生成的金句 ===")
    quotes = writer.generate_quotes("成长与离别", count=5)
    for i, quote in enumerate(quotes, 1):
        print(f"{i}. {quote}")
