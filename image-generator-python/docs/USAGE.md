# Image Generator Python SDK - 使用文档

## 🚀 快速开始

### 1. 安装依赖

```bash
cd skills/image-generator-python
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 3. 基础使用

```python
from image_generator import ImageGenerator

# 初始化
generator = ImageGenerator(
    google_api_key='your-key',
    google_project_id='your-project',
    seadream_api_key='your-seadream-key',
)

# 生成（自动选择 API）
result = generator.generate(
    prompt='A beautiful sunset',
    scenario='cover',
)

print(f"使用 API: {result['used_api']}")
print(f"成本：${result['cost']}")
```

---

## 📖 API 文档

### ImageGenerator 类

#### 初始化参数

```python
ImageGenerator(
    google_api_key: str,        # Google API Key
    google_project_id: str,     # Google 项目 ID
    google_location: str,       # Google Cloud 区域（默认 us-central1）
    seadream_api_key: str,      # SeaDream API Key
    default_api: str,           # 默认 API（默认 auto 自动选择）
    budget_mode: str,           # 预算模式：low|medium|high
    max_daily_cost: float,      # 每日预算上限（默认 $10）
)
```

#### generate() - 生成单张

```python
result = generator.generate(
    prompt='A sunset',              # 必需：提示词
    scenario='cover',               # 场景：cover|product|illustration|text|general
    api='auto',                     # 指定 API（None 表示自动）
    budget='medium',                # 预算：low|medium|high
    negative_prompt='ugly',         # 负面提示词
    resolution='1024x1024',         # 分辨率
    count=1,                        # 数量
)
```

**返回值：**
```python
{
    'images': [{'url': '...', 'width': 1024, 'height': 1024}],
    'cost': 0.04,                   # 成本（美元）
    'used_api': 'imagen-4',         # 使用的 API
    'scenario': 'cover',            # 场景
    'metadata': {...},              # 元数据
}
```

#### batch_generate() - 批量生成

```python
result = generator.batch_generate(
    prompts=['prompt1', 'prompt2'], # 提示词列表
    scenario='illustration',        # 场景
    max_cost=5.0,                   # 预算上限
)
```

**返回值：**
```python
{
    'results': [...],               # 结果列表
    'total_cost': 0.12,             # 总成本
    'count': 3,                     # 成功数量
}
```

#### get_cost_stats() - 成本统计

```python
stats = generator.get_cost_stats(
    period='day',                   # day|week|month
    api='all',                      # 指定 API 或 all
)
```

**返回值：**
```python
{
    'period': 'day',
    'total_cost': 0.50,
    'count': 10,
    'avg_cost': 0.05,
    'by_api': {'imagen-4': {'cost': 0.30, 'count': 6}},
    'remaining_budget': 9.50,
}
```

#### get_supported_apis() - 支持的 API

```python
apis = generator.get_supported_apis()
```

**返回值：**
```python
[
    {'name': 'imagen-4-fast', 'pricing': 0.02, 'capabilities': [...]},
    ...
]
```

---

## 🎯 场景说明

| 场景 | 说明 | 推荐 API |
|------|------|---------|
| **cover** | 封面/主图 | imagen-4-ultra, seadream-v2 |
| **product** | 产品图（带文字） | imagen-4-ultra, imagen-4 |
| **illustration** | 插画/艺术 | seadream-v2, seadream-v1 |
| **text** | 文字渲染 | imagen-4-ultra, imagen-4 |
| **general** | 通用 | imagen-4, imagen-4-fast |

---

## 💰 定价

| API | 价格/张 | 适用场景 |
|-----|--------|---------|
| imagen-4-fast | $0.02 | 快速出图 |
| imagen-4 | $0.04 | 通用 |
| imagen-4-ultra | $0.06 | 高质量 |
| seadream-v1 | $0.01 | 二次元 |
| seadream-v2 | $0.03 | 艺术插画 |

---

## 🔧 扩展新 API

### 1. 创建提供商类

```python
# image_generator/providers/newapi.py
from .base import BaseProvider

class NewApiProvider(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'newapi'
        self.pricing = 0.05
        self.capabilities = ['art', 'realistic']
    
    def validate_config(self):
        if not self.api_key:
            raise ValueError("Missing API Key")
        return True
    
    def generate(self, prompt, options=None):
        # 实现生成逻辑
        return {
            'images': [...],
            'cost': self.pricing,
            'api': self.name,
        }
```

### 2. 注册到生成器

```python
# image_generator/generator.py
from .providers.newapi import NewApiProvider

self.providers['newapi'] = NewApiProvider(config)
```

### 3. 更新选择器评分

```python
# image_generator/selector.py
self.api_ratings['newapi'] = {
    'quality': 4,
    'speed': 4,
    'cost': 3,
    'text': 3,
    'art': 4,
}
```

---

## 📝 使用示例

### 小红书封面

```python
result = generator.generate(
    prompt='小红书封面，极简风格，莫兰迪色系',
    scenario='cover',
    resolution='1242x1660',  # 3:4 竖屏
)
```

### 产品图（带文字）

```python
result = generator.generate(
    prompt='Product photo with "SALE 50% OFF" text',
    scenario='product',
    api='imagen-4-ultra',
)
```

### 批量生成

```python
result = generator.batch_generate(
    prompts=['prompt1', 'prompt2', 'prompt3'],
    scenario='illustration',
    max_cost=3.0,
)
```

---

## ⚠️ 注意事项

1. **API Key 安全**：使用环境变量，不要硬编码
2. **预算控制**：设置 `max_daily_cost` 避免超支
3. **错误处理**：捕获异常
4. **成本监控**：定期调用 `get_cost_stats()`

---

## 🆘 常见问题

### Q: 如何知道选择了哪个 API？
A: 返回结果包含 `used_api` 字段。

### Q: 如何切换预算模式？
A: 初始化时设置 `budget_mode='low'` 或 `'high'`。

### Q: 超出预算会怎样？
A: 抛出 `RuntimeError("超出每日预算限制")`。

### Q: 如何添加更多 API？
A: 继承 `BaseProvider` 并注册到生成器。
