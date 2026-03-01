---
name: zizhi-tongjian
description: 资治通鉴现代语言讲解，一集一集输出，存储到 Google Sheets
user-invocable: true
disable-model-invocation: false
metadata:
  openclaw:
    emoji: "📜"
    os: [darwin, linux, win32]
    requires:
      bins: [python3, curl]
---

# 资治通鉴讲解 Bot

将资治通鉴用通俗易懂的现代语言讲解，按卷顺序生成，保存在 Google Sheets 中。

## 目标

- 按顺序生成每一卷的现代语言译文
- 保持原文原意，语言风趣有文化
- 将原文、译文、启示存储到 Google Sheets
- 记录进度，可继续、可跳转

## 核心流程

### 1. 获取原文

资治通鉴原文从以下来源获取：
- 搜索相关卷的内容
- 提取关键段落

### 2. 生成译文（使用 Gemini 3 Flash）

调用 Gemini 3 Flash 将原文翻译为现代白话文，要求：
- 通俗易懂
- 保留原意
- 语言风趣有文化
- 不偏离原文

### 3. 存储到 Google Sheets

写入内容：
- 集数
- 卷号
- 标题
- 原文选段
- 译文
- 启示
- 生成时间

### 4. 状态管理

- 本地记录当前集数
- 可查询进度
- 支持"继续"和指定集数

## Google Sheets 结构

表头：
```
A: 集数 | B: 卷号 | C: 标题 | D: 原文 | E: 译文 | F: 启示 | G: 生成时间
```

## 触发方式

用户说以下关键词时触发：
- "讲资治通鉴" / "开始讲"
- "继续" / "下一集"
- "第X集" / "我要看XX"
- "进度" / "现在讲到哪了"

## 注意事项

- 翻译模型固定使用 Gemini 3 Flash
- 原文必须从公共来源获取，尊重版权
- 每生成一集后更新本地进度