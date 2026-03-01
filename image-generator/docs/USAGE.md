# Image Generator Skill - 使用文档

## 🚀 快速开始

### 1. 安装依赖
```bash
cd skills/image-generator
npm install
```

### 2. 配置环境变量
```bash
# .env 文件
GOOGLE_API_KEY=your-google-api-key
GOOGLE_PROJECT_ID=your-project-id
SEADREAM_API_KEY=your-seadream-api-key
```

### 3. 基础使用
```javascript
const { ImageGenerator } = require('./src/generator');

const generator = new ImageGenerator();

// 生成一张图（自动选择最优 API）
const result = await generator.generate({
  prompt: 'A beautiful sunset',
  scenario: 'cover',
});

console.log(`使用了 ${result.usedApi}, 成本 $${result.cost}`);
```

---

## 📖 API 文档

### ImageGenerator 类

#### 构造函数参数
```javascript
new ImageGenerator({
  googleApiKey: string,      // Google API Key
  googleProjectId: string,   // Google 项目 ID
  googleLocation: string,    // Google Cloud 区域（默认 us-central1）
  seaDreamApiKey: string,    // SeaDream API Key
  defaultApi: string,        // 默认 API（默认 auto 自动选择）
  budgetMode: string,        // 预算模式：low|medium|high
  maxDailyCost: number,      // 每日预算上限（默认 $10）
})
```

#### generate() - 生成单张
```javascript
await generator.generate({
  prompt: string,           // 必需：提示词
  api?: string,             // 可选：指定 API（默认 auto）
  scenario?: string,        // 可选：场景（cover|product|illustration|text|general）
  budget?: string,          // 可选：预算（low|medium|high）
  negativePrompt?: string,  // 可选：负面提示词
  resolution?: string,      // 可选：分辨率（默认 1024x1024）
  count?: number,           // 可选：数量（默认 1）
})
```

**返回值：**
```javascript
{
  images: [{ url, width, height }],
  cost: number,             // 实际成本（美元）
  usedApi: string,          // 使用的 API
  scenario: string,         // 场景
  metadata: object,         // 元数据
}
```

#### batchGenerate() - 批量生成
```javascript
await generator.batchGenerate({
  prompts: string[],        // 必需：提示词数组
  scenario?: string,        // 可选：场景
  maxCost?: number,         // 可选：预算上限
})
```

**返回值：**
```javascript
{
  results: [...],           // 生成结果数组
  totalCost: number,        // 总成本
  count: number,            // 成功数量
}
```

#### getCostStats() - 成本统计
```javascript
generator.getCostStats({
  period?: string,          // day|week|month
  api?: string,             // 指定 API 或 all
})
```

**返回值：**
```javascript
{
  period: string,
  totalCost: number,
  count: number,
  avgCost: number,
  byApi: { [api]: { cost, count } },
  remainingBudget: number,
}
```

#### getSupportedApis() - 支持的 API
```javascript
generator.getSupportedApis()
```

**返回值：**
```javascript
[
  { name: 'imagen-4-fast', pricing: 0.02, capabilities: [...] },
  { name: 'imagen-4', pricing: 0.04, capabilities: [...] },
  ...
]
```

---

## 🎯 场景说明

| 场景 | 说明 | 推荐 API |
|------|------|---------|
| **cover** | 封面/主图 | imagen-4-ultra, seadream-v2 |
| **product** | 产品图（需要文字） | imagen-4-ultra, imagen-4 |
| **illustration** | 插画/艺术 | seadream-v2, seadream-v1 |
| **text** | 文字渲染 | imagen-4-ultra, imagen-4 |
| **general** | 通用 | imagen-4, imagen-4-fast |

---

## 💰 定价参考

| API | 价格/张 | 适用场景 |
|-----|--------|---------|
| imagen-4-fast | $0.02 | 快速出图、配图 |
| imagen-4 | $0.04 | 通用场景 |
| imagen-4-ultra | $0.06 | 高质量封面 |
| seadream-v1 | $0.01 | 二次元/草图 |
| seadream-v2 | $0.03 | 艺术插画 |

---

## 🔧 扩展新 API

### 步骤 1: 创建提供商类
```javascript
// src/providers/newapi.js
const { BaseProvider } = require('./base');

class NewApiProvider extends BaseProvider {
  constructor(config) {
    super(config);
    this.name = 'newapi';
    this.pricing = 0.05;
    this.capabilities = ['art', 'realistic'];
  }

  async generate(prompt, options) {
    // 实现生成逻辑
    return { images, cost: this.pricing, api: this.name };
  }

  validateConfig() {
    // 验证配置
  }
}
```

### 步骤 2: 注册到生成器
```javascript
// src/generator.js
const { NewApiProvider } = require('./providers/newapi');

// 在构造函数中添加
this.providers['newapi'] = new NewApiProvider(config);
```

### 步骤 3: 更新选择器评分
```javascript
// src/selector.js
this.apiRatings['newapi'] = {
  quality: 4,
  speed: 4,
  cost: 3,
  text: 3,
  art: 4,
};
```

---

## ⚠️ 注意事项

1. **API Key 安全**：使用环境变量，不要硬编码
2. **预算控制**：设置 `maxDailyCost` 避免超支
3. **错误处理**：捕获 API 调用异常
4. **成本追踪**：定期调用 `getCostStats()` 监控

---

## 📝 示例代码

### 小红书封面生成
```javascript
const result = await generator.generate({
  prompt: '小红书封面，极简风格，莫兰迪色系，文字空间',
  scenario: 'cover',
  budget: 'medium',
  resolution: '1242x1660', // 小红书竖屏比例
});
```

### 产品图（带文字）
```javascript
const result = await generator.generate({
  prompt: 'Product photo with "SALE 50% OFF" text overlay',
  scenario: 'product',
  api: 'imagen-4-ultra', // 强制使用高质量
});
```

### 批量生成配图
```javascript
const prompts = [
  'Morning coffee aesthetic',
  'Cozy reading corner',
  'Minimalist workspace',
];

const result = await generator.batchGenerate({
  prompts,
  scenario: 'illustration',
  maxCost: 3.0,
});
```

---

## 🆘 常见问题

### Q: 如何知道选择了哪个 API？
A: 返回结果包含 `usedApi` 字段，或开启日志查看。

### Q: 如何切换预算模式？
A: 初始化时设置 `budgetMode: 'low'` 或 `'high'`。

### Q: 超出预算会怎样？
A: `generate()` 会抛出错误，提示超出每日预算限制。

### Q: 如何添加更多 API？
A: 参考"扩展新 API"章节，继承 `BaseProvider` 并注册。
