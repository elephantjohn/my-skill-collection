"""
基础使用示例
"""

import os
from dotenv import load_dotenv
from image_generator import ImageGenerator

# 加载环境变量
load_dotenv()

# 初始化生成器
generator = ImageGenerator(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_project_id=os.getenv("GOOGLE_PROJECT_ID"),
    seadream_api_key=os.getenv("SEADREAM_API_KEY"),
    max_daily_cost=10.0,
)

# 示例 1: 智能选择 API
print("\n📸 示例 1: 智能选择 API")
result = generator.generate(
    prompt="A beautiful sunset over the ocean, cinematic lighting",
    scenario="cover",
    budget="medium",
)
print(f"使用 API: {result['used_api']}")
print(f"成本：${result['cost']}")
print(f"图片 URL: {result['images'][0]['url']}")

# 示例 2: 指定 API
print("\n📸 示例 2: 指定 API")
result = generator.generate(
    prompt="A cute cat playing with a ball",
    api="imagen-4-fast",
)
print(f"使用 API: {result['used_api']}")
print(f"成本：${result['cost']}")

# 示例 3: 查看成本统计
print("\n📊 示例 3: 成本统计")
stats = generator.get_cost_stats(period="day")
print(f"今日已用：${stats['total_cost']:.4f}")
print(f"剩余预算：${stats['remaining_budget']:.4f}")
print(f"生成数量：{stats['count']} 张")
