---
name: gemini-image-gen
description: >
  使用 Gemini 3.1 Flash Image Preview 生成高质量图片。
  支持文章配图、封面图、插图等多种场景。
  自动优化提示词，生成符合文章内容的图片。
  触发条件：用户要求"生成图片"、"Gemini 绘图"、"创建配图"等。
---

# Gemini 图像生成 Skill

## 功能特性

- ✅ 使用 Gemini 3.1 Flash Image Preview 模型
- ✅ 自动优化提示词
- ✅ 支持批量生成
- ✅ 高质量输出（PNG 格式）
- ✅ 适合文章配图、封面、插图

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `GEMINI3PRO_API_KEY` | 是 | Gemini API Key |

## 编程接口

```python
from gemini_image_generator import GeminiImageGenerator

generator = GeminiImageGenerator()

# 生成单张图片
image_path = generator.generate(
    prompt="Create a picture of a nano banana dish in a fancy restaurant",
    save_path="output.png"
)

# 生成文章配图
images = generator.generate_for_article(
    title="年过完了，我在高铁上哭了",
    content="文章内容...",
    count=2,
    category="人生思考"
)

# 批量生成
images = generator.batch_generate(
    prompts=["prompt1", "prompt2", "prompt3"],
    save_dir="./images"
)
```

## 使用示例

### 基础生成

```python
from gemini_image_generator import GeminiImageGenerator

generator = GeminiImageGenerator()

# 简单描述
image = generator.generate(
    prompt="A beautiful sunset over the ocean",
    save_path="sunset.png"
)
```

### 文章配图

```python
# 根据文章内容自动生成配图
images = generator.generate_for_article(
    title="年过完了，从老家回到大城市",
    content="高铁缓缓驶出站台...",
    count=2,  # 生成 2 张
    category="人生思考",  # 人生思考/童话故事/科技探索等
    save_dir="./article_images"
)
```

### 提示词优化

```python
# 自动为不同类别优化提示词
optimized = generator.optimize_prompt(
    prompt="离别场景",
    category="人生思考",
    style="温馨感人"
)
# 输出："【水彩画风格】离别场景，温馨感人的氛围，暖色调，插画风格，高质量"
```

## 输出格式

- **格式**: PNG
- **尺寸**: 根据内容自动适配
- **质量**: 高质量
- **保存**: 本地文件路径

## 错误处理

- API 调用失败时返回 None
- 自动重试最多 3 次
- 记录详细日志

## 文件结构

```
gemini-image-gen/
├── SKILL.md
├── scripts/
│   └── gemini_image_generator.py
└── examples/
    └── basic_usage.py
```

## 与其他技能集成

### 与 wechat_pub 集成

```python
# 在 content_automation_engine.py 中
from gemini_image_generator import GeminiImageGenerator

image_gen = GeminiImageGenerator()
images = image_gen.generate_for_article(
    title=article_title,
    content=article_content,
    count=2,
    category=category
)
```

### 与 segmented_censor 配合

```python
# 生成图片 → 审核内容 → 发布
images = image_gen.generate_for_article(...)
is_ok, _ = censor_article_content(content)
if is_ok:
    publish_to_wechat(images=images)
```

## 最佳实践

1. **提示词优化**: 使用 `optimize_prompt()` 为不同类别定制风格
2. **批量生成**: 使用 `batch_generate()` 提高效率
3. **错误处理**: 始终检查返回值是否为 None
4. **缓存**: 相同 prompt 可复用结果（可选）
5. **成本控制**: 设置每日生成上限

## 成本说明

- Gemini 3.1 Flash Image Preview 按生成次数计费
- 建议设置每日预算上限
- 批量生成可享受优惠

## 注意事项

1. **API Key 安全**: 使用环境变量，不要硬编码
2. **图片版权**: 生成的图片可用于商业用途
3. **内容合规**: 确保 prompt 符合平台规范
4. **网络要求**: 需要稳定的网络连接
