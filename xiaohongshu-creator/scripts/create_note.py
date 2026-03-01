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
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 加载 .env 文件
env_path = Path("/home/ubuntu/.openclaw/workspace-xiang_xiaohongshu/.env")
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"📍 加载 .env: {env_path}")
else:
    logger.warning(f"⚠️  .env 不存在：{env_path}")

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from google import genai
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from smart_censor import SmartCensor

logger = logging.getLogger(__name__)


class XiaohongshuCreator:
    """小红书创作者"""

    def __init__(self):
        """初始化创作者"""
        # 配置 API Keys
        self.gemini_api_key = os.getenv("GEMINI3PRO_API_KEY")
        logger.info(f"🔑 Gemini API Key: {'已加载' if self.gemini_api_key else '❌ 未加载'}")
        
        if not self.gemini_api_key:
            raise ValueError("缺少 GEMINI3PRO_API_KEY 环境变量")
        
        logger.info(f"📍 .env 路径：{env_path}")

        # 初始化 Gemini 客户端（必须传入 api_key）
        self.gemini_client = genai.Client(api_key=self.gemini_api_key)
        logger.info(f"✅ Gemini 客户端初始化成功")

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

        # 第 3 步：生成多平台内容
        logger.info("🌐 生成多平台内容...")
        platform_contents = self.generate_multi_platform_content(final_text, theme)

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
            "title": platform_contents.get("小红书", {}).get("title", "默认标题"),
            "content": final_text,
            "tags": platform_contents.get("小红书", {}).get("tags", ""),
            "video_path": str(video_path) if video_path else None,
            "theme": theme,
            "template": template,
            "created_at": datetime.now().isoformat(),
            "censor_passed": is_ok,
            "censor_detail": censor_detail,
            "platform_contents": platform_contents,  # 多平台内容
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
        logger.info(f"   标题：{note_data['title']}")
        logger.info(f"   文案：{len(final_text)} 字")
        logger.info(f"   视频：{video_path or '未生成'}")
        logger.info(f"   保存：{note_file}")

        # 发送多平台内容到 Telegram
        self._send_to_telegram(platform_contents, video_path)

        return note_data

    def _send_to_telegram(self, platform_contents: Dict[str, Dict[str, Any]], video_path: str):
        """
        发送多平台内容到 Telegram（优化格式）

        格式：
        【通知】开始发送小红书的文案了
          → 标题（纯内容）
          → 文案（纯内容）
          → 标签（纯内容）

        Args:
            platform_contents: 各平台内容
            video_path: 视频路径
        """
        try:
            print("\n" + "="*60)
            print("📱 发送多平台内容到 Telegram")
            print("="*60)
            
            for platform, content in platform_contents.items():
                # 1. 通知消息
                print(f"\n【通知】开始发送{platform}的文案了")
                
                # 2. 标题（纯内容，无前缀）
                print(f"【标题】{content['title']}")
                
                # 3. 文案（纯内容，无前缀）
                print(f"【文案】{content['content']}")
                
                # 4. 标签（纯内容，无前缀）
                print(f"【标签】{content['tags']}")
            
            if video_path:
                print(f"\n【视频】{video_path}")
            
        except Exception as e:
            logger.error(f"❌ 发送 Telegram 失败：{e}")

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
            logger.info(f"📝 调用 Gemini API 生成文案...")
            response = self.gemini_client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
            )
            logger.info(f"✅ 文案生成成功（{len(response.text)} 字）")
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

    def generate_multi_platform_content(self, text: str, theme: str) -> Dict[str, Dict[str, Any]]:
        """
        为 4 个平台生成差异化内容

        Args:
            text: 文案内容
            theme: 视频主题

        Returns:
            各平台内容字典
        """
        prompt = f"""
你是多平台爆款文案专家。请为以下视频内容生成 4 个平台的发布文案。

视频主题：{theme}
基础文案：
{text}

=== 各平台要求 ===

【小红书】
- 标题：15-25 字，2-3 个 emoji，情绪化，精致生活感
- 文案：300-500 字，治愈系，多 emoji，段落清晰，结尾互动
- 标签：8 个，#解压 #治愈 #ASMR #沉浸式 #解压视频 #解压神器 #治愈系 #小红书爆款

【抖音】
- 标题：10-15 字，强悬念/冲击，1-2 个 emoji，吸引完播
- 文案：50-100 字，短平快，节奏感强，引导点赞评论
- 标签：6 个，热门挑战向，#解压 #ASMR #沉浸式 #抖音热门 #解压视频 #治愈

【快手】
- 标题：8-12 字，直白接地气，1 个 emoji
- 文案：80-150 字，朴实真诚，老铁文化，引导关注
- 标签：6 个，接地气，#解压 #ASMR #老铁 #解压视频 #快手热门 #治愈

【B 站】
- 标题：15-30 字，玩梗/二次元，2-3 个 emoji，吸引点击
- 文案：200-400 字，详细有梗，可加时间轴，引导三连
- 标签：8 个，分区向，#解压 #ASMR #沉浸式 #治愈 #解压视频 #B 站热门 #解压神器 #放松

=== 返回格式 ===
小红书标题：xxx
小红书文案：xxx
小红书标签：#xxx #xxx #xxx #xxx #xxx #xxx #xxx #xxx

抖音标题：xxx
抖音文案：xxx
抖音标签：#xxx #xxx #xxx #xxx #xxx #xxx

快手标题：xxx
快手文案：xxx
快手标签：#xxx #xxx #xxx #xxx #xxx #xxx

B 站标题：xxx
B 站文案：xxx
B 站标签：#xxx #xxx #xxx #xxx #xxx #xxx #xxx #xxx
"""

        try:
            logger.info(f"🌐 调用 Gemini API 生成多平台内容...")
            response = self.gemini_client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
            )
            logger.info(f"✅ 多平台内容生成成功")
            
            # 解析结果
            return self._parse_multi_platform_result(response.text)
        except Exception as e:
            logger.error(f"❌ 多平台生成失败：{e}")
            # 返回默认内容
            return self._get_default_multi_platform_content(text)

    def _parse_multi_platform_result(self, result: str) -> Dict[str, Dict[str, Any]]:
        """解析多平台结果"""
        platforms = {}
        lines = result.split("\n")
        
        current_platform = None
        current_content = {"title": "", "content": "", "tags": ""}
        content_buffer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测平台行
            for platform in ["小红书", "抖音", "快手", "B 站"]:
                if line.startswith(f"{platform}标题："):
                    # 保存上一个平台
                    if current_platform and current_platform in platforms:
                        platforms[current_platform]["content"] = "\n".join(content_buffer).strip()
                    
                    current_platform = platform
                    content_buffer = []
                    current_content = {"title": "", "content": "", "tags": ""}
                    current_content["title"] = line.split("：", 1)[-1].strip()
                    break
                elif line.startswith(f"{platform}文案："):
                    continue  # 文案内容在后续行
                elif line.startswith(f"{platform}标签："):
                    current_content["tags"] = line.split("：", 1)[-1].strip()
                    platforms[current_platform] = current_content.copy()
                    break
            else:
                # 不是平台行，加入文案缓冲
                if current_platform and line not in ["标题：", "文案：", "标签："]:
                    content_buffer.append(line)
        
        # 保存最后一个平台
        if current_platform and current_platform in platforms:
            platforms[current_platform]["content"] = "\n".join(content_buffer).strip()
        
        return platforms

    def _get_default_multi_platform_content(self, text: str) -> Dict[str, Dict[str, Any]]:
        """默认多平台内容"""
        return {
            "小红书": {
                "title": "✨ 解压治愈时刻",
                "content": text,
                "tags": "#解压 #治愈 #ASMR #沉浸式 #解压视频 #解压神器 #治愈系 #小红书爆款",
            },
            "抖音": {
                "title": "这个解压视频太上头了！",
                "content": "看着太治愈了！你们喜欢什么解压方式？评论区告诉我～",
                "tags": "#解压 #ASMR #沉浸式 #抖音热门 #解压视频 #治愈",
            },
            "快手": {
                "title": "超级解压的视频",
                "content": "老铁们，这个视频真的太治愈了！喜欢的双击关注，每天更新解压内容！",
                "tags": "#解压 #ASMR #老铁 #解压视频 #快手热门 #治愈",
            },
            "B 站": {
                "title": "【解压】这个视频我能看 100 遍！ASMR 沉浸式体验",
                "content": "大家好，今天分享一个超级治愈的解压视频～\n\n视频主题：解压 ASMR\n时长：8 秒\n\n看着这些画面，感觉整个人都放松下来了。学习工作累了的时候看一看，真的很治愈！\n\n如果喜欢这个视频，请三连支持一下哦～你们的支持是我更新的动力！",
                "tags": "#解压 #ASMR #沉浸式 #治愈 #解压视频 #B 站热门 #解压神器 #放松",
            },
        }

        try:
            logger.info(f"🏷️ 调用 Gemini API 生成标题和标签...")
            response = self.gemini_client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
            )
            logger.info(f"✅ 标题标签生成成功")
            result = response.text.strip()

            # 解析结果
            lines = result.split("\n")
            titles = []
            tags = []

            for line in lines:
                if line.startswith("标题"):
                    # 提取标题（支持标题 1/2/3）
                    title_text = line.split(":", 1)[-1].strip()
                    if title_text:
                        titles.append(title_text)
                elif line.startswith("标签："):
                    tag_str = line.replace("标签：", "").strip()
                    tags = tag_str.split()

            # 选择最佳标题（优先第 1 个）
            title = titles[0] if titles else "✨ 解压治愈时刻"
            
            # 默认标签（如果生成失败）
            if not tags:
                tags = ["#解压", "#ASMR", "#治愈", "#放松", "#减压", "#沉浸式", "#解压神器", "#小红书爆款"]

            logger.info(f"🏷️ 生成 {len(titles)} 个标题备选，{len(tags)} 个标签")

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
            # 调用 gemini-video skill（使用绝对路径）
            sys.path.insert(0, "/home/ubuntu/.openclaw/workspace-xiang_xiaohongshu/skills/gemini-video/scripts")
            from generate_video import GeminiVideoGenerator

            gen = GeminiVideoGenerator(api_key=self.gemini_api_key)

            # 生成 9:16 竖屏，720p，8 秒
            video_path = gen.generate_from_text(
                theme,
                aspect_ratio="9:16",
                resolution="720p",
                duration=8,
            )

            return video_path
        except ImportError as e:
            logger.error(f"❌ gemini-video 模块未找到：{e}")
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

    # 配置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)

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
