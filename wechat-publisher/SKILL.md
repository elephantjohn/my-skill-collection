---
name: wechat-publisher
description: >
  微信公众号文章发布技能。
  包含完整的排版规范、HTML 结构、配色方案。
  记录所有踩过的坑和解决方案。
  触发条件：用户要求"发布公众号文章"、"微信排版"等。
---

# 微信公众号发布 Skill

## 📋 排版规范（已验证可用）

### 核心原则
1. **使用内联样式** - 微信不支持 CSS class，必须用 inline style
2. **段落间距** - 两段之间用 `</p><p>` 分隔，行距 `line-height: 2.3`
3. **标题层级** - 故事标题 26px，章节标题 28px
4. **颜色搭配** - 红色主标题，深蓝正文，黄色卡片
5. **HTML 结构** - 先分割段落，再逐个添加样式

---

## 🎨 配色方案

### 主色调
- **红色**：`#c0392b` - 故事标题、重点文字
- **紫色**：`#667eea` → `#764ba2` - 章节标题渐变
- **黄色**：`#f39c12` - 启示卡片边框
- **深蓝**：`#2c3e50` - 正文文字
- **白色**：`#ffffff` - 背景

### 背景色
- **故事标题**：`linear-gradient(135deg,#fdf2f2 0%,#fff5f5 50%,#fdf2f2 100%)`
- **章节标题**：`linear-gradient(135deg,#667eea 0%,#764ba2 100%)`
- **启示卡片**：`linear-gradient(135deg,#fff9e6 0%,#fff 100%)`

---

## 📐 尺寸规范

### 字体大小
- **章节标题**：28px
- **故事标题**：26px
- **正文**：19px
- **重点文字**：20px
- **底部说明**：14px

### 间距
- **段落间距**：`margin: 25px 0`
- **标题间距**：`margin: 50px 0 30px`
- **行距**：`line-height: 2.3`
- **内边距**：`padding: 20px 30px`

---

## 🏗️ HTML 结构

