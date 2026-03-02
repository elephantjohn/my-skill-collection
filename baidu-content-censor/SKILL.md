---
name: baidu-content-censor
description: >
  百度文本内容审核 + 自动修正 skill。
  调用百度内容审核平台 API（user_defined 策略）对中文文本做合规检查，
  若不合规则自动调用 ernie-4.5-turbo-128k 做最小化改写，最多循环指定次数直至合规。
  适用于：小说内容审核、用户生成内容（UGC）过滤、任何需要合规自动修正的文本处理场景。
  触发条件：用户要求"审核文本"、"内容合规检查"、"百度文字审核"、"自动修正违规内容"。
---

# 百度内容审核 + 自动修正

## 官方文档

- **产品名称**: 百度内容审核平台
- **文档地址**: https://cloud.baidu.com/doc/ANTIPORN/s/Rk3h6xb3i
- **API 端点**: https://aip.baidubce.com/rest/2.0/solution/v1/content_censor/v2/user_defined
- **需要充值**: 是（百度智能云账户需要充值才能使用）

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `TEXT_API_KEY` | 是 | 百度内容审核 API Key（从应用管理获取） |
| `TEXT_SECRET_KEY` | 是 | 百度内容审核 Secret Key（从应用管理获取） |
| `BAIDU_API_KEY` | 仅 --fix 时必填 | 千帆 API Key / Bearer Token（用于 ernie-4.5-turbo-128k 修正） |

## 获取 API Key 步骤

1. 登录百度智能云：https://cloud.baidu.com
2. 进入内容审核平台：https://console.bce.baidu.com/contentreview/
3. 点击"应用管理"或右上角应用名称
4. 创建新应用或查看现有应用
5. 复制 `API Key` 和 `Secret Key`
6. **重要**: 账户需要充值才能使用 API

## 脚本使用

主脚本：`scripts/censor.py`（仅依赖标准库 + `requests`，无需其他第三方包）。

### 仅审核（不自动修正）

```bash
python censor.py chapter.txt
python censor.py --text "待审核文本内容"
```

### 审核 + 自动修正（循环最多3次）

```bash
python censor.py chapter.txt --fix
python censor.py chapter.txt --fix --max-retries 5 --output fixed.txt
```

退出码：`0` = 合规，`1` = 未通过。

## 编程接口

```python
from censor import CensorManager

mgr = CensorManager(
    censor_api_key=os.getenv("TEXT_API_KEY"),
    censor_secret_key=os.getenv("TEXT_SECRET_KEY"),
    ernie_api_key=os.getenv("BAIDU_API_KEY"),   # 可选，不传则禁用自动修正
    logs_dir=Path("logs/censor"),               # 可选，保存审核/修正日志
)

# 审核 + 自动修正循环
is_ok, final_text = mgr.censor_and_fix_loop(
    text=chapter_text,
    item_id=chapter_num,   # 任意整数，用于日志命名
    max_retries=3,
)

# 仅审核一次（不修正）
is_ok, violations = mgr.censor_once(text, item_id=0)
# violations: [{"type": ..., "msg": ..., "hits": [...]}]
```

## 工作流程

```
输入文本
  → censor_once()  调用百度审核 API
      conclusionType: 1=合规 2=不合规 3=疑似 4=失败
  → 合规 → 返回 (True, text)
  → 不合规 → 提取 violations (type/msg/hits)
      → fix_violations()  ernie-4.5-turbo-128k 最小化改写 (temperature=0.3)
      → 循环，直至合规或达 max_retries
  → 超过重试 → 返回 (False, 最后文本)
```

## 嵌入现有项目

将 `scripts/censor.py` 复制到目标项目，按需导入 `CensorManager`。
类包含：`BaiduTextCensor`（审核）、`BaiduErnieClient`（修正）、`CensorManager`（主控）。
所有类均可独立使用，无循环依赖。
