---
name: xiaohongshu-creator
description: >
  小红书自动创作 skill。
  每 10 小时自动生成一篇小红书图文笔记：
  1. 使用 Gemini 3 Pro 生成文案
  2. 使用百度审核 API 智能审查（分段定位 + 局部修改）
  3. 使用 Veo 3.1 生成 9:16 竖屏视频（解压/ASMR 主题）
  4. 输出完整笔记（文案 + 视频）
  触发条件：定时任务触发，或用户要求"创作小红书"、"生成笔记"。
---

# 小红书自动创作 Skill

## 工作流程

```
定时触发 (每 10 小时)
  ↓
1. Gemini 3 Pro 生成文案
  ↓
2. 百度智能审核
  ├─ 整体审核 → 通过 → 完成
  └─ 不通过 → 分段定位 → 问题段落 → 局部修改 → 重新审核
  ↓
3. Veo 3.1 生成视频 (9:16, 720p, 8s)
  ↓
4. 输出完整笔记
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `GEMINI3PRO_API_KEY` | Gemini 3 Pro API Key |
| `TEXT_API_KEY` | 百度文本审核 API Key |
| `TEXT_SECRET_KEY` | 百度文本审核 Secret Key |
| `BAIDU_API_KEY` | 百度千帆 API Key（用于修正） |

## 脚本使用

```bash
# 生成一篇小红书笔记
python scripts/create_note.py

# 指定主题
python scripts/create_note.py --theme "解压视频"

# 仅生成文案（不生成视频）
python scripts/create_note.py --text-only

# 仅审核已有文案
python scripts/create_note.py --censor-only --input note.txt
```

## 编程接口

```python
from xiaohongshu_creator import XiaohongshuCreator

creator = XiaohongshuCreator()

# 生成完整笔记
note = creator.create_note(theme="解压视频")

# 生成文案
text = creator.generate_text(theme="ASMR")

# 智能审核
is_ok, final_text = creator.smart_censor(text)

# 生成视频
video_path = creator.generate_video(prompt="解压视频")
```

## 输出格式

```json
{
  "title": "笔记标题",
  "content": "完整文案",
  "video_path": "videos/xxx.mp4",
  "tags": ["#解压", "#ASMR"],
  "created_at": "2026-03-01T16:00:00+08:00",
  "censor_passed": true
}
```
