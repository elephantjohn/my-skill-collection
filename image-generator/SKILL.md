# Image Generator Skill

通用图片生成技能 - 智能选择最优 API

## 功能
- 根据需求自动选择最佳图片生成 API
- 支持多个后端：Google Imagen 4 (Nano Banana), SeaDream, 等
- 成本优化：自动选择性价比最高的方案
- 场景适配：封面/产品图/插画/文字渲染

## 支持的 API

| API | 适用场景 | 价格 | 优先级 |
|-----|---------|------|--------|
| **Imagen 4 Fast** | 快速出图、配图 | $0.02/张 | 2 |
| **Imagen 4** | 通用场景 | $0.04/张 | 3 |
| **Imagen 4 Ultra** | 高质量封面 | $0.06/张 | 4 |
| **SeaDream V1** | 二次元/艺术 | $0.01/张 | 1 |
| **SeaDream V2** | 真实感人像 | $0.03/张 | 2 |

## 使用方式

### 基础调用
```javascript
const { ImageGenerator } = require('./src/generator.js');

const generator = new ImageGenerator({
  googleApiKey: process.env.GOOGLE_API_KEY,
  seaDreamApiKey: process.env.SEADREAM_API_KEY,
});

// 自动生成（智能选择 API）
const result = await generator.generate({
  prompt: "A beautiful sunset over the ocean",
  scenario: 'cover', // cover|product|illustration|text
  budget: 'low', // low|medium|high
});
```

### 指定 API
```javascript
const result = await generator.generate({
  prompt: "...",
  api: 'imagen-4-fast', // 强制指定
});
```

### 批量生成
```javascript
const results = await generator.batchGenerate({
  prompts: ['prompt1', 'prompt2', 'prompt3'],
  scenario: 'product',
  maxCost: 5.0, // 预算上限（美元）
});
```

## 配置

### 环境变量
```bash
# Google Cloud
GOOGLE_API_KEY=your-key
GOOGLE_PROJECT_ID=your-project
GOOGLE_LOCATION=us-central1

# SeaDream
SEADREAM_API_KEY=your-key

# 默认配置
DEFAULT_API=auto # auto|imagen-4|imagen-4-fast|seadream-v2
DEFAULT_SCENARIO=general
BUDGET_MODE=medium # low|medium|high
```

### 场景定义
```javascript
const SCENARIOS = {
  cover: {
    priority: 'quality',
    minResolution: '2K',
    preferredApis: ['imagen-4-ultra', 'seadream-v2'],
  },
  product: {
    priority: 'accuracy',
    textRendering: true,
    preferredApis: ['imagen-4', 'imagen-4-ultra'],
  },
  illustration: {
    priority: 'artistic',
    preferredApis: ['seadream-v2', 'seadream-v1'],
  },
  text: {
    priority: 'text_accuracy',
    textRendering: true,
    preferredApis: ['imagen-4-ultra', 'imagen-4'],
  },
};
```

## 扩展新 API

### 1. 添加 API 配置
```javascript
// src/providers/newapi.js
class NewApiProvider {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.name = 'newapi';
    this.pricing = { perImage: 0.05 };
    this.capabilities = ['text', 'art', 'realistic'];
  }

  async generate(prompt, options) {
    // 实现生成逻辑
    return { imageUrl, cost, metadata };
  }
}
```

### 2. 注册到生成器
```javascript
// src/generator.js
const providers = {
  'imagen-4': ImagenProvider,
  'seadream': SeaDreamProvider,
  'newapi': NewApiProvider, // 新增
};
```

### 3. 更新选择逻辑
```javascript
// src/selector.js
const API_RANKING = {
  'newapi': { quality: 4, speed: 3, cost: 2 },
};
```

## 文件结构
```
image-generator/
├── SKILL.md
├── src/
│   ├── generator.js      # 主生成器
│   ├── selector.js       # API 选择器
│   ├── providers/
│   │   ├── imagen.js     # Google Imagen
│   │   ├── seadream.js   # SeaDream
│   │   └── base.js       # 基础接口
│   └── utils/
│       ├── cost.js       # 成本计算
│       └── prompt.js     # 提示词优化
├── config/
│   └── default.json
└── docs/
    └── API.md
```

## 成本追踪

每次生成都会记录：
- 使用的 API
- 实际成本
- 生成时间
- 图片质量评分

```javascript
// 查询历史成本
const stats = await generator.getCostStats({
  period: 'month',
  api: 'all',
});
// 返回：{ totalCost: 12.5, count: 300, avgCost: 0.042 }
```

## 注意事项

1. **API Key 安全**：不要硬编码密钥，使用环境变量
2. **成本限制**：设置每日/每月预算上限
3. **错误处理**：API 失败时自动降级到其他服务
4. **缓存**：相同 prompt 可复用结果（可选）
