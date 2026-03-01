---
name: wechat-emotional-writer
description: >
  微信公众号温情类爆款文章写作技能。
  学习并模仿公众号温情领域的爆款文章风格，
  生成高阅读量、高转发率的情感文案。
  触发条件：用户要求"写温情文章"、"公众号爆款文案"、"情感文"等。
---

# 微信公众号温情类爆款写作 Skill

## 风格特点

基于对 10 万 + 爆款文章的分析，总结以下特点：

### 1. 标题风格
- **情绪化**：直接表达情感，如"哭了"、"心疼"、"泪目"
- **场景化**：具体场景描述，如"高铁上"、"医院里"、"深夜"
- **数字对比**：如"7 天"vs"358 天"，"2.9 亿人"
- **悬念式**：引发好奇心，如"那一刻，我明白了"

### 2. 开头技巧
- **场景切入**：直接描述具体场景，让读者身临其境
- **细节描写**：用感官细节（视觉、听觉、触觉）营造氛围
- **情绪铺垫**：快速建立情感基调
- **金句点题**：第一段就抛出核心观点

### 3. 正文结构
- **短段落**：每段 2-4 句，便于手机阅读
- **对话穿插**：增加真实感和代入感
- **细节放大**：把小细节写成情感爆发点
- **节奏控制**：张弛有度，有铺垫有高潮

### 4. 语言特色
- **口语化**：像朋友聊天，不用书面语
- **第二人称**：常用"你"，增强代入感
- **排比句**：增强节奏感和感染力
- **对比手法**：过去 vs 现在，理想 vs 现实

### 5. 情感爆发点
- **亲情类**：父母的爱、离别的不舍、成长的愧疚
- **爱情类**：错过的遗憾、陪伴的温暖、等待的坚持
- **友情类**：散场的无奈、重逢的惊喜、默默的支持
- **成长类**：孤独的奋斗、梦想的坚持、自我的和解

### 6. 结尾技巧
- **金句收尾**：一句让人记住的话
- **情感升华**：从个人经历上升到普世价值
- **互动引导**：引发读者评论和转发
- **留白余韵**：不说满，让读者自己体会

## 编程接口

```python
from wechat_emotional_writer import WechatEmotionalWriter

writer = WechatEmotionalWriter()

# 生成温情文章
article = writer.write(
    topic="年后离别",
    category="亲情",
    style="温情治愈",
    word_count=3000
)

# 生成标题
titles = writer.generate_titles(
    topic="父母送别",
    count=10,
    style="情绪化"
)

# 生成金句
quotes = writer.generate_quotes(
    theme="成长与离别",
    count=5
)
```

## 使用示例

### 基础写作

```python
from wechat_emotional_writer import WechatEmotionalWriter

writer = WechatEmotionalWriter()

article = writer.write(
    topic="年过完了，离开老家的那一刻",
    category="亲情",
    style="温情治愈"
)
```

### 标题生成

```python
titles = writer.generate_titles(
    topic="父母送别",
    count=10,
    style="情绪化"  # 情绪化/场景化/数字对比/悬念式
)

# 输出示例：
# 1. "年过完了，我在高铁上哭了：成年人的告别，连眼泪都要忍住"
# 2. "后备箱塞满的那一刻，我才知道什么叫舍不得"
# 3. "过年 7 天，想家 358 天：每个游子的真实写照"
```

### 金句生成

```python
quotes = writer.generate_quotes(
    theme="成长与离别",
    count=5
)

# 输出示例：
# 1. "成年人的告别，连眼泪都要忍住"
# 2. "故乡永远在身后，而你正在走向配得上这份牵挂的未来"
# 3. "热闹散场后的安静，才是异乡最真实的底色"
```

## 模板库

### 亲情类模板

```markdown
【开头】场景切入 + 细节描写
高铁缓缓驶出站台，后视镜里父母的身影越来越小...

【正文】3-4 个情感爆发点
1. 离别前的准备（父母的付出）
2. 离别时的场景（不舍的细节）
3. 离别后的感受（孤独与成长）
4. 感悟与升华（理解与感恩）

【结尾】金句 + 互动
"xxx"
📌 互动话题：你的行李箱里，爸妈偷偷塞了什么？
```

### 成长类模板

```markdown
【开头】对比手法
小时候以为...长大后才发现...

【正文】成长的心路历程
1. 曾经的梦想
2. 现实的打击
3. 挣扎与坚持
4. 和解与成长

【结尾】正能量升华
"xxx"
```

### 爱情类模板

```markdown
【开头】悬念式
有些话，当时没说，就再也没机会说了...

【正文】错过的遗憾
1. 相遇的美好
2. 错过的原因
3. 后来的我们
4. 如果当初

【结尾】释然与祝福
"xxx"
```

## 情感词汇库

### 高频情绪词
- 温暖、感动、心疼、泪目、破防
- 孤独、无助、迷茫、挣扎、释然
- 不舍、愧疚、遗憾、怀念、感恩

### 高频场景词
- 高铁站、医院、深夜、出租屋、老家
- 行李箱、后备箱、电话、微信、照片
- 饭菜、拥抱、目送、转身、眼泪

### 高频金句模式
- "xxx 的那一刻，我才明白..."
- "不是 xxx，而是 xxx"
- "你以为...其实..."
- "xxx 永远在 xxx，而你正在 xxx"

## 最佳实践

1. **真实感**：用具体细节代替空洞抒情
2. **代入感**：多用"你"，让读者觉得在说自己
3. **节奏感**：短句为主，适当用排比增强气势
4. **画面感**：多描写少议论，让画面自己说话
5. **共鸣感**：写大多数人的经历，不是个别现象

## 注意事项

1. **避免过度煽情**：真情实感比华丽辞藻更重要
2. **避免说教**：用故事打动人，不用道理说服人
3. **避免套话**：少用"让我们"、"一定要"等说教词汇
4. **避免负能量**：即使写痛苦也要有希望和温暖
5. **避免标题党**：标题要吸引人，但不能欺骗读者

## 与其他技能集成

### 与 wechat_pub 集成

```python
# 在 content_automation_engine.py 中
from wechat_emotional_writer import WechatEmotionalWriter

writer = WechatEmotionalWriter()
article = writer.write(
    topic=selected_topic,
    category=category,
    style="温情治愈"
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
wechat-emotional-writer/
├── SKILL.md
├── scripts/
│   └── wechat_emotional_writer.py
├── templates/
│   ├── family.json
│   ├── growth.json
│   └── love.json
└── examples/
    └── sample_articles.md
```

## 成本说明

- 纯文本生成，无额外 API 调用
- 使用现有 LLM 即可
- 建议设置每日生成上限
