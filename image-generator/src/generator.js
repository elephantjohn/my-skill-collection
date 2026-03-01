/**
 * 通用图片生成器
 * 智能选择最优 API，支持多个后端
 */

const { ImageSelector } = require('./selector');
const { ImagenProvider } = require('./providers/imagen');
const { SeaDreamProvider } = require('./providers/seadream');
const { CostTracker } = require('./utils/cost');

class ImageGenerator {
  constructor(config = {}) {
    this.config = {
      googleApiKey: config.googleApiKey || process.env.GOOGLE_API_KEY,
      googleProjectId: config.googleProjectId || process.env.GOOGLE_PROJECT_ID,
      googleLocation: config.googleLocation || 'us-central1',
      seaDreamApiKey: config.seaDreamApiKey || process.env.SEADREAM_API_KEY,
      defaultApi: config.defaultApi || 'auto',
      budgetMode: config.budgetMode || 'medium', // low|medium|high
      maxDailyCost: config.maxDailyCost || 10.0,
    };

    // 初始化提供商
    this.providers = {
      'imagen-4-fast': new ImagenProvider({ ...this.config, version: '4-fast' }),
      'imagen-4': new ImagenProvider({ ...this.config, version: '4' }),
      'imagen-4-ultra': new ImagenProvider({ ...this.config, version: '4-ultra' }),
      'seadream-v1': new SeaDreamProvider({ ...this.config, version: 'v1' }),
      'seadream-v2': new SeaDreamProvider({ ...this.config, version: 'v2' }),
    };

    // 初始化选择器和成本追踪
    this.selector = new ImageSelector(this.config);
    this.costTracker = new CostTracker(this.config.maxDailyCost);

    // 场景配置
    this.scenarios = {
      cover: {
        priority: 'quality',
        minResolution: '2K',
        preferredApis: ['imagen-4-ultra', 'seadream-v2', 'imagen-4'],
      },
      product: {
        priority: 'accuracy',
        textRendering: true,
        preferredApis: ['imagen-4-ultra', 'imagen-4', 'imagen-4-fast'],
      },
      illustration: {
        priority: 'artistic',
        preferredApis: ['seadream-v2', 'seadream-v1', 'imagen-4-ultra'],
      },
      text: {
        priority: 'text_accuracy',
        textRendering: true,
        preferredApis: ['imagen-4-ultra', 'imagen-4'],
      },
      general: {
        priority: 'balance',
        preferredApis: ['imagen-4', 'imagen-4-fast', 'seadream-v2'],
      },
    };
  }

  /**
   * 生成单张图片（智能选择 API）
   */
  async generate(options) {
    const {
      prompt,
      scenario = 'general',
      api = this.config.defaultApi,
      budget = this.config.budgetMode,
      negativePrompt,
      resolution = '1024x1024',
      count = 1,
    } = options;

    // 检查预算
    if (!this.costTracker.canSpend(this._estimateCost(api, count))) {
      throw new Error('超出每日预算限制');
    }

    // 智能选择 API
    const selectedApi = api === 'auto' 
      ? this._selectBestApi(prompt, scenario, budget)
      : api;

    console.log(`🎨 选择 API: ${selectedApi} (场景：${scenario})`);

    // 生成图片
    const provider = this.providers[selectedApi];
    if (!provider) {
      throw new Error(`不支持的 API: ${selectedApi}`);
    }

    const result = await provider.generate(prompt, {
      negativePrompt,
      resolution,
      count,
    });

    // 记录成本
    this.costTracker.record(selectedApi, result.cost);

    return {
      ...result,
      usedApi: selectedApi,
      scenario,
    };
  }

  /**
   * 批量生成
   */
  async batchGenerate(options) {
    const { prompts, scenario = 'general', maxCost = 10.0 } = options;
    
    const results = [];
    let totalCost = 0;

    for (const prompt of prompts) {
      const estimate = this._estimateCost('auto', 1);
      if (totalCost + estimate > maxCost) {
        console.log(`⚠️ 达到预算上限，剩余 ${prompts.length - results.length} 个未生成`);
        break;
      }

      try {
        const result = await this.generate({ prompt, scenario });
        results.push(result);
        totalCost += result.cost;
      } catch (error) {
        console.error(`❌ 生成失败：${prompt}`, error.message);
        results.push({ error: error.message, prompt });
      }
    }

    return {
      results,
      totalCost,
      count: results.length,
    };
  }

  /**
   * 智能选择最佳 API
   */
  _selectBestApi(prompt, scenario, budget) {
    const scenarioConfig = this.scenarios[scenario] || this.scenarios.general;
    
    // 使用选择器评分
    const scores = this.selector.score({
      prompt,
      scenario: scenarioConfig,
      budget,
      availableApis: Object.keys(this.providers),
    });

    // 返回最高分的 API
    const bestApi = Object.entries(scores)
      .sort(([, a], [, b]) => b - a)[0]?.[0];

    console.log(`📊 API 评分：${JSON.stringify(scores, null, 2)}`);

    return bestApi || 'imagen-4-fast';
  }

  /**
   * 估算成本
   */
  _estimateCost(api, count) {
    const pricing = {
      'imagen-4-fast': 0.02,
      'imagen-4': 0.04,
      'imagen-4-ultra': 0.06,
      'seadream-v1': 0.01,
      'seadream-v2': 0.03,
    };
    return (pricing[api] || 0.04) * count;
  }

  /**
   * 获取成本统计
   */
  getCostStats(options = {}) {
    return this.costTracker.getStats(options);
  }

  /**
   * 获取支持的 API 列表
   */
  getSupportedApis() {
    return Object.keys(this.providers).map(api => ({
      name: api,
      pricing: this._estimateCost(api, 1),
      capabilities: this.providers[api].capabilities,
    }));
  }
}

module.exports = { ImageGenerator };
