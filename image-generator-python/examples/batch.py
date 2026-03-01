"""
批量生成示例
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

# 批量生成配图
prompts = [
    "Morning coffee aesthetic, minimalist style",
    "Cozy reading corner with plants",
    "Minimalist workspace setup",
    "Sunny balcony with flowers",
    "Evening city lights view",
]

print("\n🎨 批量生成配图")
result = generator.batch_generate(
    prompts=prompts,
    scenario="illustration",
    max_cost=5.0,  # 预算上限 $5
)

print(f"成功生成：{result['count']} 张")
print(f"总成本：${result['total_cost']:.4f}")

for i, res in enumerate(result["results"]):
    if "error" in res:
        print(f"❌ 第 {i+1} 张失败：{res['error']}")
    else:
        print(f"✅ 第 {i+1} 张：{res['used_api']} - ${res['cost']:.4f}")
