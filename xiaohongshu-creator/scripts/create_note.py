"""
小红书创作者主程序
自动生成图文笔记 + 视频
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from google import genai
from smart_censor import SmartCensor

logger = logging.getLogger(__name__)


class XiaohongshuCreator:
    """小红书创作者"""

    def __init__(self):
        """初始化创作者"""
        # 配置 API Keys
        self.gemini_api_key = os.getenv("GEMINI3PRO_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("缺少 GEMINI3PRO_API_KEY 环境变量")

        # 初始化 Gemini 客户端
        self.gemini_client = genai.Client()

        # 初始化智能审核器
        self.censor = SmartCensor()

        # 配置
        self.video_themes = [
            "解压视频，ASMR，史莱姆挤压，肥皂切割",
            "解压视频，ASMR，沙子流动，彩色沙漏",
            "解压视频，ASMR，泡泡纸挤压，泡沫破裂",
            "解压视频，ASMR，水晶泥拉伸，透明胶质",
            "解压视频，ASMR，多米诺骨牌，整齐排列",
            "解压视频，ASMR，液压机压物，缓慢挤压",
            "解压视频，ASMR，切肥皂，薄片飘落",
            "解压视频，ASMR，洗地毯，高压水枪",
        ]

        self.note_templates = [
            "解压日常",
            "ASMR 沉浸式",
            "治愈瞬间",
            "放松时刻",
            "减压神器",
        ]

    def create_note(
        self,
        theme: str = None,
        generate_video: bool = True,
        output_dir: str = "output",
    ) -> Dict[str, Any]:
        """
        创建完整的小红书笔记

        Args:
            theme: 主题（可选，随机选择）
            generate_video: 是否生成视频
            output_dir: 输出目录

        Returns:
            笔记数据
        """
        logger.info("🎨 开始创建小红书笔记...")

        # 选择主题
        if not theme:
            theme = self.video_themes[
                datetime.now().hour % len(self.video_themes)
            ]

        template = self.note_templates[
            datetime.now().hour % len(self.note_templates)
        ]

        # 第 1 步：生成文案
        logger.info("📝 生成文案...")
        text_content = self.generate_text(theme, template)

        # 第 2 步：智能审核
        logger.info("🔍 智能审核...")
        is_ok, final_text, censor_detail = self.censor.censor_and_fix(text_content)

        if not is_ok:
            logger.warning("⚠️ 审核未通过，但继续生成（可手动修改）")

        # 第 3 步：生成标题和标签
        logger.info("🏷️ 生成标题和标签...")
        title, tags = self.generate_title_tags(final_text)

        # 第 4 步：生成视频
        video_path = None
        if generate_video:
            logger.info("🎬 生成视频...")
            video_path = self.generate_video(theme)

        # 第 5 步：保存笔记
        logger.info("💾 保存笔记...")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        note_data = {
            "title": title,
            "content": final_text,
            "tags": tags,
            "video_path": str(video_path) if video_path else None,
            "theme": theme,
            "template": template,
            "created_at": datetime.now().isoformat(),
            "censor_passed": is_ok,
            "censor_detail": censor_detail,
        }

        # 保存 JSON
        note_file = output_path / f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(note_file, "w", encoding="utf-8") as f:
            json.dump(note_data, f, ensure_ascii=False, indent=2)

        # 保存纯文本（方便复制）
        text_file = output_path / f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(f"标题：{title}\n\n")
            f.write(f"{final_text}\n\n")
            f.write(f"标签：{' '.join(tags)}\n")
            if video_path:
                f.write(f"\n视频：{video_path}\n")

        logger.info(f"✅ 笔记创建完成！")
        logger.info(f"   标题：{title}")
        logger.info(f"   文案：{len(final_text)} 字")
        logger.info(f"   视频：{video_path or '未生成'}")
        logger.info(f"   保存：{note_file}")

        return note_data

    def generate_text(self, theme: str, template: str) -> str:
        """
        使用 Gemini 生成文案

        Args:
            theme: 视频主题
            template: 笔记模板

        Returns:
            文案内容
        """
        prompt = f"""
请为小红书平台创作一篇{template}笔记的文案。

主题：{theme}

要求：
1. 语气轻松治愈，符合小红书风格
2. 包含 emoji 表情（适量）
3. 段落清晰，每段 2-4 句话
4. 字数 300-500 字
5. 不要包含具体品牌名称
6. 结尾引导互动（点赞/收藏/评论）

请直接返回文案内容，不要标题和标签。
"""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"❌ Gemini 生成失败：{e}")
            # 返回默认文案
            return f"""
✨ {template} | {theme}

今天分享一个超级解压的视频～
看着这些画面，感觉整个人都放松下来了 😌

生活节奏太快，偶尔也要给自己一点放空的时间。
这样的视频真的很治愈，推荐给大家！

你们喜欢什么类型的解压视频呢？
评论区告诉我吧～ 👇

#解压 #ASMR #治愈 #放松 #减压
"""

    def generate_title_tags(self, text: str) -> tuple:
        """
        生成标题和标签

        Args:
            text: 文案内容

        Returns:
            (标题，标签列表)
        """
        prompt = f"""
请为以下小红书文案生成一个吸引人的标题和 5 个标签。

文案：
{text}

要求：
1. 标题：15-25 字，包含 emoji，吸引点击
2. 标签：5 个，#开头，热门话题

返回格式：
标题：xxx
标签：#xxx #xxx #xxx #xxx #xxx
"""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
            )
            result = response.text.strip()

            # 解析结果
            lines = result.split("\n")
            title = ""
            tags = []

            for line in lines:
                if line.startswith("标题："):
                    title = line.replace("标题：", "").strip()
                elif line.startswith("标签："):
                    tag_str = line.replace("标签：", "").strip()
                    tags = tag_str.split()

            if not title:
                title = "✨ 解压治愈时刻"
            if not tags:
                tags = ["#解压", "#ASMR", "#治愈", "#放松", "#减压"]

            return title, tags
        except Exception as e:
            logger.error(f"❌ 标题生成失败：{e}")
            return "✨ 解压治愈时刻", ["#解压", "#ASMR", "#治愈", "#放松", "#减压"]

    def generate_video(self, theme: str) -> Optional[str]:
        """
        使用 Veo 3.1 生成视频

        Args:
            theme: 视频主题

        Returns:
            视频文件路径
        """
        try:
            # 调用 gemini-video skill
            from gemini_video.scripts.generate_video import GeminiVideoGenerator

            gen = GeminiVideoGenerator(api_key=self.gemini_api_key)

            # 生成 9:16 竖屏，720p，8 秒
            video_path = gen.generate_from_text(
                theme,
                aspect_ratio="9:16",
                resolution="720p",
                duration=8,
            )

            return video_path
        except ImportError:
            logger.error("❌ gemini-video 模块未找到")
            return None
        except Exception as e:
            logger.error(f"❌ 视频生成失败：{e}")
            return None


# 命令行执行
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="小红书创作者")
    parser.add_argument("--theme", type=str, help="视频主题")
    parser.add_argument("--text-only", action="store_true", help="仅生成文案")
    parser.add_argument("--output", type=str, default="output", help="输出目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    args = parser.parse_args()

    # 配置日志
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 创建笔记
    creator = XiaohongshuCreator()
    note = creator.create_note(
        theme=args.theme,
        generate_video=not args.text_only,
        output_dir=args.output,
    )

    print("\n✅ 创作完成！")
    print(f"标题：{note['title']}")
    print(f"文案：{len(note['content'])} 字")
    print(f"视频：{note['video_path'] or '未生成'}")
