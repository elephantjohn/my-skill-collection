#!/usr/bin/env python3
"""
小红书创作者 - Telegram 发送包装器
生成内容并发送到 Telegram（多平台分组）
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# 加载 .env
env_path = Path("/home/ubuntu/.openclaw/workspace-xiang_xiaohongshu/.env")
load_dotenv(env_path)

from create_note import XiaohongshuCreator


async def send_multi_platform_content(note_data: dict):
    """发送多平台内容到 Telegram"""
    from telegram import Bot
    
    # 从环境变量获取 Telegram Bot Token 和 Chat ID
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "7523511013")
    
    if not bot_token:
        print("⚠️  未配置 TELEGRAM_BOT_TOKEN，跳过发送")
        return
    
    bot = Bot(token=bot_token)
    platform_contents = note_data.get("platform_contents", {})
    video_path = note_data.get("video_path")
    
    # 平台顺序
    platforms = ["小红书", "抖音", "快手", "B 站"]
    
    for platform in platforms:
        content = platform_contents.get(platform, {})
        if not content:
            continue
        
        # 1. 发送标题
        await bot.send_message(
            chat_id=chat_id,
            text=f"📝 **{platform} - 标题**（复制用）\n\n{content['title']}",
            parse_mode="Markdown",
        )
        
        # 2. 发送文案
        await bot.send_message(
            chat_id=chat_id,
            text=f"📄 **{platform} - 文案**（复制用）\n\n{content['content']}",
            parse_mode="Markdown",
        )
        
        # 3. 发送标签
        await bot.send_message(
            chat_id=chat_id,
            text=f"🏷️ **{platform} - 标签**（复制用）\n\n{content['tags']}",
            parse_mode="Markdown",
        )
    
    # 4. 发送视频
    if video_path and Path(video_path).exists():
        await bot.send_video(
            chat_id=chat_id,
            video=open(video_path, "rb"),
            caption=f"🎬 **视频文件**\n\n直接上传到{platforms[0]}即可～",
            parse_mode="Markdown",
        )


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="小红书创作者 - 带 Telegram 发送")
    parser.add_argument("--theme", type=str, help="视频主题")
    parser.add_argument("--text-only", action="store_true", help="仅生成文案")
    parser.add_argument("--output", type=str, default="output", help="输出目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")
    parser.add_argument("--send-telegram", action="store_true", help="发送到 Telegram")
    
    args = parser.parse_args()
    
    # 创建笔记
    creator = XiaohongshuCreator()
    note = creator.create_note(
        theme=args.theme,
        generate_video=not args.text_only,
        output_dir=args.output,
    )
    
    # 发送到 Telegram
    if args.send_telegram:
        print("\n📱 正在发送到 Telegram...")
        asyncio.run(send_multi_platform_content(note))
        print("✅ 发送完成！")
    
    print("\n✅ 创作完成！")
    print(f"标题：{note['title']}")
    print(f"文案：{len(note['content'])} 字")
    print(f"视频：{note['video_path'] or '未生成'}")


if __name__ == "__main__":
    main()
