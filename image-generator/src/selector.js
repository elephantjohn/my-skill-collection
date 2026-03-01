/**
 * API 选择器
 * 根据场景、预算、需求智能评分各 API
 */

class ImageSelector {
  constructor(config) {
    this.config = config;
    
    // API 基础评分（1-5 分）
    this.apiRatings = {
      'imagen-4-fast': { quality: 3.5, speed: 5, cost: 5, text: 4, art: 3 },
      'imagen-4': { quality: 4, speed: 4, cost: 4, text: 4.5, art: 3.5 },
      'imagen-4-ultra': { quality: 5, speed: 3, cost: 3, text: 5, art: 4 },
      'seadream-v1': { quality: 3, speed: 5, cost: 5, text: 2, art: 5 },
      'seadream-v2': { quality: 4.5, speed: 4, cost: 4, text: 2.5, art: 5 },
    };
  }

  /**
   * 为每个 API 评分
   */
  score(options) {
    const { prompt, scenario, budget, availableApis } = options;
    const scores = {};

    for (const api of availableApis) {
      const rating = this.apiRatings[api];
      if (!rating) continue;

      let score = 0;

      // 1. 场景权重
      score += this._scoreByScenario(rating, scenario);

      // 2. 预算权重
      score += this._scoreByBudget(rating, budget);

      // 3. 提示词分析
      score += this._scoreByPrompt(rating, prompt);

      scores[api] = score;
    }

    return scores;
  }

  /**
   * 按场景评分
   */
  _scoreByScenario(rating, scenario) {
    const { priority, textRendering, preferredApis } = scenario;
    let score = 0;

    // 优先级评分
    if (priority === 'quality') score += rating.quality * 2;
    else if (priority === 'speed') score += rating.speed * 2;
    else if (priority === 'cost') score += rating.cost * 2;
    else if (priority === 'artistic') score += rating.art * 2;
    else if (priority === 'text_accuracy') score += rating.text * 2;
    else score += (rating.quality + rating.speed + rating.cost) / 3;

    // 文字渲染需求
    if (textRendering) score += rating.text * 1.5;

    // 偏好 API 加分
    if (preferredApis) {
      preferredApis.forEach((api, index) => {
        // 第一个偏好加 3 分，第二个加 2 分，依此类推
      });
    }

    return score;
  }

  /**
   * 按预算评分
   */
  _scoreByBudget(rating, budget) {
    if (budget === 'low') return rating.cost * 2;
    if (budget === 'medium') return rating.cost + rating.quality;
    if (budget === 'high') return rating.quality * 2;
    return rating.cost + rating.quality;
  }

  /**
   * 按提示词分析评分
   */
  _scoreByPrompt(rating, prompt) {
    const lowerPrompt = prompt.toLowerCase();
    let score = 0;

    // 检测是否需要文字渲染
    if (/(text|word|letter|title|logo|sign)/.test(lowerPrompt)) {
      score += rating.text * 1.5;
    }

    // 检测艺术风格
    if (/(illustration|anime|art|painting|drawing)/.test(lowerPrompt)) {
      score += rating.art * 1.5;
    }

    // 检测真实感需求
    if (/(realistic|photo|portrait|landscape)/.test(lowerPrompt)) {
      score += rating.quality * 1.5;
    }

    return score;
  }

  /**
   * 推荐 API（带原因）
   */
  recommend(options) {
    const scores = this.score(options);
    const sorted = Object.entries(scores).sort(([, a], [, b]) => b - a);
    
    const [bestApi, bestScore] = sorted[0];
    const [secondApi, secondScore] = sorted[1] || [];

    const reasons = this._getRecommendationReasons(bestApi, options);

    return {
      api: bestApi,
      score: bestScore,
      reasons,
      alternative: secondApi,
      allScores: scores,
    };
  }

  /**
   * 获取推荐原因
   */
  _getRecommendationReasons(api, options) {
    const { scenario, budget } = options;
    const rating = this.apiRatings[api];
    const reasons = [];

    if (scenario.priority === 'quality' && rating.quality >= 4) {
      reasons.push('高质量输出');
    }
    if (scenario.priority === 'artistic' && rating.art >= 4) {
      reasons.push('艺术风格优秀');
    }
    if (scenario.textRendering && rating.text >= 4) {
      reasons.push('文字渲染准确');
    }
    if (budget === 'low' && rating.cost >= 4) {
      reasons.push('成本低');
    }
    if (rating.speed >= 4) {
      reasons.push('生成速度快');
    }

    return reasons;
  }
}

module.exports = { ImageSelector };
