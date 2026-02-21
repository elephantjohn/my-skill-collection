---
name: elevenlabs
description: ElevenLabs AI 语音全功能工具集 — 支持文字转语音(TTS)、语音转文字(STT)、语音克隆、语音变声、AI音乐生成、文字转对话、音效生成、音频降噪、配音翻译、强制对齐、发音词典、对话式AI Agent等16项功能。通过 ElevenLabs API 为 OpenClaw 赋予完整的 AI 语音能力。
user-invocable: true
disable-model-invocation: false
metadata:
  openclaw:
    emoji: "🎙️"
    os: [darwin, linux, win32]
    requires:
      bins: [curl]
---

# ElevenLabs AI 语音工具集

你是一个 ElevenLabs 语音助手，集成在 OpenClaw 中。当用户触发此技能时，帮助他们使用 ElevenLabs 的各项 AI 语音功能。

## API 基础信息

- **Base URL**: `https://api.elevenlabs.io/v1`
- **认证方式**: HTTP Header `xi-api-key`
- **API Key**: 安装后在 openclaw.json 的 `skills.entries.elevenlabs.apiKey` 中配置
- **套餐建议**: Creator 套餐起步（300,000 字符/月），免费套餐 10,000 字符/月
- **默认模型**: `eleven_v3`（最新，70+ 语言，表现力最强）
- **稳定备选**: `eleven_multilingual_v2`（29 语言，简单易用）
- **低延迟模型**: `eleven_flash_v2_5`（适合实时对话）

## 功能列表（共 16 项）

### 核心生成功能

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 文字转语音 (TTS) | `POST /text-to-speech/{voice_id}` | 将文字转为语音音频 |
| 文字转语音 (流式) | `POST /text-to-speech/{voice_id}/stream` | 流式返回音频 |
| 语音转文字 (STT) | `POST /speech-to-text` | 音频转录为文字，支持说话人分离 |
| AI 音乐生成 | `POST /music/generate` | 用文字描述生成音乐 |
| 文字转对话 | `POST /text-to-dialogue` | 生成多角色自然对话音频 |
| 音效生成 | `POST /sound-generation` | 用自然语言描述生成音效 |

### 语音处理功能

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 语音变声 | `POST /speech-to-speech/{voice_id}` | 将一段音频转为另一个声音 |
| 音频降噪 | `POST /audio-isolation` | 从音频中去除背景噪音 |
| 配音翻译 | `POST /dubbing` | 将音视频翻译配音为其他语言 |
| 强制对齐 | `POST /forced-alignment` | 音频与文字的时间戳精确对齐 |

### 语音管理功能

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 语音克隆 | `POST /voices/add` | 上传音频创建克隆语音 |
| 语音库浏览 | `GET /shared-voices` | 浏览社区共享的 10,000+ 语音 |
| 发音词典 | `POST /pronunciation-dictionaries` | 自定义特定词汇的发音方式 |

### 高级功能

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 对话式 AI Agent | `POST /convai/agents` | 创建实时语音对话 Agent |
| 项目/工作室 | `GET /projects` | 长篇有声书/播客制作 |

### 账户管理

| 功能 | API 端点 | 说明 |
|------|---------|------|
| 语音列表 | `GET /voices` | 列出所有可用语音 |
| 模型列表 | `GET /models` | 列出所有可用模型 |
| 用户信息 | `GET /user` | 查看账户信息和用量 |
| 历史记录 | `GET /history` | 查看生成历史 |

## 使用流程

### 第一步：理解用户需求

用户可能的需求场景：
1. **"帮我把这段文字转成语音"** → 文字转语音 (TTS)
2. **"帮我生成一段音效"** → 音效生成
3. **"帮我把这段音频降噪"** → 音频降噪
4. **"帮我把这段视频翻译成中文配音"** → 配音翻译
5. **"我想用某个声音读这段话"** → 先查语音列表，再 TTS
6. **"帮我变声"** → 语音变声 (Speech-to-Speech)
7. **"把这段音频转成文字"** → 语音转文字 (Scribe)
8. **"帮我生成一段背景音乐"** → AI 音乐生成
9. **"帮我克隆一个声音"** → 语音克隆
10. **"生成两个人的对话音频"** → 文字转对话
11. **"帮我对齐字幕和音频"** → 强制对齐
12. **"自定义某个词的发音"** → 发音词典
13. **"创建一个语音客服机器人"** → 对话式 AI Agent
14. **"查看我的额度"** → 用户信息

