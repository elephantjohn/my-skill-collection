# LESSONS.md - 经验教训库

> 所有踩过的坑和最佳实践，按类别分区管理。  
> 新机器部署时，让 OpenClaw 学习此文件即可继承全部经验。  
> 每次犯错后：追加记录 → 更新相关 SKILL.md → 提交推送。

---

## 目录

- [1. OpenClaw 插件管理](#1-openclaw-插件管理)
- [2. Telegram 多 Bot 配置](#2-telegram-多-bot-配置)
- [3. 配置文件管理](#3-配置文件管理)
- [4. ElevenLabs TTS](#4-elevenlabs-tts)
- [5. 图片生成](#5-图片生成)
- [6. 语音识别（STT）](#6-语音识别stt)
- [7. 工作流与部署](#7-工作流与部署)

---

## 1. OpenClaw 插件管理

### 1.1 插件路径必须用绝对路径

- **日期**：2026-02-25
- **场景**：安装 memory-lancedb-pro 插件
- **错误**：`plugins.load.paths` 用了相对路径 `plugins/memory-lancedb-pro`
- **原因**：gateway 进程的工作目录不一定是 workspace，相对路径会解析到错误位置
- **正确做法**：始终使用绝对路径，如 `/home/ubuntu/.openclaw/workspace/plugins/memory-lancedb-pro`

### 1.2 先读 configSchema 再写配置

- **日期**：2026-02-25
- **场景**：安装 memory-lancedb-pro 插件
- **错误**：`rerank` 放在顶层（和 `embedding` 并列），插件报 `must NOT have additional properties`
- **原因**：没先看插件的 `openclaw.plugin.json` 中的 `configSchema`
- **正确做法**：安装任何插件前，先读 `openclaw.plugin.json`，按 schema 严格填写配置
- **示例**：rerank 相关字段（`rerankApiKey`、`rerankModel`）属于 `retrieval` 对象内部

### 1.3 配置必须一次性完整写入

- **日期**：2026-02-25
- **场景**：安装 memory-lancedb-pro 插件
- **错误**：分多次写入 `paths`、`entries`、`slots`，每次重启 gateway 的 doctor 清掉了无效项
- **原因**：gateway 重启时会校验配置，entries 引用了未 load 的插件会被视为无效并清除
- **正确做法**：`paths` + `entries` + `slots` 必须在同一次写入中完成，写完验证后再重启

### 1.4 插件安装标准流程

```
1. git clone 插件到 workspace/plugins/ 目录
2. cd 进去执行 npm install
3. 读取 openclaw.plugin.json，了解 configSchema
4. 一次性写入 openclaw.json：
   - plugins.load.paths（绝对路径）
   - plugins.entries.<name>（按 schema 填写）
   - plugins.slots.<kind>（如 memory）
5. 验证配置已正确写入
6. openclaw gateway restart
```

---

## 2. Telegram 多 Bot 配置

### 2.1 多 Bot 必须用 accounts 模式

- **日期**：2026-02-22
- **场景**：国资预算 bot 出现重复回复
- **错误**：单一 `botToken` 模式 + 多条 `bindings`
- **原因**：同一消息被多个 agent 同时匹配处理
- **正确做法**：

```json
"channels": {
  "telegram": {
    "accounts": {
      "main": { "botToken": "主bot token" },
      "project_x": { "botToken": "项目bot token" }
    }
  }
},
"bindings": [
  { "agentId": "main", "match": { "channel": "telegram", "accountId": "main" } },
  { "agentId": "project_x", "match": { "channel": "telegram", "accountId": "project_x" } }
]
```

### 2.2 bindings.match 必须用 accountId

- **日期**：2026-02-21
- **场景**：add-project.py 生成的 bindings 无效
- **错误**：使用了已废弃的 `match.account` 字段
- **正确做法**：必须用 `match.accountId`

### 2.3 Bot 显示名可通过 API 修改

- **日期**：2026-02-25
- **场景**：修改 wechat_creater bot 的显示名为「公创」
- **方法**：`curl "https://api.telegram.org/bot<TOKEN>/setMyName" -d "name=公创"`
- **注意**：仅改 Telegram 显示名，不影响内部 project_name 和配置

---

## 3. 配置文件管理

### 3.1 运行时配置 vs 仓库配置

- **运行时**：`~/.openclaw/openclaw.json`（gateway 实际读取）
- **仓库**：`/home/ubuntu/openclaw-server-config/openclaw.json`（版本管理）
- **流程**：修改仓库 → `cp` 到运行时目录 → `openclaw gateway restart`
- **注意**：修改运行时配置后也要同步回仓库并提交

### 3.2 gateway 重启会校验并清理无效配置

- **日期**：2026-02-25
- **场景**：分步写入插件配置
- **现象**：重启后部分配置消失
- **原因**：doctor 会清理引用了不存在插件的 entries 和 slots
- **教训**：所有相关配置必须同时写入，保证引用关系完整

### 3.3 每个 Bot 的 workspace 独立

- **结构**：`~/.openclaw/workspace-<project_name>/`
- **内容**：每个 bot 有独立的 SOUL.md、PROJECT.md、memory 等
- **共享**：所有 bot 共用一份 `openclaw.json`，通过 accounts + bindings 隔离

---

## 4. ElevenLabs TTS

### 4.1 v3 模型不支持 style 参数

- **日期**：2026-02-20
- **场景**：使用 eleven_v3 生成中文语音
- **错误**：`voice_settings` 中包含 `style` 参数，返回 400
- **正确做法**：v3 的 `voice_settings` 只支持 `stability`、`similarity_boost`、`speed`

### 4.2 speed 参数最大 1.2x

- **日期**：2026-02-20
- **场景**：设置 2x 速度播放
- **错误**：API `speed` 设为 2.0，实际被静默限制在 1.2x
- **正确做法**：API 设 `speed: 1.2`，再用 ffmpeg `atempo` 进一步加速
- **公式**：目标 2x → API 1.2x → ffmpeg atempo=1.667（1.2 × 1.667 ≈ 2.0）

### 4.3 音频拼接流程

```
1. 长文本按段落切分（每段 < 5000 字符）
2. 逐段调用 ElevenLabs API 生成音频
3. ffmpeg concat 合并所有片段
4. ffmpeg atempo 调速（如需 >1.2x）
```

---

## 5. 图片生成

### 5.1 优先使用 Nano Banana Pro

- **偏好**：用户指定 Nano Banana Pro（Gemini 3 Pro Image）作为默认图片生成工具
- **API Key**：配置在环境中，使用 skill 调用

---

## 6. 语音识别（STT）

### 6.1 本地 Whisper 配置

- **模型**：base（CPU-only PyTorch）
- **脚本**：`/home/ubuntu/transcribe.py`
- **优势**：无需 API key，离线可用
- **限制**：CPU 模式较慢，中文识别有少量错误

---

## 7. 工作流与部署

### 7.1 创建新 Bot 的标准流程

```
1. 收集信息：project_name、bot_token、description
2. 验证 token：curl getMe
3. 生成 SOUL.md 和 PROJECT.md
4. 执行 add-project.py --dry-run 预览
5. 用户确认后正式执行
6. 复制 openclaw.json 到运行时目录
7. 创建 workspace 目录并复制文件
8. openclaw gateway restart
9. pairing 验证
```

### 7.2 SSH Host Key 验证失败

- **日期**：2026-02-21
- **场景**：尝试 SSH 到 VM-16-15-ubuntu
- **现象**：Host key verification failed
- **解决**：需要用户本地操作，或更新 known_hosts

### 7.3 错误记录流程

```
1. 发生错误时，追加到本文件对应分区
2. 更新相关 SKILL.md（如适用）
3. git add + commit + push 到仓库
4. 新 session 或新机器部署时读取本文件
```

---

## 附录：关键路径速查

| 用途 | 路径 |
|------|------|
| 运行时配置 | `~/.openclaw/openclaw.json` |
| 仓库配置 | `/home/ubuntu/openclaw-server-config/openclaw.json` |
| 主 workspace | `~/.openclaw/workspace/` |
| 项目 workspace | `~/.openclaw/workspace-<name>/` |
| 插件目录 | `~/.openclaw/workspace/plugins/` |
| 技能仓库 | `/home/ubuntu/my-skill-collection/` |
| 服务器配置仓库 | `/home/ubuntu/openclaw-server-config/` |
| Whisper 脚本 | `/home/ubuntu/transcribe.py` |
| ElevenLabs Voice ID | `fKASJ3Uf1WtkAk2W9tUo` |
| ElevenLabs 模型 | `eleven_v3` |
