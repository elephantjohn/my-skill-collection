#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gemini 3 Pro 文本生成器
用于微信公众号内容创作
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

try:
    from google import genai
except ImportError:
    print("错误：需要安装 google-genai 包")
    print("运行：pip install google-genai")
    sys.exit(1)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiTextGenerator:
    """Gemini 3 Pro 文本生成器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化生成器
        
        Args:
            api_key: Gemini API 密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('GEMINI3PRO_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置 GEMINI3PRO_API_KEY 环境变量")
        
        # 初始化客户端
        self.client = genai.Client()
        
        # 设置日志目录
        self.logs_dir = Path("logs/gemini")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_content(self, system_prompt: str, user_prompt: str, max_tokens: int = 8000) -> str:
        """调用 Gemini API 生成内容
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            max_tokens: 最大生成 token 数
            
        Returns:
            生成的内容
        """
        try:
            # 构建完整的提示
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=full_prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API 调用失败：{e}")
            # 记录错误日志
            error_log = self.logs_dir / f"error_{Path(__file__).stem}.log"
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(f"\n{e}\n")
            raise
    
    def generate_fairy_tale(self, theme: str = None) -> Dict:
        """生成童话故事"""
        theme_prompt = f"关于{theme}的" if theme else ""
        
        system_prompt = """你是一位优秀的童话故事作家。请创作一个温馨、富有想象力的童话故事。

【要求】
- 完全原创，有独特的情节和视角
- 蕴含教育意义，传递美好品德（诚信、友善、勇敢、感恩等）
- 语言优美流畅，适合儿童理解
- 激发想象力，培养美好情感

【风格】
- 像安徒生那样富有诗意和深刻寓意
- 像格林兄弟那样情节生动曲折
- 像王尔德那样语言优美细腻

【字数要求】
- 总字数必须≥4500 字
- 必须 10 个主体段落，每段 400-500 字
- 引言 150-200 字，结语 150-200 字
- 精彩情节每个 150-200 字（共 3 个）
- 寓意 150-200 字

【重要】
1. 每个段落必须有充实的内容：环境描写、人物刻画、对话、心理描写
2. 包含至少 3-4 处对话或引言
3. 故事要有完整的故事线：起因 - 发展 - 转折 - 高潮 - 结局
4. 善用比喻、拟人、排比等修辞手法
5. 确保内容健康向上

请以 JSON 格式返回：
{
    "title": "故事标题",
    "subtitle": "副标题",
    "introduction": "引言（150-200 字）",
    "paragraphs": ["段落 1(400-500 字)", "段落 2(400-500 字)", ...共 10 段],
    "highlights": ["精彩情节 1", "精彩情节 2", "精彩情节 3"],
    "quotes": [{"text": "引用句", "author": "说话人"}],
    "moral": "故事寓意（150-200 字）",
    "conclusion": "结语（150-200 字）"
}"""

        user_prompt = f"请创作一个{theme_prompt}童话故事，要温馨有趣，富有想象力。"
        
        try:
            content = self._generate_content(system_prompt, user_prompt)
            return self._parse_json_response(content)
        except Exception as e:
            logger.error(f"生成童话故事失败：{e}")
            return self._get_default_fairy_tale(theme)
    
    def generate_life_thinking(self, topic: str = None) -> Dict:
        """生成人生思考"""
        topic_prompt = f"关于{topic}" if topic else "关于人生意义"
        
        system_prompt = """你是一位深邃的生活观察者与随笔作家。请写一篇具有人文深度的随笔。

【要求】
- 独特视角，有思想密度和哲学深度
- 启发读者思考，提供精神价值和人生智慧
- 文字优美，克制有力，理性温和
- 即使讨论困境也要有希望，传递生活的美好

【风格】
- 冷静克制，叙述中含有悲悯与力度
- 自省与尊严，疼痛感背后的哲学韧性
- 温和理性的体悟，清朗且有思想密度

【字数要求】
- 总字数必须≥4000 字
- 必须 8 个主体段落，每段 450-550 字
- 开篇导语 200-250 字，结尾感悟 200-250 字
- 核心观点每个 100-150 字（共 4 个）
- 思考片段每个 150-200 字（共 2 个）

【重要】
1. 不要写成总结/概述式开头；直接进入论述或场景细节
2. 段落要有思想密度，每段都要有核心观点和充分论述
3. 观点层层递进，逻辑清晰
4. 始终保持深度和文学性

请以 JSON 格式返回：
{
    "title": "文章标题",
    "subtitle": "副标题",
    "quote": "引言句子",
    "quote_author": "引言作者",
    "introduction": "开篇导语（200-250 字）",
    "paragraphs": ["段落 1(450-550 字)", ...共 8 段],
    "insights": ["核心观点 1", "核心观点 2", "核心观点 3", "核心观点 4"],
    "reflections": ["思考片段 1", "思考片段 2"],
    "conclusion": "结尾感悟（200-250 字）"
}"""

        user_prompt = f"请写一篇{topic_prompt}的人生思考文章，要有深度和启发性。"
        
        try:
            content = self._generate_content(system_prompt, user_prompt)
            return self._parse_json_response(content)
        except Exception as e:
            logger.error(f"生成人生思考失败：{e}")
            return self._get_default_life_thinking(topic)
    
    def generate_tech_exploration(self, topic: str = None) -> Dict:
        """生成科技探索"""
        topic_prompt = topic if topic else "人工智能的基础概念"
        
        system_prompt = """你是一位面向中学生的科技讲解老师。只解释"某个技术/领域是什么"。