### 第二步：根据需求执行对应功能

---

## 功能一：文字转语音 (TTS)

这是最常用的功能。将文字转为高质量语音音频。

### 常用语音 ID

先通过 API 查询可用语音：

```bash
curl -s "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" | python3 -m json.tool
```

**常见预设语音**（ElevenLabs 内置）：

| 语音名称 | 风格 | 适用场景 |
|---------|------|---------|
| Rachel | 女性、温暖 | 旁白、有声书 |
| Adam | 男性、深沉 | 新闻播报 |
| Antoni | 男性、亲切 | 对话、教程 |
| Bella | 女性、柔和 | 冥想、ASMR |
| Domi | 女性、活力 | 营销、广告 |
| Elli | 女性、年轻 | 动画、游戏 |
| Josh | 男性、年轻 | 播客 |
| Sam | 男性、沙哑 | 叙事 |

### TTS 生成命令

```bash
# 基础 TTS（输出为 mp3）
curl -s "https://api.elevenlabs.io/v1/text-to-speech/<VOICE_ID>" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<TEXT_TO_SPEAK>",
    "model_id": "eleven_v3",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75,
      "style": 0.0,
      "use_speaker_boost": true
    }
  }' \
  --output "<OUTPUT_FILE>.mp3"
```

### voice_settings 参数说明

| 参数 | 范围 | 说明 |
|------|------|------|
| `stability` | 0.0-1.0 | 稳定性。低=更富表现力/多变，高=更稳定/一致 |
| `similarity_boost` | 0.0-1.0 | 相似度增强。越高越接近原始声音，但可能有瑕疵 |
| `style` | 0.0-1.0 | 风格增强。增加说话风格，但会增加延迟 |
| `use_speaker_boost` | true/false | 说话者增强。提升声音清晰度 |
| `speed` | 0.7-1.2 | 语速调节（部分模型支持）|

### 输出格式选项

通过 `output_format` 查询参数指定：

| 格式 | 说明 |
|------|------|
| `mp3_44100_128` | MP3 44.1kHz 128kbps（默认）|
| `mp3_44100_192` | MP3 44.1kHz 192kbps |
| `pcm_16000` | PCM 16kHz |
| `pcm_22050` | PCM 22.05kHz |
| `pcm_24000` | PCM 24kHz |
| `pcm_44100` | PCM 44.1kHz |
| `ulaw_8000` | u-law 8kHz（电话质量）|

```bash
# 指定高质量输出格式
curl -s "https://api.elevenlabs.io/v1/text-to-speech/<VOICE_ID>?output_format=mp3_44100_192" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text": "<TEXT>", "model_id": "eleven_v3"}' \
  --output output.mp3
```

---

## 功能二：音效生成

用自然语言描述生成音效（如"雷雨声"、"脚步声"、"玻璃破碎"）。

```bash
curl -s "https://api.elevenlabs.io/v1/sound-generation" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<DESCRIPTION_OF_SOUND_EFFECT>",
    "duration_seconds": 5.0
  }' \
  --output sound_effect.mp3
```

**示例描述**：
- `"Heavy rain with distant thunder"` — 暴雨加远处雷声
- `"Footsteps on gravel, slow pace"` — 碎石路上的慢步行走
- `"Glass breaking and shattering on tile floor"` — 玻璃在瓷砖地面上破碎
- `"Crowd cheering in a stadium"` — 体育场观众欢呼
- `"Cat purring softly"` — 猫咪轻柔的呼噜声

---

## 功能三：语音变声 (Speech-to-Speech)

将一段音频转为另一个声音的音色，保留原始的情感和节奏。

```bash
curl -s "https://api.elevenlabs.io/v1/speech-to-speech/<VOICE_ID>" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "audio=@<INPUT_AUDIO_FILE>" \
  -F "model_id=eleven_v3" \
  --output converted_voice.mp3
```

---

## 功能四：音频降噪 (Audio Isolation)

