---
name: wechat-history-writer
description: >
  微信公众号历史趣闻类文章写作技能。
  学习当年明月、马伯庸、六神磊磊的写作风格，
  生成有趣且真实的历史故事文章。
  触发条件：用户要求"写历史文章"、"历史趣闻"、"历史故事"等。
---

# 微信公众号历史趣闻写作 Skill

## 风格定位

**学习对象：**
- 当年明月（《明朝那些事儿》）- 幽默风趣讲历史
- 马伯庸（历史悬疑）- 细节考据 + 故事性
- 六神磊磊（金庸 + 历史）- 有梗有料

**核心特点：**
- ✅ 有趣：幽默风趣，不枯燥
- ✅ 真实：尊重史实，有据可查
- ✅ 通俗：通俗易懂，不卖弄
- ✅ 有料：有梗有料，引发思考

## 标题风格

### 1. 悬念式
- "你可能不知道，XXX 其实..."
- "历史上最 XXX 的皇帝，竟然是..."
- "XXX 的背后，藏着一个秘密"

### 2. 反差式
- "被误解千年的 XXX"
- "XXX 的另一面：和你想的不一样"
- "正史里的 XXX，颠覆你的认知"

### 3. 真相式
- "历史上的 XXX：真相是..."
- "XXX 的真实面貌：史料里的记载"
- "揭开 XXX 的历史真相"

### 4. 趣味式
- "如果 XXX 有朋友圈"
- "XXX 的日常：比现代人还..."
- "XXX 的 XXX：古代人的智慧"

## 文章结构

```
【开头】悬念引入（100-150 字）
- 颠覆认知的观点
- 引发好奇心的问题
- 简洁有力的金句

【正文】4-5 个部分（每部分 400-500 字）
1. 历史背景介绍（简洁明了）
2. 有趣的故事细节（生动具体）
3. 历史真相揭秘（有据可查）
4. 人物性格分析（立体饱满）
5. 现代启示思考（引发共鸣）

【结尾】历史智慧（150-200 字）
- 总结历史教训
- 联系现实生活
- 留下思考空间
```

## 语言特色

### ✅ 推荐的表达
- "你可能不知道..."
- "有趣的是..."
- "史料记载..."
- "说白了就是..."
- "用现在的话说..."
- "这操作，绝了..."

### ❌ 避免的表达
- 过度煽情（温情风格）
- 空洞抒情（没有史料）
- 说教口吻（居高临下）
- 戏说过度（违背史实）

## 选题方向

### 1. 历史人物
- 帝王将相的另一面
- 文人墨客的趣事
- 被误解的历史人物

### 2. 历史事件
- 改变历史的关键时刻
- 历史事件的幕后
- 被忽略的历史细节

### 3. 古代生活
- 古人的日常生活
- 古代的衣食住行
- 古人的娱乐方式

### 4. 历史冷知识
- 颠覆认知的真相
- 有趣的历史巧合
- 历史上的今天

## 编程接口

```python
from wechat_history_writer import WechatHistoryWriter

writer = WechatHistoryWriter()

# 生成历史文章
article = writer.write(
    topic="曹操的真实面貌",
    style="humorous",  # humorous/suspense/truth
    word_count=3000
)

# 生成标题
titles = writer.generate_titles(
    topic="苏轼的吃货人生",
    count=10,
    style="contrast"  # suspense/contrast/truth/fun
)

# 生成金句
quotes = writer.generate_quotes(
    theme="历史智慧",
    count=5
)
```

## 史料来源

**推荐来源：**
- 二十四史（正史）
- 资治通鉴（编年体）
- 各朝实录（官方记录）
- 名人笔记（私人记录）
- 考古发现（实物证据）

**使用原则：**
1. 优先使用正史记载
2. 多方印证（孤证不立）
3. 注明史料来源
4. 区分史实与推测

## 与其他技能集成

### 与 wechat_pub 集成

```python
# 在 content_automation_engine.py 中
from wechat_history_writer import WechatHistoryWriter

writer = WechatHistoryWriter()
article = writer.write(
    topic=selected_topic,
    category="历史趣闻",
    style="humorous"
)
```

### 与 segmented_censor 配合

```python
# 生成文章 → 审核内容 → 发布
article = writer.write(topic)
is_ok, _ = censor_article_content(article)
if is_ok:
    publish_to_wechat()
```

## 文件结构

```
wechat-history-writer/
├── SKILL.md
├── scripts/
│   └── wechat_history_writer.py
└── examples/
    └── sample_articles.md
```

## 注意事项

1. **尊重史实** - 不编造、不歪曲历史
2. **通俗易懂** - 用现代语言讲古代故事
3. **有趣有料** - 有梗有料，不枯燥
4. **有据可查** - 重要观点注明史料来源
5. **避免戏说** - 幽默但不恶搞

## 成本说明

- 纯文本生成，无额外 API 调用
- 使用现有 LLM 即可
- 建议设置每日生成上限
