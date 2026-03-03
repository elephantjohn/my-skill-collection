---
name: wechat-zizhitongjian-publisher
description: >
  资治通鉴系列文章发布技能。
  从 Google Sheet 读取内容，使用固定模板排版，
  生成配图并发布到微信草稿箱。
  触发条件：用户要求"发布资治通鉴"、"资治通鉴第 X 章"等。
---

# 资治通鉴发布 Skill

## 核心功能

1. **从 Google Sheet 读取内容** - 自动获取章节内容
2. **使用已验证模板** - 白色背景，统一风格
3. **Gemini 生成配图** - 每章 2 张历史场景图
4. **自动发布到微信** - 草稿箱

## 使用方式

```python
from wechat_zizhitongjian_publisher import ZizhitongjianPublisher

publisher = ZizhitongjianPublisher()

# 发布指定章节
publisher.publish_chapter(
    chapter=1,  # 第几章
    google_sheet_url="https://docs.google.com/spreadsheets/d/..."
)

# 或者使用已配置的 URL
publisher.publish_chapter(chapter=2)
```

## 配置要求

### 环境变量
```bash
# 微信公众号
WECHAT_APPID=你的 AppID
WECHAT_SECRET=你的 Secret

# Gemini（配图生成）
GEMINI3PRO_API_KEY=你的 API Key
```

### Google Sheet 配置
表格需要包含以下列：
- **序号** - 章节号（1, 2, 3...）
- **标题** - 章节标题（如"三家分晋"）
- **内容** - 通俗版故事内容
- **状态** - 已审核/未审核

## 排版规范

### 白色背景模板（已验证）
- **正文颜色**：黑色 `#000000`
- **标题颜色**：红色 `#c0392b`
- **段落间距**：30px
- **行距**：2.4
- **字体大小**：18px

### 标题样式
```html
<h2 style="font-size:24px;color:#c0392b;background:...;border-left:5px solid #c0392b;">
  标题文字
</h2>
```

### 段落样式
```html
<p style="margin:30px 0;line-height:2.4;color:#000000;">
  段落内容
</p>
```

## 配图规范

### 风格要求
- **历史场景** - 符合时代背景
- **工笔画/水墨画** - 中国传统风格
- **高质量** - 800x450 像素

### 提示词模板
```
【中国古代场景】朝代 + 场景描述 + 人物活动 + 建筑风格 + 绘画风格，高质量
```

**示例：**
- 第 1 章：战国时期，魏文侯与李克讨论选相，古代君臣对话
- 第 2 章：三国时期，战场厮杀，古代军队布阵

## 发布流程

```
1. 读取 Google Sheet → 2. 生成配图 → 3. 生成 HTML 
→ 4. 上传图片 → 5. 发布到微信 → 6. 返回媒体 ID
```

## 注意事项

1. **内容隔离** - 与温情文章完全独立
2. **模板统一** - 每章使用相同模板
3. **章节编号** - 自动递增（1, 2, 3...）
4. **配图复用** - 如已生成可复用

## 错误处理

- **Google Sheet 读取失败** - 返回错误信息
- **配图生成失败** - 使用占位图
- **微信发布失败** - 返回错误详情

## 日志记录

每次发布记录：
- 章节号
- 发布时间
- 媒体 ID
- 配图路径
- 发布状态

## 与其他技能配合

### 百度审核
```python
from segmented_censor import censor_article_content

is_ok, _ = censor_article_content(content)
if is_ok:
    publisher.publish_chapter(...)
```

### 定时任务
```python
# cron 定时调用
publisher.auto_publish_next_chapter()
```

## 文件结构

```
wechat-zizhitongjian-publisher/
├── SKILL.md
├── scripts/
│   └── zizhitongjian_publisher.py
└── examples/
    └── usage.py
```

## 成本说明

- **Gemini 配图** - 每章 2 张
- **微信发布** - 免费
- **Google Sheet** - 免费

## 最佳实践

1. **提前准备内容** - Google Sheet 提前填写
2. **检查配图质量** - 手动审核生成的图片
3. **统一标题格式** - 【资治通鉴】数字：标题
4. **记录发布历史** - 避免重复发布
