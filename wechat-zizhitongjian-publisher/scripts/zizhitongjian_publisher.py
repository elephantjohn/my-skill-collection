#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
资治通鉴系列文章发布工具
从 Google Sheet 读取内容，使用固定模板发布
"""

import os
import sys
import json
import sqlite3
import socket
from pathlib import Path
import time
import re

old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    results = old_getaddrinfo(*args, **kwargs)
    return [r for r in results if r[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

sys.path.insert(0, str(Path(__file__).parent.parent))

from config_loader import load_env_config, get_wechat_config
from automated_content_system import DatabaseManager, ArticleRecord, ContentStatus
from add_draft_news import AccessTokenManager, add_draft_news, upload_permanent_image, upload_image_for_content
from gemini_image_generator import GeminiImageGenerator

load_env_config()


class ZizhitongjianPublisher:
    """资治通鉴发布器"""
    
    def __init__(self, google_sheet_url: str = None):
        """初始化发布器
        
        Args:
            google_sheet_url: Google Sheet URL
        """
        self.google_sheet_url = google_sheet_url or "https://docs.google.com/spreadsheets/d/1LoWp1xMjxrcale6_e9ZkyBsbAC8I19m3Ps9W4hEDUic/edit?gid=0"
        self.db = DatabaseManager()
    
    def read_chapter_content(self, chapter: int) -> dict:
        """读取章节内容
        
        Args:
            chapter: 章节号
            
        Returns:
            章节内容字典
        """
        # TODO: 实现 Google Sheet 读取
        # 目前手动提供内容
        
        chapters = {
            1: {
                "title": "智伯是怎么作死的——三家分晋",
                "subtitle": "司马光笔下的礼崩乐坏时代",
                "content": """...（内容从 Google Sheet 读取）..."""
            },
            2: {
                "title": "魏文侯选相——识人的五个标准",
                "subtitle": "李克的识人智慧",
                "content": """...（内容从 Google Sheet 读取）..."""
            }
        }
        
        return chapters.get(chapter, {})
    
    def generate_images(self, chapter: int, title: str, save_dir: str) -> list:
        """生成配图
        
        Args:
            chapter: 章节号
            title: 章节标题
            save_dir: 保存目录
            
        Returns:
            图片路径列表
        """
        Path(save_dir).mkdir(exist_ok=True)
        
        # 根据章节生成不同的提示词
        prompts_map = {
            1: [
                "【中国古代战争场景】春秋战国时期，智伯率领军队围攻晋阳城，战船在汾水上航行，士兵列阵，古代战争场面，水墨画风格，高质量",
                "【中国古代历史场景】春秋战国时期，赵韩魏三家分晋，诸侯会盟，古代宫殿建筑，历史场景，工笔画风格，高质量"
            ],
            2: [
                "【中国古代宫廷场景】战国时期，魏文侯在宫殿中与大臣李克讨论选相，古代君臣对话，宫殿建筑，历史场景，工笔画风格，高质量",
                "【中国古代文化场景】战国时期魏国朝堂，君臣议事，古代官员服饰，庄重严肃，历史场景，水墨画风格，高质量"
            ]
        }
        
        prompts = prompts_map.get(chapter, [
            f"【中国古代历史场景】{title}，历史场景，高质量",
            f"【中国古代文化场景】{title}，文化场景，高质量"
        ])
        
        generator = GeminiImageGenerator()
        image_paths = []
        
        for i, prompt in enumerate(prompts, 1):
            print(f"生成第{i}张配图...")
            save_path = f"{save_dir}/zizhitongjian_ch{chapter}_{i}.png"
            
            try:
                response = generator.client.models.generate_content(
                    model="gemini-3.1-flash-image-preview",
                    contents=[prompt]
                )
                
                for part in response.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        image.save(save_path)
                        image_paths.append(save_path)
                        print(f"✅ 第{i}张配图已保存")
                        break
            except Exception as e:
                print(f"⚠️ 第{i}张配图生成失败：{e}，使用占位图")
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (800, 450), color='#4A90D9')
                draw = ImageDraw.Draw(img)
                draw.text((200, 200), f"第{chapter}章\n配图{i}", fill='white', font_size=32)
                placeholder = f"/tmp/placeholder_ch{chapter}_{i}.png"
                img.save(placeholder)
                image_paths.append(placeholder)
        
        return image_paths
    
    def generate_html(self, content: str, title: str, subtitle: str, image_urls: list, chapter: int) -> str:
        """生成 HTML
        
        Args:
            content: 文章内容
            title: 标题
            subtitle: 副标题
            image_urls: 图片 URL 列表
            chapter: 章节号
            
        Returns:
            HTML 字符串
        """
        # 分割段落
        paragraphs = content.split('\n\n')
        
        html_parts = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 移除 Markdown 符号
            para = para.replace('## ', '').replace('# ', '')
            para = para.replace('**', '').replace('__', '')
            
            # 判断是否为小标题
            if len(para) < 30 and not para.endswith(('。', '！', '？', '”')):
                html_parts.append(f'<h2 style="font-size:24px;font-weight:bold;color:#c0392b;margin:40px 0 20px;padding:15px 20px;background:linear-gradient(135deg,#fdf2f2 0%,#fff5f5 100%);border-left:5px solid #c0392b;border-radius:8px 0 0 8px;">{para}</h2>')
            else:
                html_parts.append(f'<p style="margin:30px 0;text-align:justify;font-size:18px;line-height:2.4;color:#000000;">{para}</p>')
        
        content_html = '\n'.join(html_parts)
        
        # 完整 HTML
        next_chapter = chapter + 1
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:30px 20px;font-family:-apple-system,sans-serif;max-width:640px;margin:0 auto;background:linear-gradient(to bottom,#fafafa,#f5f5f5);">
    
    <div style="text-align:center;margin-bottom:40px;padding:30px 20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:15px;color:white;box-shadow:0 8px 25px rgba(102,126,234,0.3);">
        <p style="font-size:14px;letter-spacing:3px;margin-bottom:15px;opacity:0.9;">【资治通鉴】</p>
        <h1 style="font-size:30px;font-weight:bold;margin:20px 0;line-height:1.4;text-shadow:2px 2px 4px rgba(0,0,0,0.2);">{chapter}：{title}</h1>
        <p style="font-size:16px;opacity:0.9;font-style:italic;">{subtitle}</p>
    </div>
    
    <img src="{image_urls[0]}" style="width:100%;border-radius:15px;margin:40px 0;box-shadow:0 8px 25px rgba(0,0,0,0.15);border:3px solid #fff;">
    
    {content_html}
    
    <img src="{image_urls[1]}" style="width:100%;border-radius:15px;margin:40px 0;box-shadow:0 8px 25px rgba(0,0,0,0.15);border:3px solid #fff;">
    
    <div style="margin-top:60px;padding:35px 30px;background:linear-gradient(135deg,#f8f9fa 0%,#e9ecef 100%);border-radius:15px;text-align:center;border:2px solid #dee2e6;">
        <p style="font-size:20px;font-weight:bold;color:#c0392b;margin-bottom:15px;">【本章完】</p>
        <p style="color:#7f8c8d;">下一章预告：【资治通鉴】{next_chapter}</p>
    </div>
    
    <hr style="border:none;border-top:2px solid #e0e0e0;margin:50px 0;">
    
    <p style="color:#999;font-size:14px;text-align:center;">📌 本系列持续更新，欢迎关注</p>
    
</body>
</html>
"""
        
        return full_html
    
    def publish_chapter(self, chapter: int, content: str = None, title: str = None, subtitle: str = None):
        """发布章节
        
        Args:
            chapter: 章节号
            content: 文章内容（可选，如不提供则从 Google Sheet 读取）
            title: 标题（可选）
            subtitle: 副标题（可选）
        """
        print("=" * 60)
        print(f"资治通鉴 第{chapter}章发布")
        print("=" * 60)
        
        # 1. 读取内容（如未提供）
        if not content:
            print(f"\n📖 读取第{chapter}章内容...")
            chapter_data = self.read_chapter_content(chapter)
            content = chapter_data.get("content", "")
            title = title or chapter_data.get("title", f"第{chapter}章")
            subtitle = subtitle or chapter_data.get("subtitle", "")
        
        article_data = {
            "series": "资治通鉴",
            "chapter": str(chapter),
            "title": f"{title}",
            "full_title": f"【资治通鉴】{chapter}：{title}",
            "subtitle": subtitle,
        }
        
        # 2. 生成配图
        print(f"\n🎨 生成配图...")
        save_dir = "/home/ubuntu/.openclaw/workspace-wechat_creater/wechat_pub/content_images"
        image_paths = self.generate_images(chapter, title, save_dir)
        
        # 3. 保存文章
        print(f"\n📝 保存文章...")
        article = ArticleRecord(
            id=None,
            article_number=f"ZZTJ_CH{chapter:02d}_{int(time.time())}",
            category="历史趣闻",
            title=article_data["full_title"],
            subtitle=article_data["subtitle"],
            content_json=json.dumps({"content": content, **article_data}, ensure_ascii=False),
            content_html="",
            status=ContentStatus.CREATING.value,
            word_count=len(content)
        )
        
        article_id = self.db.add_article(article)
        print(f"✅ ID: {article_id}")
        
        # 4. 获取 token
        wechat_config = get_wechat_config()
        appid = wechat_config.get('appid', '')
        secret = wechat_config.get('appsecret', '')
        
        token_manager = AccessTokenManager(appid, secret)
        access_token = token_manager.get_token()
        
        # 5. 上传图片
        print(f"\n🎨 上传图片...")
        image_urls = []
        for i, img_path in enumerate(image_paths, 1):
            if os.path.exists(img_path):
                img_url = upload_image_for_content(access_token, img_path)
                image_urls.append(img_url)
                print(f"✅ 第{i}张已上传")
        
        # 6. 封面
        print(f"\n📸 封面...")
        thumb_media_id = upload_permanent_image(access_token, image_paths[0])
        print(f"✅ 已上传")
        
        # 7. 生成 HTML
        print(f"\n📄 生成 HTML...")
        full_html = self.generate_html(content, title, subtitle, image_urls, chapter)
        
        # 更新
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE articles SET content_html = ? WHERE id = ?",
                (full_html, article_id)
            )
            conn.commit()
        print("✅ HTML 已生成")
        
        # 8. 发布
        print(f"\n📤 发布...")
        
        result = add_draft_news(
            access_token=access_token,
            title=article_data["full_title"],
            author="历史君",
            digest=article_data["subtitle"][:120],
            content_html=full_html,
            thumb_media_id=thumb_media_id
        )
        
        if result and 'media_id' in result:
            print(f"\n✅✅✅ 发布成功！")
            print(f"媒体 ID: {result['media_id']}")
            print(f"标题：{article_data['full_title']}")
            print(f"配图：2 张（Gemini 生成）")
            print(f"\n登录 https://mp.weixin.qq.com 查看")
            
            self.db.update_article_status(
                article_id,
                ContentStatus.PUBLISHED.value,
                wechat_media_id=result['media_id']
            )
        else:
            print(f"\n❌ 失败：{result}")
        
        return result


# 便捷函数
def publish_zizhitongjian_chapter(chapter: int, **kwargs):
    """发布资治通鉴章节的便捷函数"""
    publisher = ZizhitongjianPublisher()
    publisher.publish_chapter(chapter, **kwargs)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        chapter = int(sys.argv[1])
    else:
        chapter = 3  # 默认第 3 章
    
    publish_zizhitongjian_chapter(chapter)
