"""
高级用法示例
"""

import os
from dotenv import load_dotenv
from image_generator import ImageGenerator, ImageSelector

# 加载环境变量
load_dotenv()

# ==================== 示例 1: 获取 API 推荐 ====================
print("\n🎯 示例 1: 获取 API 推荐")

selector = ImageSelector({})

recommendation = selector.recommend({
    "prompt": "Product photo with 'SALE 50% OFF' text overlay",
    "scenario": {
        "priority": "text_accuracy",
        "text_rendering": True,
    },
    "budget": "medium",
    "available_apis": ["imagen-4-fast", "imagen-4", "seadream-v2"],
})

print(f"推荐 API: {recommendation['api']}")
print(f"评分：{recommendation['score']:.2f}")
print(f"原因：{', '.join(recommendation['reasons'])}")
print(f"备选：{recommendation['alternative']}")

# ==================== 示例 2: 小红书封面生成 ====================
print("\n📸 示例 2: 小红书封面生成")

generator = ImageGenerator(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_project_id=os.getenv("GOOGLE_PROJECT_ID"),
    seadream_api_key=os.getenv("SEADREAM_API_KEY"),
)

result = generator.generate(
    prompt="小红书封面，极简风格，莫兰迪色系，留白空间",
    scenario="cover",
    budget="medium",
    resolution="1242x1660",  # 小红书竖屏比例 3:4
)

print(f"使用 API: {result['used_api']}")
print(f"成本：${result['cost']}")
print(f"分辨率：{result['metadata']['resolution']}")

# ==================== 示例 3: 获取支持的 API 列表 ====================
print("\n📋 示例 3: 支持的 API 列表")

apis = generator.get_supported_apis()
for api in apis:
    print(f"- {api['name']}: ${api['pricing']}/张 - {', '.join(api['capabilities'])}")

# ==================== 示例 4: 成本统计与导出 ====================
print("\n💰 示例 4: 成本统计")

stats = generator.get_cost_stats(period="day")
print(f"今日统计:")
print(f"  总成本：${stats['total_cost']:.4f}")
print(f"  生成数量：{stats['count']} 张")
print(f"  平均成本：${stats['avg_cost']:.4f}/张")
print(f"  剩余预算：${stats['remaining_budget']:.4f}")

print(f"\n各 API 使用:")
for api_name, data in stats["by_api"].items():
    print(f"  - {api_name}: ${data['cost']:.4f} ({data['count']} 张)")

# 导出记录（用于持久化）
exported = generator.cost_tracker.export()
print(f"\n导出记录：{len(exported)} 字节")