### 完整模板
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:30px 20px;font-family:-apple-system,sans-serif;max-width:640px;margin:0 auto;background:linear-gradient(to bottom,#fafafa,#f5f5f5);">
    
    <!-- 头部标题 -->
    <div style="text-align:center;margin-bottom:40px;padding:30px 20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:15px;color:white;box-shadow:0 8px 25px rgba(102,126,234,0.3);">
        <p style="font-size:14px;letter-spacing:3px;margin-bottom:15px;opacity:0.9;">【系列名】</p>
        <h1 style="font-size:30px;font-weight:bold;margin:20px 0;line-height:1.4;text-shadow:2px 2px 4px rgba(0,0,0,0.2);">1：标题</h1>
        <p style="font-size:16px;opacity:0.9;font-style:italic;">副标题</p>
    </div>
    
    <!-- 配图 1 -->
    <img src="图片 URL" style="width:100%;border-radius:15px;margin:40px 0;box-shadow:0 8px 25px rgba(0,0,0,0.15);border:3px solid #fff;">
    
    <!-- 内容 -->
    <p style="margin:25px 0;text-align:justify;font-size:19px;line-height:2.3;color:#2c3e50;">段落内容</p>
    
    <h2 style="font-size:26px;font-weight:bold;color:#c0392b;margin:50px 0 30px;padding:20px 30px;background:linear-gradient(135deg,#fdf2f2 0%,#fff5f5 50%,#fdf2f2 100%);border-left:6px solid #c0392b;border-radius:12px 0 0 12px;box-shadow:0 4px 15px rgba(192,57,43,0.15);">👑 故事标题</h2>
    
    <h2 style="font-size:28px;font-weight:bold;color:#fff;margin:60px 0 35px;padding:25px 35px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:15px;text-align:center;box-shadow:0 6px 20px rgba(102,126,234,0.3);">【启 示】</h2>
    
    <div style="margin:35px 0;padding:25px 30px;background:linear-gradient(135deg,#fff9e6 0%,#fff 100%);border-radius:15px;border:2px solid #f39c12;box-shadow:0 4px 15px rgba(243,156,18,0.2);font-size:19px;line-height:2.2;">启示内容</div>
    
    <!-- 配图 2 -->
    <img src="图片 URL" style="width:100%;border-radius:15px;margin:40px 0;box-shadow:0 8px 25px rgba(0,0,0,0.15);border:3px solid #fff;">
    
    <!-- 章节结束 -->
    <div style="margin-top:60px;padding:35px 30px;background:linear-gradient(135deg,#f8f9fa 0%,#e9ecef 100%);border-radius:15px;text-align:center;border:2px solid #dee2e6;">
        <p style="font-size:20px;font-weight:bold;color:#c0392b;margin-bottom:15px;">【本章完】</p>
        <p style="color:#7f8c8d;">下一章预告：【系列名】2</p>
    </div>
    
    <!-- 底部分割线 -->
    <hr style="border:none;border-top:2px solid #e0e0e0;margin:50px 0;">
    
    <!-- 底部说明 -->
    <p style="color:#999;font-size:14px;text-align:center;">📌 本系列持续更新，欢迎关注</p>
    
</body>
</html>
```

---

## 🔧 内容处理流程

### 步骤 1：分割段落
```python
paragraphs = content_text.split('\n\n')
```

### 步骤 2：标记特殊内容
```python
# 用占位符标记
content = content.replace("👑 故事一：", "👑 故事一：智家选老板¶STORY¶")
content = content.replace("【启示】", "【启 示】¶SECTION¶")
content = content.replace("1. 名分混乱", "1️⃣ 名分混乱¶LESSON¶")
content = content.replace("\n\n", "¶PARA¶")
```

### 步骤 3：转换为 HTML
```python
content = content.replace('¶STORY¶', '</p><h2 style="...">')
content = content.replace('¶PARA¶', '</p><p>')
content = content.replace('¶SECTION¶', '</p><h2 style="...">')
content = content.replace('¶LESSON¶', '</p><div style="...">')

# 添加首尾标签
if not content.startswith('<p>'):
    content = '<p>' + content
if not content.endswith('</p>'):
    content = content + '</p>'
```

---

## ⚠️ 踩过的坑（重要！）

### 坑 1：使用 CSS class
**错误做法：**
```html
<h2 class="story-title">标题</h2>
```
**问题：** 微信不支持 CSS class，样式不生效

**正确做法：**
```html
<h2 style="font-size:26px;font-weight:bold;color:#c0392b;">标题</h2>
```

---

### 坑 2：HTML 标签未闭合
**错误做法：**
```python
content = content.replace('¶STORY¶', '</p><h2 class="story-title">')
# 没有后续闭合标签
```
**问题：** 导致 HTML 结构错乱，文字重复出现

**正确做法：**
```python
# 每个段落都完整闭合
html_parts.append(f'<h2 style="...">标题</h2>')
html_parts.append(f'<p style="...">内容</p>')
```

---

### 坑 3：直接在内容中嵌入 HTML
**错误做法：**
```python
content = content.replace("司马光说：", '<p style="...">司马光说：</p>')
```
**问题：** 导致 HTML 代码泄漏到正文

**正确做法：**
```python
# 先用占位符标记
content = content.replace("司马光说：", "司马光说：¶QUOTE¶")

# 统一转换
content = content.replace('¶QUOTE¶', '</p><p style="...">')
```

---

### 坑 4：段落间距不够
**错误做法：**
```python
content = content.replace("\n\n", "</p><p>")
```
**问题：** 段落之间只有一个换行，太挤

**正确做法：**
```python
content = content.replace("\n\n", "</p><p><br><br>")
# 或使用 margin 控制
<p style="margin:25px 0;">
```

---

### 坑 5：正文颜色太浅
**错误做法：**
```html
<p style="color:#bdc3c7;">正文</p>
```
**问题：** 浅灰色在手机上看不清

**正确做法：**
```html
<p style="color:#000000;">正文</p>
<!-- 或深蓝色 -->
<p style="color:#2c3e50;">正文</p>
```

---

### 坑 6：未移除星号
**错误做法：**
```python
# 直接处理内容
```
**问题：** 原文中的 `*` 会显示在正文中

**正确做法：**
```python
content = content.replace("*", "")
```

---

## ✅ 验证清单

发布前检查：
- [ ] 所有样式都是 inline（内联）
- [ ] HTML 标签正确闭合
- [ ] 段落间距足够（25px 或两个换行）
- [ ] 正文颜色够深（黑色或深蓝）
- [ ] 已移除所有星号 `*`
- [ ] 标题层级清晰（26px/28px）
- [ ] 配图已上传并替换 URL
- [ ] 封面图已上传

---

## 📝 使用示例

```python
from wechat_publisher import WechatPublisher

publisher = WechatPublisher()

# 发布文章
publisher.publish(
    title="【资治通鉴】1：智伯是怎么作死的——三家分晋",
    content=content_text,
    images=["图片 1 路径", "图片 2 路径"],
    category="历史趣闻"
)
```

---

## 🎯 核心要点总结

1. **必须用内联样式** - 微信不支持 CSS class
2. **先分割后转换** - 不要直接在内容里嵌 HTML
3. **占位符最安全** - 用 ¶XXX¶ 标记，统一转换
4. **标签要闭合** - 每个 `<p>` 都要有 `</p>`
5. **颜色要够深** - 正文用黑色或深蓝
6. **间距要足够** - margin 25px 或两个换行
7. **移除星号** - 内容中的 `*` 要删除

---

## 💡 最佳实践

### 推荐的 HTML 生成方式
```python
# 1. 分割段落
paragraphs = content_text.split('\n\n')

# 2. 逐个处理
html_parts = []
for para in paragraphs:
    if para.startswith('👑 故事'):
        html_parts.append(f'<h2 style="...">{para}</h2>')
    elif para.startswith('【启示】'):
        html_parts.append(f'<h2 style="...">{para}</h2>')
    else:
        para = para.replace('*', '')
        html_parts.append(f'<p style="...">{para}</p>')

# 3. 拼接
content_html = '\n'.join(html_parts)
```

### 不推荐的方式
```python
# ❌ 直接在内容里替换
content = content.replace("故事", '<h2>故事</h2>')

# ❌ 使用 CSS class
content = content.replace("故事", '<h2 class="title">故事</h2>')

# ❌ 不闭合标签
content = content.replace("故事", '<h2>故事')
```

---

## 📚 相关文件

- **发布脚本**：`/home/ubuntu/.openclaw/workspace-wechat_creater/wechat_pub/publish_fixed.py`
- **深色主题**：`/home/ubuntu/.openclaw/workspace-wechat_creater/wechat_pub/publish_dark_theme.py`
- **排版规范**：本文档

---

## 🚀 快速开始

1. 复制 `publish_fixed.py` 脚本
2. 修改文章内容和标题
3. 运行脚本发布
4. 登录微信后台查看

**记住：用内联样式！用内联样式！用内联样式！**