从音频中分离人声，去除背景噪音、音乐等。

```bash
curl -s "https://api.elevenlabs.io/v1/audio-isolation" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "audio=@<INPUT_AUDIO_FILE>" \
  --output isolated_voice.mp3
```

---

## 功能五：配音翻译 (Dubbing)

将音频/视频翻译配音为其他语言，保留原始说话者的语气和节奏。

```bash
# 从文件配音
curl -s "https://api.elevenlabs.io/v1/dubbing" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "file=@<INPUT_VIDEO_OR_AUDIO>" \
  -F "target_lang=zh" \
  -F "source_lang=en" \
  --output dubbing_response.json

# 从 URL 配音
curl -s "https://api.elevenlabs.io/v1/dubbing" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "<VIDEO_URL>",
    "target_lang": "zh",
    "source_lang": "en"
  }' \
  --output dubbing_response.json
```

**支持的语言代码示例**：`en`(英语), `zh`(中文), `ja`(日语), `ko`(韩语), `es`(西班牙语), `fr`(法语), `de`(德语), `pt`(葡萄牙语), `it`(意大利语), `hi`(印地语), `ar`(阿拉伯语)

配音是异步操作，返回 `dubbing_id`，需要轮询状态：

```bash
# 查询配音状态
curl -s "https://api.elevenlabs.io/v1/dubbing/<DUBBING_ID>" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>"

# 下载配音后的音频
curl -s "https://api.elevenlabs.io/v1/dubbing/<DUBBING_ID>/audio/<LANGUAGE_CODE>" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  --output dubbed_audio.mp3
```

---

## 功能六：语音转文字 (Speech-to-Text / Scribe)

将音频转录为文字，支持说话人分离（diarization）和字级时间戳。

```bash
curl -s "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "file=@<AUDIO_FILE>" \
  -F "model_id=scribe_v1" \
  -F "language_code=zh"
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `file` | 音频文件（mp3/wav/m4a 等）|
| `model_id` | 固定为 `scribe_v1` |
| `language_code` | 语言代码（`zh`中文, `en`英语, `ja`日语等），不填则自动检测 |
| `diarize` | 设为 `true` 启用说话人分离（识别不同说话者）|
| `timestamps_granularity` | `word` 或 `character`，返回每个词/字的时间戳 |

---

## 功能七：AI 音乐生成 (Eleven Music)

用自然语言描述生成音乐，支持各种风格和流派。

```bash
# 通过 prompt 生成音乐
curl -s "https://api.elevenlabs.io/v1/music/generate" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "<MUSIC_DESCRIPTION>"
  }' \
  --output music.mp3
```

**示例 prompt**：
- `"Upbeat electronic dance music with heavy bass drops, 128 BPM"` — 电子舞曲
- `"Soft acoustic guitar with gentle piano, relaxing ambient"` — 轻柔原声吉他
- `"Epic orchestral cinematic score with dramatic strings"` — 史诗管弦乐
- `"Lo-fi hip hop beat with jazzy chords, chill and relaxing"` — Lo-fi 嘻哈
- `"Traditional Chinese erhu melody with modern arrangement"` — 中国二胡旋律

---

## 功能八：语音克隆 (Voice Cloning)

上传音频样本创建自己的克隆语音。支持即时克隆（10 秒音频即可）和专业克隆（需要更多样本）。

### 即时语音克隆（Instant Voice Clone）

```bash
curl -s "https://api.elevenlabs.io/v1/voices/add" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "name=<VOICE_NAME>" \
  -F "description=<VOICE_DESCRIPTION>" \
  -F "files=@<AUDIO_SAMPLE_1.mp3>" \
  -F "files=@<AUDIO_SAMPLE_2.mp3>"
```

**要求**：
- 至少上传 1 个音频文件（建议 10 秒以上清晰录音）
- 多个样本效果更好
- 音频应无背景噪音
- 仅限本人声音或已获授权的声音

**注意**：API Key 需要有 `create_instant_voice_clone` 权限。在 ElevenLabs 后台的 API Key 设置中启用。

### 克隆后使用

```bash
# 返回 JSON 中包含 voice_id，之后用这个 ID 做 TTS
curl -s "https://api.elevenlabs.io/v1/text-to-speech/<CLONED_VOICE_ID>" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text": "用我自己的声音说话", "model_id": "eleven_v3"}' \
  --output my_voice.mp3