【要求】
- 传播准确的科学知识，有实际教育意义
- 用独特的方式解释复杂概念，通俗易懂
- 结构清晰，语言生动，适合青少年理解
- 激发科学兴趣，培养理性思考能力

【风格】
- 用非常通俗的语言，把复杂概念讲清楚
- 结构清楚，分小节解释
- 不引用未验证的数据，不堆砌术语
- 确保科学性和准确性

【字数要求】
- 总字数必须≥4000 字
- 每个 section 内容 600-700 字
- 开篇引入 200-300 字，总结要点 200-300 字
- 每个要点 50-80 字（共 4 个）

【重要】
1. 每个 section 必须充实饱满：概念解释、原理分析、例子、类比
2. 避免重复和套话，每段都要有独特内容
3. 保持科学严谨性的同时通俗易懂
4. 标题固定为"AI 帮你解释什么是 xxxx"

请以 JSON 格式返回：
{
    "title": "AI 帮你解释什么是{主题}",
    "subtitle": "通俗易懂的科技解读",
    "introduction": "开篇引入（200-300 字）",
    "sections": [
        {"title": "基本概念", "content": "详细解释（600-700 字）"},
        {"title": "工作原理", "content": "通俗解释（600-700 字）"},
        {"title": "实际应用", "content": "具体例子（600-700 字）"},
        {"title": "形象比喻", "content": "类比说明（600-700 字）"},
        {"title": "知识拓展", "content": "有趣知识（600-700 字）"}
    ],
    "key_points": ["要点 1", "要点 2", "要点 3", "要点 4"],
    "summary": "总结要点（200-300 字）"
}"""

        user_prompt = f"主题：{topic_prompt}。请严格按照上面的结构，只做解释。"
        
        try:
            content = self._generate_content(system_prompt, user_prompt)
            data = self._parse_json_response(content)
            # 强制规范标题
            data["title"] = f"AI 帮你解释什么是{topic_prompt}"
            return data
        except Exception as e:
            logger.error(f"生成科技探索失败：{e}")
            return self._get_default_tech_exploration(topic_prompt)
    
    def generate_food_culture(self, dish: str = None) -> Dict:
        """生成美食文化"""
        dish_prompt = dish if dish else "传统美食"
        
        system_prompt = """你是一位小说写作者，请创作一篇"与美食相关的第一人称微小说"。

【要求】
- 不允许介绍烹饪方法、配方、步骤
- 不允许出现"我发明/创造/创作了某道菜"等表述
- 美食仅作为故事出现物：我吃过/吃了/见过/梦见过
- 需要有一个内心问题或思想转折，故事结尾有余味
- 传递节俭、感恩、分享的美好品德

【字数要求】
- 总字数必须≥4500 字
- 必须 6 个章节叙述，每章节 600-700 字
- 开场白 200-250 字，结尾思考 200-250 字
- 每个感悟 150-200 字（共 3 个）

【重要】
1. 第一人称叙事，细节丰富，画面感强
2. 包含至少 3 处对话，5 处内心独白
3. 有明确的情节起伏和情感转折
4. 情感真挚，细节动人

请以 JSON 格式返回：
{
    "title": "标题",
    "subtitle": "副标题",
    "introduction": "开场白（200-250 字）",
    "story_parts": [
        {"subtitle": "章节 1 标题", "content": "内容（600-700 字）"},
        ...共 6 个章节
    ],
    "dialogues": [
        {"speaker": "人物 1", "text": "对话（50-100 字）"}
    ],
    "reflections": ["感悟 1", "感悟 2", "感悟 3"],
    "conclusion": "结尾思考（200-250 字）"
}"""

        user_prompt = f"美食元素：{dish_prompt}。请按上面的结构写一篇第一人称微小说。"
        
        try:
            content = self._generate_content(system_prompt, user_prompt)
            return self._parse_json_response(content)
        except Exception as e:
            logger.error(f"生成美食文化失败：{e}")
            return self._get_default_food_culture(dish_prompt)
    
    def generate_travel_note(self, destination: str = None) -> Dict:
        """生成旅行游记"""
        dest_prompt = destination if destination else "诗意远方"
        
        system_prompt = """你是一位严谨的旅行信息作者。客观介绍某地的著名景点与特色。

【要求】
- 介绍真实的地理、历史、文化知识
- 提供有用的旅行参考信息和建议
- 尊重各地文化风俗，促进文化理解
- 基于事实描述，不夸大不虚构

【风格】
- 信息性、客观、可读
- 以段落描述景点与特色
- 避免"我/我们"的第一人称叙事
- 确保信息准确，尊重事实

