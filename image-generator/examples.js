/**
 * 使用示例
 */

const { ImageGenerator } = require('./src/generator');

// 初始化
const generator = new ImageGenerator({
  googleApiKey: process.env.GOOGLE_API_KEY,
  googleProjectId: process.env.GOOGLE_PROJECT_ID,
  seaDreamApiKey: process.env.SEADREAM_API_KEY,
  maxDailyCost: 10.0,
});

// 示例 1: 智能选择 API（推荐）
async function example1() {
  const result = await generator.generate({
    prompt: 'A beautiful sunset over the ocean, cinematic lighting',
    scenario: 'cover', // 封面图
    budget: 'medium',
  });

  console.log('生成结果:', result);
  // 输出：使用了哪个 API、成本多少
}

// 示例 2: 指定 API
async function example2() {
  const result = await generator.generate({
    prompt: 'A cute cat playing with a ball',
    api: 'imagen-4-fast', // 强制使用 Imagen 4 Fast
  });

  console.log('生成结果:', result);
}

// 示例 3: 批量生成
async function example3() {
  const prompts = [
    'Morning coffee aesthetic',
    'Workspace setup minimal',
    'Plant corner cozy',
  ];

  const result = await generator.batchGenerate({
    prompts,
    scenario: 'illustration',
    maxCost: 5.0, // 预算上限
  });

  console.log('批量生成:', result);
  console.log('总成本:', result.totalCost);
}

// 示例 4: 查看成本统计
async function example4() {
  const stats = generator.getCostStats({
    period: 'day', // day|week|month
  });

  console.log('成本统计:', stats);
  // 输出：今日花费、剩余预算、各 API 使用情况
}

// 示例 5: 获取 API 推荐
async function example5() {
  const { ImageSelector } = require('./src/selector');
  const selector = new ImageSelector({});

  const recommendation = selector.recommend({
    prompt: 'Product photo with text overlay',
    scenario: {
      priority: 'text_accuracy',
      textRendering: true,
    },
    budget: 'medium',
    availableApis: ['imagen-4-fast', 'imagen-4', 'seadream-v2'],
  });

  console.log('推荐 API:', recommendation.api);
  console.log('原因:', recommendation.reasons);
}

// 运行示例
(async () => {
  await example1();
  // await example2();
  // await example3();
  // await example4();
  // await example5();
})();