```

---

## 功能九：文字转对话 (Text to Dialogue)

生成多角色自然对话音频，自动分配不同声音给不同角色。

```bash
curl -s "https://api.elevenlabs.io/v1/text-to-dialogue" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "text": "Hello, how can I help you today?",
        "voice_id": "<VOICE_ID_1>"
      },
      {
        "text": "I would like to know about your services.",
        "voice_id": "<VOICE_ID_2>"
      }
    ],
    "model_id": "eleven_v3"
  }' \
  --output dialogue.mp3
```

适用场景：播客对话、教学对话、有声剧、游戏对白。

---

## 功能十：强制对齐 (Forced Alignment)

将音频和对应文字精确对齐，生成每个词/字的时间戳。适合制作字幕。

```bash
curl -s "https://api.elevenlabs.io/v1/forced-alignment" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "file=@<AUDIO_FILE>" \
  -F "text=<CORRESPONDING_TEXT>"
```

返回 JSON 包含每个词的 `start_time` 和 `end_time`，可用于：
- 生成精确字幕 (SRT/VTT)
- 卡拉 OK 式同步歌词
- 视频字幕自动对齐

---

## 功能十一：语音库浏览 (Voice Library)

浏览 ElevenLabs 社区共享的 10,000+ 语音，添加到自己的收藏。

```bash
# 浏览语音库（分页）
curl -s "https://api.elevenlabs.io/v1/shared-voices?page_size=20" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  | python3 -c "
import sys,json
d=json.load(sys.stdin)
for v in d.get('voices',[]):
    print(f\"{v['voice_id']}: {v['name']} ({v.get('language','')}) - {v.get('category','')}\")
"

# 按关键词搜索
curl -s "https://api.elevenlabs.io/v1/shared-voices?page_size=10&search=chinese" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>"

# 把社区语音添加到自己的账户
curl -s -X POST "https://api.elevenlabs.io/v1/voices/add/<VOICE_ID>/add" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>"
```

---

## 功能十二：发音词典 (Pronunciation Dictionaries)

自定义特定词汇的发音方式，确保 TTS 正确读出专有名词、品牌名等。

```bash
# 创建发音词典（从规则）
curl -s "https://api.elevenlabs.io/v1/pronunciation-dictionaries/create-from-rules" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-dictionary",
    "rules": [
      {"string_or_regex": "OpenClaw", "type": "phoneme", "phoneme": "oʊpən klɔː", "alphabet": "ipa"},
      {"string_or_regex": "ElevenLabs", "type": "alias", "alias": "Eleven Labs"}
    ]
  }'

# 查看所有词典
curl -s "https://api.elevenlabs.io/v1/pronunciation-dictionaries" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>"
```

在 TTS 请求中使用词典：在 `voice_settings` 中添加 `pronunciation_dictionary_locators` 参数引用词典 ID。

---

## 功能十三：对话式 AI Agent (Conversational AI)

创建可实时对话的 AI 语音 Agent，支持电话、网页嵌入等场景。

```bash
# 列出所有 Agent
curl -s "https://api.elevenlabs.io/v1/convai/agents" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>"

# 创建 Agent
curl -s "https://api.elevenlabs.io/v1/convai/agents/create" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Service Bot",
    "conversation_config": {
      "agent": {
        "prompt": {
          "prompt": "You are a helpful customer service agent. Be polite and concise."
        },
        "first_message": "Hello! How can I help you today?",
        "language": "en"
      },
      "tts": {
        "voice_id": "<VOICE_ID>"
      }
    }
  }'
```

**Conversational AI 特性**：
- 延迟低于 100ms
- 支持 32+ 语言
- 可接入 LLM（Claude、GPT、Gemini 等）
- 支持函数调用（查数据库、调 API 等）
- 可嵌入网页 Widget 或接入电话线路

---

## 功能十四：项目/工作室 (Studio/Projects)

用于长篇内容制作，如有声书、播客系列等。在 ElevenLabs 网页端操作更方便，API 提供基础管理能力。

```bash
# 查看所有项目
curl -s "https://api.elevenlabs.io/v1/projects" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>"
```

**注意**：Projects API 需要更高权限，部分操作建议在 https://elevenlabs.io/app/projects 网页端完成。

---

## 功能十五：查看账户与用量

```bash
# 查看用户信息和剩余额度
curl -s "https://api.elevenlabs.io/v1/user" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" | python3 -m json.tool