【字数要求】
- 总字数必须≥4500 字
- 必须 5 个主题板块，每板块 700-800 字
- 目的地概览 250-350 字，总结感言 250-350 字
- 每个亮点 80-100 字（共 4 个）
- 每个建议 100-150 字（共 3 个）

【重要】
1. 每个 section 必须充实饱满：景点介绍、历史文化、地理位置、实用建议
2. 信息要准确可靠，有参考价值
3. 语言生动但保持客观性
4. 避免第一人称叙述

请以 JSON 格式返回：
{
    "title": "目的地旅行指南",
    "subtitle": "副标题",
    "destination": "目的地",
    "introduction": "目的地概览（250-350 字）",
    "sections": [
        {"title": "自然风光", "content": "详细介绍（700-800 字）"},
        {"title": "历史文化", "content": "详细介绍（700-800 字）"},
        {"title": "美食特产", "content": "详细介绍（700-800 字）"}
    ],
    "highlights": ["亮点 1", "亮点 2", "亮点 3", "亮点 4"],
    "tips": ["建议 1", "建议 2", "建议 3"],
    "conclusion": "总结感言（250-350 字）"
}"""

        user_prompt = f"目的地：{dest_prompt}。请按上面的结构写信息介绍文。"
        
        try:
            content = self._generate_content(system_prompt, user_prompt)
            return self._parse_json_response(content)
        except Exception as e:
            logger.error(f"生成旅行游记失败：{e}")
            return self._get_default_travel_note(dest_prompt)
    
    def _parse_json_response(self, content: str) -> Dict:
        """解析 JSON 响应"""
        try:
            # 清理可能的 markdown 标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败：{e}")
            raise
    
    # 默认内容方法（API 失败时使用）
    def _get_default_fairy_tale(self, title: str = None) -> Dict:
        return {
            "title": title if title else "月光下的小精灵",
            "subtitle": "一个关于友谊和勇气的故事",
            "introduction": "在一片古老的森林深处...",
            "paragraphs": ["段落内容"] * 10,
            "highlights": ["精彩片段 1", "精彩片段 2", "精彩片段 3"],
            "quotes": [{"text": "引用 1", "author": "作者 1"}],
            "moral": "故事寓意",
            "conclusion": "结语"
        }
    
    def _get_default_life_thinking(self, title: str = None) -> Dict:
        return {
            "title": title if title else "时间的礼物",
            "subtitle": "关于生命意义的思考",
            "quote": "我们无法增加生命的长度，但可以拓展生命的宽度。",
            "quote_author": "蒙田",
            "introduction": "引言内容",
            "paragraphs": ["段落内容"] * 8,
            "insights": ["观点 1", "观点 2", "观点 3", "观点 4"],
            "reflections": ["思考 1", "思考 2"],
            "conclusion": "结语"
        }
    
    def _get_default_tech_exploration(self, title: str = None) -> Dict:
        return {
            "title": f"AI 帮你解释什么是{title}",
            "sections": [
                {"title": "基本概念", "content": "内容..."},
                {"title": "工作原理", "content": "内容..."},
                {"title": "实际应用", "content": "内容..."}
            ],
            "key_points": ["要点 1", "要点 2", "要点 3"],
            "summary": "总结"
        }
    
    def _get_default_food_culture(self, title: str = None) -> Dict:
        return {
            "title": "在雨夜吃到的一碗面",
            "introduction": "",
            "story_parts": [{"subtitle": "章节", "content": "内容"}] * 6,
            "reflections": ["感悟"],
            "conclusion": "结语"
        }
    
    def _get_default_travel_note(self, title: str = None) -> Dict:
        return {
            "title": "寻找失落的古城",
            "destination": "丽江古城",
            "introduction": "有些地方，你还没去过，却感觉似曾相识。",
            "sections": [
                {"title": "自然风光", "content": "内容..."},
                {"title": "历史文化", "content": "内容..."},
                {"title": "美食特产", "content": "内容..."}
            ],
            "highlights": ["亮点 1", "亮点 2"],
            "tips": ["建议 1", "建议 2"],
            "conclusion": "结语"
        }


def generate_article_content(category: str, topic: Optional[str] = None) -> Dict:
    """生成指定类别的文章内容"""
    generator = GeminiTextGenerator()
    
    if category == "童话故事":
        return generator.generate_fairy_tale(topic)
    elif category == "人生思考":
        return generator.generate_life_thinking(topic)
    elif category == "科技探索":
        return generator.generate_tech_exploration(topic)
    elif category == "美食文化":
        return generator.generate_food_culture(topic)
    elif category == "旅行游记":
        return generator.generate_travel_note(topic)
    else:
        return generator.generate_fairy_tale(topic)


if __name__ == "__main__":
    # 测试
    import sys
    category = sys.argv[1] if len(sys.argv) > 1 else "童话故事"
    topic = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"生成 {category} 类别的内容...")
    content = generate_article_content(category, topic)
    print(json.dumps(content, ensure_ascii=False, indent=2))
