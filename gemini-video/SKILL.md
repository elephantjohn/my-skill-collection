---
name: gemini-video
description: >
  Gemini Veo 视频生成 skill。
  使用 Google Gemini Veo 3.1 模型，支持文本生成视频和图片生成视频。
  默认参数：9:16 竖屏、720p、8 秒。
  也支持 16:9 横屏、1080p/4k 分辨率、4/6/8 秒时长。
  触发条件：用户要求"生成视频"、"文生视频"、"图生视频"、"AI 视频"、"Gemini 视频"、"Veo 视频"。
---

# Gemini Veo 视频生成

使用 Google Veo 3.1 模型生成 AI 视频。

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `GEMINI3PRO_API_KEY` | 是 | Google AI API Key（从 https://aistudio.google.com/apikey 获取，也兼容 `GEMINI_API_KEY`） |

## 依赖安装

```bash
pip install google-genai
```

## 默认参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 宽高比 | `9:16` | 竖屏（短视频/手机屏幕） |
| 分辨率 | `720p` | 标清 |
| 时长 | `8s` | 8 秒 |
| 模式 | 文本生成视频 | 纯文字描述 → 视频 |

## 脚本使用

主脚本：`scripts/generate_video.py`

### 文本生成视频（默认模式）

```bash
# 默认参数：9:16 竖屏 720p 8s
python generate_video.py "一只橘猫在钢琴上弹月光奏鸣曲"

# 指定横屏 1080p
python generate_video.py "日落时分的海滩" --ratio 16:9 --resolution 1080p

# 短视频 4 秒
python generate_video.py "烟花绽放" --duration 4

# 带负面提示词
python generate_video.py "森林中奔跑的小鹿" --negative "模糊,低质量,变形"

# 指定输出路径
python generate_video.py "城市夜景延时摄影" -o city_night.mp4
```

### 图片生成视频

```bash
# 图片 + 描述 → 视频
python generate_video.py "让画面中的花朵缓缓绽放" --image flower.jpg

# 图片生成 + 横屏
python generate_video.py "镜头缓慢推进" --image landscape.png --ratio 16:9
```

### 参数一览

| 参数 | 缩写 | 可选值 | 默认 |
|------|------|--------|------|
| `--ratio` | `-r` | `9:16`, `16:9` | `9:16` |
| `--resolution` | `-res` | `720p`, `1080p`, `4k` | `720p` |
| `--duration` | `-d` | `4`, `6`, `8` | `8` |
| `--image` | `-i` | 图片文件路径 | 无（纯文本模式） |
| `--negative` | `-n` | 负面提示词 | 无 |
| `--output` | `-o` | 输出文件路径 | `video_<时间戳>.mp4` |
| `--api-key` | | API Key | 从环境变量读取 |

### 约束

- `1080p` 和 `4k` 分辨率仅支持 8 秒时长
- 生成耗时约 11 秒 ~ 6 分钟（取决于负载）
- 视频含 SynthID 水印

## 编程接口

```python
from generate_video import GeminiVideoGenerator

gen = GeminiVideoGenerator(api_key="your-key")

# 文本生成视频（默认 9:16 竖屏 720p 8s）
path = gen.generate_from_text("一只猫在弹钢琴")

# 自定义参数
path = gen.generate_from_text(
    "日落海滩",
    aspect_ratio="16:9",
    resolution="1080p",
    duration=8,
    negative_prompt="模糊,低质量",
    output_path="sunset.mp4",
)

# 图片生成视频
path = gen.generate_from_image(
    "让这朵花缓缓绽放",
    image_path="flower.jpg",
    aspect_ratio="9:16",
)
```

## 工作流程

```
用户输入 (prompt + 可选图片)
  → _validate_params()  校验宽高比/分辨率/时长
  → 有图片? → client.files.upload() 上传图片
  → client.models.generate_videos()  发起生成
  → _wait_and_save()  每 10s 轮询一次
      → operation.done? → 下载并保存 .mp4
  → 返回视频文件路径
```

## 嵌入现有项目

将 `scripts/generate_video.py` 复制到目标项目，导入 `GeminiVideoGenerator` 类即可。
无循环依赖，仅依赖 `google-genai` 包。

## Claude 执行指南

当用户要求生成视频时，按以下流程执行：

1. **确认 API Key**：检查 `GEMINI3PRO_API_KEY` 环境变量是否存在（脚本自动加载 `~/.env`）
2. **确认 google-genai 已安装**：`pip install google-genai`（如未安装）
3. **获取用户需求**：
   - prompt（必须）：视频内容描述
   - 是否有参考图片（可选）
   - 宽高比偏好（默认 9:16 竖屏）
   - 分辨率偏好（默认 720p）
   - 时长偏好（默认 8s）
4. **执行生成**：运行 `python scripts/generate_video.py "<prompt>" [参数]`
5. **返回结果**：告知用户视频保存路径
