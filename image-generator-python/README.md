# Image Generator Python SDK

通用图片生成 Python 库 - 智能选择最优 API

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
from image_generator import ImageGenerator

# 初始化
generator = ImageGenerator(
    google_api_key='your-google-key',
    google_project_id='your-project',
    seadream_api_key='your-seadream-key',
    max_daily_cost=10.0,
)

# 生成图片（智能选择 API）
result = generator.generate(
    prompt='A beautiful sunset over the ocean',
    scenario='cover',
    budget='medium'
)

print(f"使用 API: {result['used_api']}")
print(f"成本：${result['cost']}")
print(f"图片 URL: {result['images'][0]['url']}")
```

## 功能特性

- ✅ 智能 API 选择（根据场景/预算/需求）
- ✅ 支持多个后端（Google Imagen, SeaDream, 等）
- ✅ 成本优化（自动选择性价比最高）
- ✅ 批量生成
- ✅ 成本追踪与预算控制
- ✅ 场景适配（封面/产品/插画/文字）

## 文档

详细文档：`docs/USAGE.md`
