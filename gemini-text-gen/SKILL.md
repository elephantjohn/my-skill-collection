---
name: gemini-text-gen
description: >
  使用 Gemini 3 Pro 生成微信公众号文章内容。
  支持 5 大类别：童话故事、人生思考、科技探索、美食文化、旅行游记。
  生成内容符合微信平台规范，字数充足，结构完整。
  触发条件：用户要求"生成公众号文章"、"Gemini 写作"、"创作内容"等。
---

# Gemini 文本生成 Skill

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `GEMINI3PRO_API_KEY` | 是 | Gemini 3 Pro API Key |

## 编程接口

```python
from gemini_generator import GeminiTextGenerator

generator = GeminiTextGenerator()

# 生成童话故事
content = generator.generate_fairy_tale("聪明的稻草人")

# 生成人生思考
content = generator.generate_life_thinking("时间的重量")

# 生成科技探索
content = generator.generate_tech_exploration("人工智能的边界")

# 生成美食文化
content = generator.generate_food_culture("一碗面条的故事")

# 生成旅行游记
content = generator.generate_travel_note("西藏的呼唤")
```

## 输出格式

返回 JSON 格式的内容，包含：
- `title`: 标题
- `subtitle`: 副标题
- `introduction`: 引言
- `paragraphs`: 段落列表
- `highlights`: 精彩片段
- `conclusion`: 结尾

## 字数控制

- 童话故事：≥4500 字
- 人生思考：≥4000 字
- 科技探索：≥4000 字
- 美食文化：≥4500 字
- 旅行游记：≥4500 字

## 错误处理

- API 调用失败时返回默认内容
- 自动重试最多 3 次
- 记录详细日志到 `logs/gemini/`
