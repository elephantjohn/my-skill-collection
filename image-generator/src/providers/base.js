/**
 * 图片生成器基础类
 * 所有提供商必须继承此类
 */

class BaseProvider {
  constructor(config) {
    if (new.target === BaseProvider) {
      throw new Error('BaseProvider 是抽象类，不能直接实例化');
    }
    this.config = config;
    this.name = 'base';
    this.pricing = { perImage: 0 };
    this.capabilities = [];
  }

  /**
   * 生成图片（必须由子类实现）
   */
  async generate(prompt, options) {
    throw new Error('子类必须实现 generate 方法');
  }

  /**
   * 获取提供商信息
   */
  getInfo() {
    return {
      name: this.name,
      pricing: this.pricing,
      capabilities: this.capabilities,
    };
  }

  /**
   * 验证配置
   */
  validateConfig() {
    throw new Error('子类必须实现 validateConfig 方法');
  }
}

module.exports = { BaseProvider };
