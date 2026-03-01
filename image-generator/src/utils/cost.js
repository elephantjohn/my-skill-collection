/**
 * 成本追踪器
 * 记录和统计 API 使用成本
 */

class CostTracker {
  constructor(maxDailyCost = 10.0) {
    this.maxDailyCost = maxDailyCost;
    this.records = [];
    this.dailyLimit = maxDailyCost;
  }

  /**
   * 记录一次使用
   */
  record(api, cost, metadata = {}) {
    const record = {
      timestamp: Date.now(),
      date: new Date().toISOString().split('T')[0],
      api,
      cost,
      ...metadata,
    };

    this.records.push(record);
    
    console.log(`💰 记录成本：$${cost.toFixed(4)} (${api})`);
  }

  /**
   * 检查是否可以支出
   */
  canSpend(estimatedCost) {
    const today = new Date().toISOString().split('T')[0];
    const todayCost = this.records
      .filter(r => r.date === today)
      .reduce((sum, r) => sum + r.cost, 0);

    return todayCost + estimatedCost <= this.dailyLimit;
  }

  /**
   * 获取今日已用成本
   */
  getTodayCost() {
    const today = new Date().toISOString().split('T')[0];
    return this.records
      .filter(r => r.date === today)
      .reduce((sum, r) => sum + r.cost, 0);
  }

  /**
   * 获取统计信息
   */
  getStats(options = {}) {
    const { period = 'day', api = 'all' } = options;
    const now = new Date();
    
    let filtered = this.records;

    // 按 API 筛选
    if (api !== 'all') {
      filtered = filtered.filter(r => r.api === api);
    }

    // 按时间筛选
    if (period === 'day') {
      const today = now.toISOString().split('T')[0];
      filtered = filtered.filter(r => r.date === today);
    } else if (period === 'week') {
      const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(r => new Date(r.timestamp) >= weekAgo);
    } else if (period === 'month') {
      const monthAgo = new Date(now - 30 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(r => new Date(r.timestamp) >= monthAgo);
    }

    const totalCost = filtered.reduce((sum, r) => sum + r.cost, 0);
    const count = filtered.length;

    // 按 API 分组
    const byApi = {};
    for (const record of filtered) {
      if (!byApi[record.api]) {
        byApi[record.api] = { cost: 0, count: 0 };
      }
      byApi[record.api].cost += record.cost;
      byApi[record.api].count++;
    }

    return {
      period,
      totalCost,
      count,
      avgCost: count > 0 ? totalCost / count : 0,
      byApi,
      remainingBudget: this.dailyLimit - this.getTodayCost(),
    };
  }

  /**
   * 重置记录
   */
  reset() {
    this.records = [];
  }

  /**
   * 导出记录（用于持久化）
   */
  export() {
    return JSON.stringify(this.records);
  }

  /**
   * 导入记录（从持久化恢复）
   */
  import(json) {
    try {
      this.records = JSON.parse(json);
    } catch (error) {
      console.error('导入记录失败:', error);
    }
  }
}

module.exports = { CostTracker };