# 查看可用模型
curl -s "https://api.elevenlabs.io/v1/models" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" | python3 -m json.tool

# 查看生成历史
curl -s "https://api.elevenlabs.io/v1/history" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" | python3 -m json.tool
```

---

## 可用模型

| 模型 ID | 说明 |
|---------|------|
| `eleven_v3` | **最新** v3（70+ 语言，最强表现力，需要更精确的 prompt）|
| `eleven_multilingual_v2` | 多语言 v2（29 种语言，最逼真、情感最丰富）|
| `eleven_flash_v2_5` | Flash v2.5（32 种语言，超低延迟，适合对话场景）|
| `eleven_turbo_v2_5` | Turbo v2.5（32 种语言，质量与延迟平衡）|
| `eleven_turbo_v2` | Turbo v2（仅英语，低延迟）|
| `eleven_english_sts_v2` | English STS v2（英语语音变声专用）|
| `eleven_multilingual_sts_v2` | Multilingual STS v2（多语言语音变声专用）|

建议：追求最高质量用 `eleven_v3`，稳定多语言用 `eleven_multilingual_v2`，对延迟敏感用 `eleven_flash_v2_5`，语音变声用对应 STS 模型。

---

## 实用组合示例

### 示例 1：快速生成中文语音旁白

```bash
# 1. 查看可用语音，找到合适的 voice_id
curl -s "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  | python3 -c "import sys,json; [print(f\"{v['voice_id']}: {v['name']}\") for v in json.load(sys.stdin)['voices']]"

# 2. 用选中的语音生成中文音频
curl -s "https://api.elevenlabs.io/v1/text-to-speech/<VOICE_ID>?output_format=mp3_44100_192" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用 ElevenLabs 语音合成服务。",
    "model_id": "eleven_v3",
    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
  }' \
  --output narration.mp3
```

### 示例 2：为视频生成背景音效

```bash
curl -s "https://api.elevenlabs.io/v1/sound-generation" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Gentle ocean waves with seagulls in the background", "duration_seconds": 10.0}' \
  --output ocean_ambience.mp3
```

### 示例 3：录音降噪后变声

```bash
# 1. 先降噪
curl -s "https://api.elevenlabs.io/v1/audio-isolation" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "audio=@raw_recording.mp3" \
  --output clean_audio.mp3

# 2. 再变声
curl -s "https://api.elevenlabs.io/v1/speech-to-speech/<VOICE_ID>" \
  -H "xi-api-key: <YOUR_ELEVENLABS_API_KEY>" \
  -F "audio=@clean_audio.mp3" \
  -F "model_id=eleven_v3" \
  --output final_output.mp3
```

---

## 注意事项

1. **字符计费**: 每个字符都计费，包括空格和标点。请注意用量。
2. **文件大小限制**: 上传音频文件通常限制在 50MB 以内。
3. **中文支持**: 使用 `eleven_v3`（推荐）或 `eleven_multilingual_v2` 模型才支持中文。
4. **配音是异步的**: dubbing API 不会立即返回结果，需要轮询 `dubbing_id` 查状态。
5. **音频格式**: 输入支持 mp3、wav、m4a 等常见格式。
6. **速率限制**: 免费用户有并发限制，付费用户限制更宽。

## 故障排查

| 错误 | 原因 | 解决 |
|------|------|------|
| 401 `payment_issue` | 订阅付款失败或未完成 | 到 https://elevenlabs.io/subscription 完成支付 |
| 401 Unauthorized | API Key 无效或过期 | 检查 key 是否正确 |
| 422 Validation Error | 请求参数有误 | 检查 voice_id、model_id 等参数 |
| 429 Too Many Requests | 超出速率限制 | 等待后重试，或升级计划 |
| 额度用完 | 月度字符额度耗尽 | 升级计划或等待下月刷新 |
